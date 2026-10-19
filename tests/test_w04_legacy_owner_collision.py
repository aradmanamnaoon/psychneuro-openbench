"""Prevent ambiguous legacy W04 job owners when IDs contain periods.

The fixtures represent fictional internal tenants, not human subject records.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from fastapi.testclient import TestClient

from psychneuro.w04.api import create_app
from psychneuro.w04.rights import Principal


def test_dotted_tenant_and_subject_are_distinct_owners(tmp_path: Path) -> None:
    first = Principal(tenant="a", subject="b.c", role="researcher")
    second = Principal(tenant="a.b", subject="c", role="researcher")
    # Under the former ambiguous tenant + "." + subject encoding both
    # actors became "a.b.c", so the same synthetic job could be hijacked.
    assert first.tenant + "." + first.subject == second.tenant + "." + second.subject
    key_first = "fixture-first-legacy-job-token-0123456789"
    key_second = "fixture-second-legacy-job-token-0123456789"
    client = TestClient(create_app(
        db_path=tmp_path / "test.sqlite",
        registry_path=tmp_path / "unused-registry.json",
        credentials={key_first: first, key_second: second},
    ))
    job_id = sha256(b"fictional-owner-collision").hexdigest()
    route = f"/w04/v1/jobs/{job_id}"
    h_first = {"X-Internal-Token": key_first}
    h_second = {"X-Internal-Token": key_second}
    created = client.post(route, headers=h_first)
    assert created.status_code == 200
    assert created.json()["actor"] == "v2:1:a:b.c"
    assert client.get(route, headers=h_first).status_code == 200
    assert client.get(route, headers=h_second).status_code == 403
    assert client.post(route, headers=h_second).status_code == 409
    assert client.get(route + "/audit", headers=h_second).status_code == 403

    second_id = sha256(b"another-fictional-job").hexdigest()
    response = client.post(f"/w04/v1/jobs/{second_id}", headers=h_second)
    assert response.status_code == 200
    assert response.json()["actor"] == "v2:3:a.b:c"
    assert client.get(f"/w04/v1/jobs/{second_id}", headers=h_first).status_code == 403
