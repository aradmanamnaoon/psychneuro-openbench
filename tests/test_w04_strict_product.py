"""Real, synthetic-only strict product acceptance; no mock W03 runner."""
from pathlib import Path

from fastapi.testclient import TestClient

from psychneuro.w03.contracts import ExperimentRequest
from psychneuro.w04.durable_bridge import source_sha256
from psychneuro.w04.policy_v2 import PolicyRecord, PolicyStore
from psychneuro.w04.rights import Principal
from psychneuro.w04.strict_facade import create_strict_app

KEY = b"test-key-for-only-fictional-private-policy-0000000"
TOKEN = "private-test-token-1234567890-1234567890"
REQ = {"generator_seed": 73, "split_seed": 42, "n_participants": 36,
       "trials_per_participant": 12}


def test_real_w03_run_and_p25_revocation(tmp_path: Path) -> None:
    db = tmp_path / "strict.sqlite"
    registry = Path(__file__).resolve().parents[1] / "data" / "registry.json"
    policy = PolicyStore(db, permit_key=KEY)
    source = source_sha256(ExperimentRequest(**REQ), registry)
    policy.install(PolicyRecord(tenant="local", source_sha256=source,
        actions=frozenset({"run","read_aggregate","export_aggregate"}),
        attestation_ref="operator-fictional-source-checked-v1",
        retention_until_ns=10**20), operator="test-operator")
    app = create_strict_app(db_path=db, registry_path=registry,
        credentials={TOKEN: Principal(tenant="local", subject="alice", role="researcher")},
        policy=policy)
    client = TestClient(app)
    h = {"X-Internal-Token": TOKEN}
    response = client.post("/w04/v2/runs", json=REQ)
    assert response.status_code == 403, response.text
    created = client.post("/w04/v2/runs", json=REQ, headers=h)
    assert created.status_code == 201, created.text
    run_id = created.json()["run_id"]
    assert client.get("/w04/v2/runs/"+run_id+"/graph", headers=h).json()["verified"]
    receipt = client.get("/w04/v2/runs/"+run_id+"/artifact", headers=h).json()
    assert client.post("/w04/v2/artifacts/verify", headers=h, json=receipt).status_code == 200
    # An authenticated maintainer must not import an unsigned legacy envelope,
    # even if it passes SHA-based integrity verification.
    maintainer_app = create_strict_app(
        db_path=db, registry_path=registry,
        credentials={TOKEN: Principal(tenant="local", subject="maintainer", role="maintainer")},
        policy=policy,
    )
    maintainer_client = TestClient(maintainer_app)
    import_attempt = maintainer_client.post(
        "/w04/v2/artifacts/import", headers=h, json=receipt,
    )
    assert import_attempt.status_code == 403
    assert import_attempt.json()["detail"]["code"] == "W04_FORBIDDEN"
    receipt["payload"]["result"]["test_balanced_accuracy"] = 0.99
    assert client.post("/w04/v2/artifacts/verify", headers=h, json=receipt).status_code == 422
    assert client.post("/w04/v2/runs", headers=h, json={**REQ, "generator_seed":74}).status_code == 403
    policy.revoke(tenant="local", dataset="w03-original-synthetic", operator="test-operator")
    assert client.get("/w04/v2/runs/"+run_id, headers=h).status_code == 403
