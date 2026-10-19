"""Private real P25 v2 → fenced queue → real W03 → P13 HTTP negative path."""
from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from psychneuro.w03.contracts import ExperimentRequest
from psychneuro.w04.durable_bridge import source_sha256
from psychneuro.w04.policy_v2 import PolicyRecord, PolicyStore
from psychneuro.w04.private_worker_v4 import AtomicWorker
from psychneuro.w04.queue_v2 import QueueStore
from psychneuro.w04.rights import Principal
from psychneuro.w04.strict_facade import create_strict_app

KEY = b"fictional-worker-route-test-0-not-for-deployment-123456789"
A = "synthetic-private-a-token-00000000000000001"
B = "synthetic-private-b-token-00000000000000002"
V = "synthetic-private-viewer-token-00000000000003"
REQ = {"generator_seed": 73, "split_seed": 42, "n_participants": 36,
       "trials_per_participant": 12}


def setup(tmp_path: Path):
    db = tmp_path / "worker.sqlite"
    source_registry = Path(__file__).resolve().parents[1] / "data" / "registry.json"
    rights = PolicyStore(db, permit_key=KEY)
    sha = source_sha256(ExperimentRequest(**REQ), source_registry)
    for tenant in ("a", "b"):
        rights.install(PolicyRecord(
            tenant=tenant, source_sha256=sha,
            actions=frozenset({"run", "read_aggregate", "export_aggregate"}),
            attestation_ref="internal-fictional-reviewed-by-test",
            retention_until_ns=time.time_ns() + 600_000_000_000,
        ), operator="test-owner")
    client = TestClient(create_strict_app(
        db_path=db, registry_path=source_registry, policy=rights,
        credentials={
            A: Principal(tenant="a", subject="alice", role="researcher"),
            B: Principal(tenant="b", subject="bob", role="researcher"),
            V: Principal(tenant="a", subject="eve", role="viewer"),
        },
    ))
    worker = AtomicWorker(database=db, policy=rights,
                          queue=QueueStore(db), registry_path=source_registry)
    return client, worker, rights


def h(token: str) -> dict[str, str]:
    return {"X-Internal-Token": token}


def test_real_worker_lifecycle_and_denials(tmp_path: Path) -> None:
    client, worker, policy = setup(tmp_path)
    body = {"idempotency_key": "first-idempotency", "experiment": REQ}
    assert client.post("/w04/v3/jobs", json=body).status_code == 403
    assert client.post("/w04/v3/jobs", headers=h(V), json=body).status_code == 403
    resp = client.post("/w04/v3/jobs", headers=h(A), json=body)
    assert resp.status_code == 201, resp.text
    job_id = resp.json()["id"]
    assert resp.json()["state"] == "queued"
    same = client.post("/w04/v3/jobs", headers=h(A), json=body)
    assert same.status_code == 201 and same.json()["id"] == job_id
    assert client.get(f"/w04/v3/jobs/{job_id}", headers=h(B)).status_code == 403
    assert client.get(f"/w04/v3/jobs/{job_id}", headers=h(A)).json()["state"] == "queued"
    assert client.get(f"/w04/v3/jobs/{job_id}/receipt", headers=h(A)).status_code == 403
    assert worker.run_one(tenant="a", job_id=job_id, worker="trusted-cpu",
                          correlation="real-computation").state == "succeeded"
    finished = client.get(f"/w04/v3/jobs/{job_id}", headers=h(A)).json()
    assert finished["state"] == "succeeded"
    receipt = client.get(f"/w04/v3/jobs/{job_id}/receipt", headers=h(A))
    assert receipt.status_code == 200
    assert receipt.json()["record"]["result"]["source_sha256"] == (
        source_sha256(ExperimentRequest(**REQ), worker.registry_path))
    assert client.post(f"/w04/v3/jobs/{job_id}/cancel", headers=h(A)).status_code == 409
    assert client.post("/w04/v3/jobs", headers=h(A),
                       json={**body, "experiment": {**REQ, "generator_seed": 74}}).status_code == 403
    policy.revoke(tenant="a", dataset="w03-original-synthetic", operator="test-owner")
    assert client.get(f"/w04/v3/jobs/{job_id}", headers=h(A)).status_code == 403
    assert client.get(f"/w04/v3/jobs/{job_id}/receipt", headers=h(A)).status_code == 403


def test_cancel_and_fresh_permit_resume(tmp_path: Path) -> None:
    client, worker, _rights = setup(tmp_path)
    resp = client.post("/w04/v3/jobs", headers=h(A),
                       json={"idempotency_key": "cancel-me", "experiment": REQ})
    assert resp.status_code == 201, resp.text
    job_id = resp.json()["id"]
    assert client.post(f"/w04/v3/jobs/{job_id}/cancel", headers=h(B)).status_code == 409
    cancelled = client.post(f"/w04/v3/jobs/{job_id}/cancel", headers=h(A))
    assert cancelled.status_code == 200 and cancelled.json()["state"] == "cancelled"
    resumed = client.post(f"/w04/v3/jobs/{job_id}/resume", headers=h(A))
    assert resumed.status_code == 200 and resumed.json()["state"] == "queued"
    assert worker.run_one(tenant="a", job_id=job_id, worker="trusted-cpu",
                          correlation="resumed-computation").state == "succeeded"
    assert client.post(f"/w04/v3/jobs/{job_id}/resume", headers=h(A)).status_code == 409
