"""Operator-only explicit installation of an INTERNAL fictional-data policy.

No HTTP grant endpoint; no human data or inferred public redistribution rights.
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from psychneuro.w03.contracts import ExperimentRequest

from .durable_bridge import source_sha256
from .policy_v2 import PolicyRecord, PolicyStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Install verified synthetic-only P25 grant")
    parser.add_argument("--attestation-ref", required=True)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--acknowledge-internal-only", action="store_true")
    parser.add_argument("--seed", type=int, default=73)
    parser.add_argument("--participants", type=int, default=36)
    parser.add_argument("--trials", type=int, default=12)
    args = parser.parse_args()
    if not args.acknowledge_internal_only:
        parser.error("operator must explicitly acknowledge internal synthetic-only use")
    key = os.environ.get("W04_P25_PERMIT_KEY", "")
    if len(key) < 32:
        parser.error("W04_P25_PERMIT_KEY must be configured out-of-band")
    req = ExperimentRequest(generator_seed=args.seed,
                            n_participants=args.participants,
                            trials_per_participant=args.trials)
    path = Path(os.getenv("W04_DB_PATH", "/tmp/w04/private.sqlite"))
    registry = Path(os.getenv("W04_REGISTRY_PATH", "data/registry.json"))
    store = PolicyStore(path, permit_key=key.encode("utf-8"))
    policy = PolicyRecord(
        tenant="local", source_sha256=source_sha256(req, registry),
        actions=frozenset({"run", "read_aggregate", "export_aggregate"}),
        attestation_ref=args.attestation_ref,
        retention_until_ns=time.time_ns() + 24 * 60 * 60 * 1_000_000_000,
    )
    store.install(policy, operator=args.operator, expected_revision=0)
    # Do not print secret, receipt or operator PII.
    print("Internal synthetic-only P25 grant installed for local tenant (24 h)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
