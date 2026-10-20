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


@app.post("/v1/spectral/synthetic")
def synthetic_spectral(req: JobRequest, tenant: str = Depends(_authorize)) -> dict[str, object]:
    """Bounded, synthetic-only, one-sided Welch PSD; no file uploads or human data."""
    import numpy as np

    from .fixtures import SyntheticReader
    from .spectral_w06 import StreamingWelch

    if req.samples > 8192:
        raise HTTPException(status_code=422, detail="spectral preview capped at 8192 samples")
    reader = SyntheticReader(samples=req.samples, seed=req.seed)
    estimator = StreamingWelch(reader.metadata.sample_rate_hz,
                               len(reader.metadata.channels), 256)
    for start in range(0, req.samples, req.chunk_size):
        end = min(start + req.chunk_size, req.samples)
        estimator.update(reader.read(start, end).as_array(), start)
    frequencies, density = estimator.result()
    if not np.isfinite(density).all():
        raise HTTPException(status_code=422, detail="invalid spectrum")
    return {"schema_version": "1.0", "synthetic_only": True, "seed": req.seed,
            "sample_rate_hz": reader.metadata.sample_rate_hz,
            "unit": "V^2/Hz", "segments": estimator.segments,
            "frequencies_hz": frequencies.tolist(), "power_v2_per_hz": density.tolist(),
            "channels": [c.name for c in reader.metadata.channels]}


@app.post("/v1/artifacts/synthetic")
def synthetic_artifacts(req: JobRequest, tenant: str = Depends(_authorize)) -> dict[str, object]:
    """Tenant-gated synthetic-only QC, ERP and bounded one-channel trace."""
    from .artifacts_w07 import event_locked_erp, minmax_downsample
    from .fixtures import SyntheticReader

    if req.samples > 8192:
        raise HTTPException(status_code=422, detail="preview capped at 8192 samples")
    reader = SyntheticReader(seed=req.seed, samples=req.samples)
    signal = reader.read(0, req.samples).as_array()
    events = [int(event.sample) for event in reader.metadata.events]
    trace = minmax_downsample(signal[0], max_bins=128)
    try:
        result = event_locked_erp(signal, events, reader.sample_rate_hz,
                                  pre_samples=64, post_samples=128)
        erp = {"retained": result.retained, "rejected": result.rejected,
               "out_of_bounds": result.out_of_bounds,
               "time_seconds": result.time_seconds.tolist(),
               "mean_volts": result.mean_volts.tolist(),
               "sem_volts": (result.sem_volts.tolist() if result.retained >= 2 else None),
               "rejected_event_indices": list(result.rejected_event_indices)}
    except ValueError as exc:
        # A zero-epoch result is explicit, not silently converted into a mean.
        erp = {"error": str(exc)}
    return {"schema_version": "1.0", "synthetic_only": True, "seed": req.seed,
            "license": "CC0-1.0-synthetic", "unit": "V",
            "channel": reader.metadata.channels[0].name,
            "trace_volts_minmax": trace.tolist(),
            "artifact_absolute_uv": 120, "artifact_peak_to_peak_uv": 180,
            "erp": erp}


@app.post("/v1/artifacts/synthetic/export")
def export_synthetic_artifacts(req: JobRequest, tenant: str = Depends(_authorize)):
    """Authenticated deterministic provenance JSON download, synthetic fixtures only."""
    from fastapi.responses import Response

    from .qc_w07 import deterministic_json_manifest

    record = synthetic_artifacts(req, tenant)
    payload = {"schema_version": "1.0", "kind": "synthetic-artifact-erp",
               "source": "generated:seeded-sine", "license": "CC0-1.0-synthetic",
               "threshold_absolute_uv": 120, "threshold_peak_to_peak_uv": 180,
               "seed": req.seed, "samples": req.samples,
               "channel": record["channel"], "erp": record["erp"]}
    encoded = deterministic_json_manifest(payload)
    # Never place caller-controlled keys in filenames or response headers.
    return Response(content=encoded, media_type="application/json",
                    headers={"Content-Disposition": 'attachment; filename="synthetic-qc-manifest.json"',
                             "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


class ComparisonRequest(BaseModel):
    baseline_sha256: str = Field(pattern="^[a-f0-9]{64}$")
    candidate_sha256: str = Field(pattern="^[a-f0-9]{64}$")
    metric: str = Field(min_length=1, max_length=64, pattern="^[a-zA-Z0-9_]+$")
    max_relative_regression: float = Field(default=0.05, ge=0, le=1)


@app.post("/v1/evalops/compare")
def compare_registered_runs(req: ComparisonRequest, tenant: str = Depends(_authorize)):
    """Tenant-scoped synthetic registry comparisons; no public upload endpoint."""
    from .registry_w08 import EvidenceRegistry

    root = Path(os.environ.get("NEUROSIGNAL_DB_PATH", "./.private_w05/jobs.sqlite3"))
    registry = EvidenceRegistry(root.with_name("evidence.sqlite3"))
    try:
        return registry.compare(tenant, req.baseline_sha256, req.candidate_sha256,
                                metric=req.metric,
                                max_relative_regression=req.max_relative_regression)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="no such registered run") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
