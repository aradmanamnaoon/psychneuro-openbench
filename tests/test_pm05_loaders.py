"""PM-05 regression tests: deterministic exports, rights gate, and negative quality paths."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from psychneuro.loaders import load_dataset, manifest_json
from psychneuro.quality import DataQualityError, validate_quality
from psychneuro.synthetic import (
    CSV_COLUMNS,
    SyntheticConfig,
    dataset_card,
    generate_trials,
    to_csv_text,
)

REGISTRY = Path(__file__).resolve().parents[1] / "data" / "registry.json"


@pytest.fixture
def config() -> SyntheticConfig:
    return SyntheticConfig(seed=31, n_participants=3, trials_per_participant=4)


def test_explicit_synthetic_fallback_has_no_raw_file_hash(config: SyntheticConfig) -> None:
    loaded = load_dataset(config, REGISTRY)
    assert loaded.quality.valid
    assert loaded.quality.n_trials == 12
    assert loaded.provenance.raw_file_sha256 is None
    assert loaded.provenance.rights_basis == "synthetic-original"
    assert loaded.provenance.input_format == "generator"
    assert json.loads(manifest_json(loaded.provenance))["raw_file_sha256"] is None


def test_generation_is_reproducible(config: SyntheticConfig) -> None:
    first = load_dataset(config, REGISTRY)
    second = load_dataset(config, REGISTRY)
    assert first.records == second.records
    assert first.provenance == second.provenance


def test_csv_round_trip_hashes_real_bytes(tmp_path: Path, config: SyntheticConfig) -> None:
    data = load_dataset(config, REGISTRY)
    path = tmp_path / "fixture.csv"
    raw = to_csv_text(data.records).encode("utf-8")
    path.write_bytes(raw)
    read = load_dataset(path, REGISTRY, card=data.card)
    assert read.records == data.records
    assert read.provenance.raw_file_sha256 == hashlib.sha256(raw).hexdigest()
    assert read.provenance.canonical_csv_sha256 == data.card["source_sha256"]
    assert read.provenance.transformations == ()


def test_noncanonical_csv_newlines_have_distinct_raw_hash(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    data = load_dataset(config, REGISTRY)
    path = tmp_path / "windows.csv"
    raw = to_csv_text(data.records).replace("\n", "\r\n").encode()
    path.write_bytes(raw)
    loaded = load_dataset(path, REGISTRY, card=data.card)
    assert loaded.provenance.raw_file_sha256 == hashlib.sha256(raw).hexdigest()
    assert loaded.provenance.raw_file_sha256 != loaded.provenance.canonical_csv_sha256


def test_missing_file_does_not_silently_fallback(tmp_path: Path, config: SyntheticConfig) -> None:
    card = dataset_card(config, generate_trials(config))
    with pytest.raises(ValueError, match="existing regular"):
        load_dataset(tmp_path / "missing.csv", REGISTRY, card=card)


def test_external_attestation_cannot_authorize_file(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    card = dict(dataset_card(config, generate_trials(config)))
    card["source_kind"] = "external_human"
    path = tmp_path / "data.csv"
    path.write_text(to_csv_text(generate_trials(config)), encoding="utf-8")
    with pytest.raises(ValueError, match="external"):
        load_dataset(path, REGISTRY, card=card)


def test_missing_card_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="reviewed dataset card"):
        load_dataset(tmp_path / "unknown.csv", REGISTRY)


def test_generated_cannot_accept_user_attestation(config: SyntheticConfig) -> None:
    with pytest.raises(ValueError, match="caller-supplied"):
        load_dataset(config, REGISTRY, card={})


def test_wrong_header_and_extra_column_rejected(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    path = tmp_path / "test.csv"
    raw = to_csv_text(generate_trials(config))
    path.write_text(raw.replace("dataset_id", "unknown_id", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="CSV header"):
        load_dataset(path, REGISTRY, card=dataset_card(config, generate_trials(config)))
    path.write_text(raw.replace("generator_seed\n", "generator_seed,extra\n", 1))
    with pytest.raises(ValueError, match="CSV header"):
        load_dataset(path, REGISTRY, card=dataset_card(config, generate_trials(config)))


def test_bad_missing_numeric_value_fails_closed(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    raw = to_csv_text(generate_trials(config))
    rows = list(csv.reader(io.StringIO(raw)))
    idx = rows[0].index("difficulty")
    rows[1][idx] = ""
    path = tmp_path / "empty.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        csv.writer(stream).writerows(rows)
    with pytest.raises(ValueError, match="difficulty"):
        load_dataset(path, REGISTRY, card=dataset_card(config, generate_trials(config)))


@pytest.mark.parametrize("field,value", [
    ("participant_id", ""), ("trial_id", "first last"),
    ("difficulty", float("nan")), ("difficulty", 1.5),
    ("response_time_ms", -1.0), ("response_time_ms", float("inf")),
    ("response_time_ms", 10.0), ("response_time_ms", 10_001.0),
])
def test_quality_rejects_missing_or_out_of_range(
    config: SyntheticConfig, field: str, value: object
) -> None:
    rows = list(generate_trials(config))
    rows[0] = replace(rows[0], **{field: value})
    with pytest.raises(DataQualityError) as error:
        validate_quality(rows)
    assert not error.value.summary.valid
    assert error.value.summary.errors



def test_quality_summary_counts_missing_numeric_cell(config: SyntheticConfig) -> None:
    records = list(generate_trials(config))
    records[0] = replace(records[0], difficulty=None)
    with pytest.raises(DataQualityError) as error:
        validate_quality(records)
    assert error.value.summary.missing_values == 1
    assert error.value.summary.invalid_ranges_or_types >= 1


def test_collision_quality_summary(config: SyntheticConfig) -> None:
    rows = list(generate_trials(config))
    rows[1] = rows[0]
    with pytest.raises(DataQualityError) as error:
        validate_quality(rows)
    assert error.value.summary.duplicate_trial_keys == 1
    assert error.value.summary.duplicate_trial_orders >= 1


def test_duplicate_order_in_session(config: SyntheticConfig) -> None:
    rows = list(generate_trials(config))
    rows[1] = replace(rows[1], trial_order=rows[0].trial_order)
    with pytest.raises(DataQualityError) as error:
        validate_quality(rows)
    assert error.value.summary.duplicate_trial_orders == 1


def test_forged_source_with_updated_hash_cannot_replay(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    rows = list(generate_trials(config))
    rows[0] = replace(rows[0], difficulty=0.25)
    card = dict(dataset_card(config, generate_trials(config)))
    raw = to_csv_text(rows)
    card["source_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
    path = tmp_path / "forged.csv"
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(ValueError, match="exact replay"):
        load_dataset(path, REGISTRY, card=card)


def test_unsupported_file_extension_rejected(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    path = tmp_path / "file.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="only local"):
        load_dataset(path, REGISTRY, card=dataset_card(config, generate_trials(config)))


def test_reject_oversized_file(tmp_path: Path, config: SyntheticConfig) -> None:
    path = tmp_path / "too-big.csv"
    with path.open("wb") as stream:
        stream.truncate(32 * 1024 * 1024 + 1)
    with pytest.raises(ValueError, match="size limit"):
        load_dataset(path, REGISTRY, card=dataset_card(config, generate_trials(config)))


def test_parquet_round_trip_optional(tmp_path: Path, config: SyntheticConfig) -> None:
    arrow = pytest.importorskip("pyarrow")
    parquet = pytest.importorskip("pyarrow.parquet")
    rows = generate_trials(config)
    card = dataset_card(config, rows)
    table = arrow.Table.from_pylist([asdict(rec) for rec in rows])
    table = table.select(list(CSV_COLUMNS))
    path = tmp_path / "fixture.parquet"
    parquet.write_table(table, path)
    loaded = load_dataset(path, REGISTRY, card=card)
    assert loaded.records == rows
    assert loaded.provenance.input_format == "parquet"
    assert len(loaded.provenance.raw_file_sha256 or "") == 64


def test_missing_registry_fails_closed(tmp_path: Path, config: SyntheticConfig) -> None:
    with pytest.raises(FileNotFoundError):
        load_dataset(config, tmp_path / "registry-missing.json")
