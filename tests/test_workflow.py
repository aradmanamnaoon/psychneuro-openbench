"""PM-13 scenario runner and uncertainty display quality gates.

The true integration test uses the ORIGINAL rights-checked loader and real
grouped baseline models, never fabricated ML results. Test fixtures elsewhere
remain strictly separate from research/evidence claims. All tests NOT RUN here.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from psychneuro.config import load_baseline_config
from psychneuro.explorer import (
    nominal_uncertainty_intervals,
)
from psychneuro.reporting import build_bundle, parse_report
from psychneuro.workflow import (
    SCENARIO_MAX_TOTAL_TRIALS,
    Scenario,
    ScenarioError,
    _scenario_baseline,
    run_scenario,
)

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "configs" / "baseline.json"


def test_default_scenario_uses_same_hashed_locked_baseline() -> None:
    frozen = load_baseline_config(BASELINE)
    chosen = _scenario_baseline(Scenario(), BASELINE)
    assert chosen == frozen
    assert asdict(chosen) == asdict(frozen)


def test_change_seed_and_participants_changes_hash_not_protocol() -> None:
    default = _scenario_baseline(Scenario(), BASELINE)
    varied = _scenario_baseline(
        Scenario(generator_seed=101, n_participants=30, repeats=3), BASELINE
    )
    assert varied.config_sha256 != default.config_sha256
    assert varied.config_version == default.config_version
    assert varied.split_seed == default.split_seed == 42
    assert varied.cv_folds == default.cv_folds == 5
    raw = json.loads(BASELINE.read_text(encoding="utf-8"))
    raw["dataset"].update({"generator_seed": 101, "n_participants": 30})
    expected = json.dumps(
        raw, sort_keys=True, ensure_ascii=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert varied.config_sha256 == hashlib.sha256(expected).hexdigest()


@pytest.mark.parametrize(
    "bad",
    [
        Scenario(generator_seed=999),
        Scenario(generator_seed=True),  # type: ignore[arg-type]
        Scenario(n_participants=1000),
        Scenario(n_participants=True),  # type: ignore[arg-type]
        Scenario(trials_per_participant=120),
        Scenario(repeats=0),
        Scenario(repeats=20),
        Scenario(repeats=True),  # type: ignore[arg-type]
    ],
)
def test_invalid_scenario_fail_closed_before_any_training(bad: Scenario) -> None:
    with pytest.raises(ScenarioError, match="approved synthetic-only"):
        _scenario_baseline(bad, BASELINE)


def test_scenario_budget_is_predeclared() -> None:
    assert 30 * 20 * 5 <= SCENARIO_MAX_TOTAL_TRIALS
    assert SCENARIO_MAX_TOTAL_TRIALS == 3000


def test_default_scenario_without_synthetic_registry_rejected(tmp_path: Path) -> None:
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "baseline.json").write_bytes(BASELINE.read_bytes())
    with pytest.raises(ScenarioError, match="registry"):
        run_scenario(Scenario(repeats=1), tmp_path)


def test_true_one_repeat_synthetic_e2e_and_no_sensitive_raw_fields() -> None:
    """Actual scikit-learn run on original synthetic records, never a fake model.

    CI executes this ONLY in an authorized runner; no numerical metrics are
    assumed in the test. Ineligible splits remain visible/NA rather than hidden.
    """
    result = run_scenario(Scenario(repeats=1), ROOT)
    assert result["report_version"] == "psychneuro-pm10-synthetic-repeat-v1"
    assert result["n_requested"] == 1
    assert result["n_eligible"] + result["n_ineligible"] == 1
    assert result["source_policy"] == "original synthetic only; no external or human data"
    assert result["runs"][0]["generator_seed"] == 73
    assert result["runs"][0]["split_seed"] == 42
    assert len(result["runs"][0]["source_sha256"]) == 64
    payload = build_bundle(result)
    assert parse_report(payload.report_json) == result
    report_bytes = payload.report_json.lower()
    for disallowed in (b"response_time_ms", b"patient_name", b"email_address"):
        assert disallowed not in report_bytes
    manifest = json.loads(payload.artifact_manifest)
    assert manifest["rights_basis"] == "synthetic-original"
    assert manifest["ci_run_id"] is None
    assert manifest["source_commit_sha"] is None
    for name, raw in (
        ("report.json", payload.report_json),
        ("report.md", payload.report_markdown),
    ):
        assert manifest["artifacts"][name]["sha256"] == hashlib.sha256(raw).hexdigest()


def test_uncertainty_plot_requires_five_real_eligible_seeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import psychneuro.pipeline as pipeline
    from psychneuro.pipeline import PipelineConfig, run_pipeline

    def fake_experiment(config: Any, path: Path) -> dict[str, Any]:
        # Constant scores here are artificial software-test fixtures only.
        h = hashlib.sha256(str(config.generator_seed).encode()).hexdigest()
        model_scores = {
            "dummy_prior": {"status": "ok", "balanced_accuracy": 0.5, "macro_f1": 0.4},
            "logistic_regression": {
                "status": "ok", "balanced_accuracy": 0.6, "macro_f1": 0.5,
            },
        }
        slices = [
            {
                "feature": "stimulus_condition",
                "slice": side,
                "n_trials": 40,
                "n_participants": 5,
                "status": "suppressed",
                "reason": "insufficient_independent_participants_or_trials",
                "metrics": None,
            } for side in ("left", "right")
        ]
        return {
            "status": "ok",
            "source": {
                "source_kind": "synthetic",
                "rights_basis": "synthetic-original",
                "source_sha256": h,
            },
            "split": {"assignment_sha256": h},
            "manifest_sha256": h,
            "selected_model": "dummy_prior",
            "reasons": [],
            "test_metrics": model_scores,
            "test_slice_errors": slices,
        }

    monkeypatch.setattr(pipeline, "run_experiment", fake_experiment)
    frozen = load_baseline_config(BASELINE)
    short = run_pipeline(PipelineConfig(frozen, repeats=3), ROOT / "data" / "registry.json")
    assert nominal_uncertainty_intervals(short, "balanced_accuracy", ["dummy_prior"]) == []
    full = run_pipeline(PipelineConfig(frozen, repeats=5), ROOT / "data" / "registry.json")
    chart = nominal_uncertainty_intervals(
        full, "balanced_accuracy", ["dummy_prior", "cv_selected_policy"]
    )
    assert len(chart) == 2
    assert chart[0]["Eligible repeats"] == 5
    assert chart[0]["Mean"] == 0.5
    assert chart[0]["Lower 95%"] == chart[0]["Upper 95%"] == 0.5


def test_uncertainty_plot_no_fake_intervals_for_failed_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import psychneuro.pipeline as pipeline
    from psychneuro.pipeline import PipelineConfig, run_pipeline
    from psychneuro.uncertainty import summary_dict

    # Recreate a wholly synthetic test-output shape with four good/one blocked.
    # No CI should be computed for n=4.
    def fake_exp(config: Any, path: Path) -> dict[str, Any]:
        h = hashlib.sha256(str(config.generator_seed).encode()).hexdigest()
        valid = config.generator_seed != 77
        scores = {
            "dummy_prior": {"status": "ok", "balanced_accuracy": 0.5, "macro_f1": 0.4},
            "logistic_regression": {
                "status": "ok", "balanced_accuracy": 0.6, "macro_f1": 0.5,
            },
        }
        slices = [
            {
                "feature": "stimulus_condition", "slice": side,
                "n_trials": 40, "n_participants": 5,
                "metrics": None, "status": "suppressed",
                "reason": "insufficient_independent_participants_or_trials",
            } for side in ("left", "right")
        ]
        return {
            "status": "ok" if valid else "ineligible",
            "source": {
                "source_kind": "synthetic",
                "rights_basis": "synthetic-original",
                "source_sha256": h,
            },
            "split": {"assignment_sha256": h},
            "manifest_sha256": h,
            "selected_model": "dummy_prior" if valid else None,
            "reasons": [] if valid else ["blocked fixture"],
            "test_metrics": scores if valid else None,
            "test_slice_errors": slices if valid else None,
        }

    monkeypatch.setattr(pipeline, "run_experiment", fake_exp)
    report = run_pipeline(
        PipelineConfig(load_baseline_config(BASELINE), 5),
        ROOT / "data" / "registry.json",
    )
    assert report["n_eligible"] == 4
    assert report["summary"]["dummy_prior"]["balanced_accuracy"] == summary_dict([0.5] * 4)
    assert nominal_uncertainty_intervals(report, "balanced_accuracy", ["dummy_prior"]) == []


def test_exports_are_not_subsetted_by_graph_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from psychneuro import workflow
    from psychneuro.explorer import filter_report_scores
    from psychneuro.pipeline import PipelineConfig, run_pipeline

    def fake_experiment(config: Any, path: Path) -> dict[str, Any]:
        h = hashlib.sha256(str(config.generator_seed).encode()).hexdigest()
        scores = {
            "dummy_prior": {"status": "ok", "balanced_accuracy": 0.5, "macro_f1": 0.4},
            "logistic_regression": {
                "status": "ok", "balanced_accuracy": 0.6, "macro_f1": 0.5,
            },
        }
        slices = [
            {
                "feature": "stimulus_condition", "slice": side,
                "n_trials": 40, "n_participants": 5,
                "metrics": None, "status": "suppressed",
                "reason": "insufficient_independent_participants_or_trials",
            } for side in ("left", "right")
        ]
        return {
            "status": "ok",
            "source": {
                "source_kind": "synthetic",
                "rights_basis": "synthetic-original",
                "source_sha256": h,
            },
            "split": {"assignment_sha256": h},
            "manifest_sha256": h,
            "selected_model": "dummy_prior",
            "reasons": [],
            "test_metrics": scores,
            "test_slice_errors": slices,
        }

    monkeypatch.setattr(workflow, "run_pipeline", run_pipeline)
    monkeypatch.setattr("psychneuro.pipeline.run_experiment", fake_experiment)
    report = workflow.run_scenario(Scenario(repeats=3), ROOT)
    subset = filter_report_scores(
        report, metric="balanced_accuracy",
        selected_models=["dummy_prior"], selected_repeats=[2],
    )
    assert len(subset) == 1
    full_export = build_bundle(report)
    assert len(parse_report(full_export.report_json)["runs"]) == 3


def test_live_app_mode_does_not_train_on_page_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Streamlit simulated shell must not start any model work without a click."""
    from streamlit.testing.v1 import AppTest
    from psychneuro.explorer import DATA_MODES
    from psychneuro import workflow

    def forbidden_run(scenario: Scenario, root: Path) -> dict[str, Any]:
        raise AssertionError("model execution happened without explicit scenario submission")

    monkeypatch.setattr(workflow, "run_scenario", forbidden_run)
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    assert not at.exception
    at.sidebar.selectbox[0].set_value(DATA_MODES[2]).run()
    assert not at.exception
    assert any("No in-app run yet" in item.value for item in at.info)
    assert len(at.file_uploader) == 0
    assert len(at.download_button) == 0


