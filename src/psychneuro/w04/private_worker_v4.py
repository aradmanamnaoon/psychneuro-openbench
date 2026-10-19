"""Private, synthetic-only W03/P13/P25 job processor with atomic publication.

The existing W03 `execute` performs a REAL GroupKFold model fit, but normally
writes directly to RunStore. This adapter replaces *only* its output sink with
an in-memory verification buffer. No W03 aggregate becomes a durable or readable
artifact until P25 and the fenced job state are rechecked within ONE SQLite
BEGIN IMMEDIATE transaction. PolicyStore and QueueStore MUST share that database.

At-least-once delivery, not arbitrary model-fit checkpointing. Crash before the
commit may repeat deterministic training; crash after commit is idempotent and
cannot double-publish. No human data, remote adapters, or public routes.
"""
from __future__ import annotations

from collections.abc import Callable

import hmac
import re
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Protocol, cast

from pydantic import BaseModel, ConfigDict, Field

from .policy_v2 import Permit, PolicyError, PolicyStore, canonical, digest
from .queue_v2 import JobConflict, QueueItem, QueueStore
from .receipt_v3 import P13P25Receipt, issue_receipt, verify_receipt, verify_record

DATASET = "w03-original-synthetic"
PURPOSE = "internal-method-validation"
MAX_REQUEST_BYTES = 8192
MAX_ARTIFACT_BYTES = 250_000
_SHA = re.compile(r"[0-9a-f]{64}\Z")


class Request(BaseModel):
    """Strict versioned transport; nested experiment remains W03's strict v1 model."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    version: str = Field(pattern=r"^w04-worker-request-4$")
    generator_seed: int = Field(ge=0, le=2**64 - 1)
    split_seed: int = Field(ge=0, le=2**64 - 1)
    n_participants: int = Field(ge=24, le=80)
    trials_per_participant: int = Field(ge=8, le=40)
    outer_folds: int = Field(default=3, ge=3, le=3)
    inner_folds: int = Field(default=2, ge=2, le=2)
    predictors: tuple[str, str] = ("difficulty", "stimulus_condition")

    def w03_payload(self) -> dict[str, Any]:
        data = self.model_dump(mode="json")
        if data.pop("version") != "w04-worker-request-4":
            raise ValueError("unsupported worker request version")
        if data["predictors"] != ["difficulty", "stimulus_condition"]:
            raise ValueError("post-response or unapproved predictors")
        return data


class InMemorySink:
    """W03's ``RunStore.put`` interface, without persistence before authorization."""

    def __init__(self) -> None:
        self.record: dict[str, Any] | None = None

    def put(self, record: dict[str, Any]) -> None:
        if self.record is not None:
            raise ValueError("multiple W03 report writes refused")
        verify_record(record)
        self.record = record


class Execution(Protocol):
    def __call__(self, request: Any, registry_path: Path, store: Any) -> Any: ...


def preflight_source(request: Request, registry_path: Path) -> str:
    """Regenerate and validate actual W03 synthetic registry BEFORE fitting.

    The generated records are local, invented data; no external adapter is ever
    enabled by this preflight. W03 still independently validates in `execute`.
    """
    from psychneuro.loaders import load_dataset
    from psychneuro.synthetic import SyntheticConfig

    data = load_dataset(SyntheticConfig(
        seed=request.generator_seed,
        n_participants=request.n_participants,
        trials_per_participant=request.trials_per_participant), registry_path)
    if (data.provenance.license != "not-separately-specified" or
            data.provenance.source_kind != "synthetic"):
        raise PolicyError("only original internal synthetic rights permitted")
    return str(data.schema.source_sha256)


