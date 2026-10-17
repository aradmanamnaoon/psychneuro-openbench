"""PM-10: synthetic-only dataset -> grouped benchmark -> repeated uncertainty report.

Usage:
    python -m psychneuro.pipeline --config configs/baseline.json \
        --registry data/registry.json --repeats 5 --output-dir artifacts/pm10

The predeclared model/metric protocol cannot be changed here. This is not
empirical neuroscience evidence and never loads external participant data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import cast

from .config import CONFIG_VERSION, BaselineConfig, load_baseline_config
from .experiments import ExperimentConfig, run_experiment
from .uncertainty import summary_dict

_MAX_SEED = 2**64 - 1
_MODELS = ("dummy_prior", "logistic_regression", "cv_selected_policy")
_METRICS = ("balanced_accuracy", "macro_f1")
_REPORT_VERSION = "psychneuro-pm10-synthetic-repeat-v1"


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    baseline: BaselineConfig
    repeats: int = 5


class PipelineError(ValueError):
    """A report cannot be trusted or emitted due to invalid inputs/results."""


def _validate(config: PipelineConfig) -> None:
    b = config.baseline
    if type(config.repeats) is not int or not 1 <= config.repeats <= 20:
        raise PipelineError("repeats must be a predeclared integer from 1 to 20")
    if b.config_version != CONFIG_VERSION or len(b.config_sha256) != 64:
        raise PipelineError("unrecognized or unhashed baseline configuration")
    for seed in (b.generator_seed, b.split_seed):
        if type(seed) is not int or seed < 0 or seed + config.repeats - 1 > _MAX_SEED:
            raise PipelineError("seed sequence exceeds uint64 or has invalid type")
    if b.cv_folds != 5 or b.n_participants < 9 or b.trials_per_participant < 1:
        raise PipelineError("invalid grouped synthetic benchmark dimensions")
    if b.n_participants * b.trials_per_participant * config.repeats > 2_000_000:
        raise PipelineError("total synthetic trial budget exceeded")


def _score(metrics: object, name: str) -> dict[str, float]:
    if not isinstance(metrics, dict) or metrics.get("status") != "ok":
        raise PipelineError(f"{name}: no valid held-out test score")
    out: dict[str, float] = {}
    for metric in _METRICS:
        value = metrics.get(metric)
        if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
            raise PipelineError(f"{name}: invalid {metric} score")
        out[metric] = float(value)
    return out


def _digest(report: dict[str, object]) -> str:
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_pipeline(config: PipelineConfig, registry_path: Path) -> dict[str, object]:
    """Run locked protocol on distinct synthetic seeds, then summarize valid runs.

    Seed list and policy are fixed up front; no best-seed selection. Each run has
    its own fictional cohort; IDs within cohorts are not unique across runs.
    Ineligible runs remain in the denominator and are never scored as zeros.
    """
    _validate(config)
    b = config.baseline
    runs: list[dict[str, object]] = []
    kept: dict[str, dict[str, list[float]]] = {
        name: {metric: [] for metric in _METRICS} for name in _MODELS
    }
    for i in range(config.repeats):
        generator_seed = b.generator_seed + i
        split_seed = b.split_seed + i
        try:
            result = run_experiment(
                ExperimentConfig(
                    generator_seed=generator_seed,
                    n_participants=b.n_participants,
                    trials_per_participant=b.trials_per_participant,
                    split_seed=split_seed,
                    cv_folds=b.cv_folds,
                    config_version=b.config_version,
                    config_sha256=b.config_sha256,
                ),
                registry_path,
            )
        except (ValueError, RuntimeError) as exc:
            raise PipelineError(f"repeat {i + 1}: benchmark failed: {exc}") from exc
        source = cast(dict[str, object], result["source"])
        if source.get("source_kind") != "synthetic" or source.get("rights_basis") != "synthetic-original":
            raise PipelineError("only approved original synthetic data are allowed")
        status = result.get("status")
        if status not in ("ok", "ineligible"):
            raise PipelineError("unexpected experiment status")
        record: dict[str, object] = {
            "repeat": i + 1,
            "generator_seed": generator_seed,
            "split_seed": split_seed,
            "status": status,
            "source_sha256": source["source_sha256"],
            "split_sha256": cast(dict[str, object], result["split"])["assignment_sha256"],
            "experiment_manifest_sha256": result["manifest_sha256"],
            "selected_model": result["selected_model"],
            "reasons": result["reasons"],
            "test_metrics": None,
            "test_slice_errors": None,
        }
        if status == "ok":
            choice = result["selected_model"]
            if choice not in _MODELS[:2]:
                raise PipelineError("invalid or missing training-selected model")
            results = cast(dict[str, object], result["test_metrics"])
            if not isinstance(results, dict):
                raise PipelineError("missing test metrics")
            scored = {
                name: _score(results.get(name), name) for name in _MODELS[:2]
            }
            selected = scored[cast(str, choice)]
            scored["cv_selected_policy"] = selected
            for name, metrics in scored.items():
                for metric in _METRICS:
                    kept[name][metric].append(metrics[metric])
            record["test_metrics"] = scored
            record["test_slice_errors"] = result.get("test_slice_errors")
        runs.append(record)
    eligible = len(kept["cv_selected_policy"]["balanced_accuracy"])
    report: dict[str, object] = {
        "report_version": _REPORT_VERSION,
        "status": "complete" if eligible == config.repeats else "incomplete",
        "source_policy": "original synthetic only; no external or human data",
        "independence_unit": "distinctly seeded synthetic cohort; not trial rows",
        "config": {
            "baseline": asdict(b),
            "repeats": config.repeats,
            "seed_rule": "generator_seed+index and split_seed+index, index starts at 0",
        },
        "n_requested": config.repeats,
        "n_eligible": eligible,
        "n_ineligible": config.repeats - eligible,
        "runs": runs,
        "summary": {
            name: {metric: summary_dict(values) for metric, values in bucket.items()}
            for name, bucket in kept.items()
        },
        "interpretation": (
            "Only descriptive uncertainty across predetermined synthetic draws. "
            "Not a CI for human participants, model significance, clinical utility, "
            "or generalization. No best-seed picking; ineligible runs disclosed."
        ),
    }
    report["report_sha256"] = _digest(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded synthetic repeated benchmark report")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=Path("data/registry.json"))
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        frozen = load_baseline_config(args.config)
        report = run_pipeline(PipelineConfig(frozen, args.repeats), args.registry)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    output: Path = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    target = output / "report.json"
    target.write_text(
        json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"status={report['status']} report={target} sha256={report['report_sha256']}")
    return 0 if report["status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
