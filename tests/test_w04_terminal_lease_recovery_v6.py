"""Operator-only terminal-state reconciliation for original synthetic W04 jobs.

These deterministic SQLite tests do not fit models, use live datasets, or
claim physical power-loss recovery or trusted external provenance.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from psychneuro.w04.queue_v2 import JobConflict, QueueStore

START = 1_000_000_000
LEASE = 1_000_000
TENANT = "fictional-a"
SUBJECT = "fictional-worker-owner"


def _enqueue(queue: QueueStore, *, tenant: str = TENANT, key: str = "attempts") -> str:
    item = queue.enqueue(
        tenant=tenant, subject=SUBJECT, dataset="w03-original-synthetic",
        idempotency_key=key, payload={"seed": 73},
        correlation="synthetic-enqueue", now_ns=START,
    )
    return item.id


def test_sigkill_style_expired_final_lease_becomes_terminal_once(tmp_path: Path) -> None:
    queue = QueueStore(tmp_path / "private.sqlite")
    job_id = _enqueue(queue)
    for n in range(3):
        claimed = queue.claim(
            tenant=TENANT, job_id=job_id, worker=f"worker-{n}",
            correlation="synthetic-claim", lease_ns=LEASE,
            now_ns=START + n * 2 * LEASE,
        )
        assert claimed.attempts == n + 1
        assert claimed.state == "running"

    # The third worker has died; a normal due scan cannot claim it again.
    assert queue.reconcile_terminal(
        tenant=TENANT, correlation="operator-pass", now_ns=START + 6 * LEASE,
    ) == 1
    final = queue.get(tenant=TENANT, job_id=job_id, subject=SUBJECT)
    assert final.state == "failed"
    assert final.attempts == 3
    assert final.lease_until_ns == 0
    audit = queue.audit(tenant=TENANT, job_id=job_id, subject=SUBJECT)
    assert [event["event"] for event in audit].count("retry_budget_exhausted") == 1
    assert queue.reconcile_terminal(
        tenant=TENANT, correlation="operator-pass", now_ns=START + 10 * LEASE,
    ) == 0
    with pytest.raises(JobConflict):
        queue.claim(
            tenant=TENANT, job_id=job_id, worker="stale",
            correlation="synthetic-claim", lease_ns=LEASE,
            now_ns=START + 10 * LEASE,
        )


def test_cancel_fence_is_finalized_without_cooperating_worker(tmp_path: Path) -> None:
    queue = QueueStore(tmp_path / "private.sqlite")
    job_id = _enqueue(queue, key="cancel")
    claim = queue.claim(
        tenant=TENANT, job_id=job_id, worker="killed-worker",
        correlation="claim", lease_ns=LEASE, now_ns=START,
    )
    pending = queue.cancel(
        tenant=TENANT, job_id=job_id, subject=SUBJECT,
        correlation="user-cancel", now_ns=START + 1,
    )
    assert pending.state == "cancel_requested"
    assert pending.fence > claim.fence
    assert queue.reconcile_terminal(
        tenant=TENANT, correlation="operator-pass", now_ns=START + 2,
    ) == 1
    final = queue.get(tenant=TENANT, job_id=job_id, subject=SUBJECT)
    assert final.state == "cancelled"
    assert queue.reconcile_terminal(
        tenant=TENANT, correlation="operator-pass", now_ns=START + 3,
    ) == 0
    with pytest.raises(JobConflict):
        queue.heartbeat(
            tenant=TENANT, job_id=job_id, worker="killed-worker",
            fence=claim.fence, lease_ns=LEASE, now_ns=START + 4,
        )


def test_reconciliation_is_tenant_isolated_and_keeps_live_lease(tmp_path: Path) -> None:
    queue = QueueStore(tmp_path / "private.sqlite")
    a = _enqueue(queue, tenant="fictional-a", key="one")
    b = _enqueue(queue, tenant="fictional-b", key="two")
    for tenant, job_id in (("fictional-a", a), ("fictional-b", b)):
        for n in range(3):
            queue.claim(
                tenant=tenant, job_id=job_id, worker=f"worker-{n}",
                correlation="claim", lease_ns=LEASE,
                now_ns=START + n * 2 * LEASE,
            )
    # A remains live at this moment, so neither tenant changes.
    assert queue.reconcile_terminal(
        tenant="fictional-a", correlation="operator-pass",
        now_ns=START + 4 * LEASE + LEASE // 2,
    ) == 0
    # A's expired lease fails, but B remains untouched (even if expired).
    assert queue.reconcile_terminal(
        tenant="fictional-a", correlation="operator-pass",
        now_ns=START + 6 * LEASE,
    ) == 1
    assert queue.get(tenant="fictional-a", job_id=a, subject=SUBJECT).state == "failed"
    assert queue.get(tenant="fictional-b", job_id=b, subject=SUBJECT).state == "running"


def test_maintenance_bounds_validate_before_mutation(tmp_path: Path) -> None:
    queue = QueueStore(tmp_path / "private.sqlite")
    for kwargs in (
        {"tenant": "bad/tenant", "correlation": "audit"},
        {"tenant": TENANT, "correlation": "bad/path"},
        {"tenant": TENANT, "correlation": "audit", "max_attempts": 0},
        {"tenant": TENANT, "correlation": "audit", "limit": 1001},
    ):
        with pytest.raises(ValueError):
            queue.reconcile_terminal(**kwargs)
