"""W08 P14 content-addressed, schema-versioned synthetic benchmark registry."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path


class EvidenceRegistry:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS evidence (
                digest TEXT PRIMARY KEY, tenant TEXT NOT NULL,
                schema TEXT NOT NULL, payload TEXT NOT NULL)""")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    @staticmethod
    def _canonical(payload: dict[str, object]) -> str:
        if payload.get("schema_version") != "1.0" or payload.get("synthetic_only") is not True:
            raise ValueError("only schema 1.0 synthetic benchmark evidence accepted")
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)

    def register(self, tenant: str, payload: dict[str, object]) -> str:
        if not tenant or len(tenant) > 64:
            raise ValueError("valid tenant required")
        body = self._canonical(payload)
        digest = hashlib.sha256(body.encode()).hexdigest()
        with self._connect() as db:
            prior = db.execute("SELECT tenant,payload FROM evidence WHERE digest=?", (digest,)).fetchone()
            if prior is not None and (prior[0] != tenant or prior[1] != body):
                raise ValueError("evidence hash collision or cross-tenant duplicate")
            db.execute("INSERT OR IGNORE INTO evidence VALUES (?,?,?,?)",
                       (digest, tenant, "1.0", body))
        return digest

    def read(self, tenant: str, digest: str) -> dict[str, object]:
        with self._connect() as db:
            row = db.execute("SELECT payload FROM evidence WHERE tenant=? AND digest=?",
                             (tenant, digest)).fetchone()
        if row is None:
            raise KeyError("no such evidence for tenant")
        return json.loads(row[0])

    def compare(self, tenant: str, before: str, after: str,
                *, metric: str, max_relative_regression: float = 0.05) -> dict[str, object]:
        if not 0 <= max_relative_regression <= 1:
            raise ValueError("regression tolerance must be 0..1")
        a, b = self.read(tenant, before), self.read(tenant, after)
        if a.get("cohort") != b.get("cohort") or a.get("metric_units") != b.get("metric_units"):
            raise ValueError("benchmark cohort or units mismatch")
        x, y = a.get(metric), b.get(metric)
        if isinstance(x, bool) or isinstance(y, bool) or not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise ValueError("metric must be numeric")
        import math
        if not math.isfinite(x) or not math.isfinite(y) or x <= 0:
            raise ValueError("finite positive baseline required")
        delta = (y-x)/x
        return {"baseline_sha256": before, "candidate_sha256": after, "metric": metric,
                "relative_change": delta, "regressed": delta > max_relative_regression,
                "synthetic_only": True}
