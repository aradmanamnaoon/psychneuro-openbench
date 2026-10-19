"""Private SQLite backup/restore regressions for a genuine W03 fitted artifact.

These tests exercise SQLite's online backup API and recovery via independently
constructed policy, queue and worker instances. They DO NOT prove host crash
durability, migration rollback, encryption at rest, or production RPO/RTO.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from test_w04_worker_v4_real_w03_integration import KEY, REGISTRY, make_system

from psychneuro.w04.policy_v2 import PolicyStore
from psychneuro.w04.private_worker_v4 import AtomicWorker
from psychneuro.w04.queue_v2 import QueueStore


def _backup(source: Path, target: Path) -> None:
    with sqlite3.connect(source) as origin, sqlite3.connect(target) as destination:
        origin.backup(destination)


def _reopen(database: Path) -> AtomicWorker:
    return AtomicWorker(
        database=database,
        policy=PolicyStore(database, permit_key=KEY),
        queue=QueueStore(database),
        registry_path=REGISTRY,
    )


def test_completed_synthetic_fit_survives_sqlite_online_backup_restore(tmp_path: Path) -> None:
    original, _, request, database = make_system(tmp_path / "original")
    item = original.submit(
        tenant="w04-test", subject="fictional-researcher", role="researcher",
        idempotency_key="backed-up-fit", request=request, correlation="backup-submit",
    )
    result = original.run_one(
        tenant="w04-test", job_id=item.id, worker="backup-worker",
        correlation="backup-run",
    )
    assert result.state == "succeeded"
    before = original.read(
        tenant="w04-test", subject="fictional-researcher", role="researcher",
        job_id=item.id, correlation="backup-before",
    )
    copied = tmp_path / "restored.sqlite"
    _backup(database, copied)
    restored = _reopen(copied)
    after = restored.read(
        tenant="w04-test", subject="fictional-researcher", role="researcher",
        job_id=item.id, correlation="backup-after",
    )
    assert before.model_dump(mode="json") == after.model_dump(mode="json")
    assert restored.queue.get(
        tenant="w04-test", job_id=item.id, subject="fictional-researcher",
    ).state == "succeeded"
    with sqlite3.connect(copied) as con:
        assert con.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert con.execute("SELECT COUNT(*) FROM w04_v4_artifacts").fetchone()[0] == 1
        assert con.execute(
            "SELECT COUNT(*) FROM w04_v2_audit WHERE id=? AND event='published_v4'",
            (item.id,),
        ).fetchone()[0] == 1


def test_restored_artifact_corruption_is_rejected(tmp_path: Path) -> None:
    original, _, request, database = make_system(tmp_path / "tamper")
    item = original.submit(
        tenant="w04-test", subject="fictional-researcher", role="researcher",
        idempotency_key="tamper-after-backup", request=request,
        correlation="tamper-submit",
    )
    assert original.run_one(
        tenant="w04-test", job_id=item.id, worker="tamper-worker",
        correlation="tamper-run",
    ).state == "succeeded"
    copied = tmp_path / "tampered-restored.sqlite"
    _backup(database, copied)
    with sqlite3.connect(copied) as con:
        con.execute("UPDATE w04_v4_artifacts SET payload='{}' WHERE id=?", (item.id,))
    restored = _reopen(copied)
    with pytest.raises((ValueError, KeyError)):
        restored.read(
            tenant="w04-test", subject="fictional-researcher", role="researcher",
            job_id=item.id, correlation="tampered-read",
        )
