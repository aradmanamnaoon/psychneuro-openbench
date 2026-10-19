"""Full-repository-only genuine P1->P13->P25 synthetic integration.

This test MUST run against the actual checked-out repository with its real
registry, W03 sklearn nested-CV, W04 SQLite P25 and fenced queue. It is NOT
part of the isolated test-double suite and is NOT claimed as already passing.
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

import pytest

from psychneuro.w04.policy_v2 import PolicyError, PolicyRecord, PolicyStore
from psychneuro.w04.private_worker_v4 import AtomicWorker, Request, preflight_source
from psychneuro.w04.queue_v2 import JobConflict, QueueStore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry.json"
KEY = b"W04-test-only-hmac-key-never-store-real-production-secrets"


def make_system(tmp_path: Path, *, seed: int = 73, wrong_source: bool = False):
    assert REGISTRY.exists(), "source registry required: never silently use fake data"
    request = Request(version="w04-worker-request-4", generator_seed=seed, split_seed=42,
                      n_participants=36, trials_per_participant=12)
    source_sha = preflight_source(request, REGISTRY)
    assert len(source_sha) == 64
    db = tmp_path / "atomic.sqlite"
    policy = PolicyStore(db, permit_key=KEY)
    grant = PolicyRecord(
        tenant="w04-test", source_sha256=("f"*64 if wrong_source else source_sha),
        actions=frozenset({"run", "read_aggregate"}),
        attestation_ref="TEST-ONLY-no-independent-real-attestation",
        retention_until_ns=time.time_ns() + 600_000_000_000,
    )
    assert policy.install(grant, operator="test-operator") == 1
    queue = QueueStore(db)
    return AtomicWorker(database=db, policy=policy, queue=queue, registry_path=REGISTRY), policy, request, db


@pytest.mark.parametrize("seed", [73, 101])
def test_real_grouped_w03_run_authorization_and_receipt(tmp_path: Path, seed: int):
    processor, policy, request, db = make_system(tmp_path, seed=seed)
    item = processor.submit(tenant="w04-test", subject="fictional-researcher",
                            role="researcher", idempotency_key=f"seed-{seed}",
                            request=request, correlation="pre-run")
    # No manually supplied model score. execute() loads registry and runs W03 fit.
    assert processor.run_one(tenant="w04-test", job_id=item.id,
                             worker="internal-worker", correlation="training").state == "succeeded"
    receipt = processor.read(tenant="w04-test", subject="fictional-researcher",
                             role="researcher", job_id=item.id, correlation="inspect")
    record = receipt.record
    assert receipt.run_id == record["result"]["run_id"]
    assert record["result"]["source_sha256"] == preflight_source(request, REGISTRY)
    assert record["result"]["n_train_groups"] > 0
    assert record["result"]["n_test_groups"] > 0
    assert 0 <= record["result"]["outer_balanced_accuracy"] <= 1
    assert 0 <= record["result"]["dummy_outer_balanced_accuracy"] <= 1
    assert 0 <= record["result"]["test_balanced_accuracy"] <= 1
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT count(*) FROM w04_v4_artifacts").fetchone()[0] == 1
    with pytest.raises(JobConflict):
        processor.read(tenant="w04-test", subject="other-user", role="researcher",
                       job_id=item.id, correlation="denied")
    policy.revoke(tenant="w04-test", dataset="w03-original-synthetic", operator="test-operator")
    with pytest.raises(PolicyError):
        processor.read(tenant="w04-test", subject="fictional-researcher", role="researcher",
                       job_id=item.id, correlation="after-revocation")


def test_wrong_source_denied_before_calling_w03_training(tmp_path: Path):
    processor, _, request, db = make_system(tmp_path, wrong_source=True)
    def forbidden_training(*_):
        raise AssertionError("model fitting should not start with wrong data digest")
    processor.execute = forbidden_training
    item = processor.submit(tenant="w04-test", subject="fictional-researcher", role="researcher",
                            idempotency_key="wrong-digest", request=request, correlation="pre-run")
    with pytest.raises(PolicyError):
        processor.run_one(tenant="w04-test", job_id=item.id,
                          worker="internal-worker", correlation="deny-pre-fit")
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT count(*) FROM w04_v4_artifacts").fetchone()[0] == 0
