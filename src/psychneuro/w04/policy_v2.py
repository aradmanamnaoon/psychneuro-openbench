"""Fail-closed, versioned, tenant-isolated P25 policy/authorization ledger.

SQLite protects atomicity, *not* authenticity against a database administrator.
This module never infers consent, licence permission or human data rights.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_IDENTIFIER = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
_DIGEST = re.compile(r"[a-f0-9]{64}\Z")
_ALLOWED = frozenset({"run", "read_aggregate", "export_aggregate"})


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def policy_payload(policy: PolicyRecord) -> dict[str, object]:
    record: dict[str, object] = policy.model_dump(mode="json")
    record["actions"] = sorted(policy.actions)
    return record


class PolicyError(PermissionError):
    """Fail-closed policy refusal; never expose sensitive policy internals to clients."""


class IntegrityError(ValueError):
    """Stored bytes or event sequencing is inconsistent."""


class PolicyRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    version: Literal["p25-policy-2"] = "p25-policy-2"
    tenant: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,80}$")
    dataset: Literal["w03-original-synthetic"] = "w03-original-synthetic"
    origin: Literal["original-synthetic"] = "original-synthetic"
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    purpose: Literal["internal-method-validation"] = "internal-method-validation"
    actions: frozenset[Literal["run", "read_aggregate", "export_aggregate"]]
    # Must be set *server side* after independent human/operator validation.
    attestation_ref: str = Field(pattern=r"^[A-Za-z0-9_.:-]{8,128}$")
    data_license: Literal["unattested-synthetic-internal-only"] = "unattested-synthetic-internal-only"
    consent: Literal["not-applicable"] = "not-applicable"
    ethics: Literal["synthetic-only"] = "synthetic-only"
    export_scope: Literal["aggregate-internal-only"] = "aggregate-internal-only"
    retention_until_ns: int = Field(gt=0)
    revoked: bool = False


class Permit(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    version: Literal["p25-permit-2"] = "p25-permit-2"
    tenant: str
    dataset: str
    subject: str
    purpose: str
    action: str
    policy_revision: int
    policy_sha256: str
    expires_ns: int
    correlation_id: str
    mac_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class PolicyStore:
    """Persistent policy records and ordered event audit.

    Policy installation is an *operator-only* Python interface. Caller must
    independently authenticate the operator and validate attestation_ref.
    """

    def __init__(self, path: Path, *, permit_key: bytes):
        if not isinstance(permit_key, bytes) or len(permit_key) < 32:
            raise ValueError("out-of-band HMAC key of at least 32 bytes required")
        self._permit_key = permit_key
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("CREATE TABLE IF NOT EXISTS p25_v2_meta (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
            ver = db.execute("SELECT v FROM p25_v2_meta WHERE k='version'").fetchone()
            if ver is None:
                db.execute("INSERT INTO p25_v2_meta VALUES ('version', '2')")
            elif ver[0] != "2":
                raise IntegrityError("unsupported database schema version")
            db.execute("CREATE TABLE IF NOT EXISTS p25_v2_policy (tenant TEXT NOT NULL, dataset TEXT NOT NULL, "
                       "revision INTEGER NOT NULL CHECK(revision>0), payload TEXT NOT NULL, sha TEXT NOT NULL, "
                       "PRIMARY KEY(tenant,dataset))")
            db.execute("CREATE TABLE IF NOT EXISTS p25_v2_events (seq INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "parent TEXT NOT NULL, payload TEXT NOT NULL, sha TEXT NOT NULL)")

    def _db(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    @staticmethod
    def _ident(value: str) -> str:
        if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
            raise ValueError("invalid bounded identifier")
        return value

    def _verify_events(self, db: sqlite3.Connection) -> str:
        parent = "0" * 64
        previous = 0
        for seq, upstream, raw, current in db.execute(
            "SELECT seq,parent,payload,sha FROM p25_v2_events ORDER BY seq"
        ):
            if seq != previous + 1 or upstream != parent or len(raw) > 8192:
                raise IntegrityError("policy audit sequence/link corruption")
            try:
                item = json.loads(raw)
            except (ValueError, TypeError) as exc:
                raise IntegrityError("policy audit invalid JSON") from exc
            if canonical(item) != raw or digest({"parent": upstream, "payload": item}) != current:
                raise IntegrityError("policy audit digest corruption")
            parent, previous = current, seq
        return parent

    def _verify_snapshots(self, db: sqlite3.Connection) -> None:
        # Every mutable policy snapshot must be committed in the hash-linked audit.
        latest: dict[tuple[str, str], tuple[int, str]] = {}
        for (raw,) in db.execute("SELECT payload FROM p25_v2_events ORDER BY seq"):
            event = json.loads(raw)
            if event.get("type") in {"install", "revoke"}:
                key = (event["tenant"], event["dataset"])
                latest[key] = (event["revision"], event["policy_sha256"])
        seen = set()
        for tenant, dataset, revision, raw, stored_sha in db.execute(
            "SELECT tenant,dataset,revision,payload,sha FROM p25_v2_policy"
        ):
            self._checked(tenant, dataset, revision, raw, stored_sha)
            key = (tenant, dataset)
            if key not in latest or latest[key] != (revision, stored_sha):
                raise IntegrityError("policy snapshot detached from audit history")
            seen.add(key)
        if seen != set(latest):
            raise IntegrityError("policy snapshot omitted from audit history")

    def verify(self, *, trusted_root: str | None = None) -> tuple[int, str]:
        with self._db() as db:
            root = self._verify_events(db)
            self._verify_snapshots(db)
            count = db.execute("SELECT count(*) FROM p25_v2_events").fetchone()[0]
        if trusted_root is not None and (not _DIGEST.fullmatch(trusted_root) or trusted_root != root):
            raise IntegrityError("audit root differs from independently held anchor")
        return count, root

    @staticmethod
    def _checked(tenant: str, dataset: str, revision: int, raw: str, sha: str) -> PolicyRecord:
        try:
            parsed = PolicyRecord.model_validate_json(raw)
        except ValueError as exc:
            raise IntegrityError("stored policy schema invalid") from exc
        if (parsed.tenant != tenant or parsed.dataset != dataset or revision < 1 or
                canonical(policy_payload(parsed)) != raw or
                digest({"revision": revision, "policy": policy_payload(parsed)}) != sha):
            raise IntegrityError("stored policy corrupted")
        return parsed

    def _event(self, db: sqlite3.Connection, payload: dict[str, object]) -> None:
        if len(canonical(payload)) > 4096:
            raise ValueError("audit payload too large")
        parent = self._verify_events(db)
        db.execute("INSERT INTO p25_v2_events(parent,payload,sha) VALUES (?,?,?)", (
            parent, canonical(payload), digest({"parent": parent, "payload": payload})
        ))

    def install(self, policy: PolicyRecord, *, operator: str, expected_revision: int | None = None) -> int:
        """Operator-controlled transition; once revoked a dataset cannot be regranted."""
        self._ident(operator)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT revision,payload,sha FROM p25_v2_policy WHERE tenant=? AND dataset=?",
                             (policy.tenant, policy.dataset)).fetchone()
            if row is None:
                if expected_revision not in (None, 0):
                    raise PolicyError("revision conflict")
                revision = 1
            else:
                prior = self._checked(policy.tenant, policy.dataset, *row)
                if prior.revoked:
                    raise PolicyError("revocation is terminal for this policy identity")
                if expected_revision != row[0]:
                    raise PolicyError("revision conflict")
                revision = row[0] + 1
            payload = policy_payload(policy)
            db.execute("INSERT INTO p25_v2_policy(tenant,dataset,revision,payload,sha) VALUES(?,?,?,?,?) "
                       "ON CONFLICT(tenant,dataset) DO UPDATE SET revision=excluded.revision, "
                       "payload=excluded.payload,sha=excluded.sha", (policy.tenant, policy.dataset, revision,
                       canonical(payload), digest({"revision": revision, "policy": payload})))
            self._event(db, {"version": "p25-event-2", "type": "install", "tenant": policy.tenant,
                             "dataset": policy.dataset, "revision": revision, "operator": operator,
                             "policy_sha256": digest({"revision": revision, "policy": payload}),
                             "revoked": policy.revoked})
            return revision

    def revoke(self, *, tenant: str, dataset: str, operator: str) -> int:
        self._ident(tenant)
        self._ident(dataset)
        self._ident(operator)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT revision,payload,sha FROM p25_v2_policy WHERE tenant=? AND dataset=?",
                             (tenant, dataset)).fetchone()
            if row is None:
                raise PolicyError("unknown policy")
            old = self._checked(tenant, dataset, *row)
            if old.revoked:
                return int(row[0])
            return_revision = int(row[0]) + 1
            updated = old.model_copy(update={"revoked": True})
            payload = policy_payload(updated)
            db.execute("UPDATE p25_v2_policy SET revision=?,payload=?,sha=? WHERE tenant=? AND dataset=?", (
                return_revision, canonical(payload), digest({"revision": return_revision, "policy": payload}),
                tenant, dataset))
            self._event(db, {"version": "p25-event-2", "type": "revoke", "tenant": tenant,
                             "dataset": dataset, "revision": return_revision, "operator": operator,
                             "policy_sha256": digest({"revision": return_revision, "policy": payload})})
            return return_revision

    def _mac(self, payload: dict[str, object]) -> str:
        return hmac.new(self._permit_key, canonical(payload).encode("utf-8"), hashlib.sha256).hexdigest()

    def authorize(self, *, tenant: str, dataset: str, subject: str, role: str,
                  action: str, purpose: str, correlation_id: str, ttl_ns: int = 60_000_000_000,
                  now_ns: int | None = None) -> Permit:
        for value in (tenant, dataset, subject, correlation_id):
            self._ident(value)
        now = time.time_ns() if now_ns is None else now_ns
        if ttl_ns <= 0 or ttl_ns > 60_000_000_000:
            raise PolicyError("invalid permit lifetime")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            self._verify_events(db)
            self._verify_snapshots(db)
            row = db.execute("SELECT revision,payload,sha FROM p25_v2_policy WHERE tenant=? AND dataset=?",
                             (tenant, dataset)).fetchone()
            # No audit entry on an unknown tenant/dataset: avoid revealing its existence.
            if row is None:
                raise PolicyError("not authorized")
            policy = self._checked(tenant, dataset, *row)
            allowed = (not policy.revoked and role in {"researcher", "maintainer"}
                       and purpose == policy.purpose and action in policy.actions
                       and action in _ALLOWED and policy.retention_until_ns > now
                       and policy.origin == "original-synthetic")
            if action == "read_aggregate" and role == "viewer":
                allowed = (not policy.revoked and purpose == policy.purpose
                           and action in policy.actions and policy.retention_until_ns > now)
            self._event(db, {"version": "p25-event-2", "type": "decision", "tenant": tenant,
                             "dataset": dataset, "revision": row[0], "subject": subject,
                             "action": action[:64], "allowed": allowed, "correlation": correlation_id})
            claim = {"version": "p25-permit-2", "tenant": tenant, "dataset": dataset,
                     "subject": subject, "action": action, "purpose": purpose,
                     "policy_revision": row[0], "policy_sha256": row[2],
                     "expires_ns": min(now + ttl_ns, policy.retention_until_ns),
                     "correlation_id": correlation_id}
            decision_permit = Permit.model_validate({**claim, "mac_sha256": self._mac(claim)}) if allowed else None
        if decision_permit is None:
            raise PolicyError("not authorized")
        return decision_permit

    def validate_permit(self, permit: Permit, *, now_ns: int | None = None) -> None:
        unsigned = permit.model_dump(mode="json", exclude={"mac_sha256"})
        if not hmac.compare_digest(permit.mac_sha256, self._mac(unsigned)):
            raise PolicyError("invalid permit authentication tag")
        now = time.time_ns() if now_ns is None else now_ns
        with self._db() as db:
            self._verify_events(db)
            self._verify_snapshots(db)
            row = db.execute("SELECT revision,payload,sha FROM p25_v2_policy WHERE tenant=? AND dataset=?",
                             (permit.tenant, permit.dataset)).fetchone()
            if row is None:
                raise PolicyError("not authorized")
            policy = self._checked(permit.tenant, permit.dataset, *row)
            if (policy.revoked or permit.policy_revision != row[0] or permit.policy_sha256 != row[2]
                    or permit.expires_ns <= now or permit.expires_ns > policy.retention_until_ns
                    or permit.action not in policy.actions or permit.purpose != policy.purpose):
                raise PolicyError("stale or revoked permit")