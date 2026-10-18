"""Strict quality gate for the fixed, wholly synthetic v0 trial schema.

Latency limits are engineering plausibility bounds for invented fixtures,
NOT physiological thresholds for real participants.
"""
from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass

from .synthetic import MAX_TRIALS, TrialRecord, validate_trials

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z")
MIN_SYNTHETIC_RT_MS = 100.0
MAX_SYNTHETIC_RT_MS = 3000.0


@dataclass(frozen=True, slots=True)
class QualitySummary:
    n_trials: int
    n_participants: int
    n_sessions: int
    missing_values: int
    duplicate_trial_keys: int
    duplicate_trial_orders: int
    invalid_response_times: int
    invalid_ranges_or_types: int
    invalid_identifiers: int
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


class DataQualityError(ValueError):
    def __init__(self, summary: QualitySummary) -> None:
        self.summary = summary
        super().__init__("dataset rejected: " + "; ".join(summary.errors[:8]))


def validate_quality(records: Sequence[TrialRecord]) -> QualitySummary:
    """Audit all rows, then fail closed with machine-readable error counts."""
    seen: set[tuple[str, str, str, str]] = set()
    orders: set[tuple[str, str, str, int]] = set()
    participants: set[str] = set()
    sessions: set[tuple[str, str]] = set()
    errors: list[str] = []
    missing = duplicates = duplicate_orders = invalid_rt = invalid_values = invalid_ids = 0
    if not records or len(records) > MAX_TRIALS:
        errors.append("row count must be 1..100000")
    for row in records:
        identifiers = (row.dataset_id, row.participant_id, row.session_id, row.trial_id)
        values = (*identifiers, row.trial_order, row.stimulus_condition,
                  row.difficulty, row.correct, row.response,
                  row.response_time_ms, row.generator_seed)
        missing += sum(
            value is None or (isinstance(value, str) and not value.strip())
            for value in values
        )
        if any(not isinstance(v, str) or _ID.fullmatch(v) is None for v in identifiers):
            invalid_ids += 1
        if all(isinstance(v, str) for v in identifiers):
            key = (row.dataset_id, row.participant_id, row.session_id, row.trial_id)
            if key in seen:
                duplicates += 1
            seen.add(key)
            participants.add(row.participant_id)
            sessions.add((row.participant_id, row.session_id))
            if type(row.trial_order) is int:
                order_key = (row.dataset_id, row.participant_id, row.session_id, row.trial_order)
                if order_key in orders:
                    duplicate_orders += 1
                orders.add(order_key)
        rt = row.response_time_ms
        if (type(rt) is not float or not math.isfinite(rt)
                or not MIN_SYNTHETIC_RT_MS <= rt <= MAX_SYNTHETIC_RT_MS):
            invalid_rt += 1
        difficulty = row.difficulty
        if (type(difficulty) is not float or not math.isfinite(difficulty)
                or not 0.0 <= difficulty <= 1.0
                or type(row.correct) is not int or row.correct not in (0, 1)
                or type(row.trial_order) is not int or row.trial_order <= 0
                or type(row.generator_seed) is not int
                or not 0 <= row.generator_seed <= 2**64 - 1
                or row.stimulus_condition not in ("left", "right")
                or row.response not in ("left", "right")):
            invalid_values += 1
    for name, count in (
        ("missing values", missing),
        ("invalid identifiers", invalid_ids),
        ("duplicate trial keys", duplicates),
        ("duplicate trial orders", duplicate_orders),
        ("impossible synthetic reaction times", invalid_rt),
        ("invalid ranges or types", invalid_values),
    ):
        if count:
            errors.append(f"{name}: {count}")
    try:
        validate_trials(records)
    except (ValueError, TypeError) as exc:
        errors.append(f"schema: {exc}")
    summary = QualitySummary(
        n_trials=len(records), n_participants=len(participants), n_sessions=len(sessions),
        missing_values=missing, duplicate_trial_keys=duplicates,
        duplicate_trial_orders=duplicate_orders, invalid_response_times=invalid_rt,
        invalid_ranges_or_types=invalid_values, invalid_identifiers=invalid_ids,
        errors=tuple(errors),
    )
    if not summary.valid:
        raise DataQualityError(summary)
    return summary
