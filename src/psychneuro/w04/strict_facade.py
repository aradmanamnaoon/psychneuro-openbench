"""Opt-in private W04 application: authoritative P25-v2 → W03 → P13 path.

This application replaces the older v1 browser routes for the CPU-only local demo.
No production IAM, human datasets, published service, or actual async worker.
"""

import hmac
import json
from pathlib import Path
from typing import Annotated, Any, Literal, NoReturn

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict

from psychneuro.w03.contracts import ExperimentRequest, RunResult
from psychneuro.w03.service import execute
from psychneuro.w03.store import ConflictError, RunStore

from .durable_bridge import DurableRightsBridge
from .interop import Envelope, export_record, verify_envelope
from .policy_v2 import PolicyStore
from .product import ImportResult, OwnerBoundRunStore, RunComparison, SplitSummary, TenantRunACL
from .rights import W03_INTERNAL, Action, Decision, Principal
from .ui import PAGE
from .worker_routes_v5 import install_worker_routes


class Catalog(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["w04-strict-catalog-1"] = "w04-strict-catalog-1"
    datasets: list[dict[str, str]] = [{"id": "w03-original-synthetic", "scope": "original-fictional-only"}]
    limitation: str = "Synthetic-only, one attested fixture per tenant; no human-data claims"


def create_strict_app(*, db_path: Path, registry_path: Path,
                      credentials: dict[str, Principal],
                      policy: PolicyStore) -> FastAPI:
    if not credentials or any(len(k) < 32 for k in credentials):
        raise ValueError("long operator-provisioned internal tokens required")
    store = RunStore(db_path)
    acl = TenantRunACL(db_path)
    gate = DurableRightsBridge(policy, registry_path)
    app = FastAPI(title="W04 restricted P1 P13 P25 review", version="0.4.3",
                  docs_url=None, redoc_url=None, openapi_url="/w04/openapi.json")

    def principal(x_internal_token: str | None = Header(default=None)) -> Principal:
        actor: Principal | None = None
        for token, p in credentials.items():
            if hmac.compare_digest(x_internal_token or "", token):
                actor = p
        if actor is None:
            raise HTTPException(status_code=403, detail="private_access_denied")
        return actor

    def refuse(status: int = 403) -> NoReturn:
        raise HTTPException(status_code=status, detail={
            "schema_version": "w04-error-2", "code": "W04_FORBIDDEN",
            "message": "Private synthetic policy or owner denied"})

    def require(actor: Principal, action: Action) -> None:
        try:
            gate.authorize(actor, action)
        except (PermissionError, ValueError):
            refuse()

    def record(run_id: str, actor: Principal, action: Action) -> dict[str, Any]:
        require(actor, action)
        try:
            acl.check(run_id, actor)
            item = store.get(run_id)
            if item is None:
                refuse(404)
            gate.check_record(actor, action, item)
            return item
        except PermissionError:
            refuse()
        except (ValueError, TypeError):
            refuse(422)

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "private-only", "dataset": "original-synthetic"}

    # Extract immutable first-party browser assets from the original source.
    # The served HTML contains NO inline script/style: a strict CSP is enforceable.
    head, remainder = PAGE.split("<style>", 1)
    style, remainder = remainder.split("</style>", 1)
    body, remainder = remainder.split("<script>", 1)
    script, tail = remainder.split("</script>", 1)
    page = (head + '<link rel="stylesheet" href="/w04/private/style.css">' + body
            + '<script src="/w04/private/app.js" defer></script>' + tail)
    headers = {
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": (
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' blob:; object-src 'none'; "
            "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
        ),
    }

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home() -> Response:
        return HTMLResponse(page, headers=headers)

    @app.get("/w04/private/style.css", include_in_schema=False)
    def stylesheet() -> Response:
        return Response(style, media_type="text/css",
                        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

    @app.get("/w04/private/app.js", include_in_schema=False)
    def browser_script() -> Response:
        return Response(script, media_type="application/javascript",
                        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

    @app.get("/w04/v2/catalog", response_model=Catalog)
    def catalog(actor: Annotated[Principal, Depends(principal)]) -> Catalog:
        require(actor, Action.READ_AGGREGATE)
        return Catalog()

    @app.get("/w04/v2/rights/preview", response_model=Decision)
    def preview(actor: Annotated[Principal, Depends(principal)]) -> Decision:
        try:
            require(actor, Action.RUN)
            allowed = True
        except HTTPException:
            allowed = False
        return Decision(allowed=allowed, reason="allowed" if allowed else "action_not_granted",
                        dataset_id=W03_INTERNAL.dataset_id, action=Action.RUN)

    @app.post("/w04/v2/runs", response_model=RunResult, status_code=201)
    def run(req: ExperimentRequest, actor: Annotated[Principal, Depends(principal)]) -> RunResult:
        try:
            check, locked_check = gate.prepare_atomic_run(actor, req)
            result = execute(
                req, registry_path,
                OwnerBoundRunStore(store, acl, actor, before_commit=locked_check),
                before_persist=check,
            )
            gate.check_result(actor, result)
            return result
        except PermissionError:
            refuse()
        except ConflictError:
            refuse(409)
        except (TypeError, ValueError):
            refuse(422)

    @app.get("/w04/v2/runs/{run_id}", response_model=RunResult)
    def read_run(run_id: str, actor: Annotated[Principal, Depends(principal)]) -> RunResult:
        return RunResult.model_validate(record(run_id, actor, Action.READ_AGGREGATE)["result"])

    @app.get("/w04/v2/runs/{run_id}/split", response_model=SplitSummary)
    def split(run_id: str, actor: Annotated[Principal, Depends(principal)]) -> SplitSummary:
        item = record(run_id, actor, Action.READ_AGGREGATE)
        result = RunResult.model_validate(item["result"])
        metadata = item["nodes"][1]["metadata"]
        if (metadata.get("train_groups") != result.n_train_groups or
            metadata.get("test_groups") != result.n_test_groups):
            refuse(422)
        return SplitSummary(run_id=run_id, train_groups=result.n_train_groups,
                            test_groups=result.n_test_groups, split_sha256=result.split_sha256)

    @app.get("/w04/v2/runs/{run_id}/graph")
    def graph(run_id: str, actor: Annotated[Principal, Depends(principal)]) -> dict[str, object]:
        item = record(run_id, actor, Action.READ_AGGREGATE)
        return {"schema_version": "w04-graph-2", "root": item["provenance_root"],
                "nodes": item["nodes"], "verified": True,
                "warning": "SHA hashes are not independent signatures."}

    @app.get("/w04/v2/runs/{run_id}/artifact")
    def artifact(run_id: str, actor: Annotated[Principal, Depends(principal)]) -> Response:
        item = record(run_id, actor, Action.EXPORT_AGGREGATE)
        envelope = export_record(item, W03_INTERNAL, actor)
        return Response(
            json.dumps(envelope.model_dump(mode="json"), sort_keys=True, allow_nan=False),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="w04-{run_id}.json"',
                     "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

    @app.post("/w04/v2/artifacts/verify", response_model=ImportResult)
    def verify(receipt: Envelope, actor: Annotated[Principal, Depends(principal)]) -> ImportResult:
        try:
            item = verify_envelope(receipt)
            gate.check_record(actor, Action.READ_AGGREGATE, item)
        except PermissionError:
            refuse()
        except (ValueError, TypeError):
            refuse(422)
        return ImportResult(run_id=receipt.run_id, provenance_root=receipt.provenance_root)

    @app.post("/w04/v2/artifacts/import", response_model=ImportResult)
    def import_receipt(
        receipt: Envelope, actor: Annotated[Principal, Depends(principal)],
    ) -> ImportResult:
        # Deliberately unavailable: a matching SHA does not authenticate source,
        # signer, legal rights or the externally retained trusted root.
        # Never claim ownership of an untrusted uploaded aggregate.
        refuse()

    @app.get("/w04/v2/compare", response_model=RunComparison)
    def compare(left: str, right: str,
                actor: Annotated[Principal, Depends(principal)]) -> RunComparison:
        a = RunResult.model_validate(record(left, actor, Action.READ_AGGREGATE)["result"])
        b = RunResult.model_validate(record(right, actor, Action.READ_AGGREGATE)["result"])
        return RunComparison(left=a, right=b,
                             balanced_accuracy_difference=a.outer_balanced_accuracy -
                             b.outer_balanced_accuracy)
    install_worker_routes(app, database=db_path, registry=registry_path,
                          policy=policy, actor=principal)
    return app
