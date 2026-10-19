from __future__ import annotations

import pytest

from psychneuro.w04.server import app_factory


def test_server_refuses_missing_token(monkeypatch):
    monkeypatch.delenv("W04_PRIVATE_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="W04_PRIVATE_TOKEN"):
        app_factory()
