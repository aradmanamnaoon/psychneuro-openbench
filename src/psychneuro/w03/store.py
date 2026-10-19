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
        raise TypeError("invalid result record")
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
            conn.execute(
                "CREATE TABLE IF NOT EXISTS provenance_index ("
                "run_id TEXT NOT NULL, ordinal INTEGER NOT NULL, "
                "node_sha256 TEXT NOT NULL, kind TEXT NOT NULL, parents_json TEXT NOT NULL, "
                "PRIMARY KEY (run_id, ordinal), "
                "FOREIGN KEY (run_id) REFERENCES runs(run_id))"
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5.0)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def _index_rows(record: dict[str, Any]) -> list[tuple[int, str, str, str]]:
        nodes: list[dict[str, Any]] = record["nodes"]
        return [
            (position, item["sha256"], item["kind"], canonical(item["parents"]).decode("utf-8"))
            for position, item in enumerate(nodes)
        ]

    @classmethod
    def _verify_index(cls, conn: sqlite3.Connection, record: dict[str, Any]) -> None:
        actual = conn.execute(
            "SELECT ordinal, node_sha256, kind, parents_json FROM provenance_index "
            "WHERE run_id=? ORDER BY ordinal", (record["run_id"],)
        ).fetchall()
        if actual != cls._index_rows(record):
            raise ValueError("provenance sidecar integrity mismatch")

    @classmethod
    def put_in_connection(cls, conn: sqlite3.Connection, record: dict[str, Any]) -> None:
        """Write the validated record within a caller-owned SQLite transaction."""
        run_id = record.get("run_id")
        if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
            raise ValueError("invalid run ID")
        _check_record(record)
        blob = canonical(record)
        if len(blob) > _MAX_RECORD_BYTES:
            raise ValueError("run record exceeds storage cap")
        cursor = conn.execute(
            "INSERT OR IGNORE INTO runs (run_id, payload) VALUES (?, ?)", (run_id, blob)
        )
        stored = conn.execute("SELECT payload FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if stored is None or stored[0] != blob:
            raise ConflictError("run ID already exists with different evidence")
        if cursor.rowcount == 1:
            conn.executemany(
                "INSERT INTO provenance_index "
                "(run_id, ordinal, node_sha256, kind, parents_json) "
                "VALUES (?, ?, ?, ?, ?)",
                [(run_id, *row) for row in cls._index_rows(record)],
            )
        cls._verify_index(conn, record)


    def put(self, record: dict[str, Any]) -> None:
        with self._connect() as conn:
            self.put_in_connection(conn, record)

    def get(self, run_id: str) -> dict[str, Any] | None:
        if not _RUN_ID.fullmatch(run_id):
            raise ValueError("invalid run ID")
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if row is None:
                return None
            record: dict[str, Any] = json.loads(row[0])
            _check_record(record)
            self._verify_index(conn, record)
        return record
