"""Opt-in private v2 HTTP facade: policy-rechecked admission and job read/cancel.

Worker and grant-installation actions deliberately have no HTTP routes. This is
not a deployment entrypoint and it must not be exposed to an untrusted browser.
"""
from __future__ import annotations

import hmac
import secrets
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from psychneuro.w03.contracts import ExperimentRequest
from .policy_v2 import Permit, PolicyError, PolicyStore
from .queue_v2 import JobConflict, QueueItem, QueueStore


class Actor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    tenant: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,80}$")
    subject: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,80}$")
    role: Literal["viewer", "researcher", "maintainer"]


class EnqueueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    version: Literal["w04-enqueue-2"] = "w04-enqueue-2"
    dataset: Literal["w03-original-synthetic"] = "w03-original-synthetic"
    purpose: Literal["internal-method-validation"] = "internal-method-validation"
    idempotency_key: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,80}$")
    experiment: ExperimentRequest


class DecisionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    allowed: Literal[True] = True
    policy_revision: int
    # P25 MAC is *never* disclosed over HTTP.
    policy_sha256: str
    warning: Literal["private synthetic internal permission only"] = "private synthetic internal permission only"


def create_hardened_app(*, db_path: Path, credentials: dict[str, Actor],
                        permit_key: bytes) -> FastAPI:
    if not credentials or any(len(token) < 32 for token in credentials):
        raise ValueError("operator-configured private tokens must be 32+ characters")
    policy = PolicyStore(db_path, permit_key=permit_key)
    queue = QueueStore(db_path)
    app = FastAPI(title="Private W04 v2 admission and job coordination", version="0.4.2",
                  docs_url=None, redoc_url=None, openapi_url=None)

    def principal(x_internal_token: str | None = Header(default=None)) -> Actor:
        found: Actor | None = None
        for token, actor in credentials.items():
            if hmac.compare_digest(token, x_internal_token or ""):
                found = actor
        if found is None:
            raise HTTPException(403, detail="forbidden")
        return found

    def authorize(actor: Actor, action: str, correlation: str) -> Permit:
        try:
            return policy.authorize(tenant=actor.tenant, dataset="w03-original-synthetic",
                                    subject=actor.subject, role=actor.role, action=action,
                                    purpose="internal-method-validation", correlation_id=correlation)
        except (ValueError, PolicyError) as exc:
            raise HTTPException(403, detail="policy_denied") from exc

    @app.get("/w04/v2/rights/check", response_model=DecisionResponse)
    def check(actor: Actor = Depends(principal)) -> DecisionResponse:
        permit = authorize(actor, "read_aggregate", secrets.token_hex(12))
        return DecisionResponse(policy_revision=permit.policy_revision,
                                policy_sha256=permit.policy_sha256)

    @app.post("/w04/v2/jobs", response_model=QueueItem, status_code=202)
    def enqueue(req: EnqueueRequest, actor: Actor = Depends(principal)) -> QueueItem:
        correlation = secrets.token_hex(12)
        permit = authorize(actor, "run", correlation)
        try:
            policy.validate_permit(permit)
            return queue.enqueue(tenant=actor.tenant, subject=actor.subject, dataset=req.dataset,
                                 idempotency_key=req.idempotency_key,
                                 payload=req.experiment.model_dump(mode="json"), correlation=correlation)
        except (ValueError, JobConflict, PolicyError) as exc:
            raise HTTPException(409, detail="job_conflict_or_stale_permission") from exc

    @app.get("/w04/v2/jobs/{job_id}", response_model=QueueItem)
    def get(job_id: str, actor: Actor = Depends(principal)) -> QueueItem:
        authorize(actor, "read_aggregate", secrets.token_hex(12))
        try:
            return queue.get(tenant=actor.tenant, job_id=job_id, subject=actor.subject,
                             maintainer=actor.role == "maintainer")
        except (ValueError, JobConflict) as exc:
            raise HTTPException(404, detail="unknown_job") from exc

    @app.post("/w04/v2/jobs/{job_id}/cancel", response_model=QueueItem)
    def cancel(job_id: str, actor: Actor = Depends(principal)) -> QueueItem:
        authorize(actor, "run", secrets.token_hex(12))
        try:
            return queue.cancel(tenant=actor.tenant, job_id=job_id, subject=actor.subject,
                                correlation=secrets.token_hex(12),
                                maintainer=actor.role == "maintainer")
        except (ValueError, JobConflict) as exc:
            raise HTTPException(409, detail="cancel_conflict") from exc

    @app.post("/w04/v2/jobs/{job_id}/resume", response_model=QueueItem)
    def resume(job_id: str, actor: Actor = Depends(principal)) -> QueueItem:
        permit = authorize(actor, "run", secrets.token_hex(12))
        try:
            return queue.resume_cancelled(tenant=actor.tenant, job_id=job_id,
                                          subject=actor.subject, correlation=secrets.token_hex(12),
                                          permit=permit, policy_store=policy)
        except (ValueError, PolicyError, JobConflict) as exc:
            raise HTTPException(409, detail="resume_conflict") from exc

    return app