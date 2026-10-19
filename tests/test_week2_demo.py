"""Actual bounded Week 2 rights-cleared end-to-end diagnostic tests."""
from __future__ import annotations

from pathlib import Path

from psychneuro.week2_demo import run_demo

REGISTRY = Path(__file__).resolve().parents[1] / "data" / "registry.json"


def test_control_demo_rerun_identical_group_safe_synthetic_results() -> None:
    a = run_demo(REGISTRY)
    b = run_demo(REGISTRY)
    assert a == b
    assert a["n_rows"] == 480
    assert a["n_fictional_participants"] == 60
    assert a["test_participants"] == 12
    assert a["train_only_fit"]
    assert a["no_human_data"]
    assert len(a["source_sha256"]) == 64
    assert len(a["split_sha256"]) == 64
    assert set(a["models"]) == {"dummy_prior", "logistic_regression"}
    for entry in a["models"].values():
        assert 0 <= entry["test_balanced_accuracy"] <= 1
        assert entry["cluster_bootstrap"]["status"] == "ok"
        assert entry["cluster_bootstrap"]["n_participants"] == 12
        assert len(entry["frozen_permutation"]["null_balanced_accuracies"]) == 100
    assert a["response_time_descriptive_only"]["n_trials"] == 96
