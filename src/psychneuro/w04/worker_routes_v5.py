"""Authenticated operator-enqueued P25-v2 synthetic jobs.

The API NEVER fits models or issues worker leases. A separate trusted, private
operator process invokes worker_cli_v5. Cancel invalidates active worker fences;
any running sklearn fit may continue CPU work but cannot publish after cancel.
"""
from __future__ import annotations

import secrets
from collections.abc import Callable
from pathlib import Path
from typing import Literal, NoReturn

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from psychneuro.w03.contracts import ExperimentRequest

from .policy_snapshot import get_validated_policy
from .policy_v2 import PolicyError, PolicyStore
from .private_worker_v4 import AtomicWorker, Request, preflight_source
from .queue_v2 import JobConflict, QueueItem, QueueStore
from .rights import Principal


class JobSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal["w04-job-submit-5"] = "w04-job-submit-5"
    idempotency_key: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_.-]+$")
    experiment: ExperimentRequest


def install_worker_routes(
    app: FastAPI, *, database: Path, registry: Path, policy: PolicyStore,
    actor: Callable[..., Principal],
) -> None:
    queue = QueueStore(database)
    worker = AtomicWorker(database=database, policy=policy, queue=queue, registry_path=registry)

    def denied(status: int = 403, *, code: str = "W04_FORBIDDEN") -> NoReturn:
        raise HTTPException(status_code=status, detail={
            "schema_version": "w04-error-2", "code": code,
            "message": "Private job permission or state denied",
        })

    @app.post("/w04/v3/jobs", response_model=QueueItem, status_code=201)
    def enqueue(req: JobSubmission, principal: Principal = Depends(actor)) -> QueueItem:  # noqa: B008 - FastAPI dependency boundary
        try:
            job_req = Request.model_validate({
                **req.experiment.model_dump(mode="python"),
                "version": "w04-worker-request-4",
            })
            digest = preflight_source(job_req, registry)
            grant = get_validated_policy(policy, tenant=principal.tenant)
            if grant.revoked or grant.source_sha256 != digest:
                denied()
            return worker.submit(
                tenant=principal.tenant, subject=principal.subject, role=principal.role,
                idempotency_key=req.idempotency_key, request=job_req,
                correlation=secrets.token_hex(12),
            )
        except (PolicyError, PermissionError):
            denied()
        except JobConflict:
            denied(409, code="W04_CONFLICT")
        except (ValueError, TypeError):
            denied(422, code="W04_INVALID")

    @app.get("/w04/v3/jobs/{job_id}", response_model=QueueItem)
    def status(job_id: str, principal: Principal = Depends(actor)) -> QueueItem:  # noqa: B008 - FastAPI dependency boundary
        try:
            policy.authorize(
                tenant=principal.tenant, subject=principal.subject, role=principal.role,
                dataset="w03-original-synthetic", action="read_aggregate",
                purpose="internal-method-validation", correlation_id=secrets.token_hex(12),
            )
            return queue.get(
                tenant=principal.tenant, job_id=job_id, subject=principal.subject,
                maintainer=principal.role == "maintainer",
            )
        except (PolicyError, JobConflict, ValueError):
            denied()

    @app.post("/w04/v3/jobs/{job_id}/cancel", response_model=QueueItem)
    def cancel(job_id: str, principal: Principal = Depends(actor)) -> QueueItem:  # noqa: B008 - FastAPI dependency boundary
        # Cancellation remains available after revocation: safety must never
        # depend on retaining a valid RUN grant.
        try:
            return queue.cancel(
                tenant=principal.tenant, job_id=job_id, subject=principal.subject,
                maintainer=principal.role == "maintainer",
                correlation=secrets.token_hex(12),
            )
        except (JobConflict, ValueError):
            denied(409, code="W04_CONFLICT")

    @app.post("/w04/v3/jobs/{job_id}/resume", response_model=QueueItem)
    def resume(job_id: str, principal: Principal = Depends(actor)) -> QueueItem:  # noqa: B008 - FastAPI dependency boundary
        try:
            permit = policy.authorize(
                tenant=principal.tenant, subject=principal.subject, role=principal.role,
                dataset="w03-original-synthetic", action="run",
                purpose="internal-method-validation", correlation_id=secrets.token_hex(12),
            )
            return queue.resume_cancelled(
                tenant=principal.tenant, job_id=job_id, subject=principal.subject,
                correlation=secrets.token_hex(12), permit=permit, policy_store=policy,
            )
        except (PolicyError, PermissionError):
            denied()
        except (JobConflict, ValueError):
            denied(409, code="W04_CONFLICT")

    @app.get("/w04/v3/jobs/{job_id}/receipt")
    def receipt(job_id: str, principal: Principal = Depends(actor)) -> dict[str, object]:  # noqa: B008 - FastAPI dependency boundary
        try:
            artifact = worker.read(
                tenant=principal.tenant, subject=principal.subject, role=principal.role,
                job_id=job_id, correlation=secrets.token_hex(12),
            )
            return artifact.model_dump(mode="json")
        except (PolicyError, JobConflict, ValueError):
            denied()
