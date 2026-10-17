"""PM-10 source assertions; results are UNRUN until exact-branch hosted CI."""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from psychneuro.config import load_baseline_config
from psychneuro.pipeline import PipelineConfig, PipelineError, run_pipeline
from psychneuro.slices import guarded_slice_metrics
from psychneuro.uncertainty import summarize_scores, summary_dict

BASE = Path(__file__).resolve().parents[1]
CFG = load_baseline_config(BASE / "configs" / "baseline.json")
REGISTRY = BASE / "data" / "registry.json"


def test_empty_sample_has_no_point_estimate_or_interval() -> None:
    actual = summarize_scores([])
    assert actual.n_repeats == 0
    assert actual.mean is None
    assert actual.sample_sd is None
    assert actual.standard_error is None
    assert actual.ci95_low is None and actual.ci95_high is None


def test_single_sample_has_mean_but_no_se_or_ci() -> None:
    result = summarize_scores([0.7])
    assert result.mean == pytest.approx(0.7)
    assert result.standard_error is None
    assert result.ci95_low is None


def test_se_is_sample_sd_over_sqrt_valid_repeats() -> None:
    actual = summarize_scores([0.2, 0.4, 0.6, 0.8])
    assert actual.n_repeats == 4
    assert actual.mean == pytest.approx(0.5)
    expected_sd = math.sqrt(0.2 / 3)
    assert actual.sample_sd == pytest.approx(expected_sd)
    assert actual.standard_error == pytest.approx(expected_sd / 2)
    assert actual.ci95_low is None  # fewer than five, not a fake CI


def test_five_repeats_nominal_t_interval_is_not_significance_claim() -> None:
    result = summarize_scores([0.2, 0.3, 0.4, 0.5, 0.6])
    assert result.mean == pytest.approx(0.4)
    assert result.ci95_low is not None and result.ci95_high is not None
    assert result.ci95_low < result.mean < result.ci95_high
    assert result.ci95_high - result.mean == pytest.approx(
        2.776 * result.standard_error, rel=0.01
    )
    assert "approximation" in str(result.ci_method)
    assert "not a participant-level" in result.interpretation
    assert "significance" in result.interpretation


def test_zero_variation_does_not_imply_certainty() -> None:
    result = summarize_scores([0.5] * 5)
    assert result.standard_error == 0.0
    assert result.ci95_low == result.ci95_high == 0.5
    assert "not" in result.interpretation.lower()


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -0.1, 1.1, True, None])
def test_invalid_values_fail_closed(bad: object) -> None:
    with pytest.raises(ValueError, match="finite numeric"):
        summarize_scores([bad])  # type: ignore[list-item]


def test_summary_dict_is_strict_json_compatible() -> None:
    payload = summary_dict([])
    assert "NaN" not in json.dumps(payload, allow_nan=False)
    assert payload["ci95_low"] is None


def test_slices_suppress_five_subject_default_holdout() -> None:
    subjects = [f"fake-{i}" for i in range(5) for _ in range(6)]
    labels = [i % 2 for i in range(30)]
    slices = ["left" if i % 2 else "right" for i in range(30)]
    rows = guarded_slice_metrics(labels, labels, subjects, slices)
    assert len(rows) == 2
    assert all(row["status"] == "suppressed" and row["metrics"] is None for row in rows)
    assert all(row["reason"] == "insufficient_independent_participants_or_trials" for row in rows)


def test_slices_allow_enough_distinct_subjects_and_both_classes() -> None:
    subjects = [f"fake-{i}" for i in range(12) for _ in range(6)]
    actual = [j % 2 for i in range(12) for j in range(6)]
    strata = ["left" if j < 3 else "right" for i in range(12) for j in range(6)]
    result = guarded_slice_metrics(actual, actual, subjects, strata)
    assert all(row["status"] == "ok" for row in result)
    assert all(row["n_participants"] == 12 for row in result)
    assert all(row["metrics"]["balanced_accuracy"] == 1.0 for row in result)


def test_slice_single_class_suppresses_even_with_n() -> None:
    subjects = [f"fake-{i}" for i in range(12) for _ in range(6)]
    truths = [0 for _ in subjects]
    rows = guarded_slice_metrics(truths, truths, subjects, ["left"] * len(subjects))
    assert rows[0]["status"] == "suppressed"
    assert rows[0]["reason"] == "single_truth_class"


def test_slice_rejects_bad_shapes_labels_and_axes() -> None:
    with pytest.raises(ValueError, match="lengths"):
        guarded_slice_metrics([0], [0], [], ["left"])
    with pytest.raises(ValueError, match="nonbinary"):
        guarded_slice_metrics([True], [0], ["s"], ["left"])  # type: ignore[list-item]
    with pytest.raises(ValueError, match="predefined"):
        guarded_slice_metrics([0], [0], ["s"], ["response_time_ms"])
    with pytest.raises(ValueError, match="at least 10"):
        guarded_slice_metrics([0], [0], ["s"], ["left"], min_participants=3)


