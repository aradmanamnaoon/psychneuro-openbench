"""Fail-closed JSON configuration for the fixed synthetic benchmark v1 protocol.

No PyYAML or extra parser needed. No unapproved model, dataset or metric can
be introduced by editing a local config without a deliberate protocol revision.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

CONFIG_VERSION = "psychneuro-baseline-v1"
MAX_CONFIG_BYTES = 16_384
_MAX_SEED = 2**64 - 1
_MAX_TRIALS = 100_000

_FIXED = {
    "config_version": CONFIG_VERSION,
    "source": "synthetic-original",
    "split": {"method": "participant-shuffle-v1", "cv_folds": 5},
    "task": {"target": "correct", "predictors": ["difficulty", "stimulus_condition"]},
    "models": {
        "dummy_prior": {"strategy": "prior"},
        "logistic_regression": {
            "solver": "lbfgs", "C": 1.0, "max_iter": 1000, "random_state": 42,
        },
    },
    "metrics": {
        "primary": "balanced_accuracy", "secondary": "macro_f1", "labels": [0, 1],
    },
    "selection": {
        "method": "training_cv_mean_balanced_accuracy",
        "tie_break": "dummy_prior",
        "final_fit": "train_only",
        "test_use": "audit_once_each",
    },
}


@dataclass(frozen=True, slots=True)
class BaselineConfig:
    config_version: str
    config_sha256: str
    generator_seed: int
    n_participants: int
    trials_per_participant: int
    split_seed: int
    cv_folds: int


def _pairs_no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate configuration key: {key}")
        result[key] = value
    return result


def _object(value: object, name: str, allowed: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != allowed:
        raise ValueError(f"{name}: invalid or unknown configuration keys")
    return cast(dict[str, object], value)


def _matches(actual: object, expected: object) -> bool:
    """Strict recursive comparison; booleans are NOT interchangeable with integers."""
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict) and isinstance(actual, dict):
        return set(actual) == set(expected) and all(
            _matches(actual[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list) and isinstance(actual, list):
        return len(actual) == len(expected) and all(
            _matches(a, b) for a, b in zip(actual, expected, strict=True)
        )
    return actual == expected


def _integer(value: object, name: str, lower: int, upper: int) -> int:
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f"{name} must be an integer in [{lower}, {upper}]")
    return cast(int, value)


def load_baseline_config(path: Path) -> BaselineConfig:
    """Read an exact v1 contract, accepting seed/dimension changes only.

    Changes to model, metric, grouping, predictor timing, and selection rules
    require a different version and implementation; silently ignoring them is
    forbidden.
    """
    if path.is_symlink() or not path.is_file():
        raise ValueError("configuration must be an existing non-symlink file")
    if path.stat().st_size > MAX_CONFIG_BYTES:
        raise ValueError("configuration exceeds size limit")
    raw = path.read_bytes()
    if len(raw) > MAX_CONFIG_BYTES:
        raise ValueError("configuration exceeds size limit")
    try:
        document: object = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid UTF-8 JSON configuration") from exc
    root = _object(
        document, "root",
        {"config_version", "source", "dataset", "split", "task", "models", "metrics", "selection"},
    )
    for key, expected in _FIXED.items():
        if key == "split":
            continue
        if not _matches(root[key], expected):
            raise ValueError(f"{key}: unsupported or changed benchmark protocol")
    split = _object(root["split"], "split", {"method", "seed", "cv_folds"})
    for key, expected in cast(dict[str, object], _FIXED["split"]).items():
        if not _matches(split[key], expected):
            raise ValueError(f"split.{key}: unsupported protocol")
    dataset = _object(
        root["dataset"], "dataset",
        {"generator_seed", "n_participants", "trials_per_participant"},
    )
    generator_seed = _integer(dataset["generator_seed"], "generator_seed", 0, _MAX_SEED)
    split_seed = _integer(split["seed"], "split.seed", 0, _MAX_SEED)
    participants = _integer(dataset["n_participants"], "n_participants", 9, _MAX_TRIALS)
    trials = _integer(
        dataset["trials_per_participant"], "trials_per_participant", 1, _MAX_TRIALS
    )
    if participants * trials > _MAX_TRIALS:
        raise ValueError("synthetic trial count exceeds limit")
    folds = _integer(split["cv_folds"], "split.cv_folds", 5, 5)
    canonical = json.dumps(
        root, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return BaselineConfig(
        config_version=CONFIG_VERSION,
        config_sha256=hashlib.sha256(canonical).hexdigest(),
        generator_seed=generator_seed,
        n_participants=participants,
        trials_per_participant=trials,
        split_seed=split_seed,
        cv_folds=folds,
    )
