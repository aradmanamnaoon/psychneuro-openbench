"""Independent hand arithmetic against existing byte-identical W03 binary scorer."""
from __future__ import annotations

import random

import pytest

from psychneuro.metrics import score_binary


def oracle(y: list[int], pred: list[int]) -> float:
    """Independent count-based arithmetic (does not use W03 confusion matrix)."""
    negatives = sum(v == 0 for v in y)
    positives = sum(v == 1 for v in y)
    specificity = sum(a == 0 and b == 0 for a, b in zip(y, pred)) / negatives
    sensitivity = sum(a == 1 and b == 1 for a, b in zip(y, pred)) / positives
    return (specificity + sensitivity) / 2.0


@pytest.mark.parametrize('seed',[0,42,73,123,2026])
def test_independent_balanced_accuracy_multiple_permutations(seed: int) -> None:
    truth = [0, 0, 0, 0, 1, 1]
    predicted = [0, 0, 0, 1, 1, 0]
    z = list(zip(truth, predicted))
    random.Random(seed).shuffle(z)
    a = [r[0] for r in z]
    b = [r[1] for r in z]
    measured = score_binary(a, b)
    assert measured.balanced_accuracy == pytest.approx(0.625, abs=1e-15)
    assert measured.balanced_accuracy == pytest.approx(oracle(a, b), abs=1e-15)
    assert measured.confusion_matrix == ((3, 1), (1, 1))


def test_majority_prediction_negative_control() -> None:
    truth = [0,0,0,0,1,1]
    prediction = [0]*6
    outcome = score_binary(truth, prediction)
    assert outcome.balanced_accuracy == 0.5
    assert oracle(truth, prediction) == 0.5
    assert sum(a==b for a,b in zip(truth,prediction))/6 == pytest.approx(2/3)


@pytest.mark.parametrize('truth,prediction', [([], []),([0,0],[0,0]),([1,1],[1,1])])
def test_undefined_fold_support_is_not_zero(truth: list[int], prediction: list[int]) -> None:
    measured = score_binary(truth, prediction)
    assert measured.status == 'undefined' and measured.balanced_accuracy is None


@pytest.mark.parametrize('truth,prediction', [([0,1],[0]),([0,None],[0,1]),([0,1],[0,2])])
def test_malformed_binary_labels_are_refused(truth: list[int], prediction: list[int]) -> None:
    with pytest.raises(ValueError):
        score_binary(truth, prediction)