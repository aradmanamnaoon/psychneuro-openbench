"""P25 append-only auditable *metadata* ledger for private rights decisions.

Integrity isn't authenticity. This never stores identities/participant consent forms.
A trusted root outside this SQLite database is needed for meaningful tamper evidence.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from psychneuro.w03.vault import canonical, digest


class RightsEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["p25-event-1"] = "p25-event-1"
    event_type: Literal["permission_evaluated", "revoked", "receipt_verified"]
    dataset_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9_.-]+$")
    action: str = Field(max_length=64)
    allowed: bool
    actor_pseudonym: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9_.-]+$")
    correlation_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    at_utc: str


class LedgerStore:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS w04_rights_ledger (seq INTEGER PRIMARY KEY,"
                       " parent_sha TEXT NOT NULL, event_json TEXT NOT NULL, event_sha TEXT NOT NULL)")

    def append(self, *, event_type: Literal["permission_evaluated", "revoked", "receipt_verified"],
               dataset_id: str, action: str, allowed: bool, actor_pseudonym: str,
               correlation_id: str) -> str:
        event = RightsEvent(event_type=event_type, dataset_id=dataset_id, action=action,
                            allowed=allowed, actor_pseudonym=actor_pseudonym,
                            correlation_id=correlation_id,
                            at_utc=datetime.now(UTC).isoformat())
        with sqlite3.connect(self.path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT event_sha FROM w04_rights_ledger ORDER BY seq DESC LIMIT 1").fetchone()
            parent = row[0] if row else "0" * 64
            payload = event.model_dump(mode="json")
            sha = digest({"parent_sha": parent, "event": payload})
            db.execute("INSERT INTO w04_rights_ledger(parent_sha,event_json,event_sha) VALUES(?,?,?)",
                       (parent, canonical(payload).decode("utf-8"), sha))
        return sha

    def verify(self, *, trusted_root: str | None = None) -> tuple[int, str]:
        with sqlite3.connect(self.path) as db:
            records = db.execute("SELECT seq,parent_sha,event_json,event_sha FROM w04_rights_ledger ORDER BY seq").fetchall()
        parent = "0" * 64
        expected_seq = 1
        for seq, node_parent, serialized, sha in records:
            if seq != expected_seq or node_parent != parent:
                raise ValueError("rights ledger order/link integrity failure")
            event = RightsEvent.model_validate(json.loads(serialized))
            normalized = canonical(event.model_dump(mode="json")).decode("utf-8")
            if serialized != normalized or digest({"parent_sha": node_parent, "event": event.model_dump(mode="json")}) != sha:
                raise ValueError("rights ledger tampering detected")
            parent = sha
            expected_seq += 1
        if trusted_root is not None and parent != trusted_root:
            raise ValueError("rights ledger root disagrees with independent anchor")
        return len(records), parent
