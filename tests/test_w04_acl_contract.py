"""W04 fail-closed SQLite ownership and static API/accessibility contract sentinels.

These are not a substitute for real keyboard/axe/screen-reader or browser E2E.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path

from psychneuro.w04.api import create_app
from psychneuro.w04.product import TenantRunACL
from psychneuro.w04.rights import Principal
from psychneuro.w04.ui import PAGE

A = Principal(subject="alice", tenant="team-a", role="researcher")
B = Principal(subject="bob", tenant="team-b", role="researcher")
MA = Principal(subject="manager", tenant="team-a", role="maintainer")
MB = Principal(subject="manager", tenant="team-b", role="maintainer")


def test_atomic_ownership_claim_race(tmp_path: Path) -> None:
    store = TenantRunACL(tmp_path / "tenant_acl.sqlite")
    run_id = sha256(b"fictional-synthetic-run").hexdigest()

    def attempt(actor: Principal) -> bool:
        try:
            store.claim(run_id, actor)
            return True
        except PermissionError:
            return False

    principals = [A, B] * 10
    with ThreadPoolExecutor(max_workers=8) as executor:
        winners = list(executor.map(attempt, principals))
    # Only one identity can win; repeated same-owner requests remain idempotent.
    assert sum(winners) in (10,)
    winner = A if winners[0] else B
    store.claim(run_id, winner)
    store.check(run_id, winner)
    if winner == A:
        store.check(run_id, MA)
        for outsider in (B, MB):
            try:
                store.check(run_id, outsider)
            except PermissionError:
                pass
            else:
                raise AssertionError("cross-tenant read was allowed")
    else:
        store.check(run_id, MB)
        for outsider in (A, MA):
            try:
                store.check(run_id, outsider)
            except PermissionError:
                pass
            else:
                raise AssertionError("cross-tenant read was allowed")


def test_openapi_declared_and_static_accessibility_contract(tmp_path: Path) -> None:
    token = "unit-test-secret-token-never-deploy-1234567890"
    api = create_app(
        db_path=tmp_path / "openapi.sqlite",
        registry_path=tmp_path / "not-executed-registry.json",
        credentials={token: MA},
    )
    schema = api.openapi()
    assert schema["info"]["version"] == "0.4.2"
    for route in ("/w04/v2/catalog", "/w04/v2/runs",
                  "/w04/v2/runs/{run_id}/graph",
                  "/w04/v2/runs/{run_id}/artifact",
                  "/w04/v2/artifacts/verify", "/w04/v2/compare"):
        assert route in schema["paths"]
    assert 'aria-live' in PAGE
    assert ':focus-visible' in PAGE
    assert 'prefers-reduced-motion' in PAGE
    assert 'textContent' in PAGE
    assert 'innerHTML' not in PAGE
