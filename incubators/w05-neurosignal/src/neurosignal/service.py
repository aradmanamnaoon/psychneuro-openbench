"""Local private bearer-gated versioned API. No externally accessible deployment."""
from __future__ import annotations

import hmac
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .integration import run_synthetic
from .storage import JobStore

app = FastAPI(title="NeuroSignal Atlas / EvalOps / DSP private preview", version="0.1.0")


class JobRequest(BaseModel):
    seed: int = Field(default=42, ge=0, lt=2**32)
    samples: int = Field(default=1024, ge=512, le=65536)
    chunk_size: int = Field(default=256, ge=1, le=2048)
    idempotency_key: str = Field(min_length=8, max_length=128)


class ReviewRequest(BaseModel):
    job_id: str = Field(min_length=32, max_length=32)


def _authorize(authorization: str | None = Header(default=None),
               x_tenant: str | None = Header(default=None)) -> str:
    token = os.getenv("NEUROSIGNAL_LOCAL_TOKEN", "")
    if not token or not authorization or not hmac.compare_digest(authorization, f"Bearer {token}"):
        raise HTTPException(status_code=401, detail="local API token required")
    if not x_tenant or not x_tenant.isascii() or not x_tenant.replace("-", "").isalnum() or len(x_tenant) > 64:
        raise HTTPException(status_code=400, detail="valid tenant required")
    # Single configured tenant only: a shared credential must never authorize
    # arbitrary caller-selected tenant namespaces.
    configured = os.getenv("NEUROSIGNAL_LOCAL_TENANT", "")
    if not configured or not hmac.compare_digest(x_tenant, configured):
        raise HTTPException(status_code=403, detail="tenant not authorized")
    return configured


def _store() -> JobStore:
    path = Path(os.environ.get("NEUROSIGNAL_DB_PATH", "./.private_w05/jobs.sqlite3"))
    return JobStore(path)


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"service": "private-synthetic-preview", "version": "1.0"}


@app.post("/v1/jobs", status_code=202)
def submit(req: JobRequest, tenant: str = Depends(_authorize)) -> dict[str, object]:
    store = _store()
    try:
        job = store.submit(tenant, req.idempotency_key,
                           req.model_dump(exclude={"idempotency_key"}))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"id": job.id, "status": job.status, "revision": job.revision}


@app.get("/v1/jobs/{job_id}")
def status(job_id: str, tenant: str = Depends(_authorize)) -> dict[str, object]:
    try:
        job = _store().get(tenant, job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc
    return {"id": job.id, "status": job.status, "attempts": job.attempts,
            "revision": job.revision, "result": job.result_json, "error": job.error}


@app.post("/v1/jobs/{job_id}/cancel")
def cancel(job_id: str, tenant: str = Depends(_authorize)) -> dict[str, object]:
    try:
        job = _store().cancel(tenant, job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc
    return {"status": job.status, "requested_cancel": job.requested_cancel}


@app.post("/v1/demo")
def demo(req: JobRequest, tenant: str = Depends(_authorize)) -> dict[str, object]:
    # Strict synchronous bounded sample only; durable async worker API is not connected to UI.
    if req.samples > 8192:
        raise HTTPException(status_code=422, detail="synchronous demo is capped at 8192 samples")
    return run_synthetic(seed=req.seed, samples=req.samples, chunk_size=req.chunk_size)

# Locally hosted, keyboard-operable basic browser. Same-origin static assets, no external CDNs.
_STATIC = Path(__file__).with_name("static")
app.mount("/static", StaticFiles(directory=_STATIC), name="static")

@app.get("/", include_in_schema=False)
def homepage() -> FileResponse:
    return FileResponse(_STATIC / "index.html", headers={
        "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'",
        "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})
