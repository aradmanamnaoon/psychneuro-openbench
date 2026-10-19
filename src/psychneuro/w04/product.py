# ruff: noqa: I001  # FastAPI dependency injection uses Depends defaults.
"""W04 v2 private product facade: P25 rights -> W03 P1 -> P13 provenance.

Not production IAM: static internal tokens are operator-managed.
Run ownership is fail-closed and tenant-scoped; no raw participant data.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal, NoReturn

from fastapi import Depends, FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from psychneuro.w03.contracts import ExperimentRequest, RunResult
from psychneuro.w03.store import ConflictError, RunStore
from psychneuro.w03.vault import verify_serialized
from .interop import Envelope, export_record, verify_envelope
from .rights import Action, DatasetRights, Decision, Principal, decide


class RunComparison(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["w04-comparison-2"] = "w04-comparison-2"
    left: RunResult
    right: RunResult
    balanced_accuracy_difference: float
    interpretation: str = "Descriptive difference only; separate runs are not a paired statistical test."


class SplitSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["w04-split-2"] = "w04-split-2"
    run_id: str
    train_groups: int = Field(ge=1)
    test_groups: int = Field(ge=1)
    partition: Literal["participant-disjoint-verified-by-W03"] = "participant-disjoint-verified-by-W03"
    split_sha256: str


class ImportResult(BaseModel):
    schema_version: Literal["w04-import-2"] = "w04-import-2"
    run_id: str
    provenance_root: str
    verification: Literal["hash-integrity-only"] = "hash-integrity-only"


class TenantRunACL:
    """SQLite ownership index; unknown and cross-tenant runs are never public."""

    def __init__(self, path: Path) -> None:
        self.path = path
        with sqlite3.connect(path, timeout=5) as db:
            db.execute("CREATE TABLE IF NOT EXISTS w04_run_acl ("
                       "run_id TEXT PRIMARY KEY, tenant TEXT NOT NULL, owner TEXT NOT NULL)")

    def claim(self, run_id: str, principal: Principal) -> None:
        with sqlite3.connect(self.path, timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO w04_run_acl VALUES(?,?,?)",
                       (run_id, principal.tenant, principal.subject))
            row = db.execute("SELECT tenant,owner FROM w04_run_acl WHERE run_id=?",
                             (run_id,)).fetchone()
            if row != (principal.tenant, principal.subject):
                raise PermissionError("run ownership conflict")

    def check(self, run_id: str, principal: Principal) -> None:
        with sqlite3.connect(self.path, timeout=5) as db:
            row = db.execute("SELECT tenant,owner FROM w04_run_acl WHERE run_id=?",
                             (run_id,)).fetchone()
        if row is None or row[0] != principal.tenant or (
            row[1] != principal.subject and principal.role != "maintainer"
        ):
            raise PermissionError("run not accessible")

    def put_owned(self, runs: RunStore, record: dict[str, Any], principal: Principal) -> None:
        """Atomically bind an immutable W03 record and its W04 tenant owner.

        A preexisting run without an owner requires explicit audited migration.
        No importer or benchmark can claim an orphaned legacy record.
        """
        if self.path.resolve() != runs.path.resolve():
            raise ValueError("run and ACL stores must use the same SQLite file")
        run_id = record.get("run_id")
        if not isinstance(run_id, str):
            raise TypeError("invalid run identity")
        with runs._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            owner = conn.execute(
                "SELECT tenant, owner FROM w04_run_acl WHERE run_id=?", (run_id,)
            ).fetchone()
            if owner is None:
                existing = conn.execute(
                    "SELECT 1 FROM runs WHERE run_id=?", (run_id,)
                ).fetchone()
                if existing is not None:
                    raise PermissionError("unowned existing run needs trusted migration")
            elif owner != (principal.tenant, principal.subject):
                raise PermissionError("run is already assigned to another principal")
            runs.put_in_connection(conn, record)
            if owner is None:
                conn.execute(
                    "INSERT INTO w04_run_acl (run_id, tenant, owner) VALUES (?, ?, ?)",
                    (run_id, principal.tenant, principal.subject),
                )


class OwnerBoundRunStore(RunStore):
    """Only the authorized request principal can persist the W03 output."""

    def __init__(self, runs: RunStore, acl: TenantRunACL, principal: Principal) -> None:
        self.path = runs.path
        self._acl = acl
        self._principal = principal

    def put(self, record: dict[str, Any]) -> None:
        self._acl.put_owned(self, record, self._principal)


def _deny(code: str, message: str, status: int) -> NoReturn:
    raise HTTPException(status_code=status, detail={
        "schema_version": "w04-error-2", "code": code, "message": message,
    })


def install_product_routes(
    app: FastAPI, *, db_path: Path, runs: RunStore, rights: DatasetRights,
    actor: Callable[..., Principal], execute_request: Callable[[ExperimentRequest, RunStore], RunResult],
) -> None:
    """Add actual W03 backed endpoints to existing app, not a duplicate server."""
    acl = TenantRunACL(db_path)

    def authorize(principal: Principal, action: Action) -> Decision:
        verdict = decide(rights, principal, action)
        if not verdict.allowed:
            _deny("W04_FORBIDDEN", "Policy denied: " + verdict.reason, 403)
        return verdict

    def get_record(run_id: str, principal: Principal, action: Action) -> dict[str, Any]:
        authorize(principal, action)
        try:
            acl.check(run_id, principal)
            record = runs.get(run_id)
        except PermissionError:
            _deny("W04_FORBIDDEN", "Run not accessible to this principal", 403)
        except (ValueError, TypeError):
            _deny("W04_INVALID", "Invalid ID or persisted graph integrity", 422)
        if record is None:
            _deny("W04_NOT_FOUND", "Run not found", 404)
        return record

    @app.get("/w04/v2/catalog")
    def catalog(principal: Principal = Depends(actor)) -> dict[str, Any]:
        verdict = authorize(principal, Action.READ_AGGREGATE)
        return {"schema_version": "w04-catalog-2", "datasets": [
            {"id": rights.dataset_id, "origin": rights.origin, "consent": rights.consent,
             "scope": "private aggregated synthetic only",
             "rights": verdict.model_dump(mode="json")}
        ], "limits": {"participants": [24, 80], "trials_per_participant": [8, 40]},
            "identity_warning": "Static operator-token roles are not production IAM."}

    @app.get("/w04/v2/rights/preview", response_model=Decision)
    def preview(principal: Principal = Depends(actor)) -> Decision:
        return decide(rights, principal, Action.RUN)

    @app.post("/w04/v2/runs", response_model=RunResult, status_code=201)
    def create_run(req: ExperimentRequest, principal: Principal = Depends(actor)) -> RunResult:
        authorize(principal, Action.RUN)
        try:
            return execute_request(req, OwnerBoundRunStore(runs, acl, principal))
        except PermissionError:
            _deny("W04_CONFLICT", "Run ID belongs to a different owner", 409)
        except ConflictError:
            _deny("W04_CONFLICT", "Run identity has conflicting evidence", 409)
        except (ValueError, TypeError):
            _deny("W04_INVALID", "Invalid synthetic request or stored provenance", 422)

    @app.get("/w04/v2/runs/{run_id}", response_model=RunResult)
    def get_run(run_id: str, principal: Principal = Depends(actor)) -> RunResult:
        return RunResult.model_validate(
            get_record(run_id, principal, Action.READ_AGGREGATE)["result"]
        )

    @app.get("/w04/v2/runs/{run_id}/split", response_model=SplitSummary)
    def split(run_id: str, principal: Principal = Depends(actor)) -> SplitSummary:
        record = get_record(run_id, principal, Action.READ_AGGREGATE)
        verify_serialized(record["nodes"], record["provenance_root"])
        result = RunResult.model_validate(record["result"])
        metadata = record["nodes"][1]["metadata"]
        if metadata.get("train_groups") != result.n_train_groups or (
            metadata.get("test_groups") != result.n_test_groups
        ):
            _deny("W04_INVALID", "Split metadata disagrees with persisted result", 422)
        return SplitSummary(run_id=run_id, train_groups=result.n_train_groups,
                            test_groups=result.n_test_groups,
                            split_sha256=result.split_sha256)

    @app.get("/w04/v2/runs/{run_id}/graph")
    def graph(run_id: str, principal: Principal = Depends(actor)) -> dict[str, Any]:
        record = get_record(run_id, principal, Action.READ_AGGREGATE)
        return {"schema_version": "w04-graph-2", "root": record["provenance_root"],
                "nodes": record["nodes"], "verified": True,
                "warning": "Hash integrity does not prove independent authenticity."}

    @app.get("/w04/v2/runs/{run_id}/artifact")
    def artifact(run_id: str, principal: Principal = Depends(actor)) -> Response:
        record = get_record(run_id, principal, Action.EXPORT_AGGREGATE)
        envelope = export_record(record, rights, principal)
        contents = json.dumps(envelope.model_dump(mode="json"),
                              sort_keys=True, indent=2, allow_nan=False)
        return Response(contents, media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="w04-{run_id}.json"',
                                 "Cache-Control": "no-store",
                                 "X-Content-Type-Options": "nosniff"})

    @app.post("/w04/v2/artifacts/verify", response_model=ImportResult)
    def verify(receipt: Envelope, principal: Principal = Depends(actor)) -> ImportResult:
        authorize(principal, Action.READ_AGGREGATE)
        try:
            verify_envelope(receipt)
        except (ValueError, TypeError):
            _deny("W04_INVALID", "Receipt or DAG verification failed", 422)
        return ImportResult(run_id=receipt.run_id, provenance_root=receipt.provenance_root)

    @app.post("/w04/v2/artifacts/import", response_model=ImportResult)
    def import_artifact(receipt: Envelope, principal: Principal = Depends(actor)) -> ImportResult:
        authorize(principal, Action.EXPORT_AGGREGATE)
        if principal.role != "maintainer":
            _deny("W04_FORBIDDEN", "Maintainer role required", 403)
        # Even coherent SHA-256 receipts can be forged if the root is not anchored.
        # Leave imports disabled until a trusted signer/root and rights owner exist.
        _deny("W04_IMPORT_DISABLED", "Trusted provenance and rights anchor missing", 403)

    @app.get("/w04/v2/compare", response_model=RunComparison)
    def compare(left: str, right: str, principal: Principal = Depends(actor)) -> RunComparison:
        first = RunResult.model_validate(
            get_record(left, principal, Action.READ_AGGREGATE)["result"]
        )
        second = RunResult.model_validate(
            get_record(right, principal, Action.READ_AGGREGATE)["result"]
        )
        return RunComparison(left=first, right=second,
                             balanced_accuracy_difference=(
                                 first.outer_balanced_accuracy - second.outer_balanced_accuracy
                             ))
