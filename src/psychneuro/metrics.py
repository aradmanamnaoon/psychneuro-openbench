"""Strict binary classification metrics for synthetic, nonclinical evaluation.

Undefined means genuinely unavailable, not zero, NaN or an imputed score.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

MetricStatus = Literal["ok", "undefined"]


@dataclass(frozen=True, slots=True)
class BinaryMetrics:
    status: MetricStatus
    reason: str | None
    n_trials: int
    support_0: int
    support_1: int
    predicted_0: int
    predicted_1: int
    prevalence_1: float | None
    confusion_matrix: tuple[tuple[int, int], tuple[int, int]]
    balanced_accuracy: float | None
    macro_f1: float | None


def _validate_labels(values: Sequence[int], name: str) -> None:
    for label in values:
        if type(label) is not int or label not in (0, 1):
            raise ValueError(f"{name} contains a missing, noninteger or nonbinary label")


def score_binary(y_true: Sequence[int], y_pred: Sequence[int]) -> BinaryMetrics:
    """Score fixed binary labels [0, 1], failing closed for invalid inputs.

    Any empty or single-truth-class partition returns undefined metrics and
    explicit support/confusion diagnostics instead of misleading finite scores.
    """
    if len(y_true) != len(y_pred):
        raise ValueError("truth/prediction length mismatch")
    _validate_labels(y_true, "y_true")
    _validate_labels(y_pred, "y_pred")
    tn = fp = fn = tp = 0
    for actual, predicted in zip(y_true, y_pred, strict=True):
        if actual == 0 and predicted == 0:
            tn += 1
        elif actual == 0 and predicted == 1:
            fp += 1
        elif actual == 1 and predicted == 0:
            fn += 1
        else:
            tp += 1
    count = len(y_true)
    support_0, support_1 = tn + fp, fn + tp
    prevalence = (support_1 / count) if count else None
    reason: str | None = None
    balanced: float | None = None
    macro: float | None = None
    if not count:
        reason = "empty_partition"
    elif support_0 == 0 or support_1 == 0:
        reason = "single_truth_class"
    else:
        recall_0 = tn / support_0
        recall_1 = tp / support_1
        balanced = (recall_0 + recall_1) / 2
        f1_0 = 2 * tn / (2 * tn + fp + fn) if (2 * tn + fp + fn) else 0.0
        f1_1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
        macro = (f1_0 + f1_1) / 2
        if not (0.0 <= balanced <= 1.0 and 0.0 <= macro <= 1.0):
            raise ValueError("metric outside [0, 1]")
    return BinaryMetrics(
        status="undefined" if reason is not None else "ok",
        reason=reason,
        n_trials=count,
        support_0=support_0,
        support_1=support_1,
        predicted_0=tn + fn,
        predicted_1=fp + tp,
        prevalence_1=prevalence,
        confusion_matrix=((tn, fp), (fn, tp)),
        balanced_accuracy=balanced,
        macro_f1=macro,
    )
