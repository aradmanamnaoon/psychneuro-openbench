"""Predeclared synthetic test-slice diagnostics with strict suppression.

Only the pre-response 'stimulus_condition' is allowed as a slice axis. All
small or one-class subgroups receive NA, never a misleading finite score.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict

from .metrics import score_binary


def guarded_slice_metrics(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    participant_ids: Sequence[str],
    slice_values: Sequence[str],
    *,
    min_participants: int = 10,
    min_trials: int = 30,
) -> list[dict[str, object]]:
    """Compute fixed left/right strata, requiring distinct fictional subjects.

    Suppresses each subgroup independently. Do not treat two strata sharing
    participants as independent, or use these results for model selection.
    """
    n = len(y_true)
    if len(y_pred) != n or len(participant_ids) != n or len(slice_values) != n:
        raise ValueError("slice inputs have different lengths")
    if type(min_participants) is not int or min_participants < 10:
        raise ValueError("min_participants must be at least 10")
    if type(min_trials) is not int or min_trials < 30:
        raise ValueError("min_trials must be at least 30")
    if any(
        not isinstance(group, str) or not group.strip() for group in participant_ids
    ):
        raise ValueError("empty or invalid participant ID")
    if any(type(value) is not str or value not in ("left", "right") for value in slice_values):
        raise ValueError("only predefined stimulus_condition slices are allowed")
    # Validate even hidden/undersized rows; do not suppress malformed data.
    score_binary(y_true, y_pred)
    table: list[dict[str, object]] = []
    for label in ("left", "right"):
        indices = [i for i, value in enumerate(slice_values) if value == label]
        n_subjects = len({participant_ids[i] for i in indices})
        row: dict[str, object] = {
            "feature": "stimulus_condition",
            "slice": label,
            "n_trials": len(indices),
            "n_participants": n_subjects,
            "metrics": None,
        }
        if n_subjects < min_participants or len(indices) < min_trials:
            row["status"] = "suppressed"
            row["reason"] = "insufficient_independent_participants_or_trials"
        else:
            metric = score_binary(
                [y_true[i] for i in indices], [y_pred[i] for i in indices]
            )
            if metric.status != "ok":
                row["status"] = "suppressed"
                row["reason"] = metric.reason
            else:
                row["status"] = "ok"
                row["reason"] = None
                row["metrics"] = asdict(metric)
        table.append(row)
    return table
