"""Read validated P25 grant snapshot without trusting request-owned claims."""
from __future__ import annotations

from psychneuro.w04.policy_v2 import PolicyError, PolicyRecord, PolicyStore


def get_validated_policy(store: PolicyStore, *, tenant: str) -> PolicyRecord:
    store._ident(tenant)
    with store._db() as conn:
        store._verify_events(conn)
        store._verify_snapshots(conn)
        row = conn.execute(
            "SELECT revision,payload,sha FROM p25_v2_policy WHERE tenant=? AND dataset=?",
            (tenant, "w03-original-synthetic"),
        ).fetchone()
        if row is None:
            raise PolicyError("unknown policy")
        return store._checked(tenant, "w03-original-synthetic", *row)
