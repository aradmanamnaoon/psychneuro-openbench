"""Offline, provenance-gated CSV/Parquet ingestion of original synthetic v0 exports.

External participant datasets and URLs are never admitted or downloaded. Parsing an
untrusted file does not itself grant a dataset-rights attestation.
"""
from __future__ import annotations

import csv
import hashlib
import importlib
import io
import json
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import cast

from .quality import QualitySummary, validate_quality
from .registry import RegistryEntry, load_registry
from .schema import ValidatedDataset, validate_synthetic_dataset
from .synthetic import (
    CSV_COLUMNS, MAX_TRIALS, SCHEMA_VERSION, DatasetCard, Side, SyntheticConfig,
    TrialRecord, dataset_card, generate_trials,
)

_MAX_FILE_BYTES = 32 * 1024 * 1024
_INTEGER = re.compile(r"-?[0-9]+\Z")
_STRINGS = frozenset({"dataset_id", "participant_id", "session_id",
                       "trial_id", "stimulus_condition", "response"})
_INTEGERS = frozenset({"trial_order", "correct", "generator_seed"})
_FLOATS = frozenset({"difficulty", "response_time_ms"})


@dataclass(frozen=True, slots=True)
class ProvenanceManifest:
    schema_version: str
    dataset_id: str
    source_kind: str
    source_url: str
    source_version: str
    source_ref: str
    license: str
    rights_basis: str
    consent_boundary: str
    usage_limitations: str
    generator_revision: str
    generator_seed: int
    input_format: str
    raw_file_sha256: str | None
    canonical_csv_sha256: str
    transformations: tuple[str, ...]
    n_trials: int


@dataclass(frozen=True, slots=True)
class LoadedDataset:
    records: tuple[TrialRecord, ...]
    card: DatasetCard
    schema: ValidatedDataset
    quality: QualitySummary
    registry_entry: RegistryEntry
    provenance: ProvenanceManifest


def manifest_json(manifest: ProvenanceManifest) -> str:
    """Machine-readable attestation; missing raw bytes are represented by null."""
    return json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n"


def _int(value: object, column: str) -> int:
    if type(value) is int:
        return value
    if isinstance(value, str) and _INTEGER.fullmatch(value):
        return int(value)
    raise ValueError(f"invalid integer or missing value: {column}")


def _float(value: object, column: str) -> float:
    if type(value) is float:
        return value
    if isinstance(value, str) and value.strip():
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"invalid float: {column}") from exc
    raise ValueError(f"invalid float or missing value: {column}")


def _record(row: Mapping[str, object]) -> TrialRecord:
    if set(row) != set(CSV_COLUMNS):
        raise ValueError("missing, duplicate or unexpected trial column")
    for column in _STRINGS:
        value = row[column]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"missing or invalid string: {column}")
    return TrialRecord(
        dataset_id=cast(str, row["dataset_id"]),
        participant_id=cast(str, row["participant_id"]),
        session_id=cast(str, row["session_id"]),
        trial_id=cast(str, row["trial_id"]),
        trial_order=_int(row["trial_order"], "trial_order"),
        stimulus_condition=cast(Side, row["stimulus_condition"]),
        difficulty=_float(row["difficulty"], "difficulty"),
        correct=_int(row["correct"], "correct"),
        response=cast(Side, row["response"]),
        response_time_ms=_float(row["response_time_ms"], "response_time_ms"),
        generator_seed=_int(row["generator_seed"], "generator_seed"),
    )


def _read_csv(data: bytes) -> tuple[TrialRecord, ...]:
    text = data.decode("utf-8", errors="strict")
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if header != list(CSV_COLUMNS):
            raise ValueError("CSV header must exactly match the v0 column order")
        records: list[TrialRecord] = []
        for number, cells in enumerate(reader, start=2):
            if number > MAX_TRIALS + 1:
                raise ValueError("too many trial records")
            if len(cells) != len(CSV_COLUMNS):
                raise ValueError(f"CSV row {number}: wrong number of fields")
            try:
                records.append(_record(dict(zip(CSV_COLUMNS, cells, strict=True))))
            except ValueError as exc:
                raise ValueError(f"CSV row {number}: {exc}") from exc
        return tuple(records)
    except csv.Error as exc:
        raise ValueError(f"malformed CSV: {exc}") from exc


