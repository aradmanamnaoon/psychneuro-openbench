"""HTTP admission contract and adversarial authorization. W03 model fit not invoked."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256

from fastapi.testclient import TestClient
from psychneuro.w04.api_hardened import Actor, create_hardened_app
from psychneuro.w04.policy_v2 import PolicyStore, PolicyRecord

K = b"synthetic-only-test-hmac-key-never-use-in-production"
TOK_R = "researcher-synthetic-local-test-token-000001"
TOK_V = "viewer-synthetic-local-test-token-000000001"
TOK_X = "foreign-synthetic-local-test-token-0000001"


def test_versioned_private_auth_permits_and_tenant_boundary(tmp_path: Path) -> None:
    db = tmp_path / "api.sqlite"
    store = PolicyStore(db, permit_key=K)
    store.install(PolicyRecord(tenant="tenant-A", source_sha256=sha256(b"fictional").hexdigest(),
                               actions=frozenset({"run", "read_aggregate"}),
                               attestation_ref="operator-verified-synthetic-registry-v1",
                               retention_until_ns=10**20), operator="maintainer")
    api = TestClient(create_hardened_app(db_path=db, permit_key=K, credentials={
        TOK_R: Actor(tenant="tenant-A", subject="alice", role="researcher"),
        TOK_V: Actor(tenant="tenant-A", subject="bob", role="viewer"),
        TOK_X: Actor(tenant="tenant-B", subject="alice", role="researcher"),
    }))
    headers=lambda token: {"X-Internal-Token": token}
    assert api.get("/w04/v2/rights/check").status_code == 403
    assert api.get("/w04/v2/rights/check", headers=headers(TOK_V)).status_code == 200
    assert api.get("/w04/v2/rights/check", headers=headers(TOK_X)).status_code == 403
    req={"version":"w04-enqueue-2", "dataset":"w03-original-synthetic",
         "purpose":"internal-method-validation", "idempotency_key":"same-seed",
         "experiment":{"generator_seed":73}}
    assert api.post("/w04/v2/jobs", json=req, headers=headers(TOK_V)).status_code == 403
    result=api.post("/w04/v2/jobs", json=req, headers=headers(TOK_R))
    assert result.status_code == 202, result.text
    job=result.json()
    assert api.post("/w04/v2/jobs", json=req, headers=headers(TOK_R)).json()["id"]==job["id"]
    assert api.get("/w04/v2/jobs/"+job["id"], headers=headers(TOK_V)).status_code==404
    assert api.get("/w04/v2/jobs/"+job["id"], headers=headers(TOK_X)).status_code==403
    assert api.get("/w04/v2/jobs/"+job["id"], headers=headers(TOK_R)).status_code==200
    assert api.post("/w04/v2/jobs/"+job["id"]+"/cancel", headers=headers(TOK_R)).json()["state"]=="cancelled"
    assert api.post("/w04/v2/jobs/"+job["id"]+"/resume", headers=headers(TOK_R)).json()["state"]=="queued"
    bad = {**req, "experiment":{"predictors":["correct","stimulus_condition"]}}
    assert api.post("/w04/v2/jobs", json=bad, headers=headers(TOK_R)).status_code == 422
    assert api.post("/w04/v2/jobs", json={**req,"dataset":"human"}, headers=headers(TOK_R)).status_code==422
    assert api.app.openapi_url is None