def _synthetic_result(seed: int, *, valid: bool = True) -> dict[str, Any]:
    metrics = {
        "dummy_prior": {"status": "ok", "balanced_accuracy": 0.5, "macro_f1": 0.4},
        "logistic_regression": {"status": "ok", "balanced_accuracy": 0.6, "macro_f1": 0.5},
    }
    return {
        "status": "ok" if valid else "ineligible",
        "source": {
            "source_kind": "synthetic",
            "rights_basis": "synthetic-original",
            "source_sha256": f"synthetic-{seed}",
        },
        "split": {"assignment_sha256": f"split-{seed}"},
        "manifest_sha256": f"manifest-{seed}",
        "selected_model": "dummy_prior" if valid else None,
        "test_metrics": metrics if valid else None,
        "test_slice_errors": [{"status": "suppressed"}] if valid else None,
        "reasons": [] if valid else ["bad_training_folds"],
    }


def test_pipeline_predeclares_distinct_seed_pairs_and_digest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import psychneuro.pipeline as pipeline

    seeds: list[tuple[int, int]] = []

    def fake_run(config: object, path: Path) -> dict[str, Any]:
        assert path == REGISTRY
        seeds.append((config.generator_seed, config.split_seed))  # type: ignore[attr-defined]
        return _synthetic_result(config.generator_seed)  # type: ignore[attr-defined]

    monkeypatch.setattr(pipeline, "run_experiment", fake_run)
    report = run_pipeline(PipelineConfig(CFG, repeats=5), REGISTRY)
    assert seeds == [(73 + i, 42 + i) for i in range(5)]
    assert report["n_requested"] == report["n_eligible"] == 5
    assert report["status"] == "complete"
    assert report["summary"]["cv_selected_policy"]["balanced_accuracy"]["mean"] == 0.5
    assert report["summary"]["logistic_regression"]["balanced_accuracy"]["mean"] == 0.6
    assert report["runs"][0]["test_slice_errors"][0]["status"] == "suppressed"
    copy = dict(report)
    digest = copy.pop("report_sha256")
    canonical = json.dumps(copy, sort_keys=True, separators=(",", ":"), allow_nan=False)
    assert digest == hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_ineligible_run_disclosed_and_ci_withheld(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import psychneuro.pipeline as pipeline

    monkeypatch.setattr(
        pipeline,
        "run_experiment",
        lambda config, path: _synthetic_result(
            config.generator_seed, valid=config.generator_seed != 75
        ),
    )
    report = run_pipeline(PipelineConfig(CFG, repeats=5), REGISTRY)
    assert report["status"] == "incomplete"
    assert report["n_eligible"] == 4 and report["n_ineligible"] == 1
    assert report["runs"][2]["test_metrics"] is None
    assert report["summary"]["dummy_prior"]["macro_f1"]["ci95_low"] is None


@pytest.mark.parametrize("repeats", [-1, 0, 21, True, 1.5])
def test_invalid_repeat_count_is_rejected(repeats: object) -> None:
    with pytest.raises(PipelineError, match="repeats"):
        run_pipeline(PipelineConfig(CFG, repeats=repeats), REGISTRY)  # type: ignore[arg-type]


def test_seed_overflow_and_bad_protocol_rejected() -> None:
    with pytest.raises(PipelineError, match="seed"):
        run_pipeline(PipelineConfig(replace(CFG, generator_seed=2**64 - 2), 5), REGISTRY)
    with pytest.raises(PipelineError, match="unrecognized"):
        run_pipeline(PipelineConfig(replace(CFG, config_version="v2")), REGISTRY)


def test_wrong_rights_or_nonfinite_result_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import psychneuro.pipeline as pipeline

    def wrong_rights(config: object, path: Path) -> dict[str, Any]:
        obj = _synthetic_result(73)
        obj["source"]["rights_basis"] = "human-private"
        return obj

    monkeypatch.setattr(pipeline, "run_experiment", wrong_rights)
    with pytest.raises(PipelineError, match="synthetic"):
        run_pipeline(PipelineConfig(CFG, 1), REGISTRY)

    def nan_score(config: object, path: Path) -> dict[str, Any]:
        obj = _synthetic_result(73)
        obj["test_metrics"]["dummy_prior"]["balanced_accuracy"] = math.nan
        return obj

    monkeypatch.setattr(pipeline, "run_experiment", nan_score)
    with pytest.raises(PipelineError, match="invalid balanced_accuracy"):
        run_pipeline(PipelineConfig(CFG, 1), REGISTRY)
