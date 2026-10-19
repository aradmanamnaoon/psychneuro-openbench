"""Private SQLite idempotent run store: immutable aggregate reports, not participant data."""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from .vault import canonical, digest, verify_serialized

_RUN_ID = re.compile(r"[a-f0-9]{64}\Z")
_MAX_RECORD_BYTES = 250_000


class ConflictError(ValueError):
    """Same deterministic run identity cannot overwrite different evidence."""


def _check_record(record: dict[str, Any]) -> None:
    if set(record) != {"run_id", "provenance_root", "nodes", "rights", "result"}:
        raise ValueError("unsafe persistent record fields")
    verify_serialized(record.get("nodes"), record.get("provenance_root", ""))
    if record.get("rights") != "internal-synthetic-only":
        raise ValueError("unlicensed or external source")
    result = record.get("result")
    if not isinstance(result, dict):
        raise ValueError("invalid result record")
    if "provenance_root" in result and result["provenance_root"] != record["provenance_root"]:
        raise ValueError("result root inconsistent")
    unsigned = {key: value for key, value in result.items() if key != "provenance_root"}
    benchmark_node = record["nodes"][-1]
    if benchmark_node["metadata"].get("result_sha256") != digest(unsigned):
        raise ValueError("result provenance digest mismatch")


class RunStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, payload BLOB NOT NULL)")

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=5.0)

    def put(self, record: dict[str, Any]) -> None:
        run_id = record.get("run_id")
        if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
            raise ValueError("invalid run ID")
        _check_record(record)
        blob = canonical(record)
        if len(blob) > _MAX_RECORD_BYTES:
            raise ValueError("run record exceeds storage cap")
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO runs (run_id, payload) VALUES (?, ?)", (run_id, blob))
            stored = conn.execute("SELECT payload FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if stored is None or stored[0] != blob:
                raise ConflictError("run ID already exists with different evidence")

    def get(self, run_id: str) -> dict[str, Any] | None:
        if not _RUN_ID.fullmatch(run_id):
            raise ValueError("invalid run ID")
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            return None
        record: dict[str, Any] = json.loads(row[0])
        _check_record(record)
        return record
