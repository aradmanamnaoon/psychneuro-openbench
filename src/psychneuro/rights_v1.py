"""Conservative versioned P25 data-rights decision engine. Not legal advice."""
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

class Action(StrEnum):
    ANALYZE = "analyze"
    REDISTRIBUTE = "redistribute"

@dataclass(frozen=True)
class DatasetGrant:
    dataset_id: str
    source_sha256: str
    license_id: str | None
    verified: bool
    allowed_actions: frozenset[Action]
    revoked: bool = False
    human_data: bool = False
    consent_verified: bool = False
    ethics_approved: bool = False

@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    contract_version: Literal["p25.v1"] = "p25.v1"

def evaluate(grant: DatasetGrant, action: Action) -> Decision:
    if grant.revoked:
        return Decision(False, "revoked")
    if not grant.verified or not grant.license_id:
        return Decision(False, "unverified rights")
    if len(grant.source_sha256) != 64 or any(c not in "0123456789abcdef" for c in grant.source_sha256):
        return Decision(False, "invalid source digest")
    if grant.human_data and not (grant.consent_verified and grant.ethics_approved):
        return Decision(False, "human-data authorization incomplete")
    if action not in grant.allowed_actions:
        return Decision(False, "action not granted")
    return Decision(True, "grant verified for specific action")
