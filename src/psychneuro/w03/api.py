"""Internal-token, synthetic-only FastAPI; no public host or raw data endpoints."""
from __future__ import annotations

import hmac
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException

from .contracts import ExperimentRequest, RunResult
from .service import execute
from .store import ConflictError, RunStore


def create_app(*, db_path: Path, registry_path: Path, internal_token: str) -> FastAPI:
    if len(internal_token) < 20:
        raise ValueError("internal_token must be explicitly configured and at least 20 characters")
    store = RunStore(db_path)
    app = FastAPI(title="PsychNeuro W03 private experiment API", version="0.1.0")

    def require_token(x_internal_token: str | None = Header(default=None)) -> None:
        if not x_internal_token or not hmac.compare_digest(x_internal_token, internal_token):
            raise HTTPException(status_code=403, detail="forbidden")

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "internal-only"}

    @app.post("/v1/runs", response_model=RunResult, dependencies=[Depends(require_token)])
    def submit(request: ExperimentRequest) -> RunResult:
        try:
            return execute(request, registry_path, store)
        except ConflictError as exc:
            raise HTTPException(status_code=409, detail="run identity conflict") from exc
        except ValueError as exc:
            # Do not echo internal paths, private content or submitted data.
            raise HTTPException(status_code=422, detail="invalid synthetic experiment") from exc

    @app.get("/v1/runs/{run_id}", response_model=RunResult,
             dependencies=[Depends(require_token)])
    def read(run_id: str) -> RunResult:
        try:
            result = store.get(run_id)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="invalid run ID") from exc
        if result is None:
            raise HTTPException(status_code=404, detail="unknown run")
        return RunResult.model_validate(result["result"])

    @app.get("/v1/runs/{run_id}/provenance", dependencies=[Depends(require_token)])
    def provenance(run_id: str) -> dict[str, object]:
        try:
            result = store.get(run_id)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="invalid run ID") from exc
        if result is None:
            raise HTTPException(status_code=404, detail="unknown run")
        return {"root": result["provenance_root"], "nodes": result["nodes"]}

    return app
