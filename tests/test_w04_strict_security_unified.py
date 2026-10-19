"""Strict W04 private HTTP atomicity, unsigned-import denial, and CSP gates.

Synthetic fixtures only; no network services, keys, clinical or human data.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from psychneuro.w03.contracts import ExperimentRequest
from psychneuro.w04.durable_bridge import source_sha256
from psychneuro.w04.policy_v2 import PolicyRecord, PolicyStore
from psychneuro.w04.rights import Principal
from psychneuro.w04.strict_facade import create_strict_app

KEY = b"non-production-fixture-policy-signing-key-00000000000"
A = "A" * 48
B = "B" * 48
M = "M" * 48
REQ = {"generator_seed": 73, "split_seed": 42, "n_participants": 36,
       "trials_per_participant": 12}


def _app(tmp_path: Path) -> tuple[TestClient, Path]:
    database = tmp_path / "owned.sqlite"
    registry = Path(__file__).resolve().parents[1] / "data" / "registry.json"
    policy = PolicyStore(database, permit_key=KEY)
    source = source_sha256(ExperimentRequest(**REQ), registry)
    for tenant in ("local", "foreign"):
        policy.install(
            PolicyRecord(
                tenant=tenant, source_sha256=source,
                actions=frozenset({"run", "read_aggregate", "export_aggregate"}),
                attestation_ref="fictional-local-source-audit-only",
                retention_until_ns=10**20,
            ),
            operator="test-private-operator",
        )
    app = create_strict_app(
        db_path=database, registry_path=registry,
        credentials={
            A: Principal(tenant="local", subject="alice", role="researcher"),
            B: Principal(tenant="foreign", subject="bob", role="researcher"),
            M: Principal(tenant="local", subject="operator", role="maintainer"),
        }, policy=policy,
    )
    return TestClient(app), database


def test_atomic_run_owner_and_cross_tenant_collision(tmp_path: Path) -> None:
    client, database = _app(tmp_path)
    alice, bob = {"X-Internal-Token": A}, {"X-Internal-Token": B}
    created = client.post("/w04/v2/runs", headers=alice, json=REQ)
    assert created.status_code == 201, created.text
    run_id = created.json()["run_id"]
    assert client.post("/w04/v2/runs", headers=bob, json=REQ).status_code == 403
    assert client.get("/w04/v2/runs/" + run_id, headers=bob).status_code == 403
    assert client.get("/w04/v2/runs/" + run_id, headers=alice).status_code == 200
    with sqlite3.connect(database) as conn:
        assert conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 1
        assert conn.execute(
            "SELECT tenant,owner FROM w04_run_acl WHERE run_id=?", (run_id,)
        ).fetchone() == ("local", "alice")


def test_unsigned_artifact_import_never_claims_owner(tmp_path: Path) -> None:
    client, database = _app(tmp_path)
    headers = {"X-Internal-Token": A}
    created = client.post("/w04/v2/runs", headers=headers, json=REQ)
    assert created.status_code == 201
    run_id = created.json()["run_id"]
    receipt = client.get(
        "/w04/v2/runs/" + run_id + "/artifact", headers=headers
    ).json()
    assert client.post(
        "/w04/v2/artifacts/verify", headers=headers, json=receipt
    ).status_code == 200
    # A valid checksum does not confer signer authority or external rights.
    assert client.post(
        "/w04/v2/artifacts/import", headers=headers, json=receipt
    ).status_code == 403
    # Even a maintainer cannot silently treat a SHA checksum as signer proof.
    assert client.post(
        "/w04/v2/artifacts/import", headers={"X-Internal-Token": M}, json=receipt
    ).status_code == 403
    with sqlite3.connect(database) as conn:
        assert conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 1


def test_strict_csp_same_origin_assets_and_no_token_storage(tmp_path: Path) -> None:
    client, _ = _app(tmp_path)
    page = client.get("/")
    assert page.status_code == 200
    csp = page.headers["content-security-policy"]
    assert "script-src 'self'" in csp
    assert "style-src 'self'" in csp
    assert "unsafe-inline" not in csp
    assert "<script>" not in page.text and "<style>" not in page.text
    assert 'src="/w04/private/app.js"' in page.text
    assert 'href="/w04/private/style.css"' in page.text
    js = client.get("/w04/private/app.js")
    css = client.get("/w04/private/style.css")
    assert js.status_code == 200 and css.status_code == 200
    assert "javascript" in js.headers["content-type"]
    assert "text/css" in css.headers["content-type"]
    assert "job-receipt" in js.text
    assert "focus-visible" in css.text
    assert A not in page.text + js.text + css.text
    assert B not in page.text + js.text + css.text
    assert M not in page.text + js.text + css.text
    assert client.get("/w04/v2/catalog", headers={"X-Internal-Token": A}).json()["datasets"][0]["scope"] == "original-fictional-only"
