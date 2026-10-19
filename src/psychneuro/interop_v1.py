"""Synthetic P1/P13/P25 reference contract: rights, split, tamper-evidence."""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any
from psychneuro.rights_v1 import Action, DatasetGrant, evaluate

def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def digest(obj: Any) -> str:
    return sha256(canonical(obj)).hexdigest()

@dataclass(frozen=True)
class Split:
    train: tuple[str, ...]
    test: tuple[str, ...]

def validate_split(split: Split) -> None:
    if not split.train or not split.test:
        raise ValueError("empty partition")
    if len(set(split.train)) != len(split.train) or len(set(split.test)) != len(split.test):
        raise ValueError("duplicate group")
    if set(split.train) & set(split.test):
        raise ValueError("participant leakage")

def produce_artifact(grant: DatasetGrant, split: Split, metric: float, seed: int) -> dict[str, Any]:
    decision = evaluate(grant, Action.ANALYZE)
    if not decision.allowed:
        raise PermissionError(decision.reason)
    validate_split(split)
    if not (0 <= metric <= 1):
        raise ValueError("metric out of range")
    event = {"version": "interop.v1", "dataset": grant.dataset_id,
             "source_sha256": grant.source_sha256, "license_id": grant.license_id,
             "action": "analyze", "seed": seed, "split": asdict(split),
             "accuracy": metric, "rights_decision": decision.reason}
    return {"event": event, "sha256": digest(event)}

def verify_artifact(bundle: dict[str, Any]) -> bool:
    return (isinstance(bundle.get("event"), dict) and isinstance(bundle.get("sha256"), str)
            and digest(bundle["event"]) == bundle["sha256"])
