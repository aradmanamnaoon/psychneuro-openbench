"""Internal-only W04 FastAPI adapter for existing W03 runner and immutable ledger.

Authentication secrets supplied by operator and mapped server-side to roles.
No browser cookies, permissive CORS, public deployment, or dataset upload.
"""
from __future__ import annotations

import hmac
from pathlib import Path
import secrets
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

from psychneuro.w03.contracts import ExperimentRequest, RunResult
from psychneuro.w03.service import execute
from psychneuro.w03.store import ConflictError, RunStore
from .interop import Envelope, export_record, verify_envelope
from .jobs import Job, JobStore, RevisionConflict, State
from .ledger import LedgerStore
from .rights import Action, DatasetRights, Decision, Principal, W03_INTERNAL, decide
from .ui import PAGE


class JobTransition(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    revision: int = Field(ge=0)
    target: State
    checkpoint: str | None = Field(default=None, max_length=128)


class VerifiedReceipt(BaseModel):
    schema_version: Literal["w04-verify-1"] = "w04-verify-1"
    verified: Literal[True] = True
    run_id: str
    provenance_root: str
    warning: Literal["hash integrity is not an independent signature"] = "hash integrity is not an independent signature"


def create_app(*, db_path: Path, registry_path: Path,
               credentials: dict[str, Principal], rights: DatasetRights = W03_INTERNAL) -> FastAPI:
    if not credentials or any(len(k) < 32 for k in credentials):
        raise ValueError("explicit high-entropy internal tokens required")
    if len(credentials) != len(set(credentials)):
        raise ValueError("duplicate token")
    runs = RunStore(db_path)
    jobs = JobStore(db_path)
    policy_audit = LedgerStore(db_path)
    app = FastAPI(title="W04 private benchmark + provenance + rights", version="0.4.0",
                  docs_url=None, redoc_url=None)

    def actor(x_internal_token: str | None = Header(default=None)) -> Principal:
        # no caller-supplied role header; all roles are server-side secrets mapping
        selected: Principal | None = None
        for token, principal in credentials.items():
            if hmac.compare_digest(token, x_internal_token or ""):
                selected = principal
        if selected is None:
            raise HTTPException(status_code=403, detail="forbidden")
        return selected

    def permit(principal: Principal, action: Action) -> Decision:
        result = decide(rights, principal, action)
        # Audit both approvals and denials before performing protected operations.
        # Audit failure aborts the request (fail closed). Only scoped metadata is saved.
        policy_audit.append(event_type="permission_evaluated", dataset_id=rights.dataset_id,
                            action=action.value, allowed=result.allowed,
                            actor_pseudonym=principal.subject,
                            correlation_id=secrets.token_hex(16))
        if not result.allowed:
            raise HTTPException(status_code=403, detail=f"policy_denied:{result.reason}")
        return result

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "private-only", "scope": "synthetic"}

    @app.get("/", include_in_schema=False)
    def home() -> Response:
        # No sensitive data embedded in client HTML, page requires user-entered token.
        return Response(PAGE, media_type="text/html", headers={"Cache-Control": "no-store", "Content-Security-Policy": "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"})

    @app.get("/w04/v1/rights", response_model=Decision)
    def rights_decision(principal: Principal = Depends(actor)) -> Decision:
        return permit(principal, Action.READ_AGGREGATE)

    @app.post("/w04/v1/benchmarks", response_model=RunResult, status_code=201)
    def benchmark(req: ExperimentRequest, principal: Principal = Depends(actor)) -> RunResult:
        permit(principal, Action.RUN)
        try:
            # Existing W03 domain service validates registry, rights and group isolation.
            return execute(req, registry_path, runs)
        except ConflictError as exc:
            raise HTTPException(409, detail="run identity conflict") from exc
        except (ValueError, TypeError) as exc:
            raise HTTPException(422, detail="invalid synthetic experiment") from exc

    @app.get("/w04/v1/benchmarks/{run_id}", response_model=RunResult)
    def benchmark_read(run_id: str, principal: Principal = Depends(actor)) -> RunResult:
        permit(principal, Action.READ_AGGREGATE)
        try:
            item = runs.get(run_id)
        except ValueError as exc:
            raise HTTPException(422, detail="invalid run ID") from exc
        if item is None:
            raise HTTPException(404, detail="unknown run")
        return RunResult.model_validate(item["result"])

    @app.get("/w04/v1/provenance/{run_id}")
    def graph(run_id: str, principal: Principal = Depends(actor)) -> dict[str, object]:
        permit(principal, Action.READ_AGGREGATE)
        try:
            item = runs.get(run_id)
        except ValueError as exc:
            raise HTTPException(422, detail="invalid run ID") from exc
        if item is None:
            raise HTTPException(404, detail="unknown run")
        return {"root": item["provenance_root"], "nodes": item["nodes"], "trust": "hash-only"}

    @app.get("/w04/v1/provenance/{run_id}/export", response_model=Envelope)
    def export(run_id: str, principal: Principal = Depends(actor)) -> Envelope:
        permit(principal, Action.EXPORT_AGGREGATE)
        try:
            item = runs.get(run_id)
        except ValueError as exc:
            raise HTTPException(422, detail="invalid run ID") from exc
        if item is None:
            raise HTTPException(404, detail="unknown run")
        return export_record(item, rights, principal)

    @app.post("/w04/v1/provenance/verify", response_model=VerifiedReceipt)
    def verify(receipt: Envelope, principal: Principal = Depends(actor)) -> VerifiedReceipt:
        permit(principal, Action.READ_AGGREGATE)
        try:
            verify_envelope(receipt)
        except (TypeError, ValueError) as exc:
            raise HTTPException(422, detail="invalid provenance receipt") from exc
        return VerifiedReceipt(run_id=receipt.run_id, provenance_root=receipt.provenance_root)

    @app.post("/w04/v1/provenance/import", response_model=VerifiedReceipt)
    def import_record(receipt: Envelope, principal: Principal = Depends(actor)) -> VerifiedReceipt:
        # Explicit maintainer-only; does not grant dataset import or widen license.
        if principal.role != "maintainer":
            raise HTTPException(403, detail="maintainer required")
        permit(principal, Action.EXPORT_AGGREGATE)
        try:
            record = verify_envelope(receipt)
            runs.put(record)
        except ConflictError as exc:
            raise HTTPException(409, detail="immutable run conflict") from exc
        except (TypeError, ValueError) as exc:
            raise HTTPException(422, detail="invalid provenance receipt") from exc
        return VerifiedReceipt(run_id=receipt.run_id, provenance_root=receipt.provenance_root)

    @app.get("/w04/v1/rights/ledger")
    def rights_ledger(principal: Principal = Depends(actor)) -> dict[str, object]:
        if principal.role != "maintainer":
            raise HTTPException(403, detail="maintainer required")
        permit(principal, Action.READ_AGGREGATE)
        count, root = policy_audit.verify()
        return {"schema_version": "p25-ledger-1", "records": count, "root": root,
                "trust": "hash-only; anchor root externally for independent tamper detection"}

    @app.post("/w04/v1/jobs/{job_id}", response_model=Job)
    def create_job(job_id: str, principal: Principal = Depends(actor), x_correlation_id: str | None = Header(default=None)) -> Job:
        permit(principal, Action.RUN)
        try:
            return jobs.create(job_id, principal.subject, correlation=_correlation(x_correlation_id))
        except (ValueError, RevisionConflict) as exc:
            raise HTTPException(409, detail="invalid or conflicting job") from exc

    @app.get("/w04/v1/jobs/{job_id}", response_model=Job)
    def get_job(job_id: str, principal: Principal = Depends(actor)) -> Job:
        permit(principal, Action.READ_AGGREGATE)
        try:
            found = jobs.get(job_id)
        except ValueError as exc:
            raise HTTPException(422, detail="invalid job ID") from exc
        if found is None:
            raise HTTPException(404, detail="unknown job")
        if found.actor != principal.subject and principal.role != "maintainer":
            raise HTTPException(403, detail="not job owner")
        return found

    @app.post("/w04/v1/jobs/{job_id}/transition", response_model=Job)
    def transition(job_id: str, cmd: JobTransition, principal: Principal = Depends(actor),
                   x_correlation_id: str | None = Header(default=None)) -> Job:
        permit(principal, Action.RUN)
        try:
            return jobs.advance(job_id, expected_revision=cmd.revision, target=cmd.target,
                                checkpoint=cmd.checkpoint, actor=principal.subject,
                                correlation=_correlation(x_correlation_id))
        except ValueError as exc:
            raise HTTPException(422, detail="invalid checkpoint") from exc
        except RevisionConflict as exc:
            raise HTTPException(409, detail="job transition conflict") from exc

    @app.get("/w04/v1/jobs/{job_id}/audit")
    def audit(job_id: str, principal: Principal = Depends(actor)) -> list[dict[str, object]]:
        get_job(job_id, principal)
        return jobs.audit(job_id)

    return app


def _correlation(value: str | None) -> str:
    if value is not None and 1 <= len(value) <= 64 and all(c in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_" for c in value):
        return value
    return secrets.token_hex(16)
