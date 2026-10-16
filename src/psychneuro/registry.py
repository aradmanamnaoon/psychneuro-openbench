"""Fail-closed registry for original synthetic v0 fixtures.

Public dataset metadata is a research lead, not an ingestion permission.
This module neither downloads nor parses external participant records.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
from collections.abc import Mapping

from .schema import ValidatedDataset, validate_synthetic_dataset
from .synthetic import (
    SCHEMA_VERSION,
    DatasetCard,
    SyntheticConfig,
    TrialRecord,
    dataset_card,
    generate_trials,
)

_SYNTHETIC_ID = "psychneuro-synthetic-v0"
_GENERATOR = "psychneuro.synthetic.generate_trials"
_SYNTHETIC_URL = (
    "https://github.com/aradmanamnaoon/psychneuro-openbench/"
    "blob/main/src/psychneuro/synthetic.py"
)
_PUBLIC_LICENSES = frozenset({"CC0-1.0", "PDDL-1.0"})


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    """Versioned metadata; enabled never implies scientific validity."""

    dataset_id: str
    source_kind: str
    modality: str
    source_url: str
    source_version: str
    source_ref: str
    license: str
    rights_basis: str
    consent_boundary: str
    usage_limitations: str
    review_state: str
    enabled: bool
    download_allowed: bool
    participant_data_ingestion_allowed: bool


def _string(entry: Mapping[str, object], key: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing or invalid registry field: {key}")
    return value


def _boolean(entry: Mapping[str, object], key: str) -> bool:
    value = entry.get(key)
    if type(value) is not bool:
        raise ValueError(f"missing or invalid boolean registry field: {key}")
    return value


def _matches_external_snapshot(entry: RegistryEntry) -> bool:
    """Prevent mismatching a candidate identifier and its cited fixed snapshot."""
    parsed = urlsplit(entry.source_url)
    expected = f"/datasets/{entry.dataset_id}/versions/{entry.source_version}"
    return (
        parsed.scheme == "https"
        and parsed.netloc == "openneuro.org"
        and parsed.path in (expected, expected + "/metadata")
        and not parsed.query
        and not parsed.fragment
        and entry.source_ref == entry.dataset_id
    )


def validate_registry(payload: Mapping[str, object]) -> tuple[RegistryEntry, ...]:
    """Validate provenance metadata and deny real-data access regardless of license."""
    if payload.get("registry_schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported registry schema version")
    if payload.get("policy") != "deny_external_sources_by_default":
        raise ValueError("registry must deny external sources by default")

    source_entries = payload.get("entries")
    if not isinstance(source_entries, list) or not source_entries:
        raise ValueError("registry entries must be a nonempty list")
    entries: list[RegistryEntry] = []
    seen: set[str] = set()
    for source in source_entries:
        if not isinstance(source, dict):
            raise ValueError("registry entry must be an object")
        entry = RegistryEntry(
            dataset_id=_string(source, "dataset_id"),
            source_kind=_string(source, "source_kind"),
            modality=_string(source, "modality"),
            source_url=_string(source, "source_url"),
            source_version=_string(source, "source_version"),
            source_ref=_string(source, "source_ref"),
            license=_string(source, "license"),
            rights_basis=_string(source, "rights_basis"),
            consent_boundary=_string(source, "consent_boundary"),
            usage_limitations=_string(source, "usage_limitations"),
            review_state=_string(source, "review_state"),
            enabled=_boolean(source, "enabled"),
            download_allowed=_boolean(source, "download_allowed"),
            participant_data_ingestion_allowed=_boolean(
                source, "participant_data_ingestion_allowed"
            ),
        )
        if entry.dataset_id in seen:
            raise ValueError("duplicate dataset_id in registry")
        seen.add(entry.dataset_id)
        if entry.source_kind == "synthetic":
            if (
                entry.dataset_id != _SYNTHETIC_ID
                or entry.source_ref != _GENERATOR
                or entry.source_url != _SYNTHETIC_URL
                or entry.modality != "synthetic_behavioral_trials"
                or entry.source_version != SCHEMA_VERSION
                or entry.rights_basis != "synthetic-original"
                or entry.license != "not-separately-specified"
                or entry.consent_boundary != "no_real_participants"
                or entry.review_state != "internal_generator"
                or not entry.enabled
                or entry.download_allowed
                or entry.participant_data_ingestion_allowed
            ):
                raise ValueError("unrecognized synthetic source or unsafe registry flags")
        elif entry.source_kind == "external_human":
            if (
                entry.enabled
                or entry.download_allowed
                or entry.participant_data_ingestion_allowed
                or not _matches_external_snapshot(entry)
                or entry.license not in _PUBLIC_LICENSES
                or entry.rights_basis != "published-license-metadata-only"
                or entry.consent_boundary != "secondary_use_not_cleared"
                or entry.review_state != "metadata_only"
            ):
                raise ValueError("external human data must remain disabled")
        else:
            raise ValueError("unsupported registry source_kind")
        entries.append(entry)

    if sum(entry.enabled for entry in entries) != 1:
        raise ValueError("exactly one internal synthetic entry must be enabled")
    return tuple(entries)


def load_registry(path: Path) -> tuple[RegistryEntry, ...]:
    """Read versioned metadata locally; never fetch source URLs."""
    document: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("registry JSON must contain an object")
    return validate_registry(document)


def load_registered_synthetic(
    config: SyntheticConfig, registry_path: Path
) -> tuple[tuple[TrialRecord, ...], DatasetCard, ValidatedDataset, RegistryEntry]:
    """Generate original fixtures instead of trusting arbitrary participant data.

    The source is explicitly regenerated from the reviewed generator. Nothing
    external, including a URL or a caller-supplied CSV, is ever ingested here.
    """
    entries = load_registry(registry_path)
    selected = next(
        (entry for entry in entries if entry.dataset_id == config.dataset_id), None
    )
    if selected is None or not selected.enabled or selected.source_kind != "synthetic":
        raise ValueError("dataset is not approved for synthetic v0 generation")
    records = generate_trials(config)
    card = dataset_card(config, records)
    summary = validate_synthetic_dataset(records, card)
    return records, card, summary, selected
