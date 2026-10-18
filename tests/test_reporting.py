"""PM-11 regression specifications; synthetic mock inputs are NOT measured results.

These tests must be executed in authorized hosted CI before claiming success.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from psychneuro.config import load_baseline_config
from psychneuro.pipeline import PipelineConfig, run_pipeline
from psychneuro.reporting import (
    EXPORT_VERSION,
    ReportValidationError,
    build_bundle,
    chart_rows,
    parse_report,
    render_markdown,
    validate_report,
)

ROOT = Path(__file__).resolve().parents[1]
BASELINE = load_baseline_config(ROOT / "configs" / "baseline.json")
REGISTRY = ROOT / "data" / "registry.json"


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _fake_experiment(seed: int, *, eligible: bool = True) -> dict[str, Any]:
    """Invented TEST FIXTURE; NEVER publish its metrics as a benchmark result."""
    models = {
        "dummy_prior": {"status": "ok", "balanced_accuracy": 0.5, "macro_f1": 0.4},
        "logistic_regression": {"status": "ok", "balanced_accuracy": 0.65, "macro_f1": 0.6},
    }
    slices = [
        {
            "feature": "stimulus_condition",
            "slice": name,
            "n_trials": 40,
            "n_participants": 5,
            "metrics": None,
            "status": "suppressed",
            "reason": "insufficient_independent_participants_or_trials",
        }
        for name in ("left", "right")
    ]
    return {
        "status": "ok" if eligible else "ineligible",
        "source": {
            "source_kind": "synthetic",
            "rights_basis": "synthetic-original",
            "source_sha256": _sha(f"synthetic-{seed}"),
        },
        "split": {"assignment_sha256": _sha(f"split-{seed}")},
        "manifest_sha256": _sha(f"manifest-{seed}"),
        "selected_model": "dummy_prior" if eligible else None,
        "test_metrics": models if eligible else None,
        "test_slice_errors": slices if eligible else None,
        "reasons": [] if eligible else ["invalid training folds"],
    }


@pytest.fixture
def sample(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    from psychneuro import pipeline

    def fake_run(config: Any, registry_path: Path) -> dict[str, Any]:
        assert registry_path == REGISTRY
        return _fake_experiment(config.generator_seed)

    monkeypatch.setattr(pipeline, "run_experiment", fake_run)
    return run_pipeline(PipelineConfig(BASELINE, 5), REGISTRY)


def _rehash(value: dict[str, Any]) -> None:
    value["report_sha256"] = _sha(
        json.dumps(
            {k: v for k, v in value.items() if k != "report_sha256"},
            sort_keys=True, separators=(",", ":"), allow_nan=False,
        )
    )


def test_valid_synthetic_fixture_accepted_and_generated_exports_match(sample: dict[str, Any]) -> None:
    original = copy.deepcopy(sample)
    valid = validate_report(sample)
    bundle = build_bundle(valid)
    assert sample == original  # export never mutates input
    assert parse_report(bundle.report_json) == sample
    assert b"synthetic benchmark report" in bundle.report_markdown
    assert b"NOT a significance test" in bundle.report_markdown
    manifest = json.loads(bundle.artifact_manifest)
    assert manifest["artifact_manifest_version"] == EXPORT_VERSION
    assert manifest["ci_run_id"] is None
    assert manifest["rights_basis"] == "synthetic-original"
    assert len(manifest["repeats"]) == 5
    assert manifest["input_report_canonical_sha256"] == sample["report_sha256"]
    for name, payload in (
        ("report.json", bundle.report_json),
        ("report.md", bundle.report_markdown),
    ):
        assert manifest["artifacts"][name]["sha256"] == hashlib.sha256(payload).hexdigest()
        assert manifest["artifacts"][name]["bytes"] == len(payload)


def test_export_bytes_deterministic_and_ci_not_forged(sample: dict[str, Any]) -> None:
    first = build_bundle(sample)
    second = build_bundle(sample)
    assert first == second
    assert b"NOT VERIFIED" in first.artifact_manifest
    assert b"not independently" not in first.report_json


def test_chart_points_are_only_from_authentic_input_rows(sample: dict[str, Any]) -> None:
    points = chart_rows(sample, "balanced_accuracy")
    assert len(points) == 15  # 5 eligible repeats, two models + CV-selected policy
    assert [p["Repeat"] for p in points[::3]] == [1, 2, 3, 4, 5]
    assert {p["Score"] for p in points} == {0.5, 0.65}
    assert chart_rows(sample, "macro_f1")[0]["Score"] == 0.4
    with pytest.raises(ReportValidationError, match="unsupported chart"):
        chart_rows(sample, "latency")


def test_rehash_cannot_hide_illegal_source_or_nonfinite_score(sample: dict[str, Any]) -> None:
    broken = copy.deepcopy(sample)
    broken["source_policy"] = "real patient data"
    _rehash(broken)
    with pytest.raises(ReportValidationError, match="rights"):
        validate_report(broken)

    broken = copy.deepcopy(sample)
    broken["runs"][0]["test_metrics"]["dummy_prior"]["balanced_accuracy"] = 1.3
    _rehash(broken)
    with pytest.raises(ReportValidationError, match="finite and"):
        validate_report(broken)


def test_tamper_without_rehash_detected(sample: dict[str, Any]) -> None:
    broken = copy.deepcopy(sample)
    broken["n_eligible"] = 0
    with pytest.raises(ReportValidationError, match="SHA-256 mismatch"):
        validate_report(broken)


def test_reported_summary_must_derive_from_repeats(sample: dict[str, Any]) -> None:
    broken = copy.deepcopy(sample)
    broken["summary"]["dummy_prior"]["balanced_accuracy"]["mean"] = 0.9
    _rehash(broken)
    with pytest.raises(ReportValidationError, match="summary not derivable"):
        validate_report(broken)


def test_selected_policy_must_match_training_selected_candidate(sample: dict[str, Any]) -> None:
    broken = copy.deepcopy(sample)
    broken["runs"][0]["test_metrics"]["cv_selected_policy"] = {
        "balanced_accuracy": 0.6, "macro_f1": 0.4
    }
    _rehash(broken)
    with pytest.raises(ReportValidationError, match="selected policy"):
        validate_report(broken)


def test_no_results_no_chart_points_or_invented_numbers(
    sample: dict[str, Any],
) -> None:
    broken = copy.deepcopy(sample)
    for run in broken["runs"]:
        run["status"] = "ineligible"
        run["selected_model"] = None
        run["test_metrics"] = None
        run["test_slice_errors"] = None
        run["reasons"] = ["ineligible"]
    broken["n_eligible"] = 0
    broken["n_ineligible"] = 5
    broken["status"] = "incomplete"
    from psychneuro.uncertainty import summary_dict

    broken["summary"] = {
        model: {metric: summary_dict([]) for metric in ("balanced_accuracy", "macro_f1")}
        for model in ("dummy_prior", "logistic_regression", "cv_selected_policy")
    }
    _rehash(broken)
    assert chart_rows(broken, "balanced_accuracy") == []
    markdown = render_markdown(broken)
    assert "N/A" in markdown
    assert "**0 / 5**" in markdown or "**5 / 0 / 5**" in markdown


def test_suppressed_slice_must_not_expose_numbers(sample: dict[str, Any]) -> None:
    broken = copy.deepcopy(sample)
    broken["runs"][0]["test_slice_errors"][0]["metrics"] = {"balanced_accuracy": 1}
    _rehash(broken)
    with pytest.raises(ReportValidationError, match="suppressed slice"):
        validate_report(broken)


def test_missing_slice_is_not_silently_accepted(sample: dict[str, Any]) -> None:
    broken = copy.deepcopy(sample)
    broken["runs"][0]["test_slice_errors"] = None
    _rehash(broken)
    with pytest.raises(ReportValidationError, match="missing guarded slices"):
        validate_report(broken)


def test_invalid_parser_cases_fail_closed(sample: dict[str, Any]) -> None:
    with pytest.raises(ReportValidationError, match="empty"):
        parse_report(b"")
    with pytest.raises(ReportValidationError, match="2 MB"):
        parse_report(b" " * 2_000_001)
    with pytest.raises(ReportValidationError, match="UTF-8"):
        parse_report(b"\xff")
    with pytest.raises(ReportValidationError, match="duplicate"):
        parse_report(b'{"x":1,"x":2}')
    with pytest.raises(ReportValidationError, match="nonfinite"):
        parse_report(b'{"number":NaN}')
    assert parse_report(json.dumps(sample, allow_nan=False).encode("utf-8")) == sample


def test_validity_requires_exact_seed_order(sample: dict[str, Any]) -> None:
    broken = copy.deepcopy(sample)
    broken["runs"][0]["generator_seed"] += 99
    _rehash(broken)
    with pytest.raises(ReportValidationError, match="seed order"):
        validate_report(broken)


def test_bad_version_and_missing_repeat_rejected(sample: dict[str, Any]) -> None:
    broken = copy.deepcopy(sample)
    broken["report_version"] = "unapproved-v2"
    _rehash(broken)
    with pytest.raises(ReportValidationError, match="version"):
        validate_report(broken)
    broken = copy.deepcopy(sample)
    broken["runs"].pop()
    _rehash(broken)
    with pytest.raises(ReportValidationError, match="missing or incomplete"):
        validate_report(broken)
