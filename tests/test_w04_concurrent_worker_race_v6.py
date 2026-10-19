"""Race real synthetic worker claims across independent SQLite connections.

This is a single-host threaded coordination test, not multi-host or network
distributed-execution certification. Exactly one W03 trained result may commit.
"""
from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from test_w04_worker_v4_real_w03_integration import KEY, REGISTRY, make_system

from psychneuro.w04.policy_v2 import PolicyStore
from psychneuro.w04.private_worker_v4 import AtomicWorker
from psychneuro.w04.queue_v2 import JobConflict, QueueStore


def test_real_w03_fit_concurrent_independent_workers_single_publication(tmp_path) -> None:
    controller, _, request, db = make_system(tmp_path / "concurrent")
    item = controller.submit(
        tenant="w04-test", subject="fictional-researcher", role="researcher",
        idempotency_key="four-worker-race", request=request,
        correlation="concurrent-submit",
    )
    gate = Barrier(4)

    def attempt(index: int) -> str:
        actor = AtomicWorker(
            database=db,
            policy=PolicyStore(db, permit_key=KEY),
            queue=QueueStore(db),
            registry_path=REGISTRY,
        )
        gate.wait(timeout=15)
        try:
            return actor.run_one(
                tenant="w04-test", job_id=item.id,
                worker=f"worker-{index}", correlation=f"race-{index}",
            ).state
        except JobConflict:
            return "fenced"

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(attempt, range(4)))
    assert results.count("succeeded") == 1
    assert results.count("fenced") == 3
    with sqlite3.connect(db) as con:
        assert con.execute(
            "SELECT COUNT(*) FROM w04_v4_artifacts WHERE id=?", (item.id,),
        ).fetchone()[0] == 1
        assert con.execute(
            "SELECT COUNT(*) FROM w04_v2_audit WHERE id=? AND event='published_v4'",
            (item.id,),
        ).fetchone()[0] == 1
        assert con.execute(
            "SELECT attempts FROM w04_v2_jobs WHERE id=?", (item.id,),
        ).fetchone()[0] == 1
