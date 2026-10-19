from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from psychneuro.w03.store import RunStore
from psychneuro.w03.vault import digest, make_chain, portable_chain
from psychneuro.w04.api import create_app
from psychneuro.w04.interop import Envelope, export_record, verify_envelope
from psychneuro.w04.product import TenantRunACL
from psychneuro.w04.rights import W03_INTERNAL, Principal

M = Principal(subject="maintainer", role="maintainer")
V = Principal(subject="viewer", role="viewer")
TOK_M = "maintainer-test-token-do-not-deploy-00000"
TOK_V = "viewer-test-token-do-not-deploy-000000"


def fixture_record() -> dict:
    # Contract fixture only; scores are synthetic *test doubles*, NOT measured benchmarks.
    run_id = sha256(b"fixture-run").hexdigest()
    source = sha256(b"synthetic-fixture").hexdigest()
    split = sha256(b"fictional-participant-groups").hexdigest()
    unsigned = {
        "schema_version": "w03-engine-1", "run_id": run_id, "source_sha256": source,
        "split_sha256": split, "rights": "internal-synthetic-only",
        "n_train_groups": 21, "n_test_groups": 8,
        "outer_balanced_accuracy": .5, "dummy_outer_balanced_accuracy": .5,
        "test_balanced_accuracy": .5, "selected_c": .1,
    }
    chain = make_chain(
        {"source_sha256": source}, {"split_sha256": split},
        {"model_spec_only": True}, {"result_sha256": digest(unsigned)},
    )
    return {"run_id": run_id, "provenance_root": chain[-1].sha256,
            "nodes": portable_chain(chain), "rights": "internal-synthetic-only",
            "result": {**unsigned, "provenance_root": chain[-1].sha256}}


def test_record_export_verified_tamper_denied() -> None:
    record = fixture_record()
    envelope = export_record(record, W03_INTERNAL, M)
    assert verify_envelope(envelope, trusted_root=record["provenance_root"]) == record
    with pytest.raises(ValueError, match="externally trusted root"):
        verify_envelope(envelope, trusted_root=sha256(b"different").hexdigest())
    forged = envelope.model_dump(mode="json")
    forged["payload"]["result"]["test_balanced_accuracy"] = .99
    with pytest.raises(ValueError, match="receipt digest"):
        verify_envelope(Envelope.model_validate(forged))
    with pytest.raises(PermissionError):
        export_record(record, W03_INTERNAL, V)


def test_private_api_auth_integrity_and_job_ownership(tmp_path: Path) -> None:
    db = tmp_path / "runs.sqlite"
    record = fixture_record()
    RunStore(db).put(record)
    app = create_app(db_path=db, registry_path=tmp_path / "registry.json",
                     credentials={TOK_M: M, TOK_V: V})
    api = TestClient(app)
    assert api.get("/w04/v1/rights").status_code == 403
    assert api.get("/w04/v1/rights", headers={"X-Internal-Token": TOK_V}).status_code == 200
    get = api.get(f"/w04/v1/benchmarks/{record['run_id']}", headers={"X-Internal-Token": TOK_V})
    assert get.status_code == 403  # Historical run has no tenant/owner claim.
    TenantRunACL(db).claim(record["run_id"], M)  # Explicit migration-like ownership.
    assert api.get(f"/w04/v1/benchmarks/{record['run_id']}", headers={"X-Internal-Token": TOK_V}).status_code == 403
    claimed = api.get(f"/w04/v1/benchmarks/{record['run_id']}", headers={"X-Internal-Token": TOK_M})
    assert claimed.status_code == 200
    assert claimed.json()["n_train_groups"] == 21
    graph = api.get(f"/w04/v1/provenance/{record['run_id']}", headers={"X-Internal-Token": TOK_M})
    assert [n["kind"] for n in graph.json()["nodes"]] == ["source", "split", "model", "benchmark"]
    export = api.get(f"/w04/v1/provenance/{record['run_id']}/export", headers={"X-Internal-Token": TOK_M})
    assert export.status_code == 200
    verify = api.post("/w04/v1/provenance/verify", json=export.json(), headers={"X-Internal-Token": TOK_V})
    assert verify.status_code == 200
    assert api.post("/w04/v1/provenance/import", json=export.json(), headers={"X-Internal-Token": TOK_V}).status_code == 403
    assert api.post("/w04/v1/provenance/import", json=export.json(), headers={"X-Internal-Token": TOK_M}).status_code == 200
    tampered = export.json()
    tampered["payload"]["nodes"][0]["metadata"]["source_sha256"] = sha256(b"tampered").hexdigest()
    assert api.post("/w04/v1/provenance/verify", json=tampered, headers={"X-Internal-Token": TOK_M}).status_code == 422
    assert api.get("/").status_code == 200
    assert "aria-live" in api.get("/").text

    job_id = sha256(b"job-test").hexdigest()
    assert api.post(f"/w04/v1/jobs/{job_id}", headers={"X-Internal-Token": TOK_V}).status_code == 403
    created = api.post(f"/w04/v1/jobs/{job_id}", headers={"X-Internal-Token": TOK_M})
    assert created.status_code == 200
    assert api.get(f"/w04/v1/jobs/{job_id}/audit", headers={"X-Internal-Token": TOK_M}).status_code == 200
    assert api.post(f"/w04/v1/jobs/{job_id}/transition", headers={"X-Internal-Token": TOK_M},
                    json={"revision": 0, "target": "running"}).status_code == 200
    assert api.post(f"/w04/v1/jobs/{job_id}/transition", headers={"X-Internal-Token": TOK_M},
                    json={"revision": 0, "target": "succeeded"}).status_code == 409
