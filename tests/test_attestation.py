"""Synthetic test doubles for verification-sidecar safeguards; NOT hosted proof.

No real benchmark numbers are created here. All fixtures stand for bytes only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from psychneuro import attestation
from psychneuro.reporting import ExportBundle


def _ci_environment() -> dict[str, str]:
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": "aradmanamnaoon/psychneuro-openbench",
        "GITHUB_SHA": "a" * 40,
        "GITHUB_RUN_ID": "123456789",
    }


def _fixture_files(root: Path) -> None:
    for name in attestation._PATHS:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name.endswith("resolved-dependencies.txt"):
            target.write_bytes(b"EXAMPLE-ONLY\n")
        else:
            target.write_bytes(b"{}")


def _fixture_report(_: bytes) -> dict[str, Any]:
    return {
        "status": "complete",
        "n_eligible": 5,
        "n_requested": 5,
        "report_sha256": "b" * 64,
    }


def test_sidecar_refuses_missing_or_forged_host_identity(tmp_path: Path) -> None:
    _fixture_files(tmp_path)
    valid = _ci_environment()
    for bad in (
        {},
        {**valid, "GITHUB_ACTIONS": "false"},
        {**valid, "GITHUB_REPOSITORY": "someone/public-repo"},
        {**valid, "GITHUB_SHA": "invalid"},
        {**valid, "GITHUB_RUN_ID": "not-a-run"},
    ):
        with pytest.raises(ValueError, match="real GitHub Actions"):
            attestation.create_verification_sidecar(tmp_path, bad)


def test_sidecar_checks_expected_files_and_original_report_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _fixture_files(tmp_path)
    monkeypatch.setattr(attestation, "parse_report", _fixture_report)
    monkeypatch.setattr(
        attestation, "build_bundle",
        lambda _: ExportBundle(b"{}", b"{}", b"{}"),
    )
    result = attestation.create_verification_sidecar(tmp_path, _ci_environment())
    assert result["github_commit"] == "a" * 40
    assert result["github_run_id"] == "123456789"
    assert result["source_rights"] == "synthetic-original"
    assert result["n_eligible_fictional_cohorts"] == 5
    assert len(result["file_sha256"]) == 8
    assert "independent logs required" in result["attestation_type"]
    assert not any("password" in field or "token" in field for field in result)

    (tmp_path / "artifacts/pm13/report.md").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="exact export-byte"):
        attestation.create_verification_sidecar(tmp_path, _ci_environment())


def test_sidecar_rejects_absent_file_without_partial_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _fixture_files(tmp_path)
    (tmp_path / "artifacts/pm11/report.md").unlink()
    monkeypatch.setattr(attestation, "parse_report", _fixture_report)
    with pytest.raises(ValueError, match="missing or unsafe"):
        attestation.create_verification_sidecar(tmp_path, _ci_environment())


def test_sidecar_never_attests_ineligible_synthetic_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _fixture_files(tmp_path)
    monkeypatch.setattr(
        attestation, "parse_report",
        lambda _: {
            "status": "incomplete",
            "n_eligible": 4,
            "n_requested": 5,
            "report_sha256": "f" * 64,
        },
    )
    with pytest.raises(ValueError, match="ineligible"):
        attestation.create_verification_sidecar(tmp_path, _ci_environment())
