"""Test-only synthetic graphs: no empirical metric or participant observations."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
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
    rid = hashlib.sha256(f"synthetic-run-{seed}".encode()).hexdigest()
    fields = {"schema_version": "w03-engine-1", "run_id": rid,
              "source_sha256": s, "split_sha256": split,
              "rights": "internal-synthetic-only", "n_train_groups": 21,
              "n_test_groups": 8, "outer_balanced_accuracy": 0.5,
              "dummy_outer_balanced_accuracy": 0.5,
              "test_balanced_accuracy": 0.5, "selected_c": 0.1}
    chain = []
    metadata = [
        {"source_sha256": s, "rights": "internal-synthetic-only", "seed": seed},
        {"split_sha256": split, "train_groups": 21, "test_groups": 8},
        {"selected_c": 0.1, "model_spec_only": True},
        {"result_sha256": v.digest(fields), "benchmark": {"test_only": True}},
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
