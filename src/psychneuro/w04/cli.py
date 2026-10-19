"""P25 private rights CLI: explicit input files, no secrets and no network."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from .ledger import LedgerStore
from .rights import Action, DatasetRights, Principal, decide


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="psychneuro-w04", description="Private rights and ledger review")
    subs = parser.add_subparsers(dest="command", required=True)
    review = subs.add_parser("review-rights", help="Evaluate operator-supplied local registry metadata")
    review.add_argument("--rights", required=True, type=Path)
    review.add_argument("--subject", default="reviewer")
    review.add_argument("--role", choices=["viewer", "researcher", "maintainer"], default="viewer")
    review.add_argument("--action", choices=[a.value for a in Action], required=True)
    review.add_argument("--as-of", help="UTC evaluation date YYYY-MM-DD; defaults to current date")
    review.add_argument("--ledger", type=Path, help="Append metadata decision to local SQLite audit ledger")
    verify = subs.add_parser("verify-ledger", help="Verify ledger digest linkage")
    verify.add_argument("--ledger", type=Path, required=True)
    verify.add_argument("--trusted-root", help="Trusted independently retained root SHA-256")
    args = parser.parse_args(argv)
    try:
        if args.command == "review-rights":
            raw = args.rights.read_bytes()
            if len(raw) > 64_000:
                raise ValueError("rights registry file exceeds limit")
            rights = DatasetRights.model_validate_json(raw)
            principal = Principal(subject=args.subject, role=args.role)
            action = Action(args.action)
            at = date.fromisoformat(args.as_of) if args.as_of else None
            outcome = decide(rights, principal, action, today=at)
            if args.ledger is not None:
                LedgerStore(args.ledger).append(event_type="permission_evaluated", dataset_id=rights.dataset_id,
                    action=action.value, allowed=outcome.allowed, actor_pseudonym=principal.subject,
                    correlation_id="cli-manual")
            print(outcome.model_dump_json())
            return 0 if outcome.allowed else 3
        count, root = LedgerStore(args.ledger).verify(trusted_root=args.trusted_root)
        print(json.dumps({"records": count, "integrity_root": root, "trust": "hash-only"}))
        return 0
    except (OSError, ValueError, ValidationError, json.JSONDecodeError) as exc:
        # Do not echo source payload contents, absolute filesystem paths or personal data.
        print(f"w04 error: {type(exc).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
