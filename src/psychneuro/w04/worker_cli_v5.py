"""Private operator-only one-shot synthetic job runner; never an HTTP endpoint.

P25 policies must already exist in the *same* database. A key is supplied via
W04_PERMIT_KEY_HEX environment (not argv/URL). Key custody, policy attestation
and account authentication are duties of the operator's secure environment.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import stat
import sys
from pathlib import Path
from typing import Sequence

_ID = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
_KEY_HEX = re.compile(r"[a-fA-F0-9]{64,512}\Z")


def _configuration(args: argparse.Namespace) -> tuple[Path, Path, bytes]:
    for label in (args.tenant, args.worker):
        if _ID.fullmatch(label) is None:
            raise ValueError("invalid bounded tenant/worker identifier")
    if not 1 <= args.limit <= 10:
        raise ValueError("operator job batch must be between 1 and 10")
    db = Path(args.database).expanduser().resolve()
    registry = Path(args.registry).expanduser().resolve()
    if not registry.is_file() or not db.is_file():
        raise ValueError("existing private database and synthetic registry are required")
    if os.name == "posix" and stat.S_IMODE(db.stat().st_mode) & 0o077:
        raise PermissionError("private DB must not be group/other accessible")
    key_hex = os.environ.get("W04_PERMIT_KEY_HEX", "")
    if _KEY_HEX.fullmatch(key_hex) is None or len(key_hex) % 2:
        raise ValueError("missing or invalid operator key environment")
    key = bytes.fromhex(key_hex)
    if len(key) < 32:
        raise ValueError("operator key must contain at least 32 bytes")
    return db, registry, key


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Private one-shot W04 synthetic job worker")
    parser.add_argument("--database", required=True, help="Existing P25/Queue SQLite DB")
    parser.add_argument("--registry", required=True, help="W03 synthetic source registry JSON")
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--worker", default="w04-private-worker")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true", help="Count due jobs, never fit")
    args = parser.parse_args(argv)
    try:
        db, registry, key = _configuration(args)
        # All privileged modules are imported *after* configuration validation.
        from .policy_v2 import PolicyStore
        from .queue_v2 import QueueStore
        from .private_worker_v4 import AtomicWorker

        policy = PolicyStore(db, permit_key=key)
        queue = QueueStore(db)
        worker = AtomicWorker(database=db, policy=policy, queue=queue,
                              registry_path=registry)
        due = worker.due(tenant=args.tenant, limit=args.limit)
        if args.dry_run:
            print(json.dumps({"schema_version": "w04-worker-cli-5", "mode": "dry-run",
                              "due": len(due)}, sort_keys=True))
            return 0
        succeeded = 0
        failures = 0
        for job_id in due:
            try:
                outcome = worker.run_one(tenant=args.tenant, job_id=job_id,
                                         worker=args.worker, correlation="cli-private")
                succeeded += int(outcome.state == "succeeded")
                failures += int(outcome.state != "succeeded")
            except Exception:  # noqa: BLE001 - private operator boundary redacts details
                failures += 1
        print(json.dumps({"schema_version": "w04-worker-cli-5", "mode": "execute",
                          "succeeded": succeeded, "failed": failures}, sort_keys=True))
        return 0 if failures == 0 else 3
    except (ValueError, PermissionError, OSError, sqlite3.Error, RuntimeError):
        print("private W04 worker configuration or permissions denied", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
