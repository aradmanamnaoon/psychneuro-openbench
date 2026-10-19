"""Real W03 synthetic-fit fault injection: no unauthorized partial reports.

These tests execute the real W03 GroupKFold experiment rather than test doubles.
A raised exception immediately AFTER fit simulates a process failure at the
pre-publication boundary; it is not a claim of physical process-kill testing.
"""
from __future__ import annotations

import sqlite3
import time

import pytest
from test_w04_worker_v4_real_w03_integration import make_system

from psychneuro.w03.service import execute as real_w03_execute
from psychneuro.w04.queue_v2 import JobConflict


def _submit(worker, *, key: str):
    return worker.submit(
        tenant="w04-test",
        subject="fictional-researcher",
        role="researcher",
        idempotency_key=key,
        request=worker_request(),
        correlation="recovery-test",
    )


def worker_request():
    from psychneuro.w04.private_worker_v4 import Request

    return Request(
        version="w04-worker-request-4",
        generator_seed=73,
        split_seed=42,
        n_participants=36,
        trials_per_participant=12,
    )


def _artifact_count(db):
    with sqlite3.connect(db) as conn:
        return conn.execute("SELECT count(*) FROM w04_v4_artifacts").fetchone()[0]


def test_real_fit_post_training_exception_does_not_publish_and_retries(tmp_path):
    worker, _, _, db = make_system(tmp_path / "retry")
    item = _submit(worker, key="recover-real-fit")

    calls = []

    def fail_after_real_fit(req, registry, sink):
        result = real_w03_execute(req, registry, sink)
        calls.append(result.run_id)
        if len(calls) == 1:
            raise RuntimeError("test-only crash after real W03 fitting, before publication")
        return result

    worker.execute = fail_after_real_fit
    with pytest.raises(RuntimeError, match="crash after real W03 fitting"):
        worker.run_one(
            tenant="w04-test", job_id=item.id,
            worker="internal-worker", correlation="recovery-first",
        )

    assert calls and _artifact_count(db) == 0
    assert worker.queue.get(
        tenant="w04-test", job_id=item.id,
        subject="fictional-researcher",
    ).state == "queued"

    # The new claim is issued after the bounded queue backoff. We do not
    # reuse the old fenced lease, nor pretend to resume sklearn mid-fit.
    resumed = worker.run_one(
        tenant="w04-test", job_id=item.id,
        worker="internal-worker", correlation="recovery-retry",
        now_ns=time.time_ns() + 3_000_000_000,
    )
    assert resumed.state == "succeeded"
    assert len(calls) == 2
    assert calls[0] == calls[1]
    assert _artifact_count(db) == 1
    receipt = worker.read(
        tenant="w04-test", subject="fictional-researcher", role="researcher",
        job_id=item.id, correlation="recovery-read",
    )
    assert receipt.run_id == calls[0]
    assert receipt.record["result"]["outer_balanced_accuracy"] == 0.5


def test_real_fit_cancellation_before_atomic_commit_denies_stale_worker(tmp_path):
    worker, policy, _, db = make_system(tmp_path / "cancel")
    item = _submit(worker, key="cancel-real-fit")
    calls = []

    def cancel_after_real_fit(req, registry, sink):
        result = real_w03_execute(req, registry, sink)
        calls.append(result.run_id)
        worker.queue.cancel(
            tenant="w04-test", job_id=item.id,
            subject="fictional-researcher", correlation="cancel-after-fit",
        )
        return result

    worker.execute = cancel_after_real_fit
    with pytest.raises(JobConflict, match="cancelled|stale|revoked"):
        worker.run_one(
            tenant="w04-test", job_id=item.id,
            worker="internal-worker", correlation="cancelled-worker",
        )
    assert len(calls) == 1
    assert _artifact_count(db) == 0
    state = worker.queue.get(
        tenant="w04-test", job_id=item.id, subject="fictional-researcher",
    )
    assert state.state == "cancel_requested"

    worker.queue.acknowledge_cancel(
        tenant="w04-test", job_id=item.id,
        subject="fictional-researcher", correlation="ack-cancel",
    )
    permit = policy.authorize(
        tenant="w04-test", dataset="w03-original-synthetic",
        subject="fictional-researcher", role="researcher", action="run",
        purpose="internal-method-validation", correlation_id="fresh-restart",
    )
    worker.queue.resume_cancelled(
        tenant="w04-test", job_id=item.id,
        subject="fictional-researcher", correlation="resume-boundary",
        permit=permit, policy_store=policy,
    )

    worker.execute = real_w03_execute
    finished = worker.run_one(
        tenant="w04-test", job_id=item.id,
        worker="internal-worker", correlation="new-valid-worker",
    )
    assert finished.state == "succeeded"
    assert _artifact_count(db) == 1
    receipt = worker.read(
        tenant="w04-test", subject="fictional-researcher", role="researcher",
        job_id=item.id, correlation="read-after-restart",
    )
    assert receipt.run_id == calls[0]