def _read_parquet(path: Path) -> tuple[TrialRecord, ...]:
    try:
        parquet = importlib.import_module("pyarrow.parquet")
        arrow = importlib.import_module("pyarrow")
    except ImportError as exc:
        raise RuntimeError("Parquet requires optional dependency: pip install '.[parquet]'") from exc
    metadata = getattr(parquet, "read_metadata")(path)
    if metadata.num_rows > MAX_TRIALS:
        raise ValueError("too many parquet trial records")
    table = getattr(parquet, "read_table")(path)
    if table.column_names != list(CSV_COLUMNS):
        raise ValueError("Parquet columns must exactly match the v0 column order")
    for field in table.schema:
        name: str = field.name
        kind = field.type
        if name in _STRINGS and not (
            getattr(arrow, "types").is_string(kind) or getattr(arrow, "types").is_large_string(kind)
        ):
            raise ValueError(f"Parquet column type mismatch: {name}")
        if name in _INTEGERS and not getattr(arrow, "types").is_integer(kind):
            raise ValueError(f"Parquet column type mismatch: {name}")
        if name in _FLOATS and not getattr(arrow, "types").is_floating(kind):
            raise ValueError(f"Parquet column type mismatch: {name}")
    rows = table.to_pylist()
    if len(rows) > MAX_TRIALS:
        raise ValueError("too many parquet trial records")
    return tuple(_record(row) for row in rows)


def _read_local(path: Path) -> tuple[tuple[TrialRecord, ...], str, str]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("source must be an existing regular, non-symlink local file")
    if path.stat().st_size > _MAX_FILE_BYTES:
        raise ValueError("file size limit exceeded")
    extension = path.suffix.lower()
    if extension not in {".csv", ".parquet"}:
        raise ValueError("only local .csv or .parquet is supported")
    content = path.read_bytes()
    if len(content) > _MAX_FILE_BYTES:
        raise ValueError("file size limit exceeded")
    raw_sha256 = hashlib.sha256(content).hexdigest()
    if extension == ".csv":
        return _read_csv(content), "csv", raw_sha256
    return _read_parquet(path), "parquet", raw_sha256


def load_dataset(
    source: SyntheticConfig | Path,
    registry_path: Path,
    *,
    card: Mapping[str, object] | None = None,
) -> LoadedDataset:
    """Load known generator or local export through exactly the same validation gate.

    No implicit fallback: a missing/untrusted file is an error. To choose the
    explicit synthetic fallback, pass SyntheticConfig instead of a file path.
    External registry entries are never enabled by this method.
    """
    entries = load_registry(registry_path)
    if isinstance(source, SyntheticConfig):
        if card is not None:
            raise ValueError("generated input cannot accept a caller-supplied card")
        records = generate_trials(source)
        document = dataset_card(source, records)
        raw_hash: str | None = None
        input_format = "generator"
    elif isinstance(source, Path):
        if card is None:
            raise ValueError("local files require a reviewed dataset card")
        if card.get("source_kind") != "synthetic" or card.get("synthetic") is not True:
            raise ValueError("external human/unknown sources are disabled for v0")
        records, input_format, raw_hash = _read_local(source)
        document = cast(DatasetCard, dict(card))
    else:
        raise TypeError("source must be SyntheticConfig or a local Path")
    entry = next((e for e in entries if e.dataset_id == document["dataset_id"]), None)
    if entry is None or not entry.enabled or entry.source_kind != "synthetic":
        raise ValueError("dataset not approved by registry for synthetic-only v0")
    quality = validate_quality(records)
    schema = validate_synthetic_dataset(records, document)
    # Ingestion cannot be self-authorized by forging a card and checksum:
    # require byte-equivalent *records* from the reviewed deterministic generator.
    if isinstance(source, Path):
        n_participants = document["n_participants"]
        n_trials = document["n_trials"]
        if type(n_participants) is not int or type(n_trials) is not int or n_participants <= 0:
            raise ValueError("invalid generator dimension card")
        if n_trials % n_participants:
            raise ValueError("nonuniform generator trial count")
        config = SyntheticConfig(
            seed=document["generator_seed"], dataset_id=document["dataset_id"],
            n_participants=n_participants, trials_per_participant=n_trials // n_participants,
            session_id=records[0].session_id,
        )
        if records != generate_trials(config):
            raise ValueError("file is not an exact replay of the reviewed synthetic generator")
    manifest = ProvenanceManifest(
        schema_version=SCHEMA_VERSION,
        dataset_id=schema.dataset_id,
        source_kind=entry.source_kind,
        source_url=entry.source_url,
        source_version=entry.source_version,
        source_ref=entry.source_ref,
        license=entry.license,
        rights_basis=entry.rights_basis,
        consent_boundary=entry.consent_boundary,
        usage_limitations=entry.usage_limitations,
        generator_revision=document["generator_revision"],
        generator_seed=document["generator_seed"],
        input_format=input_format,
        raw_file_sha256=raw_hash,
        canonical_csv_sha256=schema.source_sha256,
        transformations=tuple(document["transforms"]),
        n_trials=schema.n_trials,
    )
    return LoadedDataset(
        records=records, card=document, schema=schema, quality=quality,
        registry_entry=entry, provenance=manifest,
    )
