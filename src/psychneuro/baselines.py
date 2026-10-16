"""Leakage-safe, interpretable sklearn baselines for synthetic correctness."""
from __future__ import annotations

from collections.abc import Sequence
from importlib import import_module
from typing import Literal, Protocol, cast

from .schema import validate_predictor_columns
from .synthetic import TrialRecord

ModelName = Literal["dummy_prior", "logistic_regression"]
Features = tuple[float, str]
_ALLOWED = ("difficulty", "stimulus_condition")


class Estimator(Protocol):
    """Minimal boundary isolating optional third-party untyped APIs."""

    def fit(self, x: Sequence[Features], y: Sequence[int]) -> object: ...
    def predict(self, x: Sequence[Features]) -> Sequence[int]: ...


def features_from_trials(records: Sequence[TrialRecord]) -> list[Features]:
    """Expose exactly two pre-response features, never IDs/outcomes/latency."""
    validate_predictor_columns(_ALLOWED)
    return [(row.difficulty, row.stimulus_condition) for row in records]


class _Backend(Protocol):
    def fit(self, x: object, y: object) -> object: ...
    def predict(self, x: object) -> object: ...


class _ArrayAdapter:
    """Ensure ColumnTransformer receives a proper 2-D NumPy array."""

    def __init__(self, backend: object, *, dummy: bool) -> None:
        self._backend = cast(_Backend, backend)
        self._dummy = dummy

    def _array(self, x: Sequence[Features]) -> object:
        numpy = import_module("numpy")
        if self._dummy:
            return numpy.zeros((len(x), 1), dtype=float)
        return numpy.asarray(x, dtype=object)

    def fit(self, x: Sequence[Features], y: Sequence[int]) -> object:
        self._backend.fit(self._array(x), list(y))
        return self

    def predict(self, x: Sequence[Features]) -> Sequence[int]:
        raw = cast(Sequence[int], self._backend.predict(self._array(x)))
        return tuple(int(value) for value in raw)


def make_estimator(name: ModelName) -> Estimator:
    """Construct a FRESH model for each training fold.

    Optional sklearn dependency is required at execution, never at import time.
    The logistic pipeline fits scaler and categorical vocabulary on the fold's
    training records only.
    """
    try:
        dummy = import_module("sklearn.dummy")
        linear = import_module("sklearn.linear_model")
        compose = import_module("sklearn.compose")
        preprocessing = import_module("sklearn.preprocessing")
        pipeline = import_module("sklearn.pipeline")
    except ImportError as exc:
        raise RuntimeError("Install optional benchmark dependencies: .[benchmark]") from exc
    if name == "dummy_prior":
        return _ArrayAdapter(dummy.DummyClassifier(strategy="prior"), dummy=True)
    if name == "logistic_regression":
        preprocessor = compose.ColumnTransformer(
            transformers=[
                ("difficulty", preprocessing.StandardScaler(), [0]),
                ("condition", preprocessing.OneHotEncoder(handle_unknown="ignore"), [1]),
            ],
            remainder="drop",
        )
        return _ArrayAdapter(
            pipeline.Pipeline(
                steps=[
                    ("preprocess", preprocessor),
                    (
                        "classifier",
                        linear.LogisticRegression(
                            solver="lbfgs",
                            C=1.0,
                            max_iter=1000,
                            random_state=42,
                        ),
                    ),
                ]
            ),
            dummy=False,
        )
    raise ValueError(f"unknown model: {name}")


def predict_binary(estimator: Estimator, x: Sequence[Features]) -> tuple[int, ...]:
    """Convert numpy scalar predictions to concrete Python ints for strict metrics."""
    predictions: list[int] = []
    for prediction in estimator.predict(x):
        if prediction not in (0, 1):
            raise ValueError("nonbinary model output")
        predictions.append(int(prediction))
    return tuple(predictions)
