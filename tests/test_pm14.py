"""PM-14 invalid-data, error-copy, accessible alternatives and profiler tests.

These are TEST SPECIFICATIONS; remote pytest/browser execution is NOT claimed.
Fake scores in unit tests are mock data, never empirical benchmark outcomes.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

from psychneuro.profiling import PROFILE_PROTOCOL, measure_small_synthetic_run
from psychneuro.reporting import ReportValidationError, parse_report
from psychneuro.ux import explain_scenario_failure, explain_upload_failure
from psychneuro.workflow import Scenario, ScenarioError, run_scenario

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("bad", "recovery_hint"),
    [
        (ValueError("report is empty or exceeds 2 MB"), "2 MB"),
        (ValueError("invalid UTF-8 PM-10 JSON report"), "malformed"),
        (ValueError("duplicate JSON field: score"), "malformed"),
        (ValueError("non-synthetic or unverified data rights"), "not an approved"),
        (ValueError("unexpected baseline protocol"), "does not match"),
        (ValueError("PM-10 canonical report SHA-256 mismatch"), "integrity"),
        (ValueError("unknown/missing report fields; unsafe for export"), "not an approved"),
    ],
)
def test_report_errors_recover_without_exposing_input(
    bad: ValueError, recovery_hint: str
) -> None:
    text = explain_upload_failure(bad)
    assert recovery_hint in text
    assert "report.json" in text or "pipeline" in text or "synthetic" in text
    assert "\n" not in text
    assert len(text) < 300


def test_report_recovery_never_echoes_attacker_supplied_text() -> None:
    secret = "SENSITIVE-PRIVATE-PARTICIPANT-EMAIL@example.invalid"
    for error in (
        ValueError(secret),
        ValueError("duplicate JSON field: " + secret),
        ValueError("unsafe reason string: " + secret),
        ValueError("rights violation: " + secret),
    ):
        assert secret not in explain_upload_failure(error)


@pytest.mark.parametrize(
    ("bad", "hint"),
    [
        (ScenarioError("synthetic-only dataset registry is missing or unsafe"), "registry"),
        (ScenarioError("scenario settings must use approved synthetic-only choices"), "bounds"),
        (ScenarioError("scenario exceeds the synchronous synthetic trial budget"), "bounds"),
        (ScenarioError("versioned baseline configuration cannot be verified"), "protocol"),
        (ScenarioError("benchmark failed /tmp/HIDDENSECRET"), "did not complete"),
    ],
)
def test_scenario_error_messages_have_textual_why_and_recovery(
    bad: ScenarioError, hint: str
) -> None:
    text = explain_scenario_failure(bad)
    assert hint in text
    assert "HIDDENSECRET" not in text
    assert len(text) < 350


@pytest.mark.parametrize(
    "bad_bytes",
    [
        b"",  # empty
        b"{",  # truncated JSON
        b'{"score": 1, "score": 2}',  # duplicate keys
        b'{"score": NaN}',  # nonfinite data
        b" " * 2_000_001,  # denial-of-service sized upload
        b"participant_id,response_time_ms,correct\npatient-1,230,1",  # raw CSV forbidden
    ],
)
def test_malformed_oversize_or_raw_trial_upload_never_yields_report(
    bad_bytes: bytes,
) -> None:
    with pytest.raises((ReportValidationError, ValueError)) as exc:
        parse_report(bad_bytes)
    friendly = explain_upload_failure(exc.value)
    assert friendly
    assert b"patient-1" not in friendly.encode("utf-8")


def test_missing_registry_halts_before_any_model_and_is_friendly(tmp_path: Path) -> None:
    base = ROOT / "configs" / "baseline.json"
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "baseline.json").write_bytes(base.read_bytes())
    with pytest.raises(ScenarioError, match="registry") as err:
        run_scenario(Scenario(repeats=1), tmp_path)
    assert "registry" in explain_scenario_failure(err.value)


def test_disabled_external_dataset_cannot_enter_scenario_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The real pipeline rejects wrong rights; no valid report gets exported."""
    from psychneuro import pipeline

    def illegal_source(config: Any, registry_path: Path) -> dict[str, Any]:
        sha = hashlib.sha256(b"disallowed").hexdigest()
        return {
            "status": "ineligible",
            "source": {
                "source_kind": "external_human",
                "rights_basis": "not-cleared",
                "source_sha256": sha,
            },
            "split": {"assignment_sha256": sha},
            "manifest_sha256": sha,
            "selected_model": None,
            "reasons": ["source forbidden"],
            "test_metrics": None,
            "test_slice_errors": None,
        }

    monkeypatch.setattr(pipeline, "run_experiment", illegal_source)
    with pytest.raises(ScenarioError, match="no report"):
        run_scenario(Scenario(repeats=1), ROOT)


def test_first_visit_uses_static_table_and_labeled_sources() -> None:
    page = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    assert not page.exception
    assert len(page.table) >= 1  # static preview instead of chart-only output
    assert page.sidebar.selectbox[0].label == "Permitted data source"
    assert page.sidebar.radio[0].label == "Navigation"
    assert len(page.download_button) == 0


def test_report_review_mode_without_file_has_friendly_empty_state() -> None:
    from psychneuro.explorer import DATA_MODES

    page = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    page.sidebar.selectbox[0].set_value(DATA_MODES[1]).run()
    assert not page.exception
    assert any("No report uploaded" in msg.value for msg in page.info)
    assert not page.download_button


def test_profiler_contract_single_bounded_run_without_host_identifiers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from psychneuro import profiling

    seen: list[Scenario] = []

    def synthetic_only(scenario: Scenario, root: Path) -> dict[str, object]:
        seen.append(scenario)
        return {
            "status": "incomplete",
            "n_requested": 1,
            "n_eligible": 0,
            "report_sha256": hashlib.sha256(b"mock-only").hexdigest(),
        }

    monkeypatch.setattr(profiling, "run_scenario", synthetic_only)
    record = measure_small_synthetic_run(ROOT)
    assert seen == [Scenario(repeats=1)]
    assert record["measurement_protocol"] == PROFILE_PROTOCOL
    assert record["source_policy"] == "synthetic-original"
    assert record["scenario"]["trial_budget"] == 480
    assert record["n_eligible"] == 0
    assert record["wall_seconds"] >= 0
    assert record["process_cpu_seconds"] >= 0
    assert record["python_tracemalloc_peak_bytes"] >= 0
    assert not any(
        "hostname" in str(key).lower() or "username" in str(key).lower()
        for key in record
    )
