"""Strict local-only demo entrypoint; fails closed until a P25 policy is installed."""
from __future__ import annotations
import os
from pathlib import Path
from .policy_v2 import PolicyStore
from .rights import Principal
from .strict_facade import create_strict_app


def app_factory():
    token = os.environ.get("W04_PRIVATE_TOKEN", "")
    policy_key = os.environ.get("W04_P25_PERMIT_KEY", "")
    if min(len(token), len(policy_key)) < 32 or token == policy_key:
        raise RuntimeError("separate 32+ character internal secrets required")
    db = Path(os.getenv("W04_DB_PATH", "/tmp/w04/private.sqlite"))
    return create_strict_app(
        db_path=db,
        registry_path=Path(os.getenv("W04_REGISTRY_PATH", "data/registry.json")),
        credentials={token: Principal(subject="demo-maintainer", role="maintainer")},
        policy=PolicyStore(db, permit_key=policy_key.encode("utf-8")),
    )
