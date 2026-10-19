"""P25: explicit fail-closed dataset rights and typed authorization decisions.

Policy *evidence* is supplied by a trusted registry, not by a benchmark client.
Not legal advice; legal permission and effective participant consent need review.
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Action(str, Enum):
    RUN = "run"
    READ_AGGREGATE = "read_aggregate"
    EXPORT_AGGREGATE = "export_aggregate"
    EXPORT_DATA = "export_data"
    IMPORT_REPORT = "import_report"


class Principal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    subject: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_.-]+$")
    tenant: str = Field(default="local", min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    role: Literal["viewer", "researcher", "maintainer"]


class DatasetRights(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["p25-rights-1"] = "p25-rights-1"
    dataset_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9_.-]+$")
    origin: Literal["original-synthetic", "third-party", "human"]
    license_expression: str = Field(min_length=1, max_length=120)
    consent: Literal["not-applicable", "documented", "unknown", "withdrawn"]
    verified_by: str | None = None
    approved_actions: frozenset[Action] = frozenset()
    expires_on: date | None = None
    revoked: bool = False


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["p25-decision-1"] = "p25-decision-1"
    allowed: bool
    reason: Literal["allowed", "no_review", "revoked", "expired", "consent", "action_not_granted", "role", "unapproved_source"]
    dataset_id: str
    action: Action


# Existing W03 registry: original generated data, no independent public data grant.
# This grants *only private aggregate handling*, with trusted server-side provenance.
W03_INTERNAL = DatasetRights(
    dataset_id="w03-original-synthetic", origin="original-synthetic",
    license_expression="not-separately-specified", consent="not-applicable",
    verified_by="internal-registry", approved_actions=frozenset({Action.RUN, Action.READ_AGGREGATE, Action.EXPORT_AGGREGATE}),
)


def decide(rights: DatasetRights, principal: Principal, action: Action, *, today: date | None = None) -> Decision:
    """Deny by default. In particular, no human-data execution even if caller claims a license."""
    if rights.revoked:
        reason = "revoked"
    elif rights.expires_on is not None and (today or date.today()) > rights.expires_on:
        reason = "expired"
    elif rights.consent == "withdrawn" or (rights.origin == "human" and rights.consent != "documented"):
        reason = "consent"
    elif not rights.verified_by:
        reason = "no_review"
    elif rights.origin != "original-synthetic":
        # Future licensed sources require a separate authorized registry migration.
        reason = "unapproved_source"
    elif action not in rights.approved_actions:
        reason = "action_not_granted"
    elif action in {Action.RUN, Action.EXPORT_AGGREGATE, Action.IMPORT_REPORT} and principal.role not in {"researcher", "maintainer"}:
        reason = "role"
    elif action == Action.EXPORT_DATA:
        reason = "action_not_granted"
    else:
        reason = "allowed"
    return Decision(allowed=reason == "allowed", reason=reason, dataset_id=rights.dataset_id, action=action)
