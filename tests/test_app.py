"""PM-12 smoke and integration specifications: no actual hosted CI evidence yet.

Numbers in monkeypatched tests are fictional test constants, NOT measured ML
performance. UI AppTest checks shell states; uploaded-file browser/AT verification
remains an explicit independent hosted/manual acceptance requirement.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

from psychneuro.config import load_baseline_config
from psychneuro.explorer import (
    DATA_MODES,
    PREVIEW_MAX_ROWS,
    filter_report_scores,
    full_report_summary,
    prepare_synthetic_preview,
)
from psychneuro.pipeline import PipelineConfig, run_pipeline
from psychneuro.reporting import ReportValidationError, build_bundle, parse_report

ROOT = Path(__file__).resolve().parents[1]


def _hash(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _fake_experiment(seed: int, *, eligible: bool = True) -> dict[str, Any]:
    scores = {
        "dummy_prior": {"status": "ok", "balanced_accuracy": 0.5, "macro_f1": 0.4},
        "logistic_regression": {
            "status": "ok", "balanced_accuracy": 0.6, "macro_f1": 0.5,
        },
    }
    slices = [
        {
            "feature": "stimulus_condition",
            "slice": side,
            "status": "suppressed",
            "n_trials": 40,
            "n_participants": 5,
            "metrics": None,
            "reason": "insufficient_independent_participants_or_trials",
        }
        for side in ("left", "right")
    ]
    return {
        "status": "ok" if eligible else "ineligible",
        "source": {
            "source_kind": "synthetic",
            "rights_basis": "synthetic-original",
            "source_sha256": _hash(f"source-{seed}"),
        },
        "split": {"assignment_sha256": _hash(f"split-{seed}")},
        "manifest_sha256": _hash(f"manifest-{seed}"),
        "selected_model": "dummy_prior" if eligible else None,
        "test_metrics": scores if eligible else None,
        "test_slice_errors": slices if eligible else None,
        "reasons": [] if eligible else ["fixture ineligible"],
    }


@pytest.fixture
def report(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    import psychneuro.pipeline as pipeline

    def fake_run(config: Any, registry_path: Path) -> dict[str, Any]:
        assert registry_path == ROOT / "data" / "registry.json"
        return _fake_experiment(config.generator_seed)

    monkeypatch.setattr(pipeline, "run_experiment", fake_run)
    config = load_baseline_config(ROOT / "configs" / "baseline.json")
    return run_pipeline(PipelineConfig(config, repeats=5), ROOT / "data" / "registry.json")


def test_preview_bounded_deterministic_original_synthetic_only() -> None:
    p = prepare_synthetic_preview(73, 12, 20)
    assert p == prepare_synthetic_preview(73, 12, 20)
    assert p.n_trials == 240
    assert p.n_trials <= PREVIEW_MAX_ROWS
    assert p.n_participants == 12
    assert len(p.rows) == 12
    assert p.rights_basis == "synthetic-original"
    assert len(p.source_sha256) == 64
    assert all(row.stimulus_condition in ("left", "right") for row in p.rows)
    assert all(0.0 <= row.difficulty_unitless <= 1.0 for row in p.rows)
    for row in p.rows:
        assert set(asdict(row)) == {
            "fictional_participant_id",
            "trial_order",
            "difficulty_unitless",
            "stimulus_condition",
        }


@pytest.mark.parametrize(
    ("seed", "people", "trials"),
    [(72, 12, 8), (73, 25, 8), (73, 12, 100), (True, 12, 8), (73, 0, 8)],
)
def test_preview_rejects_unapproved_or_unsafe_parameters(
    seed: int, people: int, trials: int
) -> None:
    with pytest.raises(ValueError, match="fixed original-synthetic"):
        prepare_synthetic_preview(seed, people, trials)


def test_comparison_points_remain_original_noninvented_values(report: dict[str, Any]) -> None:
    points = filter_report_scores(
        report,
        metric="balanced_accuracy",
        selected_models=["dummy_prior", "logistic_regression"],
        selected_repeats=[1, 3],
    )
    assert len(points) == 4
    assert set(row["Repeat"] for row in points) == {1, 3}
    assert set(row["Score"] for row in points) == {0.5, 0.6}
    assert all(row["Model"] in ("dummy_prior", "logistic_regression") for row in points)
    assert filter_report_scores(
        report, metric="macro_f1",
        selected_models=["cv_selected_policy"], selected_repeats=[1],
    ) == [{"Repeat": 1, "Model": "cv_selected_policy", "Score": 0.4}]
    assert len(build_bundle(parse_report(build_bundle(report).report_json)).report_markdown) > 100


def test_full_report_uncertainty_not_recomputed_after_selection(
    report: dict[str, Any],
) -> None:
    selected = full_report_summary(report, "balanced_accuracy", ["dummy_prior"])
    assert selected[0]["Eligible synthetic cohorts (full report)"] == 5
    assert selected[0]["Mean (full report)"] == 0.5
    assert selected[0]["SE (full report)"] == 0.0
    visible = filter_report_scores(
        report, metric="balanced_accuracy",
        selected_models=["dummy_prior"], selected_repeats=[4],
    )
    assert len(visible) == 1
    assert selected == full_report_summary(report, "balanced_accuracy", ["dummy_prior"])


@pytest.mark.parametrize(
    ("models", "repeats"),
    [
        (["not_model"], [1]),
        (["dummy_prior", "dummy_prior"], [1]),
        (["dummy_prior"], [0]),
        (["dummy_prior"], [21]),
        (["dummy_prior"], [True]),
        (["dummy_prior"], [1, 1]),
    ],
)
def test_comparison_controls_reject_unknown_or_duplicate_choices(
    report: dict[str, Any], models: list[str], repeats: list[int]
) -> None:
    with pytest.raises(ReportValidationError):
        filter_report_scores(
            report, metric="balanced_accuracy",
            selected_models=models, selected_repeats=repeats,
        )


def test_empty_selection_and_wrong_metric_do_not_fabricate(report: dict[str, Any]) -> None:
    assert filter_report_scores(
        report, metric="balanced_accuracy", selected_models=[], selected_repeats=[1],
    ) == []
    assert filter_report_scores(
        report, metric="balanced_accuracy",
        selected_models=["dummy_prior"], selected_repeats=[],
    ) == []
    with pytest.raises(ReportValidationError, match="unknown"):
        filter_report_scores(
            report, metric="accuracy", selected_models=["dummy_prior"], selected_repeats=[1],
        )


def test_artifact_comparison_incomplete_run_withheld(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import psychneuro.pipeline as pipeline

    def fake_run(config: Any, registry_path: Path) -> dict[str, Any]:
        return _fake_experiment(config.generator_seed, eligible=config.generator_seed != 74)

    monkeypatch.setattr(pipeline, "run_experiment", fake_run)
    config = load_baseline_config(ROOT / "configs" / "baseline.json")
    incomplete = run_pipeline(PipelineConfig(config, 5), ROOT / "data" / "registry.json")
    rows = filter_report_scores(
        incomplete, metric="macro_f1",
        selected_models=["dummy_prior"], selected_repeats=[1, 2, 3, 4, 5],
    )
    assert incomplete["status"] == "incomplete"
    assert incomplete["n_eligible"] == 4
    assert [row["Repeat"] for row in rows] == [1, 3, 4, 5]


def test_app_starts_with_original_synthetic_preview_without_heldout_results() -> None:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    assert not at.exception
    assert at.sidebar.selectbox[0].value == DATA_MODES[0]
    assert len(at.sidebar.selectbox) == 4
    assert len(at.file_uploader) == 0
    assert not at.download_button
    assert any("NOT human neuroscience evidence" in item.value for item in at.warning)


def test_app_navigation_to_results_requires_real_artifact() -> None:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    at.sidebar.radio[0].set_value("Results and charts").run()
    assert not at.exception
    assert any("No held-out model results" in item.value for item in at.info)


def test_app_upload_mode_empty_state_is_explicit() -> None:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    at.sidebar.selectbox[0].set_value(DATA_MODES[1]).run()
    assert not at.exception
    assert len(at.file_uploader) == 1
    assert any("No report uploaded" in item.value for item in at.info)
    assert not at.download_button


def test_app_limitations_page_has_rights_and_nonclinical_notice() -> None:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    at.sidebar.radio[0].set_value("Limitations").run()
    assert not at.exception
    assert len(at.warning) > 0
    assert any("rights and privacy" in item.value.lower() for item in at.subheader)

def test_app_rejects_corrupt_uploaded_report_without_downloads() -> None:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    at.sidebar.selectbox[0].set_value(DATA_MODES[1]).run()
    at.file_uploader[0].upload("report.json", b'{"invalid":true}', "application/json").run()
    assert not at.exception
    assert len(at.download_button) == 0
    assert any("Input rejected" in item.value for item in at.error)


def test_app_uploaded_fixture_exposes_real_input_only_and_comparison_controls(
    report: dict[str, Any],
) -> None:
    """Simulated app test only; fixture numbers are NOT actual benchmark results."""
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    at.sidebar.selectbox[0].set_value(DATA_MODES[1]).run()
    artifact = build_bundle(report).report_json
    at.file_uploader[0].upload("report.json", artifact, "application/json").run()
    assert not at.exception
    assert len(at.download_button) == 3
    assert any("consistent" in item.value for item in at.success)
    assert any("HOSTED CI NOT VERIFIED" in item.value for item in at.error)
    at.sidebar.radio[0].set_value("Results and charts").run()
    assert not at.exception
    assert len(at.multiselect) == 2
    assert at.multiselect[0].value == list(
        ("dummy_prior", "logistic_regression", "cv_selected_policy")
    ) or tuple(at.multiselect[0].value) == (
        "dummy_prior", "logistic_regression", "cv_selected_policy"
    )
    at.multiselect[0].set_value(["dummy_prior"]).run()
    assert not at.exception
    assert len(at.download_button) == 3
    at.multiselect[1].set_value([]).run()
    assert any("No eligible results" in item.value for item in at.info)
