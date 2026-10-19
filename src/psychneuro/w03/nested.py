"""Group-nested CV with train-only inner selection and a sealed final holdout.

No inference about real psychology: records must already pass the repo's synthetic
registry, generator and source-digest validations before this module is called.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from psychneuro.metrics import score_binary


class TrialLike(Protocol):
    participant_id: str
    difficulty: float
    stimulus_condition: str
    correct: int


@dataclass(frozen=True)
class NestedResult:
    outer_scores: tuple[float, ...]
    dummy_scores: tuple[float, ...]
    outer_c: tuple[float, ...]
    final_c: float
    test_score: float


def validate_isolation(rows: Sequence[TrialLike], train: Sequence[int], test: Sequence[int]) -> None:
    """Negative-control sentinel: duplicates, missing rows and group crossover fail."""
    all_indices = list(train) + list(test)
    if any(type(i) is not int for i in all_indices):
        raise ValueError("noninteger row index")
    if len(all_indices) != len(set(all_indices)):
        raise ValueError("row contamination across train/test")
    if any(i < 0 or i >= len(rows) for i in all_indices):
        raise ValueError("out-of-range row index")
    a = {rows[i].participant_id for i in train}
    b = {rows[i].participant_id for i in test}
    if not a or not b or a & b:
        raise ValueError("participant contamination across train/test")


def _arrays(rows: Sequence[TrialLike], indices: Sequence[int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = np.asarray([(rows[i].difficulty, rows[i].stimulus_condition) for i in indices], dtype=object)
    y = np.asarray([rows[i].correct for i in indices], dtype=int)
    groups = np.asarray([rows[i].participant_id for i in indices])
    if x.ndim != 2 or x.shape[1] != 2 or not np.isfinite(x[:, 0].astype(float)).all():
        raise ValueError("invalid pre-response features")
    if set(y) != {0, 1}:
        raise ValueError("undefined binary class support")
    return x, y, groups


def _model(c: float) -> Pipeline:
    preprocess = ColumnTransformer([
        ("numeric", StandardScaler(), [0]),
        ("condition", OneHotEncoder(handle_unknown="ignore"), [1]),
    ])
    return Pipeline([
        ("preprocess", preprocess),
        ("classifier", LogisticRegression(C=c, solver="lbfgs", max_iter=1000, random_state=42)),
    ])


def _score(y: np.ndarray, pred: Sequence[int]) -> float:
    metric = score_binary([int(v) for v in y], [int(v) for v in pred])
    if metric.balanced_accuracy is None:
        raise ValueError("undefined fold balanced accuracy")
    return metric.balanced_accuracy


def _select(x: np.ndarray, y: np.ndarray, groups: np.ndarray, folds: int) -> float:
    if len(set(groups)) < folds:
        raise ValueError("too few independent training groups")
    scored: list[tuple[float, float]] = []
    for c in (0.1, 1.0):
        scores: list[float] = []
        for tr, val in GroupKFold(n_splits=folds).split(x, y, groups):
            if set(groups[tr]) & set(groups[val]):
                raise ValueError("inner participant contamination")
            if set(y[tr]) != {0, 1}:
                raise ValueError("inner fit lacks two classes")
            est = _model(c)
            est.fit(x[tr], y[tr])
            scores.append(_score(y[val], est.predict(x[val])))
        scored.append((float(np.mean(scores)), c))
    # Frozen tie policy: prefer simpler stronger regularization C=0.1.
    return sorted(scored, key=lambda it: (-it[0], it[1]))[0][1]


def nested_grouped_benchmark(
    rows: Sequence[TrialLike], train_indices: Sequence[int], test_indices: Sequence[int],
    *, outer_folds: int = 3, inner_folds: int = 2,
) -> NestedResult:
    if (outer_folds, inner_folds) != (3, 2):
        raise ValueError("unsupported prespecified nested folds")
    validate_isolation(rows, train_indices, test_indices)
    x, y, groups = _arrays(rows, train_indices)
    xt, yt, gt = _arrays(rows, test_indices)
    if len(set(groups)) < outer_folds * inner_folds:
        raise ValueError("not enough independent groups for nested CV")
    if set(groups) & set(gt):
        raise ValueError("heldout participant contamination")
    scores: list[float] = []
    dummies: list[float] = []
    selected: list[float] = []
    for tr, val in GroupKFold(n_splits=outer_folds).split(x, y, groups):
        if set(groups[tr]) & set(groups[val]):
            raise ValueError("outer participant contamination")
        c = _select(x[tr], y[tr], groups[tr], inner_folds)
        selected.append(c)
        fitted = _model(c).fit(x[tr], y[tr])
        scores.append(_score(y[val], fitted.predict(x[val])))
        baseline = DummyClassifier(strategy="prior").fit(np.zeros((len(tr), 1)), y[tr])
        dummies.append(_score(y[val], baseline.predict(np.zeros((len(val), 1)))))
    # Final tuning sees TRAINING DATA ONLY. The sealed test is scored once.
    frozen_c = _select(x, y, groups, inner_folds)
    final = _model(frozen_c).fit(x, y)
    heldout = _score(yt, final.predict(xt))
    return NestedResult(tuple(scores), tuple(dummies), tuple(selected), frozen_c, heldout)
