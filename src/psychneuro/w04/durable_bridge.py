"""Fail-closed P25 v2 policy and W03 source-binding bridge.

Private synthetic data only. A grant is restricted to one concrete source SHA.
No participant data, browser permits, or automatic grants.
"""
from __future__ import annotations

import hmac
import secrets
import sqlite3
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from psychneuro.w03.contracts import ExperimentRequest, RunResult

from .policy_snapshot import get_validated_policy
from .policy_v2 import Permit, PolicyError, PolicyStore
from .rights import Action, Principal


def source_sha256(request: ExperimentRequest, registry: Path) -> str:
    from psychneuro.loaders import load_dataset
    from psychneuro.synthetic import SyntheticConfig

    source = load_dataset(
        SyntheticConfig(seed=request.generator_seed,
                        n_participants=request.n_participants,
                        trials_per_participant=request.trials_per_participant),
        registry,
    )
    if source.provenance.source_kind != "synthetic" or (
        source.provenance.license != "not-separately-specified"
    ):
        raise PolicyError("unapproved source")
    return source.schema.source_sha256


class DurableRightsBridge:
    def __init__(self, store: PolicyStore, registry: Path) -> None:
        self.store = store
        self.registry = registry

    def authorize(self, principal: Principal, action: Action) -> Permit:
        if action not in (Action.RUN, Action.READ_AGGREGATE, Action.EXPORT_AGGREGATE):
            raise PolicyError("unsupported action")
        permit = self.store.authorize(
            tenant=principal.tenant, subject=principal.subject, role=principal.role,
            dataset="w03-original-synthetic", action=action.value,
            purpose="internal-method-validation", correlation_id=secrets.token_hex(12))
        self.store.validate_permit(permit)
        return permit

    def assert_source(self, tenant: str, source: str) -> None:
        policy = get_validated_policy(self.store, tenant=tenant)
        if policy.revoked or policy.source_sha256 != source:
            raise PolicyError("source not covered by P25 grant")

    def prepare_run(self, principal: Principal,
                    request: ExperimentRequest) -> Callable[[], None]:
        permit = self.authorize(principal, Action.RUN)
        digest = source_sha256(request, self.registry)
        self.assert_source(principal.tenant, digest)

        def before_persist() -> None:
            self.store.validate_permit(permit)
            self.assert_source(principal.tenant, digest)
        return before_persist

    def prepare_atomic_run(
        self, principal: Principal, request: ExperimentRequest,
    ) -> tuple[Callable[[], None], Callable[[sqlite3.Connection, dict[str, Any]], None]]:
        """Bind P25 authorization to the SAME SQLite transaction as W03 publication.

        The outer check prevents unnecessary work. The inner check is the
        authorization linearization point; it closes revoke/retention races
        between the final fit and publication. The caller MUST acquire
        BEGIN IMMEDIATE before invoking the inner callback, on the exact
        PolicyStore/RunStore SQLite file.
        """
        permit = self.authorize(principal, Action.RUN)
        source = source_sha256(request, self.registry)
        self.assert_source(principal.tenant, source)

        def before_persist() -> None:
            self.store.validate_permit(permit)
            self.assert_source(principal.tenant, source)

        def before_commit(db: sqlite3.Connection, record: dict[str, Any]) -> None:
            # Recheck all P25 audit and snapshots under the writer lock. Never
            # accept a passed-in client claim as authority for the source.
            self.store._verify_events(db)
            self.store._verify_snapshots(db)
            row = db.execute(
                "SELECT revision,payload,sha FROM p25_v2_policy "
                "WHERE tenant=? AND dataset=?",
                (permit.tenant, permit.dataset),
            ).fetchone()
            if row is None:
                raise PolicyError("unknown or revoked P25 policy")
            policy = self.store._checked(permit.tenant, permit.dataset, *row)
            now = time.time_ns()
            result = record.get("result")
            if not isinstance(result, dict):
                raise PolicyError("invalid W03 record at policy boundary")
            unsigned = permit.model_dump(mode="json", exclude={"mac_sha256"})
            if (
                not hmac.compare_digest(permit.mac_sha256, self.store._mac(unsigned))
                or policy.revoked
                or permit.tenant != principal.tenant
                or permit.subject != principal.subject
                or permit.action != Action.RUN.value
                or permit.purpose != policy.purpose
                or permit.policy_revision != row[0]
                or not hmac.compare_digest(permit.policy_sha256, row[2])
                or permit.expires_ns <= now
                or policy.retention_until_ns <= now
                or permit.expires_ns > policy.retention_until_ns
                or Action.RUN.value not in policy.actions
                or policy.origin != "original-synthetic"
                or not hmac.compare_digest(policy.source_sha256, source)
                or result.get("source_sha256") != source
                or record.get("rights") != "internal-synthetic-only"
            ):
                raise PolicyError("stale, revoked or mismatched pre-publication policy")

        return before_persist, before_commit

    def check_result(self, principal: Principal, result: RunResult) -> None:
        self.authorize(principal, Action.READ_AGGREGATE)
        self.assert_source(principal.tenant, result.source_sha256)

    def check_record(self, principal: Principal, action: Action,
                     record: dict[str, object]) -> None:
        self.authorize(principal, action)
        result = record.get("result")
        if not isinstance(result, dict) or not isinstance(result.get("source_sha256"), str):
            raise PolicyError("invalid source claim")
        self.assert_source(principal.tenant, result["source_sha256"])
