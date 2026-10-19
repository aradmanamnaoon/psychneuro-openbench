"""Revocation after genuine W03 model fitting must prevent durable P13 writes."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from psychneuro.w03 import service
from psychneuro.w03.contracts import ExperimentRequest
from psychneuro.w04.durable_bridge import source_sha256
from psychneuro.w04.policy_v2 import PolicyRecord, PolicyStore
from psychneuro.w04.rights import Principal
from psychneuro.w04.strict_facade import create_strict_app


def test_revoke_after_fit_before_commit(monkeypatch, tmp_path: Path) -> None:
    registry = Path(__file__).resolve().parents[1] / "data" / "registry.json"
    db = tmp_path / "private.sqlite"
    token = "test-token-private-only-0000000000000001"
    request = ExperimentRequest(generator_seed=73, split_seed=42)
    policy = PolicyStore(db, permit_key=b"fictional-standalone-test-HMAC-key-000000000000")
    policy.install(
        PolicyRecord(tenant="local", source_sha256=source_sha256(request, registry),
                     actions=frozenset({"run", "read_aggregate", "export_aggregate"}),
                     attestation_ref="verified-fictional-local-input-v1",
                     retention_until_ns=10**20),
        operator="test-operator",
    )
    original = service.nested_grouped_benchmark

    def revoke_after_fit(*args, **kwargs):
        result = original(*args, **kwargs)
        policy.revoke(tenant="local", dataset="w03-original-synthetic",
                      operator="test-operator")
        return result

    monkeypatch.setattr(service, "nested_grouped_benchmark", revoke_after_fit)
    app = create_strict_app(
        db_path=db, registry_path=registry, policy=policy,
        credentials={token: Principal(subject="reviewer", role="researcher")},
    )
    response = TestClient(app).post(
        "/w04/v2/runs", headers={"X-Internal-Token": token},
        json={"generator_seed": 73, "split_seed": 42,
              "n_participants": 36, "trials_per_participant": 12},
    )
    assert response.status_code == 403, response.text
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT count(*) FROM runs").fetchone()[0] == 0
