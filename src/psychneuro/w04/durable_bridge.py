"""Fail-closed P25 v2 policy and W03 source-binding bridge.

Private synthetic data only. A grant is restricted to one concrete source SHA.
No participant data, browser permits, or automatic grants.
"""
from __future__ import annotations

import secrets
from pathlib import Path
from typing import Callable

from psychneuro.w03.contracts import ExperimentRequest, RunResult
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
        policy = self.store.read_policy(tenant=tenant)
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
