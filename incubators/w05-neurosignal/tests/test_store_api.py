import threading

import pytest
from fastapi.testclient import TestClient

from neurosignal.service import app
from neurosignal.storage import JobStore


def test_persistent_idempotency_and_tenant_boundary(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite")
    first = store.submit("labA", "seed42", {"seed": 42})
    assert first.id == JobStore(tmp_path / "jobs.sqlite").submit("labA", "seed42", {"seed": 42}).id
    with pytest.raises(ValueError, match="collision"):
        store.submit("labA", "seed42", {"seed": 43})
    with pytest.raises(KeyError):
        store.get("labB", first.id)
    assert len(store.history("labA", first.id)) == 1


def test_concurrent_claim_at_most_one(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite")
    job = store.submit("labA", "one")
    revisions, errors = [], []
    def try_claim():
        try:
            revisions.append(store.claim("labA", job.id).revision)
        except ValueError as exc:
            errors.append(str(exc))
    threads = [threading.Thread(target=try_claim) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(revisions) == 1 and len(errors) == 7
    done = store.finish("labA", job.id, revisions[0], {"ok": True})
    assert done.status == "succeeded"
    with pytest.raises(ValueError, match="stale"):
        store.finish("labA", job.id, revisions[0], {"ok": False})


def test_cancel_reconcile_and_fencing(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite")
    job = store.submit("lab", "cancel-job")
    started = store.claim("lab", job.id)
    assert store.cancel("lab", job.id).requested_cancel
    assert store.reconcile("lab", job.id).status == "cancelled"
    with pytest.raises(ValueError):
        store.finish("lab", job.id, started.revision, {"bad": True})
    assert store.cancel("lab", job.id).status == "cancelled"


def test_fail_retry_then_succeed(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite")
    job = store.submit("lab", "retry-job")
    started = store.claim("lab", job.id)
    assert store.finish("lab", job.id, started.revision, None, error="fictional_error").status == "failed"
    assert store.resume("lab", job.id).status == "queued"
    again = store.claim("lab", job.id)
    assert again.attempts == 2
    assert store.finish("lab", job.id, again.revision, {"success": True}).status == "succeeded"


def test_api_auth_idempotency_and_negative(monkeypatch, tmp_path):
    monkeypatch.setenv("NEUROSIGNAL_LOCAL_TOKEN", "a-long-test-token")
    monkeypatch.setenv("NEUROSIGNAL_LOCAL_TENANT", "lab-A")
    monkeypatch.setenv("NEUROSIGNAL_DB_PATH", str(tmp_path / "job.sqlite"))
    client = TestClient(app)
    req = {"seed": 3, "samples": 1024, "chunk_size": 80, "idempotency_key": "test-12345"}
    assert client.post("/v1/demo", json=req).status_code == 401
    headers = {"Authorization": "Bearer a-long-test-token", "X-Tenant": "lab-A"}
    assert client.post("/v1/demo", json=req, headers=headers).json()["synthetic_only"] is True
    first = client.post("/v1/jobs", json=req, headers=headers)
    second = client.post("/v1/jobs", json=req, headers=headers)
    assert first.status_code == 202 and first.json()["id"] == second.json()["id"]
    assert client.get(f"/v1/jobs/{first.json()['id']}", headers={**headers, "X-Tenant": "other"}).status_code == 404
    altered = client.post("/v1/jobs", json={**req, "seed": 4}, headers=headers)
    assert altered.status_code == 409
    assert client.post(f"/v1/jobs/{first.json()['id']}/cancel", headers=headers).json()["status"] == "cancelled"


def test_browser_static_csp_and_keyboard_labels():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert 'for="seed"' in response.text and 'aria-live="polite"' in response.text
    assert client.get("/static/site.js").status_code == 200
    assert client.get("/openapi.json").json()["openapi"].startswith("3.")
