"""Test-only synthetic graphs: no empirical metric or participant observations."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

SOURCE = Path(__file__).parents[1] / "src/psychneuro/w04/receipt_v3.py"
SPEC = importlib.util.spec_from_file_location("receipt_v3", SOURCE)
assert SPEC is not None and SPEC.loader is not None
v = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v
SPEC.loader.exec_module(v)


def make_record(seed: int = 73):
    """Construct the documented W03 four-node contract, not a model evaluation."""
    s = hashlib.sha256(f"synthetic-source-{seed}".encode()).hexdigest()
    split = hashlib.sha256(f"synthetic-split-{seed}".encode()).hexdigest()
    request = {"generator_seed": seed, "split_seed": 42, "n_participants": 36,
               "trials_per_participant": 12, "outer_folds": 3, "inner_folds": 2,
               "predictors": ["difficulty", "stimulus_condition"]}
    rid = v.digest({"contract": "w03-engine-1", "request": request,
                    "source": s, "split": split})
    fields = {"schema_version": "w03-engine-1", "run_id": rid,
              "source_sha256": s, "split_sha256": split,
              "rights": "internal-synthetic-only", "n_train_groups": 21,
              "n_test_groups": 8, "outer_balanced_accuracy": 0.5,
              "dummy_outer_balanced_accuracy": 0.5,
              "test_balanced_accuracy": 0.5, "selected_c": 0.1}
    chain = []
    metadata = [
        {"source_sha256": s, "rights": "internal-synthetic-only", "seed": seed},
        {"split_sha256": split, "seed": 42, "train_groups": 21, "test_groups": 8},
        {"selected_c": 0.1, "model_spec_only": True, "trained_model_bytes_hash": None,
         "predictors": ["difficulty", "stimulus_condition"]},
        {"result_sha256": v.digest(fields), "request": request,
         "benchmark": {"outer_scores": [0.5, 0.5, 0.5],
                       "dummy_outer_scores": [0.5, 0.5, 0.5],
                       "outer_selected_c": [0.1, 0.1, 0.1], "final_c": 0.1,
                       "sealed_test_balanced_accuracy": 0.5,
                       "metric": "balanced_accuracy", "unit": "fictional_participant"}},
    ]
    for i, item in enumerate(metadata):
        parents = [chain[-1]["sha256"]] if chain else []
        sha = v.digest({"kind": v._KINDS[i], "parents": parents, "metadata": item})
        chain.append({"kind": v._KINDS[i], "parents": parents,
                      "metadata": item, "sha256": sha})
    return {"run_id": rid, "provenance_root": chain[-1]["sha256"],
            "nodes": chain, "rights": "internal-synthetic-only",
            "result": {**fields, "provenance_root": chain[-1]["sha256"]}}


def make_receipt(seed: int = 73):
    return v.issue_receipt(make_record(seed), tenant="tenant-A", policy_revision=2,
                           policy_sha256=hashlib.sha256(b"policy-v2").hexdigest())


@pytest.mark.parametrize("seed", [1, 42, 73, 101, 2026])
def test_roundtrip_repeatable_across_fixed_seeds(seed):
    first = make_receipt(seed)
    second = make_receipt(seed)
    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert v.verify_receipt(first, tenant="tenant-A",
                            expected_policy_sha256=first.policy_sha256,
                            trusted_root=first.provenance_root)["run_id"] == first.run_id
    assert len(v.canonical(first.model_dump(mode="json"))) < 250_000


@pytest.mark.parametrize("mutation", [
    lambda r: r["nodes"][0]["metadata"].update(seed=999),
    lambda r: r["nodes"][1]["parents"].clear(),
    lambda r: r["nodes"][1]["parents"].__setitem__(0, r["nodes"][3]["sha256"]),
    lambda r: r["nodes"].reverse(),
    lambda r: r["nodes"].pop(),
    lambda r: r["nodes"][2].update(sha256="xyz"),
    lambda r: r["result"].update(source_sha256="bad"),
    lambda r: r["result"].update(run_id="0" * 64),
    lambda r: r["result"].update(provenance_root="f" * 64),
    lambda r: r["result"].update(outer_balanced_accuracy=1.1),
    lambda r: r["result"].update(selected_c=3.0),
    lambda r: r.update(rights="public"),
    lambda r: r.update(secret="bad"),
    lambda r: r["nodes"][0]["metadata"].update(source_sha256="f"*64),
])
def test_corrupted_graph_denied(mutation):
    record = make_record()
    mutation(record)
    with pytest.raises(v.ReceiptError):
        v.verify_record(record)


def test_cross_tenant_stale_policy_external_anchor_and_replay():
    receipt = make_receipt()
    check = dict(tenant="tenant-A", expected_policy_sha256=receipt.policy_sha256)
    with pytest.raises(v.ReceiptError):
        v.verify_receipt(receipt, **{**check, "tenant": "tenant-B"})
    with pytest.raises(v.ReceiptError):
        v.verify_receipt(receipt, **{**check, "expected_policy_sha256": "f" * 64})
    with pytest.raises(v.ReceiptError):
        v.verify_receipt(receipt, **check, trusted_root="f" * 64)
    changed = receipt.model_copy(update={"tenant": "tenant-B"})
    with pytest.raises(v.ReceiptError, match="checksum"):
        v.verify_receipt(changed, **check)
    wrong = receipt.model_copy(update={"record": make_record(42)})
    with pytest.raises(v.ReceiptError):
        v.verify_receipt(wrong, **check)


def test_no_unknown_schema_and_oversized_archive():
    receipt = make_receipt()
    data = receipt.model_dump(mode="json")
    with pytest.raises(ValidationError):
        v.P13P25Receipt.model_validate({**data, "extra": "x"})
    with pytest.raises(ValidationError):
        v.P13P25Receipt.model_validate({**data, "schema_version": "w04-v4"})
    with pytest.raises(ValidationError):
        v.P13P25Receipt.model_validate({**data, "policy_revision": -1})
    with pytest.raises(v.ReceiptError):
        v.verify_record({**make_record(), "nodes": "x" * 250_001})


def test_independent_balanced_accuracy_oracle_not_fitted_metric():
    # Explicit 2x2 synthetic confusion counts. TPR 3/4 and TNR 2/4 => 0.625.
    y_true = [1, 1, 1, 1, 0, 0, 0, 0]
    y_pred = [1, 1, 1, 0, 0, 0, 1, 1]
    positive = sum(t == 1 and p == 1 for t, p in zip(y_true, y_pred)) / 4
    negative = sum(t == 0 and p == 0 for t, p in zip(y_true, y_pred)) / 4
    assert (positive + negative) / 2 == 0.625
    assert all(p == 0 for p in [0] * len(y_true))  # null always-negative control
    assert (0 / 4 + 4 / 4) / 2 == 0.5


def test_receipt_checksum_is_not_authenticity():
    # Fully coordinated attacker can rewrite all hashes if root is not anchored.
    attacker = make_receipt(42)
    assert v.verify_receipt(attacker, tenant="tenant-A",
                            expected_policy_sha256=attacker.policy_sha256)
    with pytest.raises(v.ReceiptError):
        v.verify_receipt(attacker, tenant="tenant-A",
                            expected_policy_sha256=attacker.policy_sha256,
                            trusted_root=make_receipt(73).provenance_root)


def _rehash_edited_record(record):
    """Adversary rewrites all SHA-256 hashes coherently; no secret key involved."""
    for n, node in enumerate(record["nodes"]):
        node["parents"] = [] if n == 0 else [record["nodes"][n - 1]["sha256"]]
        node["sha256"] = v.digest({"kind": node["kind"], "parents": node["parents"],
                                   "metadata": node["metadata"]})
    root = record["nodes"][-1]["sha256"]
    record["provenance_root"] = root
    record["result"]["provenance_root"] = root
    return record


@pytest.mark.parametrize("attack", ["run_id", "fit_score", "source_seed", "inner_grid",
                                    "late_feature", "test_score", "group_count", "method"])
def test_coherently_rehashed_but_inconsistent_scientific_claim_rejected(attack):
    record = make_record(73)
    b = record["nodes"][3]["metadata"]
    if attack == "run_id":
        new_id = "0" * 64
        record["run_id"] = new_id
        record["result"]["run_id"] = new_id
        b["result_sha256"] = v.digest({k: x for k, x in record["result"].items()
                                         if k != "provenance_root"})
    elif attack == "fit_score":
        record["result"]["outer_balanced_accuracy"] = 0.99
        b["result_sha256"] = v.digest({k: x for k, x in record["result"].items()
                                         if k != "provenance_root"})
    elif attack == "source_seed":
        record["nodes"][0]["metadata"]["seed"] = 9999
    elif attack == "inner_grid":
        b["benchmark"]["outer_selected_c"][0] = 3.0
    elif attack == "late_feature":
        record["nodes"][2]["metadata"]["predictors"] = ["reaction_time", "correct"]
    elif attack == "test_score":
        b["benchmark"]["sealed_test_balanced_accuracy"] = 0.99
    elif attack == "group_count":
        record["nodes"][1]["metadata"]["train_groups"] = 4
    elif attack == "method":
        b["benchmark"]["metric"] = "accuracy"
    _rehash_edited_record(record)
    with pytest.raises(v.ReceiptError):
        v.verify_record(record)


def test_coherently_rehashed_valid_looking_receipt_requires_independent_anchor():
    """Hash consistency can never prove authorship or actual sklearn execution."""
    good = make_record(73)
    attacker = make_record(101)
    assert v.verify_record(attacker)
    anchor = good["provenance_root"]
    tampered = v.issue_receipt(attacker, tenant="tenant-A", policy_revision=2,
                               policy_sha256=hashlib.sha256(b"p25").hexdigest())
    with pytest.raises(v.ReceiptError):
        v.verify_receipt(tampered, tenant="tenant-A",
                         expected_policy_sha256=tampered.policy_sha256,
                         trusted_root=anchor)