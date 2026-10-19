"""Synthetic-only upstream educational reproducer for skrub group-aware CV proposal.

Row-wise KFold mixes repeated observations from the same fictional group;
the same records partitioned by GroupKFold pass the P1 leakage sentinel.
This does not execute skrub or establish behavioral/clinical validity.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest
from sklearn.model_selection import GroupKFold, KFold

from psychneuro.w03.nested import validate_isolation


@dataclass(frozen=True)
class ToyTrial:
    participant_id: str
    difficulty: float
    stimulus_condition: str
    correct: int


def _repeated_fictional_trials() -> tuple[ToyTrial, ...]:
    return tuple(
        ToyTrial(f"toy-{person:02d}", 0.2 + 0.2 * (i % 3),
                 "left" if i % 2 else "right", i % 2)
        for person in range(16) for i in range(6)
    )


def test_rowwise_split_is_detected_as_leakage() -> None:
    trials = _repeated_fictional_trials()
    train, heldout = next(KFold(n_splits=4, shuffle=True, random_state=73).split(trials))
    with pytest.raises(ValueError, match="participant contamination"):
        validate_isolation(trials, train.tolist(), heldout.tolist())


def test_group_split_passes_same_leakage_contract() -> None:
    trials = _repeated_fictional_trials()
    groups = np.array([trial.participant_id for trial in trials])
    for train, heldout in GroupKFold(n_splits=4).split(trials, groups=groups):
        validate_isolation(trials, train.tolist(), heldout.tolist())
        assert set(groups[train]).isdisjoint(set(groups[heldout]))