def test_unexpected_export_fields_and_sensitive_text_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A self-rehashed uploaded JSON cannot smuggle unrelated metadata."""
    from psychneuro.pipeline import PipelineConfig, run_pipeline
    from psychneuro import pipeline

    def fake_exp(config: Any, path: Path) -> dict[str, Any]:
        h = hashlib.sha256(str(config.generator_seed).encode()).hexdigest()
        scores = {
            "dummy_prior": {"status": "ok", "balanced_accuracy": 0.5, "macro_f1": 0.4},
            "logistic_regression": {
                "status": "ok", "balanced_accuracy": 0.6, "macro_f1": 0.5,
            },
        }
        return {
            "status": "ok",
            "source": {
                "source_kind": "synthetic",
                "rights_basis": "synthetic-original",
                "source_sha256": h,
            },
            "split": {"assignment_sha256": h},
            "manifest_sha256": h,
            "selected_model": "dummy_prior",
            "reasons": [],
            "test_metrics": scores,
            "test_slice_errors": [
                {
                    "feature": "stimulus_condition", "slice": side,
                    "n_trials": 40, "n_participants": 5,
                    "status": "suppressed",
                    "reason": "insufficient_independent_participants_or_trials",
                    "metrics": None,
                } for side in ("left", "right")
            ],
        }

    monkeypatch.setattr(pipeline, "run_experiment", fake_exp)
    report = run_pipeline(
        PipelineConfig(load_baseline_config(BASELINE), 1),
        ROOT / "data" / "registry.json",
    )
    report["patient_email"] = "not-real@example.invalid"
    report.pop("report_sha256")
    payload = json.dumps(report, sort_keys=True, separators=(",", ":"))
    report["report_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    with pytest.raises(ValueError, match="unsafe for export"):
        build_bundle(report)
    report.pop("patient_email")
    report["runs"][0]["reasons"].append("study@example.invalid")
    report.pop("report_sha256")
    payload = json.dumps(report, sort_keys=True, separators=(",", ":"))
    report["report_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    with pytest.raises(ValueError, match="unsafe reason"):
        build_bundle(report)
