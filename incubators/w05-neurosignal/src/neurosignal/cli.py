"""No-network CLI; all experimental outputs are explicitly synthetic."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .integration import run_synthetic
from .storage import JobStore


def main() -> None:
    parser = argparse.ArgumentParser(prog="neurosignal")
    sub = parser.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo", help="P2/P14/P26 synthetic, deterministic integration")
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--samples", type=int, default=4096)
    demo.add_argument("--chunk-size", type=int, default=333)
    validation = sub.add_parser("validate", help="W08 independent synthetic numerical oracle")
    validation.add_argument("--seed", type=int, default=42)
    validation.add_argument("--samples", type=int, default=4096)
    validation.add_argument("--chunk-size", type=int, default=127)
    worker = sub.add_parser("worker", help="Single local job execution; never open to public")
    worker.add_argument("--db", type=Path, required=True)
    worker.add_argument("--tenant", required=True)
    worker.add_argument("--job", required=True)
    args = parser.parse_args()
    if args.cmd == "demo":
        print(json.dumps(run_synthetic(args.seed, args.samples, args.chunk_size), indent=2))
    elif args.cmd == "validate":
        from .validation_w08 import validate_synthetic

        result = validate_synthetic(seed=args.seed, samples=args.samples,
                                    chunk_size=args.chunk_size)
        print(result.json())
        if not result.accepted:
            raise SystemExit(1)
    else:
        store = JobStore(args.db)
        claimed = store.claim(args.tenant, args.job)
        try:
            params = json.loads(claimed.request_json)
            result = run_synthetic(**params)
        except Exception as exc:
            store.finish(args.tenant, args.job, claimed.revision, None, error=str(exc))
            raise
        else:
            job = store.finish(args.tenant, args.job, claimed.revision, result)
            print(json.dumps({"id": job.id, "status": job.status}))


if __name__ == "__main__":
    main()
