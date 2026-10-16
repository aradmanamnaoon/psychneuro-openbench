"""Reproducible synthetic-only benchmark runner; no external data ingestion.

CLI: python -m psychneuro.experiments --output-dir artifacts/pm08
Held-out participants are evaluated once, after training-CV selection is frozen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, cast

from .baselines import ModelName, features_from_trials, make_estimator, predict_binary
from .loaders import LoadedDataset, load_dataset
from .metrics import BinaryMetrics, score_binary
from .split import GroupSplit, create_group_split, validate_group_split
from .synthetic import SyntheticConfig, TrialRecord

_MODELS: tuple[ModelName, ...] = ("dummy_prior", "logistic_regression")
_PROTOCOL = "synthetic-grouped-binary-v1"


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Frozen settings; must be chosen BEFORE outcomes/holdout are inspected."""

    generator_seed: int = 73
    n_participants: int = 24
    trials_per_participant: int = 20
    split_seed: int = 42
    cv_folds: int = 5


def _digest(obj: object) -> str:
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _rows(data: LoadedDataset, indices: tuple[int, ...]) -> tuple[TrialRecord, ...]:
    return tuple(data.records[i] for i in indices)


def _fit_evaluate(
    name: ModelName, data: LoadedDataset, fit: tuple[int, ...], evaluate: tuple[int, ...]
) -> BinaryMetrics:
    """No leakage: fresh estimator fits ONLY on the designated training rows."""
    fit_rows = _rows(data, fit)
    eval_rows = _rows(data, evaluate)
    y_train = [row.correct for row in fit_rows]
    if set(y_train) != {0, 1}:
        raise ValueError("model training has only one truth class")
    estimator = make_estimator(name)
    estimator.fit(features_from_trials(fit_rows), y_train)
    predictions = predict_binary(estimator, features_from_trials(eval_rows))
    return score_binary([row.correct for row in eval_rows], predictions)


def _cv_folds(
    data: LoadedDataset, split: GroupSplit, count: int
) -> tuple[dict[str, object], ...]:
    """Exact global row indices from grouped folds within training subjects only."""
    if count != 5:
        raise ValueError("v0 protocol requires exactly five training-only CV folds")
    sklearn_selection = import_module("sklearn.model_selection")
    selected = split.train_indices
    train_rows = _rows(data, selected)
    x = features_from_trials(train_rows)
    y = [row.correct for row in train_rows]
    groups = [row.participant_id for row in train_rows]
    if len(set(groups)) < count:
        raise ValueError("insufficient independent training groups for CV")
    folds: list[dict[str, object]] = []
    iterator = sklearn_selection.GroupKFold(n_splits=count).split(x, y, groups)
    for number, (fit_local, eval_local) in enumerate(iterator, start=1):
        fit = tuple(selected[int(i)] for i in fit_local)
        evaluate = tuple(selected[int(i)] for i in eval_local)
        fit_groups = {data.records[i].participant_id for i in fit}
        eval_groups = {data.records[i].participant_id for i in evaluate}
        if not fit_groups or not eval_groups or fit_groups & eval_groups:
            raise ValueError("group leakage in training CV")
        if set(fit) & set(evaluate) or set(fit) | set(evaluate) != set(selected):
            raise ValueError("row leakage or missing rows in training CV")
        membership = {
            "fold": number,
            "train_indices": fit,
            "validation_indices": evaluate,
            "train_participants": sorted(fit_groups),
            "validation_participants": sorted(eval_groups),
        }
        folds.append({**membership, "sha256": _digest(membership)})
    if len(folds) != count:
        raise ValueError("wrong number of grouped CV folds")
    return tuple(folds)


def _metric_dict(result: BinaryMetrics) -> dict[str, object]:
    return cast(dict[str, object], asdict(result))


