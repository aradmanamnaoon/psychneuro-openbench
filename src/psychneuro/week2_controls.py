"""Week 2 experimental controls for fictional, nonclinical behavioral trials.

These functions do NOT fit models or estimate clinical/population effects.
The fixed-prediction bootstrap must not be described as an uncertainty interval
for refitted machine learning models, or used with a five-person holdout.
"""
from __future__ import annotations

import math
import random
import statistics
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from .metrics import score_binary


@dataclass(frozen=True, slots=True)
class ClusterInterval:
    status: Literal["ok", "undefined"]
    reason: str | None
    n_participants: int
    eligible_resamples: int
    requested_resamples: int
    point_balanced_accuracy: float | None
    ci95_low: float | None
    ci95_high: float | None
    method: str = "percentile_cluster_bootstrap_fixed_predictions"
    interpretation: str = (
        "Descriptive conditional resampling of fictional participant clusters "
        "with predictions held fixed; not refitted-model or human-population "
        "uncertainty. Requires independent groups and exchangeability."
    )


def _groups(
    y_true: Sequence[int], y_pred: Sequence[int], participants: Sequence[str]
) -> tuple[dict[str, tuple[int, ...]], float | None]:
    if len(y_true) != len(y_pred) or len(y_true) != len(participants):
        raise ValueError("truth/prediction/participant length mismatch")
    metric = score_binary(y_true, y_pred)
    mapped: dict[str, list[int]] = {}
    for index, participant in enumerate(participants):
        if (
            type(participant) is not str
            or not participant
            or len(participant) > 80
            or any(ord(char) < 32 for char in participant)
        ):
            raise ValueError("participant IDs must be nonempty bounded strings")
        mapped.setdefault(participant, []).append(index)
    return {key: tuple(value) for key, value in sorted(mapped.items())}, (
        metric.balanced_accuracy
    )


def _integer(value: int, *, name: str, lower: int, upper: int) -> None:
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f"{name} must be an integer in [{lower}, {upper}]")


def participant_bootstrap_ci(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    participants: Sequence[str],
    *,
    seed: int = 73,
    n_resamples: int = 400,
    min_participants: int = 10,
) -> ClusterInterval:
    """Descriptive 95% percentile interval over independent fictional subjects.

    A duplicate sampled group replicates ALL its trials. Suppress the interval
    for <10 groups, absent truth class, or too few eligible bootstrap draws.
    A five-person test partition must therefore return an undefined interval.
    """
    _integer(seed, name="seed", lower=0, upper=2**64 - 1)
    _integer(n_resamples, name="n_resamples", lower=100, upper=5000)
    _integer(min_participants, name="min_participants", lower=10, upper=100000)
    clusters, point = _groups(y_true, y_pred, participants)
    n = len(clusters)
    reason = None
    if n < min_participants:
        reason = "insufficient_independent_participants"
    elif point is None:
        reason = "undefined_original_metric"
    if reason is not None:
        return ClusterInterval("undefined", reason, n, 0, n_resamples, point, None, None)
    names = tuple(clusters)
    rng = random.Random(seed)
    scores: list[float] = []
    for _ in range(n_resamples):
        chosen = rng.choices(names, k=n)
        indices = [index for name in chosen for index in clusters[name]]
        metric = score_binary(
            [y_true[index] for index in indices],
            [y_pred[index] for index in indices],
        )
        if metric.balanced_accuracy is not None:
            scores.append(metric.balanced_accuracy)
    if len(scores) < math.ceil(n_resamples * 0.8):
        return ClusterInterval(
            "undefined", "too_many_ineligible_resamples",
            n, len(scores), n_resamples, point, None, None,
        )
    scores.sort()
    lower = scores[max(0, math.ceil(0.025 * len(scores)) - 1)]
    upper = scores[min(len(scores) - 1, math.ceil(0.975 * len(scores)) - 1)]
    return ClusterInterval(
        "ok", None, n, len(scores), n_resamples, point, lower, upper,
    )


@dataclass(frozen=True, slots=True)
class PermutationDiagnostic:
    observed_balanced_accuracy: float
    null_balanced_accuracies: tuple[float, ...]
    n_participants: int
    interpretation: str = (
        "Frozen predictions; permutes labels inside each fictional participant. "
        "No refitting, formal p-value or exchangeability validation. Not a "
        "significance test for the trained benchmark or real participants."
    )


def frozen_prediction_permutation_diagnostic(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    participants: Sequence[str],
    *,
    seed: int = 73,
    n_permutations: int = 100,
) -> PermutationDiagnostic:
    """Keep participant membership, class support and predictions unchanged."""
    _integer(seed, name="seed", lower=0, upper=2**64 - 1)
    _integer(n_permutations, name="n_permutations", lower=20, upper=2000)
    clusters, observed = _groups(y_true, y_pred, participants)
    if observed is None or len(clusters) < 3:
        raise ValueError("permutation requires both classes and at least 3 groups")
    rng = random.Random(seed)
    null: list[float] = []
    for _ in range(n_permutations):
        shuffled = list(y_true)
        for indices in clusters.values():
            values = [y_true[index] for index in indices]
            rng.shuffle(values)
            for index, value in zip(indices, values, strict=True):
                shuffled[index] = value
        metric = score_binary(shuffled, y_pred)
        if metric.balanced_accuracy is None:
            raise ValueError("class support unexpectedly vanished")
        null.append(metric.balanced_accuracy)
    return PermutationDiagnostic(observed, tuple(null), len(clusters))


def describe_response_times_ms(values: Sequence[float]) -> dict[str, float | int]:
    """Describe post-response milliseconds only; NEVER supply as predictors."""
    if not values or any(
        type(value) not in (int, float)
        or not math.isfinite(value)
        or value < 0
        for value in values
    ):
        raise ValueError("response_time_ms must be nonempty, finite and nonnegative")
    return {
        "n_trials": len(values),
        "median_response_time_ms": float(statistics.median(values)),
        "mean_response_time_ms": float(statistics.fmean(values)),
    }
