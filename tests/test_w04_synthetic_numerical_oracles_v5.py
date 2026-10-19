"""Independent software/numerical oracles on invented vectors, not W03 fitted results.

No human or behavioral participant observations enter these tests. All scores
are calculation checks and negative controls, never scientific findings.
"""
from __future__ import annotations

import numpy as np
import pytest
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold, KFold


def independent_binary_balanced_accuracy(y_true: list[int], y_pred: list[int]) -> float:
    if len(y_true) != len(y_pred) or set(y_true) != {0, 1} or not set(y_pred) <= {0, 1}:
        raise ValueError("ill-defined binary paired comparison")
    tpr = sum(a == b == 1 for a, b in zip(y_true, y_pred)) / y_true.count(1)
    tnr = sum(a == b == 0 for a, b in zip(y_true, y_pred)) / y_true.count(0)
    return (tpr + tnr) / 2


@pytest.mark.parametrize("seed", [1, 42, 73, 101, 2026])
def test_balanced_accuracy_matches_reference_across_fixed_seeds(seed: int) -> None:
    rng = np.random.default_rng(seed)
    y_true = [0] * 40 + [1] * 20
    preds = rng.integers(0, 2, size=len(y_true)).tolist()
    own = independent_binary_balanced_accuracy(y_true, preds)
    expected = float(balanced_accuracy_score(y_true, preds))
    assert own == pytest.approx(expected, abs=1e-15)
    assert 0 <= own <= 1
    assert independent_binary_balanced_accuracy(y_true, [0] * len(y_true)) == 0.5


@pytest.mark.parametrize("seed", [1, 42, 73, 101, 2026])
def test_groupkfold_avoids_identity_overlap_where_row_kfold_does_not(seed: int) -> None:
    groups = np.repeat(np.arange(16), 6)
    x = np.arange(len(groups)).reshape(-1, 1)
    labels = np.arange(len(groups)) % 2
    y = labels[groups]
    safe = GroupKFold(n_splits=4)
    safe_folds = list(safe.split(x, y, groups))
    assert len(safe_folds) == 4
    assert all(not (set(groups[tr]) & set(groups[va])) for tr, va in safe_folds)
    assert sorted([int(i) for _, va in safe_folds for i in va]) == list(range(len(groups)))
    leaky = KFold(n_splits=4, shuffle=True, random_state=seed)
    assert any(set(groups[tr]) & set(groups[va]) for tr, va in leaky.split(x, y))


def test_negative_inputs_rejected_and_hand_computable_oracle() -> None:
    assert independent_binary_balanced_accuracy([1, 1, 1, 1, 0, 0, 0, 0],
                                                [1, 1, 1, 0, 0, 0, 1, 1]) == 0.625
    with pytest.raises(ValueError, match="ill-defined"):
        independent_binary_balanced_accuracy([0, 0], [0, 0])
    with pytest.raises(ValueError, match="ill-defined"):
        independent_binary_balanced_accuracy([0, 1], [0, 1, 1])
    with pytest.raises(ValueError, match="ill-defined"):
        independent_binary_balanced_accuracy([0, 1], [0, 2])