def run_experiment(
    config: ExperimentConfig, registry_path: Path
) -> dict[str, object]:
    """Evaluate only internally generated, provenance-validated synthetic trials.

    No tuning is performed after observing holdout metrics. CV uses training
    groups only. The dedicated validation group is reported as diagnostic but
    not used to pick hyperparameters or decide the selected model.
    """
    if config.cv_folds != 5:
        raise ValueError("v0 fixed protocol requires cv_folds=5")
    dataset = load_dataset(
        SyntheticConfig(
            seed=config.generator_seed,
            n_participants=config.n_participants,
            trials_per_participant=config.trials_per_participant,
        ),
        registry_path,
    )
    split = create_group_split(dataset, seed=config.split_seed)
    validate_group_split(dataset, split)
    folds = _cv_folds(dataset, split, config.cv_folds)
    versions = {
        "python": platform.python_version(),
        "scikit_learn": str(import_module("sklearn").__version__),
    }
    source: dict[str, object] = {
        "dataset_id": dataset.schema.dataset_id,
        "rights_basis": dataset.provenance.rights_basis,
        "source_sha256": dataset.schema.source_sha256,
        "source_kind": dataset.provenance.source_kind,
        "generator_seed": config.generator_seed,
        "n_trials": len(dataset.records),
        "n_participants": len({r.participant_id for r in dataset.records}),
    }
    memberships: dict[str, object] = asdict(split)
    candidate_cv: dict[str, list[dict[str, object]]] = {}
    means: dict[str, float] = {}
    failed: list[str] = []
    # Crucial ordering: no call below accesses test labels until CV eligibility
    # and selected model have been fixed from the training-only CV results.
    for name in _MODELS:
        scores: list[dict[str, object]] = []
        balances: list[float] = []
        for fold in folds:
            fit = cast(tuple[int, ...], fold["train_indices"])
            eval_idx = cast(tuple[int, ...], fold["validation_indices"])
            try:
                metric = _fit_evaluate(name, dataset, fit, eval_idx)
            except (ValueError, RuntimeError) as exc:
                failed.append(f"{name}/fold-{fold['fold']}: {exc}")
                break
            scores.append({
                "fold": fold["fold"], "fold_sha256": fold["sha256"],
                "metrics": _metric_dict(metric),
            })
            if metric.balanced_accuracy is None:
                failed.append(f"{name}/fold-{fold['fold']}: {metric.reason}")
                break
            balances.append(metric.balanced_accuracy)
        candidate_cv[name] = scores
        if len(balances) == config.cv_folds:
            means[name] = sum(balances) / len(balances)

    base: dict[str, object] = {
        "protocol": _PROTOCOL,
        "configuration": asdict(config),
        "source": source,
        "split": memberships,
        "cv_folds": list(folds),
        "cv_metrics": candidate_cv,
        "cv_mean_balanced_accuracy": means,
        "versions": versions,
        "code_commit": os.environ.get("GITHUB_SHA", "unavailable"),
        "final_fit_policy": "train-only; no validation/test fitting",
        "selection_policy": "training CV balanced accuracy; ties favor dummy_prior",
        "test_access_policy": "once per prespecified model; not used for model selection",
    }
    if failed or set(means) != set(_MODELS):
        base.update({
            "status": "ineligible",
            "reasons": failed or ["incomplete_grouped_cv"],
            "selected_model": None,
            "validation_metrics": None,
            "test_metrics": None,
        })
    else:
        chosen = max(_MODELS, key=lambda name: (
            means[name],
            1 if name == "dummy_prior" else 0,
        ))
        base["selected_model"] = chosen  # freeze BEFORE test evaluation
        validation: dict[str, dict[str, object]] = {}
        for name in _MODELS:
            validation[name] = _metric_dict(
                _fit_evaluate(name, dataset, split.train_indices, split.validation_indices)
            )
        base["validation_metrics"] = validation
        # Held-out test is accessed only here, once selection is frozen.
        test: dict[str, dict[str, object]] = {}
        for name in _MODELS:
            test[name] = _metric_dict(
                _fit_evaluate(name, dataset, split.train_indices, split.test_indices)
            )
        base["test_metrics"] = test
        base["status"] = (
            "ok"
            if all(m["status"] == "ok" for m in [*validation.values(), *test.values()])
            else "ineligible"
        )
        base["reasons"] = [
            f"{partition}/{name}: {metric['reason']}"
            for partition, models in (("validation", validation), ("test", test))
            for name, metric in models.items()
            if metric["status"] != "ok"
        ]
    base["uncertainty_status"] = "unavailable"
    base["uncertainty_reason"] = "small independent synthetic holdout; no CI claimed"
    base["manifest_sha256"] = _digest(base)
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthetic-only grouped ML benchmark")
    parser.add_argument("--seed", type=int, default=73)
    parser.add_argument("--participants", type=int, default=24)
    parser.add_argument("--trials-per-participant", type=int, default=20)
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--registry", type=Path, default=Path("data/registry.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    config = ExperimentConfig(
        generator_seed=args.seed,
        n_participants=args.participants,
        trials_per_participant=args.trials_per_participant,
        split_seed=args.split_seed,
    )
    result = run_experiment(config, args.registry)
    output: Path = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    target = output / "manifest.json"
    target.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"status={result['status']} manifest={target} sha256={result['manifest_sha256']}")
    return 0 if result["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
