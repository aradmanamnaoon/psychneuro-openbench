"""PM-08 correctness, leakage and reproducibility tests; synthetic-only inputs.

Host these through the manual GitHub Actions workflow; do not claim they passed
until an actual run on the exact commit is inspected.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from psychneuro.baselines import features_from_trials, make_estimator, predict_binary
from psychneuro.experiments import ExperimentConfig, run_experiment
from psychneuro.metrics import score_binary
from psychneuro.synthetic import SyntheticConfig, generate_trials

REGISTRY = Path(__file__).resolve().parents[1] / "data" / "registry.json"


def test_perfect_binary_scores() -> None:
    result = score_binary([0, 1, 0, 1], [0, 1, 0, 1])
    assert result.status == "ok"
    assert result.balanced_accuracy == 1.0
    assert result.macro_f1 == 1.0
    assert result.confusion_matrix == ((2, 0), (0, 2))


def test_imbalanced_constant_prediction_retains_explicit_confusion() -> None:
    result = score_binary([0, 0, 0, 1], [0, 0, 0, 0])
    assert result.status == "ok"
    assert result.balanced_accuracy == 0.5
    assert result.macro_f1 == pytest.approx(3 / 7)
    assert result.confusion_matrix == ((3, 0), (1, 0))
    assert result.prevalence_1 == 0.25
    assert result.predicted_1 == 0


def test_all_wrong_is_zero_not_undefined() -> None:
    result = score_binary([0, 1, 1, 0], [1, 0, 0, 1])
    assert result.status == "ok"
    assert result.balanced_accuracy == 0.0
    assert result.macro_f1 == 0.0


@pytest.mark.parametrize(
    "truth,pred,reason",
    [
        ([], [], "empty_partition"),
        ([0, 0], [0, 1], "single_truth_class"),
        ([1, 1], [0, 1], "single_truth_class"),
    ],
)
def test_undefined_scores_report_null_not_nan(
    truth: list[int], pred: list[int], reason: str
) -> None:
    result = score_binary(truth, pred)
    assert result.status == "undefined"
    assert result.reason == reason
    assert result.balanced_accuracy is None
    assert result.macro_f1 is None


@pytest.mark.parametrize("values", [[2], [-1], [True], [None], [0.0], ["0"]])
def test_reject_invalid_binary_inputs(values: list[object]) -> None:
    with pytest.raises(ValueError, match="missing|nonbinary"):
        score_binary(values, [0])  # type: ignore[arg-type]


def test_reject_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="length mismatch"):
        score_binary([0, 1], [0])


def test_pre_response_only_feature_view() -> None:
    records = generate_trials(SyntheticConfig(seed=3, n_participants=2, trials_per_participant=2))
    actual = features_from_trials(records)
    assert actual == [(row.difficulty, row.stimulus_condition) for row in records]
    forged = replace(records[0], response_time_ms=9999.0, response="right")
    assert features_from_trials((forged, *records[1:])) == actual


def test_dummy_prior_uses_training_labels_only() -> None:
    model = make_estimator("dummy_prior")
    x = [(0.1, "left")] * 3
    model.fit(x, [1, 1, 0])
    assert predict_binary(model, [(0.9, "right")] * 4) == (1,) * 4


def test_interpretable_model_predictions_binary() -> None:
    model = make_estimator("logistic_regression")
    x = [(0.1, "left"), (0.2, "right"), (0.8, "left"), (0.9, "right")] * 5
    y = [1, 1, 0, 0] * 5
    model.fit(x, y)
    assert len(predict_binary(model, x)) == len(x)
    assert set(predict_binary(model, x)) <= {0, 1}


def test_unknown_baseline_rejected() -> None:
    with pytest.raises(ValueError, match="unknown model"):
        make_estimator("neural-network")  # type: ignore[arg-type]


def test_runner_uses_one_split_for_both_models() -> None:
    config = ExperimentConfig(n_participants=24, trials_per_participant=20)
    outcome = run_experiment(config, REGISTRY)
    assert outcome["status"] == "ok"
    assert outcome["selected_model"] in ("dummy_prior", "logistic_regression")
    folds = outcome["cv_folds"]
    assert len(folds) == 5  # type: ignore[arg-type]
    cv = outcome["cv_metrics"]
    assert set(cv) == {"dummy_prior", "logistic_regression"}  # type: ignore[arg-type]
    assert all(
        len(cv[model]) == 5  # type: ignore[index]
        for model in ("dummy_prior", "logistic_regression")
    )
    assert set(outcome["test_metrics"]) == {  # type: ignore[arg-type]
        "dummy_prior", "logistic_regression"
    }
    for fold in folds:  # type: ignore[union-attr]
        assert not set(fold["train_participants"]) & set(fold["validation_participants"])


def test_identical_config_repeats_manifest_digest() -> None:
    config = ExperimentConfig(generator_seed=74, n_participants=24, trials_per_participant=20)
    one = run_experiment(config, REGISTRY)
    two = run_experiment(config, REGISTRY)
    assert one == two
    assert one["manifest_sha256"] == two["manifest_sha256"]


def test_group_insufficiency_never_uses_random_rows() -> None:
    config = ExperimentConfig(n_participants=8, trials_per_participant=3)
    with pytest.raises(ValueError, match="insufficient participants"):
        run_experiment(config, REGISTRY)


def test_small_class_coverage_keeps_test_sealed() -> None:
    # One trial per person cannot ensure both labels in each 5-fold evaluation.
    config = ExperimentConfig(n_participants=9, trials_per_participant=1)
    outcome = run_experiment(config, REGISTRY)
    assert outcome["status"] == "ineligible"
    assert outcome["selected_model"] is None
    assert outcome["test_metrics"] is None
    assert outcome["reasons"]


def test_wrong_cv_count_fails_before_generation() -> None:
    with pytest.raises(ValueError, match="cv_folds=5"):
        run_experiment(ExperimentConfig(cv_folds=2), REGISTRY)
