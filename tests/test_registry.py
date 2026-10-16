"""Regression tests for an explicit deny-by-default dataset registry."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from psychneuro.registry import load_registered_synthetic, load_registry, validate_registry
from psychneuro.synthetic import SyntheticConfig


def _registry() -> dict[str, object]:
    # Test source of truth is the checked-in metadata file, not network state.
    path = Path(__file__).resolve().parents[1] / "data" / "registry.json"
    return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def test_registry_has_six_disabled_human_candidates() -> None:
    records = validate_registry(_registry())
    assert len(records) == 7
    assert sum(entry.enabled for entry in records) == 1
    assert sum(entry.source_kind == "external_human" for entry in records) == 6
    assert all(
        not entry.enabled and not entry.download_allowed
        for entry in records if entry.source_kind == "external_human"
    )


def test_registry_loads_generated_fixture_only(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(_registry()), encoding="utf-8")
    records, card, summary, entry = load_registered_synthetic(
        SyntheticConfig(seed=4, n_participants=3, trials_per_participant=5), path
    )
    assert len(records) == 15
    assert summary.n_participants == 3
    assert entry.source_ref == card["source_url_or_generator"]
    assert entry.rights_basis == card["rights_basis"]


def test_external_dataset_is_never_generated(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(_registry()), encoding="utf-8")
    with pytest.raises(ValueError, match="not approved"):
        load_registered_synthetic(SyntheticConfig(dataset_id="ds000001"), path)


@pytest.mark.parametrize("flag", ["enabled", "download_allowed", "participant_data_ingestion_allowed"])
def test_external_permission_escalation_denied(flag: str) -> None:
    payload = deepcopy(_registry())
    payload["entries"][1][flag] = True
    with pytest.raises(ValueError, match="disabled"):
        validate_registry(payload)


def test_duplicate_dataset_id_denied() -> None:
    payload = deepcopy(_registry())
    payload["entries"][2]["dataset_id"] = "ds000001"
    with pytest.raises(ValueError, match="duplicate"):
        validate_registry(payload)


def test_unrecognized_license_denied() -> None:
    payload = deepcopy(_registry())
    payload["entries"][1]["license"] = "unknown"
    with pytest.raises(ValueError, match="disabled"):
        validate_registry(payload)


def test_missing_consent_gate_denied() -> None:
    payload = deepcopy(_registry())
    payload["entries"][1]["consent_boundary"] = "cleared"
    with pytest.raises(ValueError, match="disabled"):
        validate_registry(payload)


def test_unknown_internal_generator_denied() -> None:
    payload = deepcopy(_registry())
    payload["entries"][0]["source_ref"] = "external_file"
    with pytest.raises(ValueError, match="unrecognized"):
        validate_registry(payload)


def test_nonboolean_permission_denied() -> None:
    payload = deepcopy(_registry())
    payload["entries"][1]["download_allowed"] = "false"
    with pytest.raises(ValueError, match="boolean"):
        validate_registry(payload)


def test_missing_registry_file_is_not_silent(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_registry(tmp_path / "absent.json")