class AtomicWorker:
    """Operator-only Python interface. NEVER publish as an unauthenticated API.

    A protected process supplies the HMAC key and verified P25 attestation. An
    untrusted caller cannot install policies or impersonate service workers.
    """

    def __init__(self, *, database: Path, policy: PolicyStore, queue: QueueStore,
                 registry_path: Path, execute: Execution | None = None,
                 source_preflight: Callable[[Request, Path], str] | None = None) -> None:
        if not (database.resolve() == policy.path.resolve() == queue.path.resolve()):
            raise ValueError("P25 and queue MUST use the same SQLite database for atomicity")
        self.database = database
        self.policy = policy
        self.queue = queue
        self.registry_path = registry_path
        self.source_preflight = source_preflight or preflight_source
        self.execute: Execution
        if execute is None:
            # Import is lazy; the actual W03 runner is used in production.
            from psychneuro.w03.service import execute as w03_execute
            self.execute = cast(Execution, w03_execute)
        else:
            self.execute = execute
        with self._db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("CREATE TABLE IF NOT EXISTS w04_v4_meta(key TEXT PRIMARY KEY, version TEXT NOT NULL)")
            version = conn.execute("SELECT version FROM w04_v4_meta WHERE key='worker'").fetchone()
            if version is None:
                conn.execute("INSERT INTO w04_v4_meta VALUES('worker','4')")
            elif version[0] != "4":
                raise ValueError("unsupported worker database migration")
            conn.execute("CREATE TABLE IF NOT EXISTS w04_v4_requests("
                         "id TEXT PRIMARY KEY, tenant TEXT NOT NULL, subject TEXT NOT NULL,"
                         "payload TEXT NOT NULL, sha TEXT NOT NULL,"
                         "FOREIGN KEY(id) REFERENCES w04_v2_jobs(id))")
            conn.execute("CREATE TABLE IF NOT EXISTS w04_v4_artifacts("
                         "id TEXT PRIMARY KEY, tenant TEXT NOT NULL, subject TEXT NOT NULL,"
                         "payload TEXT NOT NULL, sha TEXT NOT NULL,"
                         "FOREIGN KEY(id) REFERENCES w04_v2_jobs(id))")

    def _db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database, isolation_level=None, timeout=10)
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    def _grant_locked(self, conn: sqlite3.Connection, permit: Permit, *, action: str,
                      now_ns: int, expected_source: str | None = None) -> None:
        # MAC authentication is checked by PolicyStore.validate_permit BEFORE
        # acquiring the transaction; re-read its revision inside this lock.
        if permit.action != action or permit.dataset != DATASET or permit.purpose != PURPOSE:
            raise PolicyError("wrong permit scope")
        self.policy._verify_events(conn)
        row = conn.execute("SELECT revision,payload,sha FROM p25_v2_policy "
                           "WHERE tenant=? AND dataset=?", (permit.tenant, DATASET)).fetchone()
        if row is None:
            raise PolicyError("policy absent")
        policy = self.policy._checked(permit.tenant, DATASET, *row)
        if (policy.revoked or policy.retention_until_ns <= now_ns or
                permit.expires_ns <= now_ns or permit.policy_revision != row[0] or
                not hmac.compare_digest(permit.policy_sha256, row[2]) or
                action not in policy.actions or policy.origin != "original-synthetic"):
            raise PolicyError("stale/revoked/incompatible policy")
        if expected_source is not None and policy.source_sha256 != expected_source:
            raise PolicyError("produced data disagrees with approved source digest")

    def submit(self, *, tenant: str, subject: str, role: str, idempotency_key: str,
               request: Request, correlation: str, now_ns: int | None = None) -> QueueItem:
        """Atomically insert immutable input and a v2 queue item. No orphan jobs."""
        for value in (tenant, subject, idempotency_key, correlation):
            QueueStore._identifier(value)
        payload = request.w03_payload()
        raw = canonical(payload)
        if len(raw.encode()) > MAX_REQUEST_BYTES:
            raise ValueError("request is too large")
        now = time.time_ns() if now_ns is None else now_ns
        permit = self.policy.authorize(tenant=tenant, dataset=DATASET, subject=subject,
                                       role=role, action="run", purpose=PURPOSE,
                                       correlation_id=correlation, now_ns=now)
        self.policy.validate_permit(permit, now_ns=now)
        identity = digest({"tenant": tenant, "subject": subject, "key": idempotency_key})
        request_sha = digest(payload)
        with self._db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            self._grant_locked(conn, permit, action="run", now_ns=now)
            existing = conn.execute("SELECT tenant,subject,dataset,payload_sha FROM w04_v2_jobs "
                                    "WHERE id=?", (identity,)).fetchone()
            if existing is None:
                conn.execute("INSERT INTO w04_v2_jobs VALUES(?,?,?,?,?,?,'queued',0,0,0,0,?,"
                             "NULL,NULL,NULL,NULL)",
                             (identity, tenant, subject, DATASET, idempotency_key, request_sha, now))
                conn.execute("INSERT INTO w04_v4_requests VALUES(?,?,?,?,?)",
                             (identity, tenant, subject, raw, request_sha))
                conn.execute("INSERT INTO w04_v2_audit(id,tenant,revision,event,actor,"
                             "correlation,at_ns) VALUES(?,?,?,?,?,?,?)",
                             (identity, tenant, 0, "enqueued_v4", subject, correlation, now))
            else:
                stored = conn.execute("SELECT payload,sha FROM w04_v4_requests WHERE id=? AND "
                                      "tenant=? AND subject=?", (identity, tenant, subject)).fetchone()
                if (existing != (tenant, subject, DATASET, request_sha) or
                        stored != (raw, request_sha)):
                    raise JobConflict("idempotency key collision or request corruption")
        return self.queue.get(tenant=tenant, job_id=identity, subject=subject)

    def due(self, *, tenant: str, limit: int = 10, now_ns: int | None = None) -> list[str]:
        """Trusted operator-only worker discovery, not a browser listing endpoint."""
        QueueStore._identifier(tenant)
        if not 1 <= limit <= 100:
            raise ValueError("bad batch limit")
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as conn:
            rows = conn.execute("SELECT id FROM w04_v2_jobs WHERE tenant=? AND "
                                "((state='queued' AND next_attempt<=?) OR "
                                "(state='running' AND lease_until<=?)) "
                                "ORDER BY next_attempt,id LIMIT ?", (tenant, now, now, limit)).fetchall()
        return [r[0] for r in rows]

    def _request(self, job: QueueItem) -> Request:
        with self._db() as conn:
            row = conn.execute("SELECT tenant,subject,payload,sha FROM w04_v4_requests "
                               "WHERE id=?", (job.id,)).fetchone()
            queue_row = conn.execute("SELECT payload_sha FROM w04_v2_jobs WHERE id=?", (job.id,)).fetchone()
        if row is None or queue_row is None or row[:2] != (job.tenant, job.subject):
            raise ValueError("request not durably present")
        _, _, raw, sha = row
        if len(raw.encode()) > MAX_REQUEST_BYTES or digest(json.loads(raw)) != sha or sha != queue_row[0]:
            raise ValueError("request checksum corrupted")
        if canonical(json.loads(raw)) != raw:
            raise ValueError("noncanonical request payload")
        obj = Request.model_validate_json(canonical({"version": "w04-worker-request-4", **json.loads(raw)}))
        obj.w03_payload()
        return obj

    def run_one(self, *, tenant: str, job_id: str, worker: str, correlation: str,
                lease_ns: int = 300_000_000_000, now_ns: int | None = None) -> QueueItem:
        """At-most-one successful publication; fit may be recomputed after crash.

        No time mocking is passed to the real W03 runner. now_ns exists only to
        make lease boundaries unit-testable; use real time in production.
        """
        now = time.time_ns() if now_ns is None else now_ns
        current = self.queue.get(tenant=tenant, job_id=job_id, subject=worker, maintainer=True)
        permit = self.policy.authorize(tenant=tenant, dataset=DATASET, subject=current.subject,
                                       role="researcher", action="run", purpose=PURPOSE,
                                       correlation_id=correlation, now_ns=now)
        self.policy.validate_permit(permit, now_ns=now)
        claimed = self.queue.claim(tenant=tenant, job_id=job_id, worker=worker,
                                   correlation=correlation, lease_ns=lease_ns, now_ns=now)
        try:
            req = self._request(claimed)
            # The *real* W03 implementation validates the original synthetic
            # registry and uses GroupKFold/nested-CV; it is not fed metrics.
            source_sha = self.source_preflight(req, self.registry_path)
            if not isinstance(source_sha, str) or not _SHA.fullmatch(source_sha):
                raise ValueError("W03 preflight supplied invalid source hash")
            self.policy.validate_permit(permit, now_ns=(time.time_ns() if now_ns is None else now))
            with self._db() as preflight_db:
                preflight_db.execute("BEGIN IMMEDIATE")
                self._grant_locked(preflight_db, permit, action="run",
                                   expected_source=source_sha,
                                   now_ns=(time.time_ns() if now_ns is None else now))
            from psychneuro.w03.contracts import ExperimentRequest
            experiment = ExperimentRequest.model_validate_json(canonical(req.w03_payload()))
            stage = InMemorySink()
            result = self.execute(experiment, self.registry_path, stage)
            record = stage.record
            if record is None:
                raise ValueError("W03 did not emit a report")
            verify_record(record)
            if record["result"]["source_sha256"] != source_sha:
                raise ValueError("W03 source changed between preflight and fitted report")
            if result.run_id != record["run_id"] or result.source_sha256 != record["result"]["source_sha256"]:
                raise ValueError("W03 return/store identity mismatch")
            # The fitted model is NOT checkpointable in the existing W03 API.
            # Atomic publication is the sole persisted validated stage.
            finish_at = time.time_ns() if now_ns is None else now + 1
            return self._publish(tenant=tenant, claimed=claimed, permit=permit, record=record,
                                 worker=worker, correlation=correlation, now_ns=finish_at)
        except Exception:
            try:
                self.queue.fail(tenant=tenant, job_id=job_id, worker=worker,
                                fence=claimed.fence, correlation=correlation, now_ns=(
                                    time.time_ns() if now_ns is None else now + 1))
            except JobConflict:
                # Cancel/revoke/expired lease wins; cannot restore stale worker.
                pass
            raise

    def _publish(self, *, tenant: str, claimed: QueueItem, permit: Permit,
                 record: dict[str, Any], worker: str, correlation: str, now_ns: int) -> QueueItem:
        verify_record(record)
        if len(canonical(record).encode()) > MAX_ARTIFACT_BYTES:
            raise ValueError("oversize W03 result")
        self.policy.validate_permit(permit, now_ns=now_ns)
        with self._db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            self._grant_locked(conn, permit, action="run", now_ns=now_ns,
                               expected_source=record["result"]["source_sha256"])
            job = conn.execute("SELECT * FROM w04_v2_jobs WHERE id=? AND tenant=?",
                               (claimed.id, tenant)).fetchone()
            if (job is None or job[6] != "running" or job[8] != claimed.fence or
                    job[15] != worker or job[10] <= now_ns or job[2] != permit.subject):
                raise JobConflict("revoked, cancelled, stale or foreign worker cannot publish")
            receipt = issue_receipt(record, tenant=tenant, policy_revision=permit.policy_revision,
                                    policy_sha256=permit.policy_sha256)
            raw = canonical(receipt.model_dump(mode="json"))
            if len(raw.encode()) > MAX_ARTIFACT_BYTES:
                raise ValueError("artifact exceeds cap")
            artifact_hash = digest(receipt.model_dump(mode="json"))
            exists = conn.execute("SELECT tenant,subject,payload,sha FROM w04_v4_artifacts "
                                  "WHERE id=?", (claimed.id,)).fetchone()
            if exists and exists != (tenant, permit.subject, raw, artifact_hash):
                raise JobConflict("job has conflicting immutable artifact")
            if not exists:
                conn.execute("INSERT INTO w04_v4_artifacts VALUES(?,?,?,?,?)",
                             (claimed.id, tenant, permit.subject, raw, artifact_hash))
            conn.execute("UPDATE w04_v2_jobs SET state='succeeded',revision=revision+1,"
                         "checkpoint_stage='persisted',checkpoint_sha=?,result_sha=?,lease_until=0 "
                         "WHERE id=? AND tenant=?", (artifact_hash, artifact_hash, claimed.id, tenant))
            conn.execute("INSERT INTO w04_v2_audit(id,tenant,revision,event,actor,correlation,at_ns) "
                         "VALUES(?,?,?,?,?,?,?)", (claimed.id, tenant, job[7] + 1,
                                                  "published_v4", worker, correlation, now_ns))
        return self.queue.get(tenant=tenant, job_id=claimed.id, subject=permit.subject)

    def read(self, *, tenant: str, subject: str, role: str, job_id: str,
             correlation: str, now_ns: int | None = None) -> P13P25Receipt:
        """Reauthorize after completion; history is not a perpetual access grant."""
        item = self.queue.get(tenant=tenant, subject=subject, job_id=job_id,
                              maintainer=(role == "maintainer"))
        now = time.time_ns() if now_ns is None else now_ns
        permit = self.policy.authorize(tenant=tenant, dataset=DATASET, subject=subject,
                                       role=role, action="read_aggregate", purpose=PURPOSE,
                                       correlation_id=correlation, now_ns=now)
        self.policy.validate_permit(permit, now_ns=now)
        with self._db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            self._grant_locked(conn, permit, action="read_aggregate", now_ns=now)
            row = conn.execute("SELECT tenant,subject,payload,sha FROM w04_v4_artifacts "
                               "WHERE id=? AND tenant=?", (job_id, tenant)).fetchone()
            if row is None or item.state != "succeeded":
                raise JobConflict("no authorized completed artifact")
            if row[1] != subject and role != "maintainer":
                raise PolicyError("artifact belongs to another subject")
            raw = row[2]
            if len(raw.encode()) > MAX_ARTIFACT_BYTES or digest(json.loads(raw)) != row[3]:
                raise ValueError("artifact corrupted")
            if canonical(json.loads(raw)) != raw:
                raise ValueError("noncanonical artifact")
            receipt = P13P25Receipt.model_validate_json(raw)
            if receipt.tenant != tenant or receipt.provenance_root != receipt.record["provenance_root"]:
                raise ValueError("artifact identity corrupt")
            # Any policy update invalidates old receipts: deliberate fail-closed rule.
            verify_receipt(receipt, tenant=tenant, expected_policy_sha256=permit.policy_sha256)
        return receipt
