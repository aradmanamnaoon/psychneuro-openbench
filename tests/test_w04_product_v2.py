"""Actual registry-backed integration tests. Run on genuine W03 branch, not test stubs."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from psychneuro.w04.api import create_app
from psychneuro.w04.rights import W03_INTERNAL, Principal

A = Principal(subject="alice", tenant="team-a", role="researcher")
B = Principal(subject="bob", tenant="team-b", role="researcher")
V = Principal(subject="view", tenant="team-a", role="viewer")
M = Principal(subject="maint", tenant="team-a", role="maintainer")
TOKENS = {
    "alice-long-test-token-not-for-deployment-00000": A,
    "bob-long-test-token-not-for-deployment-000000": B,
    "viewer-long-test-token-not-for-deploy-00000": V,
    "maint-long-test-token-not-for-deploy-000000": M,
}


def hdr(principal: Principal) -> dict[str, str]:
    token = next(token for token, assigned in TOKENS.items() if assigned == principal)
    return {"X-Internal-Token": token}


def test_real_w03_product_rights_acl_graph_export_and_tamper(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    app = create_app(db_path=tmp_path / "actual.sqlite",
                     registry_path=repo_root / "data" / "registry.json",
                     credentials=TOKENS)
    client = TestClient(app)
    assert client.get("/w04/v2/catalog").status_code == 403
    assert client.get("/w04/v2/rights/preview", headers=hdr(V)).json()["allowed"] is False
    assert client.post("/w04/v2/runs", headers=hdr(V), json={}).status_code == 403
    request = {"generator_seed": 73, "split_seed": 42, "n_participants": 36,
               "trials_per_participant": 12}
    created = client.post("/w04/v2/runs", headers=hdr(A), json=request)
    assert created.status_code == 201, created.text
    run = created.json()
    run_id = run["run_id"]
    repeat = client.post("/w04/v2/runs", headers=hdr(A), json=request)
    assert repeat.status_code == 201 and repeat.json() == run
    assert client.get(f"/w04/v2/runs/{run_id}", headers=hdr(A)).status_code == 200
    assert client.get(f"/w04/v1/benchmarks/{run_id}", headers=hdr(B)).status_code == 403
    for route in [f"/w04/v2/runs/{run_id}",
                  f"/w04/v2/runs/{run_id}/graph",
                  f"/w04/v2/runs/{run_id}/artifact"]:
        assert client.get(route, headers=hdr(B)).status_code == 403
        assert client.get(route, headers=hdr(V)).status_code == 403
    assert client.get("/w04/v2/compare", headers=hdr(B),
                      params={"left": run_id, "right": run_id}).status_code == 403
    comparison = client.get("/w04/v2/compare", headers=hdr(A),
                            params={"left": run_id, "right": run_id})
    assert comparison.status_code == 200
    assert comparison.json()["balanced_accuracy_difference"] == 0.0
    split = client.get(f"/w04/v2/runs/{run_id}/split", headers=hdr(A))
    assert split.status_code == 200 and split.json()["train_groups"] == run["n_train_groups"]
    graph = client.get(f"/w04/v2/runs/{run_id}/graph", headers=hdr(A))
    assert graph.status_code == 200 and graph.json()["verified"] is True
    artifact = client.get(f"/w04/v2/runs/{run_id}/artifact", headers=hdr(A))
    assert artifact.status_code == 200
    receipt = artifact.json()
    assert client.post("/w04/v2/artifacts/verify", headers=hdr(A), json=receipt).status_code == 200
    assert client.post("/w04/v2/artifacts/import", headers=hdr(A), json=receipt).status_code == 403
    assert client.post("/w04/v2/artifacts/import", headers=hdr(M), json=receipt).status_code == 403
    receipt["payload"]["result"]["test_balanced_accuracy"] = 0.99
    assert client.post("/w04/v2/artifacts/verify", headers=hdr(A), json=receipt).status_code == 422
    revoked = create_app(db_path=tmp_path / "revoked.sqlite",
                         registry_path=repo_root / "data" / "registry.json",
                         credentials=TOKENS,
                         rights=W03_INTERNAL.model_copy(update={"revoked": True}))
    assert TestClient(revoked).post("/w04/v2/runs", headers=hdr(A), json=request).status_code == 403
