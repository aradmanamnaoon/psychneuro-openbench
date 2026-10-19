"""P1→P13→P25 interchange envelope: strict hash-validated portable report.

Hashes detect accidental corruption; an attacker able to replace the archive AND
its expected root can forge both. Provide a trusted offline digest for authenticity.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from psychneuro.w03.store import _check_record
from psychneuro.w03.vault import digest, verify_serialized

from .rights import Action, DatasetRights, Principal, decide


class Envelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["w04-envelope-1"] = "w04-envelope-1"
    dataset_id: Literal["w03-original-synthetic"] = "w03-original-synthetic"
    rights_decision: Literal["internal-aggregate-only"] = "internal-aggregate-only"
    run_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    provenance_root: str = Field(pattern=r"^[a-f0-9]{64}$")
    payload: dict[str, Any]
    receipt_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


def export_record(record: dict[str, Any], rights: DatasetRights, actor: Principal) -> Envelope:
    verdict = decide(rights, actor, Action.EXPORT_AGGREGATE)
    if not verdict.allowed or rights.dataset_id != "w03-original-synthetic":
        raise PermissionError(verdict.reason)
    _check_record(record)
    fields = {"schema_version": "w04-envelope-1", "dataset_id": rights.dataset_id,
              "rights_decision": "internal-aggregate-only", "run_id": record["run_id"],
              "provenance_root": record["provenance_root"], "payload": record}
    return Envelope.model_validate({**fields, "receipt_sha256": digest(fields)})


def verify_envelope(envelope: Envelope, *, trusted_root: str | None = None) -> dict[str, Any]:
    fields = envelope.model_dump(mode="json", exclude={"receipt_sha256"})
    if digest(fields) != envelope.receipt_sha256:
        raise ValueError("receipt digest mismatch")
    record = envelope.payload
    if set(record) != {"run_id", "provenance_root", "nodes", "rights", "result"}:
        raise ValueError("unapproved report fields")
    if record["run_id"] != envelope.run_id or record["provenance_root"] != envelope.provenance_root:
        raise ValueError("payload identity mismatch")
    if trusted_root is not None and envelope.provenance_root != trusted_root:
        raise ValueError("does not match externally trusted root")
    verify_serialized(record["nodes"], record["provenance_root"])
    _check_record(record)
    return record
