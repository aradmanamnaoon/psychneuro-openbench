"""SQLite fenced, tenant-scoped, restart-safe *coordination*, not a worker process.

The worker must enforce rights before each stage, check cancellation and commit
output idempotently. Model fitting is resumable only at completed stage boundaries.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field

from .policy_v2 import Permit, PolicyStore, canonical, digest

_ID = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
_SHA = re.compile(r"[a-f0-9]{64}\Z")
_STAGES = {"loaded": 1, "split_validated": 2, "fit_completed": 3, "persisted": 4}


class JobConflict(RuntimeError):
    pass


class QueueItem(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    schema_version: Literal["w04-job-2"] = "w04-job-2"
    id: str = Field(pattern=r"^[a-f0-9]{64}$")
    tenant: str
    subject: str
    dataset: str
    state: Literal["queued", "running", "cancel_requested", "cancelled", "succeeded", "failed"]
    revision: int = Field(ge=0)
    fence: int = Field(ge=0)
    attempts: int = Field(ge=0)
    lease_until_ns: int = Field(ge=0)
    next_attempt_ns: int = Field(ge=0)
    checkpoint_stage: str | None
    checkpoint_sha256: str | None
    result_sha256: str | None


class QueueStore:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("CREATE TABLE IF NOT EXISTS w04_v2_meta(k TEXT PRIMARY KEY, v TEXT NOT NULL)")
            version = db.execute("SELECT v FROM w04_v2_meta WHERE k='version'").fetchone()
            if version is None:
                db.execute("INSERT INTO w04_v2_meta VALUES ('version','2')")
            elif version[0] != '2':
                raise JobConflict("unsupported job migration version")
            db.execute("CREATE TABLE IF NOT EXISTS w04_v2_jobs ("
                       "id TEXT PRIMARY KEY,tenant TEXT NOT NULL,subject TEXT NOT NULL,dataset TEXT NOT NULL,"
                       "idem TEXT NOT NULL,payload_sha TEXT NOT NULL,state TEXT NOT NULL,revision INTEGER NOT NULL,"
                       "fence INTEGER NOT NULL,attempts INTEGER NOT NULL,lease_until INTEGER NOT NULL,"
                       "next_attempt INTEGER NOT NULL,checkpoint_stage TEXT,checkpoint_sha TEXT,result_sha TEXT,"
                       "worker TEXT,UNIQUE(tenant,subject,idem))")
            db.execute("CREATE INDEX IF NOT EXISTS w04_v2_due ON w04_v2_jobs(state,next_attempt,lease_until)")
            db.execute("CREATE TABLE IF NOT EXISTS w04_v2_audit (seq INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "id TEXT NOT NULL,tenant TEXT NOT NULL,revision INTEGER NOT NULL,event TEXT NOT NULL,"
                       "actor TEXT NOT NULL,correlation TEXT NOT NULL,at_ns INTEGER NOT NULL)")

    def _db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    @staticmethod
    def _identifier(x: str) -> str:
        if not isinstance(x, str) or not _ID.fullmatch(x):
            raise ValueError("invalid identifier")
        return x

    def _row(self, db: sqlite3.Connection, tenant: str, job_id: str) -> tuple[Any, ...] | None:
        self._identifier(tenant)
        if not _SHA.fullmatch(job_id):
            raise ValueError("invalid job digest")
        return cast(tuple[Any, ...] | None, db.execute("SELECT * FROM w04_v2_jobs WHERE id=? AND tenant=?", (job_id, tenant)).fetchone())

    @staticmethod
    def _item(row: tuple[Any, ...] | None) -> QueueItem:
        if row is None:
            raise JobConflict("job missing after durable transition")
        return QueueItem(id=row[0], tenant=row[1], subject=row[2], dataset=row[3], state=row[6],
                         revision=row[7], fence=row[8], attempts=row[9], lease_until_ns=row[10],
                         next_attempt_ns=row[11], checkpoint_stage=row[12], checkpoint_sha256=row[13],
                         result_sha256=row[14])

    @staticmethod
    def _event(db: sqlite3.Connection, item: QueueItem, actor: str, event: str,
               correlation: str, now: int) -> None:
        db.execute("INSERT INTO w04_v2_audit(id,tenant,revision,event,actor,correlation,at_ns) "
                   "VALUES(?,?,?,?,?,?,?)", (item.id, item.tenant, item.revision, event, actor,
                                             correlation, now))

    def enqueue(self, *, tenant: str, subject: str, dataset: str, idempotency_key: str,
                payload: dict[str, object], correlation: str, now_ns: int | None = None) -> QueueItem:
        for x in (tenant, subject, dataset, idempotency_key, correlation):
            self._identifier(x)
        raw = canonical(payload)
        if len(raw) > 8192:
            raise ValueError("excessive payload")
        identity = digest({"tenant": tenant, "subject": subject, "key": idempotency_key})
        payload_sha = hashlib.sha256(raw.encode()).hexdigest()
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._row(db, tenant, identity)
            if row is not None:
                if row[2] != subject or row[3] != dataset or row[5] != payload_sha:
                    raise JobConflict("idempotency-key reused for different work")
                return self._item(row)
            db.execute("INSERT INTO w04_v2_jobs VALUES(?,?,?,?,?,?,'queued',0,0,0,0,?,NULL,NULL,NULL,NULL)",
                       (identity, tenant, subject, dataset, idempotency_key, payload_sha, now))
            item = self._item(self._row(db, tenant, identity))
            self._event(db, item, subject, "enqueued", correlation, now)
            return item

    def get(self, *, tenant: str, job_id: str, subject: str, maintainer: bool = False) -> QueueItem:
        self._identifier(subject)
        with self._db() as db:
            row = self._row(db, tenant, job_id)
            if row is None or (row[2] != subject and not maintainer):
                raise JobConflict("unknown or unauthorized job")
            return self._item(row)

    def claim(self, *, tenant: str, job_id: str, worker: str, correlation: str,
              lease_ns: int, now_ns: int | None = None, max_attempts: int = 3) -> QueueItem:
        for x in (worker, correlation):
            self._identifier(x)
        if not 1_000_000 <= lease_ns <= 300_000_000_000 or max_attempts not in range(1, 11):
            raise ValueError("invalid lease or retry budget")
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._row(db, tenant, job_id)
            if row is None or row[9] >= max_attempts:
                raise JobConflict("unknown or exhausted job")
            # An expired lease is intentionally eligible for reassignment.
            if not ((row[6] == "queued" and row[11] <= now) or
                    (row[6] == "running" and row[10] <= now)):
                raise JobConflict("not claimable")
            db.execute("UPDATE w04_v2_jobs SET state='running',revision=revision+1,fence=fence+1,"
                       "attempts=attempts+1,lease_until=?,worker=? WHERE id=? AND tenant=?",
                       (now + lease_ns, worker, job_id, tenant))
            item = self._item(self._row(db, tenant, job_id))
            self._event(db, item, worker, "claimed", correlation, now)
            return item

    def heartbeat(self, *, tenant: str, job_id: str, worker: str, fence: int,
                  lease_ns: int, now_ns: int | None = None) -> QueueItem:
        now = time.time_ns() if now_ns is None else now_ns
        if not 1_000_000 <= lease_ns <= 300_000_000_000:
            raise ValueError("invalid lease")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._row(db, tenant, job_id)
            row = self._require_worker(row, worker, fence, now)
            db.execute("UPDATE w04_v2_jobs SET lease_until=?,revision=revision+1 WHERE id=?", (now+lease_ns, job_id))
            return self._item(self._row(db, tenant, job_id))

    @staticmethod
    def _require_worker(row: tuple[Any, ...] | None, worker: str, fence: int, now: int) -> tuple[Any, ...]:
        if row is None or row[6] != "running" or row[8] != fence or row[15] != worker or row[10] <= now:
            raise JobConflict("stale or unauthorized worker lease")
        return row

    def checkpoint(self, *, tenant: str, job_id: str, worker: str, fence: int,
                   stage: str, artifact_sha256: str, correlation: str,
                   now_ns: int | None = None) -> QueueItem:
        if stage not in _STAGES or not _SHA.fullmatch(artifact_sha256):
            raise ValueError("invalid checkpoint boundary/hash")
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._row(db, tenant, job_id)
            row = self._require_worker(row, worker, fence, now)
            if row[12] is not None:
                current = _STAGES[row[12]]
                if _STAGES[stage] < current:
                    raise JobConflict("checkpoint regression")
                if _STAGES[stage] == current and row[13] != artifact_sha256:
                    raise JobConflict("checkpoint overwrite with different bytes")
            db.execute("UPDATE w04_v2_jobs SET checkpoint_stage=?,checkpoint_sha=?,"
                       "revision=revision+1 WHERE id=?", (stage, artifact_sha256, job_id))
            item = self._item(self._row(db, tenant, job_id))
            self._event(db, item, worker, "checkpoint", correlation, now)
            return item

    def complete(self, *, tenant: str, job_id: str, worker: str, fence: int,
                 result_sha256: str, correlation: str, now_ns: int | None = None) -> QueueItem:
        if not _SHA.fullmatch(result_sha256):
            raise ValueError("invalid result hash")
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._row(db, tenant, job_id)
            row = self._require_worker(row, worker, fence, now)
            if row[12] != "persisted" or row[13] != result_sha256:
                raise JobConflict("final durable artifact checkpoint required")
            db.execute("UPDATE w04_v2_jobs SET state='succeeded',result_sha=?,revision=revision+1,"
                       "lease_until=0 WHERE id=?", (result_sha256, job_id))
            item = self._item(self._row(db, tenant, job_id))
            self._event(db, item, worker, "succeeded", correlation, now)
            return item

    def fail(self, *, tenant: str, job_id: str, worker: str, fence: int,
             correlation: str, now_ns: int | None = None, max_attempts: int = 3) -> QueueItem:
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._row(db, tenant, job_id)
            row = self._require_worker(row, worker, fence, now)
            exhausted = row[9] >= max_attempts
            delay = min(2 ** max(row[9] - 1, 0), 64) * 1_000_000_000
            db.execute("UPDATE w04_v2_jobs SET state=?,lease_until=0,revision=revision+1,"
                       "next_attempt=? WHERE id=?", ("failed" if exhausted else "queued", now + delay, job_id))
            item = self._item(self._row(db, tenant, job_id))
            self._event(db, item, worker, "failed" if exhausted else "retry_scheduled", correlation, now)
            return item

    def cancel(self, *, tenant: str, job_id: str, subject: str, correlation: str,
               maintainer: bool = False, now_ns: int | None = None) -> QueueItem:
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._row(db, tenant, job_id)
            if row is None or (row[2] != subject and not maintainer):
                raise JobConflict("unknown or unauthorized job")
            if row[6] in ("succeeded", "failed"):
                raise JobConflict("terminal state")
            if row[6] in ("cancel_requested", "cancelled"):
                return self._item(row)
            state = "cancel_requested" if row[6] == "running" and row[10] > now else "cancelled"
            # Expire worker lease immediately: a stale worker can never commit a result.
            db.execute("UPDATE w04_v2_jobs SET state=?,revision=revision+1,lease_until=0,"
                       "fence=fence+1 WHERE id=?", (state, job_id))
            item = self._item(self._row(db, tenant, job_id))
            self._event(db, item, subject, state, correlation, now)
            return item

    def acknowledge_cancel(self, *, tenant: str, job_id: str, subject: str,
                           correlation: str, now_ns: int | None = None) -> QueueItem:
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = self._row(db, tenant, job_id)
            if row is None or row[2] != subject or row[6] != "cancel_requested":
                raise JobConflict("no pending cancellation")
            db.execute("UPDATE w04_v2_jobs SET state='cancelled',revision=revision+1 WHERE id=?", (job_id,))
            item = self._item(self._row(db, tenant, job_id))
            self._event(db, item, subject, "cancelled", correlation, now)
            return item

    def resume_cancelled(self, *, tenant: str, job_id: str, subject: str,
                         correlation: str, permit: Permit, policy_store: PolicyStore,
                         now_ns: int | None = None) -> QueueItem:
        if policy_store.path.resolve() != self.path.resolve():
            raise JobConflict("cancelled-job resume requires an atomic shared policy database")
        policy_store.validate_permit(permit, now_ns=now_ns)
        if (permit.tenant != tenant or permit.subject != subject or permit.action != "run"):
            raise JobConflict("fresh scoped RUN permit required")
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            policy_store.validate_permit(permit, now_ns=now)
            row = self._row(db, tenant, job_id)
            if row is None or row[2] != subject or row[3] != permit.dataset or row[6] != "cancelled":
                raise JobConflict("invalid resume")
            db.execute("UPDATE w04_v2_jobs SET state='queued',revision=revision+1,"
                       "next_attempt=?,lease_until=0 WHERE id=?", (now, job_id))
            item = self._item(self._row(db, tenant, job_id))
            self._event(db, item, subject, "resumed", correlation, now)
            return item

    def audit(self, *, tenant: str, job_id: str, subject: str,
              maintainer: bool = False) -> list[dict[str, object]]:
        self.get(tenant=tenant, job_id=job_id, subject=subject, maintainer=maintainer)
        with self._db() as db:
            rows = db.execute("SELECT revision,event,actor,correlation,at_ns FROM w04_v2_audit "
                              "WHERE tenant=? AND id=? ORDER BY seq LIMIT 100", (tenant, job_id)).fetchall()
        return [dict(zip(("revision", "event", "actor", "correlation", "at_ns"), row)) for row in rows]