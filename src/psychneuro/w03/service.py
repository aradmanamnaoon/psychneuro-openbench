"""Integrate the existing source-gated P1 loader/split with P13's provenance chain."""
from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

from .contracts import ExperimentRequest, RunResult
from .nested import nested_grouped_benchmark
from .store import RunStore
from .vault import digest, make_chain, portable_chain


def execute(req: ExperimentRequest, registry_path: Path, store: RunStore, *,
            before_persist: Callable[[], None] | None = None) -> RunResult:
    # Import only on an explicit permitted run: fast API import never trains a model.
    from psychneuro.loaders import load_dataset
    from psychneuro.split import create_group_split, validate_group_split
    from psychneuro.synthetic import SyntheticConfig

    data = load_dataset(SyntheticConfig(seed=req.generator_seed,
        n_participants=req.n_participants,
        trials_per_participant=req.trials_per_participant), registry_path)
    split = create_group_split(data, seed=req.split_seed)
    validate_group_split(data, split)
    if data.provenance.license != "not-separately-specified" or data.provenance.source_kind != "synthetic":
        raise ValueError("rights registry no longer matches private synthetic policy")
    nested = nested_grouped_benchmark(data.records, split.train_indices, split.test_indices,
        outer_folds=req.outer_folds, inner_folds=req.inner_folds)
    source_hash = data.schema.source_sha256
    split_hash = split.assignment_sha256
    run_id = digest({"contract": "w03-engine-1", "request": req.model_dump(mode="json"),
                     "source": source_hash, "split": split_hash})
    benchmark = {
        "outer_scores": list(nested.outer_scores), "dummy_outer_scores": list(nested.dummy_scores),
        "outer_selected_c": list(nested.outer_c), "final_c": nested.final_c,
        "sealed_test_balanced_accuracy": nested.test_score,
        "metric": "balanced_accuracy", "unit": "fictional_participant",
    }
    result_fields = {"schema_version": "w03-engine-1", "run_id": run_id,
                     "source_sha256": source_hash, "split_sha256": split_hash,
                     "rights": "internal-synthetic-only",
                     "n_train_groups": len(split.train_participants),
                     "n_test_groups": len(split.test_participants),
                     "outer_balanced_accuracy": sum(nested.outer_scores) / len(nested.outer_scores),
                     "dummy_outer_balanced_accuracy": sum(nested.dummy_scores) / len(nested.dummy_scores),
                     "test_balanced_accuracy": nested.test_score, "selected_c": nested.final_c}
    chain = make_chain(
        {"source_sha256": source_hash, "rights": "internal-synthetic-only", "seed": req.generator_seed},
        {"split_sha256": split_hash, "seed": req.split_seed,
         "train_groups": len(split.train_participants), "test_groups": len(split.test_participants)},
        {"estimator": "logistic_regression", "trained_model_bytes_hash": None,
         "model_spec_only": True, "selected_c": nested.final_c,
         "predictors": list(req.predictors), "solver": "lbfgs", "max_iter": 1000,
         "code_sha": os.environ.get("GITHUB_SHA", "unattested"),
         "selection": "inner-group-CV-train-only"},
        {"benchmark": benchmark, "request": req.model_dump(mode="json"), "result_sha256": digest(result_fields)},
    )
    result = RunResult.model_validate({**result_fields, "provenance_root": chain[-1].sha256})
    if before_persist is not None:
        before_persist()  # Reject a revoked P25 grant before the durable write.
    store.put({"run_id": run_id, "provenance_root": chain[-1].sha256,
               "nodes": portable_chain(chain), "rights": "internal-synthetic-only",
               "result": result.model_dump(mode="json")})
    return result
