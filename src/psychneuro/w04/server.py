"""Private demo entrypoint; only run after operator has reviewed the security boundary."""
from __future__ import annotations

import os
from pathlib import Path

from .api import create_app
from .rights import Principal


def app_factory():
    token = os.environ.get("W04_PRIVATE_TOKEN", "")
    # All evaluation is synthetic-only. Token presence is required on every launch.
    if len(token) < 32:
        raise RuntimeError("W04_PRIVATE_TOKEN must be configured out-of-band")
    return create_app(db_path=Path(os.getenv("W04_DB_PATH", "/tmp/w04/private.sqlite")),
                      registry_path=Path(os.getenv("W04_REGISTRY_PATH", "data/registry.json")),
                      credentials={token: Principal(subject="demo-maintainer", role="maintainer")})
