"""W04 synthetic-only interoperability contract (not an authentication system)."""
from dataclasses import dataclass
from hashlib import sha256
import json
import math
import re
from typing import Any
from psychneuro.rights_v1 import Action, DatasetGrant, evaluate

_SHA256 = re.compile(r"[0-9a-f]{64}\\Z")
_MAX_EVENT_BYTES = 65_536
_EVENT_FIELDS = frozenset({"version", "dataset", "source_sha256", "license_id",
                           "action", "seed", "split", "accuracy", "rights_decision"})

def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def digest(obj: Any) -> str:
    return sha256(canonical(obj)).hexdigest()

@dataclass(frozen=True)
class Split:
    train: tuple[str, ...]
    test: tuple[str, ...]

def validate_split(split: Split) -> None:
    if not split.train or not split.test:
        raise ValueError("empty partition")
    if any(not isinstance(group, str) or not group or len(group) > 256
           for group in (*split.train, *split.test)):
        raise ValueError("invalid group identifier")
    if len(set(split.train)) != len(split.train) or len(set(split.test)) != len(split.test):
        raise ValueError("duplicate group")
    if set(split.train) & set(split.test):
        raise ValueError("participant leakage")


def _check_event(event: object) -> bool:
    """Shape validation only; no replay-time authority or dataset attestation."""
    if not isinstance(event, dict) or set(event) != _EVENT_FIELDS:
        return False
    if event["version"] != "interop.v1" or event["action"] != "analyze":
        return False
    if not isinstance(event["dataset"], str) or not 1 <= len(event["dataset"]) <= 256:
        return False
    if not isinstance(event["license_id"], str) or not 1 <= len(event["license_id"]) <= 256:
        return False
    if not isinstance(event["source_sha256"], str) or not _SHA256.fullmatch(event["source_sha256"]):
        return False
    if type(event["seed"]) is not int or not 0 <= event["seed"] < 2**64:
        return False
    if type(event["accuracy"]) not in (float, int) or not math.isfinite(event["accuracy"]):
        return False
    if not 0.0 <= event["accuracy"] <= 1.0:
        return False
    if event["rights_decision"] != "grant verified for specific action":
        return False
    split = event["split"]
    if not isinstance(split, dict) or set(split) != {"train", "test"}:
        return False
    if not all(isinstance(split[k], list) and len(split[k]) <= 100_000 for k in ("train", "test")):
        return False
    try:
        validate_split(Split(tuple(split["train"]), tuple(split["test"])))
    except (TypeError, ValueError):
        return False
    return True

def produce_artifact(grant: DatasetGrant, split: Split, metric: float, seed: int) -> dict[str, Any]:
    decision = evaluate(grant, Action.ANALYZE)
    if not decision.allowed:
        raise PermissionError(decision.reason)
    validate_split(split)
    if type(metric) not in (float, int) or not math.isfinite(metric) or not 0 <= metric <= 1:
        raise ValueError("metric out of range")
    if type(seed) is not int or not 0 <= seed < 2**64:
        raise ValueError("seed out of range")
    event = {"version": "interop.v1", "dataset": grant.dataset_id,
             "source_sha256": grant.source_sha256, "license_id": grant.license_id,
             "action": "analyze", "seed": seed,
             "split": {"train": list(split.train), "test": list(split.test)},
             "accuracy": metric, "rights_decision": decision.reason}
    if not _check_event(json.loads(canonical(event))):
        raise ValueError("invalid interoperability event")
    if len(canonical(event)) > _MAX_EVENT_BYTES:
        raise ValueError("interoperability event exceeds size limit")
    return {"event": event, "sha256": digest(event)}

def verify_artifact(bundle: object, *, expected_sha256: str | None = None) -> bool:
    """Validate shape and bytes. Externally pin a digest for meaningful integrity.

    A caller-provided rights boolean/digest never proves legal authorization,
    metric authenticity, consent, or revocation status at replay time.
    """
    if not isinstance(bundle, dict) or set(bundle) != {"event", "sha256"}:
        return False
    event, provided = bundle["event"], bundle["sha256"]
    if not isinstance(provided, str) or not _SHA256.fullmatch(provided):
        return False
    if expected_sha256 is not None and (not isinstance(expected_sha256, str)
                                        or not _SHA256.fullmatch(expected_sha256)
                                        or provided != expected_sha256):
        return False
    if not _check_event(event):
        return False
    try:
        blob = canonical(event)
    except (TypeError, ValueError, OverflowError):
        return False
    return len(blob) <= _MAX_EVENT_BYTES and sha256(blob).hexdigest() == provided
