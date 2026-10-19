"""W04 v2 security regression tests. Artificial identities and synthetic datasets only."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from pydantic import ValidationError

from psychneuro.w04.policy_v2 import IntegrityError, Permit, PolicyError, PolicyRecord, PolicyStore
from psychneuro.w04.queue_v2 import JobConflict, QueueStore

TEST_PERMIT_KEY = b"synthetic-only-test-hmac-key-never-use-in-production"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def policy(tmp_path: Path) -> tuple[PolicyStore, PolicyRecord]:
    store = PolicyStore(tmp_path / "shared.sqlite", permit_key=TEST_PERMIT_KEY)
    record = PolicyRecord(tenant="tenant-A", source_sha256=sha(b"invented data"),
                          actions=frozenset({"run", "read_aggregate"}),
                          attestation_ref="operator-verified-synthetic-registry-v1",
                          retention_until_ns=10**20)
    assert store.install(record, operator="maintainer") == 1
    return store, record


def permit(store: PolicyStore, now: int = 100_000_000_000) -> Permit:
    return store.authorize(tenant="tenant-A", dataset="w03-original-synthetic",
                           subject="researcher", role="researcher", action="run",
                           purpose="internal-method-validation", correlation_id="corr-1",
                           now_ns=now)


def test_unknown_foreign_or_unattested_denied(policy):
    store, _ = policy
    with pytest.raises(PolicyError):
        store.authorize(tenant="tenant-B", dataset="w03-original-synthetic", subject="researcher",
                        role="researcher", action="run", purpose="internal-method-validation",
                        correlation_id="x", now_ns=100)
    with pytest.raises(ValidationError):
        PolicyRecord(tenant="tenant-B", dataset="patient-database", source_sha256=sha(b"x"),
                     actions=frozenset({"run"}), attestation_ref="fake-proof",
                     retention_until_ns=10**20)
    with pytest.raises(ValidationError):
        PolicyRecord(tenant="tenant-B", source_sha256="oops", actions=frozenset({"run"}),
                     attestation_ref="fake-proof", retention_until_ns=10**20)


@pytest.mark.parametrize("change", [dict(action="export_data"), dict(purpose="clinical-diagnosis"),
                                     dict(role="viewer"), dict(action="export_aggregate")])
def test_scope_denial_is_audited(policy, change):
    store, _ = policy
    kwargs = dict(tenant="tenant-A", dataset="w03-original-synthetic", subject="researcher",
                  role="researcher", action="run", purpose="internal-method-validation",
                  correlation_id="deny-1", now_ns=100)
    kwargs.update(change)
    before, _ = store.verify()
    with pytest.raises(PolicyError):
        store.authorize(**kwargs)
    after, _ = store.verify()
    assert after == before + 1


def test_revocation_is_terminal_and_invalidates_permits(policy):
    store, rec = policy
    p = permit(store)
    store.validate_permit(p, now_ns=100_000_000_001)
    assert store.revoke(tenant=rec.tenant, dataset=rec.dataset, operator="maintainer") == 2
    with pytest.raises(PolicyError):
        store.validate_permit(p, now_ns=100_000_000_002)
    with pytest.raises(PolicyError):
        store.install(rec, operator="maintainer", expected_revision=2)
    with pytest.raises(PolicyError):
        permit(store)


def test_policy_expiry_old_permit_and_schema_migration(policy, tmp_path):
    store, rec = policy
    p = permit(store)
    with pytest.raises(PolicyError):
        store.validate_permit(p, now_ns=p.expires_ns)
    assert store.install(rec.model_copy(update={"actions": frozenset({"read_aggregate"})}),
                         operator="maintainer", expected_revision=1) == 2
    with pytest.raises(PolicyError):
        store.validate_permit(p, now_ns=100_000_000_002)
    with sqlite3.connect(store.path) as db:
        db.execute("UPDATE p25_v2_meta SET v='9' WHERE k='version'")
    with pytest.raises(IntegrityError):
        PolicyStore(store.path, permit_key=TEST_PERMIT_KEY)


def test_policy_tamper_detected_and_independent_root(policy):
    store, rec = policy
    count, anchor = store.verify()
    assert count == 1
    assert store.verify(trusted_root=anchor) == (count, anchor)
    with pytest.raises(IntegrityError):
        store.verify(trusted_root=sha(b"wrong"))
    with sqlite3.connect(store.path) as db:
        db.execute("UPDATE p25_v2_policy SET payload=? WHERE tenant=?", ('{}', rec.tenant))
    with pytest.raises(IntegrityError):
        store.verify()


def test_atomic_rollback_when_bad_operator(policy):
    store, rec = policy
    old = store.verify()
    with pytest.raises(ValueError):
        store.install(rec, operator="not safe", expected_revision=1)
    with pytest.raises(PolicyError):
        store.install(rec, operator="maintainer", expected_revision=999)
    assert store.verify() == old


def create_job(store: QueueStore, *, key="id1", payload=None):
    return store.enqueue(tenant="tenant-A", subject="researcher", dataset="w03-original-synthetic",
                         idempotency_key=key, payload=payload or {"seed": 73}, correlation="corr-1",
                         now_ns=1_000_000_000)


def test_idempotent_concurrent_enqueue_and_conflicts(tmp_path):
    queue = QueueStore(tmp_path / "jobs.sqlite")
    with ThreadPoolExecutor(max_workers=8) as pool:
        items = list(pool.map(lambda _: create_job(queue), range(24)))
    assert len({item.id for item in items}) == 1
    assert len(queue.audit(tenant="tenant-A", job_id=items[0].id, subject="researcher")) == 1
    with pytest.raises(JobConflict):
        create_job(queue, payload={"seed": 74})
    with pytest.raises(JobConflict):
        queue.get(tenant="tenant-B", job_id=items[0].id, subject="researcher")
    with pytest.raises(JobConflict):
        queue.get(tenant="tenant-A", job_id=items[0].id, subject="intruder")


def test_claim_lease_fence_crash_recovery_and_stale_completion(tmp_path):
    q = QueueStore(tmp_path / "jobs.sqlite")
    job = create_job(q)
    a = q.claim(tenant="tenant-A", job_id=job.id, worker="w1", correlation="c1",
                lease_ns=10_000_000, now_ns=2_000_000_000)
    with pytest.raises(JobConflict):
        q.claim(tenant="tenant-A", job_id=job.id, worker="w2", correlation="c2",
                lease_ns=10_000_000, now_ns=2_000_000_001)
    b = q.claim(tenant="tenant-A", job_id=job.id, worker="w2", correlation="c2",
                lease_ns=10_000_000, now_ns=2_020_000_000)
    assert b.fence > a.fence and b.attempts == 2
    with pytest.raises(JobConflict):
        q.complete(tenant="tenant-A", job_id=job.id, worker="w1", fence=a.fence,
                   result_sha256=sha(b"result"), correlation="old", now_ns=2_020_000_001)
    for stage in ("loaded", "split_validated", "fit_completed", "persisted"):
        b = q.checkpoint(tenant="tenant-A", job_id=job.id, worker="w2", fence=b.fence,
                         stage=stage, artifact_sha256=sha(b"result"), correlation="c2",
                         now_ns=2_020_000_001)
    last = q.complete(tenant="tenant-A", job_id=job.id, worker="w2", fence=b.fence,
                      result_sha256=sha(b"result"), correlation="c2", now_ns=2_020_000_002)
    assert last.state == "succeeded"
    assert QueueStore(q.path).get(tenant="tenant-A", job_id=job.id, subject="researcher") == last
    with pytest.raises(JobConflict):
        q.claim(tenant="tenant-A", job_id=job.id, worker="w3", correlation="c3",
                lease_ns=1_000_000, now_ns=2_030_000_000)


def test_cancel_then_resume_requires_fresh_policy_and_rejects_old_worker(policy, tmp_path):
    store, _ = policy
    q = QueueStore(tmp_path / "jobs.sqlite")
    job = create_job(q)
    running = q.claim(tenant="tenant-A", job_id=job.id, worker="worker", correlation="go",
                      lease_ns=50_000_000, now_ns=2_000_000_000)
    cancel = q.cancel(tenant="tenant-A", job_id=job.id, subject="researcher",
                      correlation="abort", now_ns=2_000_000_001)
    assert cancel.state == "cancel_requested"
    with pytest.raises(JobConflict):
        q.checkpoint(tenant="tenant-A", job_id=job.id, worker="worker", fence=running.fence,
                     stage="loaded", artifact_sha256=sha(b"x"), correlation="late", now_ns=2_000_000_002)
    ended = q.acknowledge_cancel(tenant="tenant-A", job_id=job.id,
                                 subject="researcher", correlation="ack", now_ns=2_000_000_003)
    assert ended.state == "cancelled"
    with pytest.raises(PolicyError):
        q.resume_cancelled(tenant="tenant-A", job_id=job.id, subject="researcher",
                           correlation="resume", permit=permit(store), policy_store=store,
                           now_ns=4_000_000_000_000)
    scoped = permit(store, now=3_000_000_000)
    resumed = q.resume_cancelled(tenant="tenant-A", job_id=job.id, subject="researcher",
                                 correlation="resume", permit=scoped, policy_store=store,
                                 now_ns=3_000_000_001)
    assert resumed.state == "queued"
    assert q.claim(tenant="tenant-A", job_id=job.id, worker="newworker", correlation="go",
                   lease_ns=50_000_000, now_ns=3_000_000_002).fence > running.fence


def test_fail_backoff_attempt_budget_and_checkpoint_regression(tmp_path):
    q = QueueStore(tmp_path / "jobs.sqlite")
    item = create_job(q)
    t = 10_000_000_000
    for attempt in range(1, 4):
        claim = q.claim(tenant="tenant-A", job_id=item.id, worker="w", correlation="retry",
                        lease_ns=20_000_000, now_ns=t)
        assert claim.attempts == attempt
        if attempt == 1:
            q.checkpoint(tenant="tenant-A", job_id=item.id, worker="w", fence=claim.fence,
                         stage="split_validated", artifact_sha256=sha(b"stage"), correlation="retry",
                         now_ns=t+1)
            with pytest.raises(JobConflict):
                q.checkpoint(tenant="tenant-A", job_id=item.id, worker="w", fence=claim.fence,
                             stage="loaded", artifact_sha256=sha(b"bad"), correlation="retry", now_ns=t+2)
        item = q.fail(tenant="tenant-A", job_id=item.id, worker="w", fence=claim.fence,
                      correlation="retry", now_ns=t+3)
        assert item.state == ("failed" if attempt == 3 else "queued")
        with pytest.raises(JobConflict):
            q.claim(tenant="tenant-A", job_id=item.id, worker="w", correlation="early",
                    lease_ns=20_000_000, now_ns=t+4)
        t = item.next_attempt_ns
    assert item.attempts == 3


def test_invalid_inputs_and_queue_migration(tmp_path):
    path = tmp_path / "jobs.sqlite"
    q = QueueStore(path)
    with pytest.raises(ValueError):
        q.enqueue(tenant="tenant-A", subject="user", dataset="w03-original-synthetic",
                  idempotency_key="invalid key", payload={}, correlation="x")
    with pytest.raises(ValueError):
        q.enqueue(tenant="tenant-A", subject="user", dataset="w03-original-synthetic",
                  idempotency_key="valid", payload={"too_big": "x"*9000}, correlation="x")
    with sqlite3.connect(path) as db:
        db.execute("UPDATE w04_v2_meta SET v='999' WHERE k='version'")
    with pytest.raises(JobConflict):
        QueueStore(path)

def test_forged_permit_rejected(policy):
    store, _ = policy
    real = permit(store)
    forged = real.model_copy(update={"action": "export_aggregate"})
    with pytest.raises(PolicyError, match="authentication tag"):
        store.validate_permit(forged, now_ns=100_000_000_001)
    other_process = PolicyStore(store.path, permit_key=b"a-different-out-of-band-hmac-secret-key!")
    with pytest.raises(PolicyError, match="authentication tag"):
        other_process.validate_permit(real, now_ns=100_000_000_001)
    with pytest.raises(ValueError):
        PolicyStore(store.path, permit_key=b"weak")