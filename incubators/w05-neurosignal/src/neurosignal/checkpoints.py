"""Transactional, tenant-scoped P26 FIR checkpoints.

Single-node SQLite store. A checkpoint is written atomically with a monotonic
sample boundary; future checkpoints cannot be rolled back by delayed workers.
Not a distributed exactly-once commit of downstream output.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np

from .dsp import CausalFIR


def _encode(state: CausalFIR) -> tuple[str, str]:
    body = json.dumps(state.checkpoint(), sort_keys=True, allow_nan=False,
                      separators=(",", ":"))
    return body, hashlib.sha256(body.encode("utf-8")).hexdigest()


class CheckpointStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS fir_checkpoints (
                tenant TEXT NOT NULL, stream_id TEXT NOT NULL,
                next_sample INTEGER NOT NULL CHECK(next_sample >= 0),
                payload TEXT NOT NULL, sha256 TEXT NOT NULL,
                PRIMARY KEY(tenant, stream_id))""")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path), timeout=10)
        conn.execute("PRAGMA busy_timeout=10000")
        return conn

    @staticmethod
    def _validate_identity(tenant: str, stream_id: str) -> None:
        if not tenant or not stream_id or len(tenant) > 128 or len(stream_id) > 128:
            raise ValueError("invalid tenant or stream identifier")

    def save(self, tenant: str, stream_id: str, state: CausalFIR) -> None:
        self._validate_identity(tenant, stream_id)
        body, digest = _encode(state)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT next_sample, sha256 FROM fir_checkpoints WHERE tenant=? AND stream_id=?",
                (tenant, stream_id)).fetchone()
            if prior:
                if state.next_sample < prior[0]:
                    raise ValueError("stale checkpoint rollback denied")
                if state.next_sample == prior[0]:
                    if digest == prior[1]:
                        return
                    raise ValueError("conflicting checkpoint at same sample")
            db.execute("""INSERT INTO fir_checkpoints
                (tenant,stream_id,next_sample,payload,sha256) VALUES (?,?,?,?,?)
                ON CONFLICT(tenant,stream_id) DO UPDATE SET
                next_sample=excluded.next_sample, payload=excluded.payload,
                sha256=excluded.sha256""",
                (tenant, stream_id, state.next_sample, body, digest))

    def load(self, tenant: str, stream_id: str,
             coefficients: np.ndarray, channels: int) -> CausalFIR:
        self._validate_identity(tenant, stream_id)
        with self._connect() as db:
            row = db.execute(
                "SELECT next_sample,payload,sha256 FROM fir_checkpoints "
                "WHERE tenant=? AND stream_id=?", (tenant, stream_id)).fetchone()
        if row is None:
            raise KeyError("checkpoint not found")
        position, body, digest = row
        if hashlib.sha256(body.encode("utf-8")).hexdigest() != digest:
            raise ValueError("checkpoint integrity failure")
        restored = CausalFIR.restore(json.loads(body))
        if restored.next_sample != position:
            raise ValueError("checkpoint position mismatch")
        expected = np.asarray(coefficients, dtype=np.float64)
        if restored.channels != channels or not np.array_equal(restored.coefficients, expected):
            raise ValueError("checkpoint FIR contract mismatch")
        return restored
