"""Independent synthetic numerical oracles; NOT a real W03/W04 integration test."""
from __future__ import annotations

import numpy as np
import pytest
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import GroupKFold, KFold


@pytest.mark.parametrize("seed", [17, 73, 101])
def test_grouped_cv_no_overlap(seed: int) -> None:
    groups = np.repeat(np.arange(16), 6)
    X = np.arange(96).reshape(-1, 1)
    y = np.tile([0, 1], 48)
    naive = KFold(n_splits=4, shuffle=True, random_state=seed)
    blocked = GroupKFold(n_splits=4)
    assert all(
        len(set(groups[train]) & set(groups[test])) > 0
        for train, test in naive.split(X, y)
    )
    assert all(
        not (set(groups[train]) & set(groups[test]))
        for train, test in blocked.split(X, y, groups)
    )


@pytest.mark.parametrize(
    ("truth", "prediction", "expected"),
    [
        ([1, 1, 1, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0, 0, 0, 1], 6 / 7),
        ([0, 0, 1, 1], [0, 0, 0, 0], 0.5),
        ([0, 0, 1, 1], [0, 0, 1, 1], 1.0),
        ([0, 0, 1, 1], [1, 1, 0, 0], 0.0),
    ],
)
def test_balanced_accuracy_independent_oracle(
    truth: list[int], prediction: list[int], expected: float
) -> None:
    t = np.asarray(truth)
    p = np.asarray(prediction)
    tp = int(((t == 1) & (p == 1)).sum())
    fn = int(((t == 1) & (p == 0)).sum())
    tn = int(((t == 0) & (p == 0)).sum())
    fp = int(((t == 0) & (p == 1)).sum())
    analytic = (tp / (tp + fn) + tn / (tn + fp)) / 2
    assert analytic == pytest.approx(expected, abs=1e-12)
    assert balanced_accuracy_score(t, p) == pytest.approx(analytic, abs=1e-12)
