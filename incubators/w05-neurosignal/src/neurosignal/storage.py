"""SQLite event-sourced job leases: atomic claim, idempotent submission, fencing, retries."""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from uuid import uuid4

Status = Literal["queued", "running", "succeeded", "failed", "cancelled"]


@dataclass(frozen=True)
class Job:
    id: str
    tenant: str
    status: Status
    revision: int
    attempts: int
    lease_until: float
    result_json: str | None
    error: str | None
    requested_cancel: bool
    request_json: str


class JobStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._initialize()

    def _db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=10000")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS jobs(
                  id TEXT PRIMARY KEY, tenant TEXT NOT NULL, idem TEXT NOT NULL,
                  status TEXT NOT NULL, request_json TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 0,
                  attempts INTEGER NOT NULL DEFAULT 0, max_attempts INTEGER NOT NULL DEFAULT 3,
                  lease_until REAL NOT NULL DEFAULT 0, requested_cancel INTEGER NOT NULL DEFAULT 0,
                  result_json TEXT, error TEXT, created REAL NOT NULL,
                  UNIQUE(tenant, idem));
                CREATE TABLE IF NOT EXISTS events(
                  id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL REFERENCES jobs(id),
                  revision INTEGER NOT NULL, state TEXT NOT NULL, at REAL NOT NULL,
                  UNIQUE(job_id, revision));
            """)

    def submit(self, tenant: str, idem: str, request: dict[str, object] | None = None) -> Job:
        if not tenant or not idem or len(tenant) > 128 or len(idem) > 128:
            raise ValueError("tenant and idempotency key required")
        encoded = json.dumps(request if request is not None else {}, sort_keys=True, allow_nan=False)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            found = db.execute("SELECT id,request_json FROM jobs WHERE tenant=? AND idem=?", (tenant, idem)).fetchone()
            if found and found["request_json"] != encoded:
                raise ValueError("idempotency key collision with changed request")
            if found:
                job_id = found["id"]
            else:
                job_id = uuid4().hex
                db.execute("INSERT INTO jobs(id,tenant,idem,status,request_json,created) VALUES(?,?,?,'queued',?,?)",
                           (job_id, tenant, idem, encoded, time.time()))
                self._event(db, job_id, 0, "queued")
            db.commit()
        return self.get(tenant, job_id)

    @staticmethod
    def _event(db: sqlite3.Connection, id_: str, rev: int, state: str) -> None:
        db.execute("INSERT INTO events(job_id,revision,state,at) VALUES(?,?,?,?)",
                   (id_, rev, state, time.time()))

    def get(self, tenant: str, job_id: str) -> Job:
        with self._db() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=? AND tenant=?", (job_id, tenant)).fetchone()
        if row is None:
            raise KeyError("job not found")
        return Job(id=row["id"], tenant=row["tenant"], status=row["status"],
                   revision=row["revision"], attempts=row["attempts"],
                   lease_until=row["lease_until"], result_json=row["result_json"],
                   error=row["error"], requested_cancel=bool(row["requested_cancel"]),
                   request_json=row["request_json"])

    def claim(self, tenant: str, job_id: str, lease_seconds: int = 60) -> Job:
        if not (1 <= lease_seconds <= 3600):
            raise ValueError("bounded lease required")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE id=? AND tenant=?", (job_id, tenant)).fetchone()
            if row is None:
                raise KeyError("job not found")
            now = time.time()
            if row["requested_cancel"] or row["status"] in {"succeeded", "failed", "cancelled"}:
                raise ValueError("job is terminal or cancelled")
            if row["status"] == "running" and row["lease_until"] > now:
                raise ValueError("active lease")
            if row["attempts"] >= row["max_attempts"]:
                raise ValueError("retry budget exhausted")
            rev = row["revision"] + 1
            db.execute("UPDATE jobs SET status='running',revision=?, attempts=attempts+1, "
                       "lease_until=? WHERE id=?", (rev, now + lease_seconds, job_id))
            self._event(db, job_id, rev, "running")
            db.commit()
        return self.get(tenant, job_id)

    def finish(self, tenant: str, job_id: str, fence: int, result: dict[str, object] | None,
               error: str | None = None) -> Job:
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE id=? AND tenant=?", (job_id, tenant)).fetchone()
            if row is None:
                raise KeyError("job not found")
            if row["status"] != "running" or row["revision"] != fence or row["lease_until"] <= time.time():
                raise ValueError("stale worker fenced out")
            status = "cancelled" if row["requested_cancel"] else ("failed" if error else "succeeded")
            rev = fence + 1
            db.execute("UPDATE jobs SET status=?, revision=?, result_json=?,error=?,lease_until=0 WHERE id=?",
                       (status, rev, json.dumps(result, allow_nan=False) if status == "succeeded" else None,
                        error[:200] if error else None, job_id))
            self._event(db, job_id, rev, status)
            db.commit()
        return self.get(tenant, job_id)

    def cancel(self, tenant: str, job_id: str) -> Job:
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE id=? AND tenant=?", (job_id, tenant)).fetchone()
            if row is None:
                raise KeyError("job not found")
            if row["status"] in {"queued", "running"}:
                state = "cancelled" if row["status"] == "queued" else "running"
                rev = row["revision"] + 1
                db.execute("UPDATE jobs SET requested_cancel=1,status=?,revision=?,lease_until=0 "
                           "WHERE id=?", (state, rev, job_id))
                self._event(db, job_id, rev, "cancel_requested" if state == "running" else "cancelled")
                # Running jobs are fenced; reconcile promotes to cancelled.
            db.commit()
        return self.get(tenant, job_id)

    def reconcile(self, tenant: str, job_id: str) -> Job:
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE id=? AND tenant=?", (job_id, tenant)).fetchone()
            if row is None:
                raise KeyError("job not found")
            if row["status"] == "running" and (
                row["requested_cancel"] or row["lease_until"] <= time.time()
            ):
                status = ("cancelled" if row["requested_cancel"] else
                          "failed" if row["attempts"] >= row["max_attempts"] else "queued")
                rev = row["revision"] + 1
                db.execute("UPDATE jobs SET status=?,revision=?,lease_until=0 WHERE id=?",
                           (status, rev, job_id))
                self._event(db, job_id, rev, status)
            db.commit()
        return self.get(tenant, job_id)

    def resume(self, tenant: str, job_id: str) -> Job:
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE id=? AND tenant=?", (job_id, tenant)).fetchone()
            if row is None:
                raise KeyError("job not found")
            if row["status"] != "failed" or row["attempts"] >= row["max_attempts"]:
                raise ValueError("only retry-budget-eligible failed jobs can resume")
            rev = row["revision"] + 1
            db.execute("UPDATE jobs SET status='queued',revision=?,error=NULL WHERE id=?",
                       (rev, job_id))
            self._event(db, job_id, rev, "queued")
            db.commit()
        return self.get(tenant, job_id)

    def history(self, tenant: str, job_id: str) -> list[dict[str, object]]:
        self.get(tenant, job_id)
        with self._db() as db:
            rows = db.execute("SELECT revision,state,at FROM events WHERE job_id=? ORDER BY id", (job_id,))
            return [dict(r) for r in rows]
