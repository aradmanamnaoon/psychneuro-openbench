"""Bounded genuine synthetic Week 2 diagnostic; never a human study or p-value."""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .baselines import features_from_trials, make_estimator, predict_binary
from .loaders import load_dataset
from .metrics import score_binary
from .split import create_group_split, validate_group_split
from .synthetic import SyntheticConfig
from .week2_controls import (
    describe_response_times_ms,
    frozen_prediction_permutation_diagnostic,
    participant_bootstrap_ci,
)


def run_demo(registry: Path) -> dict[str, Any]:
    """No external data and NO test-set model selection; two prespecified models.

    Distinct fictional participant groups: 36 training, 12 validation and
    12 test when using 60 synthetic people (480 total invented rows).
    """
    data = load_dataset(
        SyntheticConfig(seed=73, n_participants=60, trials_per_participant=8),
        registry,
    )
    split = create_group_split(data, seed=42)
    validate_group_split(data, split)
    train = tuple(data.records[i] for i in split.train_indices)
    test = tuple(data.records[i] for i in split.test_indices)
    true = [r.correct for r in test]
    groups = [r.participant_id for r in test]
    outputs: dict[str, Any] = {}
    for name in ("dummy_prior", "logistic_regression"):
        model = make_estimator(name)
        model.fit(features_from_trials(train), [r.correct for r in train])
        predicted = predict_binary(model, features_from_trials(test))
        binary = score_binary(true, predicted)
        if binary.balanced_accuracy is None:
            raise ValueError("fictional held-out task has undefined class support")
        outputs[name] = {
            "test_balanced_accuracy": binary.balanced_accuracy,
            "test_macro_f1": binary.macro_f1,
            "cluster_bootstrap": asdict(
                participant_bootstrap_ci(
                    true, predicted, groups, seed=103, n_resamples=400,
                )
            ),
            "frozen_permutation": asdict(
                frozen_prediction_permutation_diagnostic(
                    true, predicted, groups, seed=107, n_permutations=100,
                )
            ),
        }
    return {
        "kind": "original-synthetic-software-diagnostic-only",
        "generator_seed": 73,
        "split_seed": 42,
        "n_fictional_participants": 60,
        "test_participants": len(split.test_participants),
        "n_rows": len(data.records),
        "source_sha256": data.schema.source_sha256,
        "split_sha256": split.assignment_sha256,
        "code_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "train_only_fit": True,
        "no_human_data": True,
        "limitations": (
            "Fictional data and original synthetic generator, two fixed models. "
            "No held-out model selection; frozen-prediction label permutation "
            "does not refit estimators or yield a valid model significance p-value. "
            "Percentile bootstrap conditions on fixed predictions, assumes "
            "exchangeable fictional participant clusters, and cannot support "
            "clinical or real-population inference."
        ),
        "response_time_descriptive_only": describe_response_times_ms(
            [r.response_time_ms for r in test]
        ),
        "models": outputs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Private Week 2 synthetic-only check")
    parser.add_argument("--registry", type=Path, default=Path("data/registry.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = run_demo(args.registry)
    target = args.output_dir
    target.mkdir(parents=True, exist_ok=True)
    (target / "synthetic-control-summary.json").write_text(
        json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("status=synthetic_only unit=fictional_participant")
    print(f"test_participants={report['test_participants']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
