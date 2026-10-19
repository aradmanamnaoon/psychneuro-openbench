"""OS-level SIGKILL regression for the private original-synthetic W04 worker.

A child fits the genuine grouped W03 model, signals the parent *after* fitting
and blocks before the SQLite publish transaction. The parent sends SIGKILL,
opens fresh PolicyStore/QueueStore/AtomicWorker instances against the same DB,
and retries. This tests an OS process kill, not machine power loss, backup
recovery, remote storage, or checkpointed mid-fit continuation.
"""
from __future__ import annotations

import os
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest
from test_w04_worker_v4_real_w03_integration import KEY, REGISTRY, make_system

from psychneuro.w04.policy_v2 import PolicyStore
from psychneuro.w04.private_worker_v4 import AtomicWorker
from psychneuro.w04.queue_v2 import QueueStore

# The child intentionally uses a real W03 fit and reports its deterministic ID
# only *after* a successful in-memory run. No W03/P13/P25 result is committed.
_CHILD = r"""
import sys
import time
from pathlib import Path
from psychneuro.w03.service import execute as fit
from psychneuro.w04.policy_v2 import PolicyStore
from psychneuro.w04.private_worker_v4 import AtomicWorker
from psychneuro.w04.queue_v2 import QueueStore

database, registry, job_id, marker, hex_key = sys.argv[1:]
db = Path(database)
def pause_after_fit(request, registry_path, sink):
    result = fit(request, registry_path, sink)
    Path(marker).write_text(result.run_id, encoding="utf-8")
    while True:
        time.sleep(1)

processor = AtomicWorker(
    database=db,
    policy=PolicyStore(db, permit_key=bytes.fromhex(hex_key)),
    queue=QueueStore(db),
    registry_path=Path(registry),
    execute=pause_after_fit,
)
processor.run_one(
    tenant="w04-test", job_id=job_id, worker="sigkill-child",
    correlation="os-kill-after-fit", lease_ns=50_000_000,
)
"""


@pytest.mark.skipif(os.name != "posix" or not hasattr(signal, "SIGKILL"),
                    reason="requires POSIX SIGKILL")
def test_real_fit_sigkill_then_fresh_instance_recomputes_once(tmp_path: Path) -> None:
    original, _, request, database = make_system(tmp_path / "kill")
    item = original.submit(
        tenant="w04-test", subject="fictional-researcher", role="researcher",
        idempotency_key="sigkill-real-fit",
        request=request, correlation="initial-submission",
    )
    marker = tmp_path / "w03-completed-before-sigkill.txt"
    cmd = [sys.executable, "-c", _CHILD, str(database), str(REGISTRY),
           item.id, str(marker), KEY.hex()]
    child = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    run_id = ""
    try:
        deadline = time.monotonic() + 90.0
        while time.monotonic() < deadline:
            if marker.is_file():
                run_id = marker.read_text(encoding="utf-8")
                break
            if child.poll() is not None:
                _, errors = child.communicate(timeout=5)
                pytest.fail(f"child exited before test SIGKILL: {errors[-1500:]}")
            time.sleep(0.05)
        else:
            pytest.fail("real W03 fit did not reach the postfit kill boundary")
    finally:
        if child.poll() is None:
            child.kill()  # real SIGKILL; no cleanup handlers run
        child.wait(timeout=10)

    assert child.returncode == -signal.SIGKILL
    assert run_id
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM w04_v4_artifacts"
        ).fetchone()[0] == 0
    pending = original.queue.get(
        tenant="w04-test", job_id=item.id, subject="fictional-researcher",
    )
    assert pending.state == "running"
    assert pending.attempts == 1

    # Fresh process-local connections and object instances reopen durable
    # state. First lease has expired by now; no in-memory stage is reused.
    recovered = AtomicWorker(
        database=database,
        policy=PolicyStore(database, permit_key=KEY),
        queue=QueueStore(database),
        registry_path=REGISTRY,
    )
    assert item.id in recovered.due(tenant="w04-test")
    finished = recovered.run_one(
        tenant="w04-test", job_id=item.id, worker="fresh-worker",
        correlation="retry-after-os-kill",
    )
    assert finished.state == "succeeded"
    assert finished.attempts == 2
    assert finished.fence == 2

    report = recovered.read(
        tenant="w04-test", subject="fictional-researcher",
        role="researcher", job_id=item.id, correlation="postkill-read",
    )
    assert report.run_id == run_id
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM w04_v4_artifacts"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM w04_v2_audit WHERE id=? AND event='published_v4'",
            (item.id,),
        ).fetchone()[0] == 1
