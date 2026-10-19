"""Durable SQLite job coordination with compare-and-set state transitions.

This is a checkpoint protocol, NOT a distributed worker or background queue.
Callers own execution and must cooperate with cancellation at checkpoints.
"""
from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

State = Literal["queued", "running", "cancel_requested", "cancelled", "succeeded", "failed"]


class Job(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    job_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    state: State
    revision: int = Field(ge=0)
    attempts: int = Field(ge=0)
    checkpoint: str | None = Field(default=None, max_length=128)
    actor: str


class RevisionConflict(Exception):
    pass


class JobStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self._connection() as db:
            db.execute("CREATE TABLE IF NOT EXISTS w04_jobs(job_id TEXT PRIMARY KEY, state TEXT NOT NULL, "
                       "revision INTEGER NOT NULL, attempts INTEGER NOT NULL, checkpoint TEXT, actor TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS w04_audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "job_id TEXT NOT NULL, revision INTEGER NOT NULL, actor TEXT NOT NULL, event TEXT NOT NULL, "
                       "at_utc TEXT NOT NULL, correlation TEXT NOT NULL)")

    def _connection(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    def get(self, job_id: str) -> Job | None:
        if len(job_id) != 64 or any(c not in "0123456789abcdef" for c in job_id):
            raise ValueError("invalid job_id")
        with self._connection() as db:
            row = db.execute("SELECT job_id,state,revision,attempts,checkpoint,actor FROM w04_jobs WHERE job_id=?", (job_id,)).fetchone()
        return Job.model_validate(dict(zip(Job.model_fields, row))) if row else None

    def create(self, job_id: str, actor: str, *, correlation: str) -> Job:
        Job(job_id=job_id, state="queued", revision=0, attempts=0, actor=actor)
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO w04_jobs VALUES(?, 'queued', 0, 0, NULL, ?)", (job_id, actor))
            existing = db.execute("SELECT actor FROM w04_jobs WHERE job_id=?", (job_id,)).fetchone()
            if existing is None or existing[0] != actor:
                raise RevisionConflict("job identity belongs to another actor")
            db.execute("INSERT INTO w04_audit(job_id,revision,actor,event,at_utc,correlation) "
                       "SELECT ?,0,?,'created',?,? WHERE changes()=1", (job_id, actor, datetime.now(UTC).isoformat(), correlation))
        result = self.get(job_id)
        assert result is not None
        return result

    def advance(self, job_id: str, *, expected_revision: int, target: State, actor: str,
                correlation: str, checkpoint: str | None = None) -> Job:
        if checkpoint is not None and (len(checkpoint) > 128 or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.:" for c in checkpoint)):
            raise ValueError("unsafe checkpoint identifier")
        transitions: dict[str, set[str]] = {
            "queued": {"running", "cancelled"},
            "running": {"cancel_requested", "succeeded", "failed"},
            "cancel_requested": {"cancelled"},
            "failed": {"queued"},
            "cancelled": {"queued"},
            "succeeded": set(),
        }
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT state,revision,attempts,actor FROM w04_jobs WHERE job_id=?", (job_id,)).fetchone()
            if row is None or row[1] != expected_revision or row[3] != actor:
                raise RevisionConflict("revision or owner mismatch")
            if target not in transitions[row[0]]:
                raise RevisionConflict("invalid job state transition")
            if row[0] == "running" and target == "succeeded" and checkpoint is None:
                raise RevisionConflict("success requires durable checkpoint reference")
            # Failed and cancelled work can be re-queued at same safe checkpoint.
            attempts = row[2] + int(target == "running")
            cursor = db.execute("UPDATE w04_jobs SET state=?, revision=revision+1, attempts=?, "
                                "checkpoint=COALESCE(?,checkpoint) WHERE job_id=? AND revision=?", 
                                (target, attempts, checkpoint, job_id, expected_revision))
            if cursor.rowcount != 1:
                raise RevisionConflict("concurrent modification")
            db.execute("INSERT INTO w04_audit(job_id,revision,actor,event,at_utc,correlation) VALUES(?,?,?,?,?,?)",
                       (job_id, expected_revision + 1, actor, target, datetime.now(UTC).isoformat(), correlation))
        result = self.get(job_id)
        assert result is not None
        return result

    def audit(self, job_id: str, *, limit: int = 100) -> list[dict[str, object]]:
        if not 1 <= limit <= 100:
            raise ValueError("invalid audit limit")
        self.get(job_id)  # input validation
        with self._connection() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT revision,actor,event,at_utc,correlation FROM w04_audit "
                              "WHERE job_id=? ORDER BY seq LIMIT ?", (job_id, limit)).fetchall()
        return [dict(row) for row in rows]
