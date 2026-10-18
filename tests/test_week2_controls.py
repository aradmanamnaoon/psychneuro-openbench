"""Week 2 newly executed controls and existing scientific invariants.

All objects are invented trial data. Nothing here validates human-level effects.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from psychneuro.config import load_baseline_config
from psychneuro.loaders import load_dataset
from psychneuro.metrics import score_binary
from psychneuro.quality import DataQualityError, validate_quality
from psychneuro.schema import validate_predictor_columns
from psychneuro.split import create_group_split, validate_group_split
from psychneuro.synthetic import SyntheticConfig, generate_trials
from psychneuro.week2_controls import (
    describe_response_times_ms,
    frozen_prediction_permutation_diagnostic,
    participant_bootstrap_ci,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "registry.json"


def fixture_labels() -> tuple[list[int], list[int], list[str]]:
    """Twelve independent fictional clusters with two target classes each."""
    truth = [0, 1] * 12
    prediction = [0, 1] * 12
    groups = [f"fictional-{index:02d}" for index in range(12) for _ in range(2)]
    return truth, prediction, groups


def test_cluster_bootstrap_perfect_fixture_has_exact_reference_interval() -> None:
    truth, pred, groups = fixture_labels()
    a = participant_bootstrap_ci(truth, pred, groups, seed=43, n_resamples=200)
    b = participant_bootstrap_ci(truth, pred, groups, seed=43, n_resamples=200)
    assert a == b
    assert a.status == "ok"
    assert a.n_participants == 12
    assert a.eligible_resamples == 200
    assert a.point_balanced_accuracy == 1.0
    assert (a.ci95_low, a.ci95_high) == (1.0, 1.0)
    assert "fixed" in a.interpretation


def test_cluster_bootstrap_suppresses_small_five_person_holdout() -> None:
    truth, pred, groups = fixture_labels()
    result = participant_bootstrap_ci(truth[:10], pred[:10], groups[:10])
    assert result.status == "undefined"
    assert result.reason == "insufficient_independent_participants"
    assert result.n_participants == 5
    assert result.ci95_low is None and result.ci95_high is None


def test_cluster_bootstrap_reports_single_truth_class() -> None:
    _, pred, groups = fixture_labels()
    result = participant_bootstrap_ci([0] * 24, pred, groups)
    assert result.status == "undefined"
    assert result.reason == "undefined_original_metric"


@pytest.mark.parametrize("bad", [True, -1, 2**64, "42"])
def test_cluster_bootstrap_rejects_bad_seed(bad: object) -> None:
    t, p, g = fixture_labels()
    with pytest.raises(ValueError, match="seed"):
        participant_bootstrap_ci(t, p, g, seed=bad)  # type: ignore[arg-type]


def test_cluster_bootstrap_invalid_participant_and_length_fail_closed() -> None:
    t, p, g = fixture_labels()
    with pytest.raises(ValueError, match="length mismatch"):
        participant_bootstrap_ci(t, p, g[:-1])
    g[0] = "\n"
    with pytest.raises(ValueError, match="participant IDs"):
        participant_bootstrap_ci(t, p, g)


def test_cluster_bootstrap_rejects_invalid_budget() -> None:
    t, p, g = fixture_labels()
    with pytest.raises(ValueError, match="n_resamples"):
        participant_bootstrap_ci(t, p, g, n_resamples=99)
    with pytest.raises(ValueError, match="min_participants"):
        participant_bootstrap_ci(t, p, g, min_participants=1)


def test_fixed_prediction_null_permutations_are_group_safe_and_repeated() -> None:
    t, p, g = fixture_labels()
    original = list(t)
    a = frozen_prediction_permutation_diagnostic(t, p, g, seed=8, n_permutations=30)
    b = frozen_prediction_permutation_diagnostic(t, p, g, seed=8, n_permutations=30)
    assert a == b
    assert a.n_participants == 12
    assert a.observed_balanced_accuracy == 1.0
    assert len(a.null_balanced_accuracies) == 30
    assert all(0 <= x <= 1 for x in a.null_balanced_accuracies)
    assert t == original
    assert "No refitting" in a.interpretation


def test_null_controls_reject_small_or_degenerate_groups() -> None:
    t, p, g = fixture_labels()
    with pytest.raises(ValueError, match="3 groups"):
        frozen_prediction_permutation_diagnostic(t[:4], p[:4], g[:4])
    with pytest.raises(ValueError, match="both classes"):
        frozen_prediction_permutation_diagnostic([0] * 24, p, g)


def test_hand_calculated_binary_metrics_and_undefined_denominators() -> None:
    metric = score_binary([0, 0, 0, 1], [0, 0, 0, 0])
    assert metric.confusion_matrix == ((3, 0), (1, 0))
    assert metric.balanced_accuracy == 0.5
    assert metric.macro_f1 == pytest.approx(3 / 7)
    assert metric.n_trials == 4
    assert score_binary([1, 1], [1, 0]).balanced_accuracy is None
    assert score_binary([], []).status == "undefined"


def test_response_time_units_are_milliseconds_and_not_legal_features() -> None:
    summary = describe_response_times_ms([100.0, 200.0, 300.0])
    assert summary["n_trials"] == 3
    assert summary["median_response_time_ms"] == 200.0
    assert summary["mean_response_time_ms"] == 200.0
    with pytest.raises(ValueError, match="forbidden"):
        validate_predictor_columns(("difficulty", "response_time_ms"))
    for values in ([], [-1.0], [float("nan")], [True]):
        with pytest.raises(ValueError, match="response_time_ms"):
            describe_response_times_ms(values)


def test_group_contamination_fails_even_if_indices_look_valid() -> None:
    data = load_dataset(
        SyntheticConfig(seed=73, n_participants=24, trials_per_participant=4),
        REGISTRY,
    )
    split = create_group_split(data, seed=42)
    tampered = replace(
        split,
        test_participants=(split.train_participants[0], *split.test_participants[1:]),
    )
    with pytest.raises(ValueError, match="participant leakage"):
        validate_group_split(data, tampered)


def test_two_real_independent_config_reads_agree_on_seed_and_checksum() -> None:
    first = load_baseline_config(ROOT / "configs" / "baseline.json")
    second = load_baseline_config(ROOT / "configs" / "baseline.json")
    assert first == second
    assert first.config_sha256 == second.config_sha256
    assert first.generator_seed == second.generator_seed
    assert len(first.config_sha256) == 64


def test_missingness_outliers_and_shifted_synthetic_records_are_guarded() -> None:
    original = generate_trials(
        SyntheticConfig(seed=11, n_participants=12, trials_per_participant=4)
    )
    assert validate_quality(original).n_trials == 48
    # Deliberate synthetic distribution shift: no real subjects or source claim.
    shifted = tuple(replace(row, difficulty=0.8) for row in original)
    assert validate_quality(shifted).n_trials == 48
    # The modified rows MUST NOT inherit the generator's signed provenance.
    data = load_dataset(
        SyntheticConfig(seed=11, n_participants=12, trials_per_participant=4),
        REGISTRY,
    )
    with pytest.raises(ValueError, match="stale|source|metadata"):
        create_group_split(replace(data, records=shifted))
    for changed in (
        replace(original[0], difficulty=float("nan")),
        replace(original[0], response_time_ms=-100.0),
        replace(original[0], response_time_ms=float("inf")),
    ):
        with pytest.raises((DataQualityError, ValueError)):
            validate_quality((changed, *original[1:]))


def test_synthetic_repeat_and_seed_change_are_visible() -> None:
    a = generate_trials(SyntheticConfig(seed=71, n_participants=12, trials_per_participant=4))
    b = generate_trials(SyntheticConfig(seed=71, n_participants=12, trials_per_participant=4))
    c = generate_trials(SyntheticConfig(seed=72, n_participants=12, trials_per_participant=4))
    assert a == b
    assert a != c
