"""W07 P14: recording-level QC disparity without pseudo-replicated epoch intervals."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import sqrt

import numpy as np


@dataclass(frozen=True)
class RecordingQC:
    recording: str
    dataset: str
    trials: int
    rejected: int
    rejection_rate: float
    wilson_low: float
    wilson_high: float


def _wilson(count: int, total: int, z: float = 1.95996398454) -> tuple[float, float]:
    if not 0 <= count <= total or total < 1:
        raise ValueError("invalid Bernoulli counts")
    proportion = count / total
    denom = 1 + z*z/total
    center = (proportion+z*z/(2*total))/denom
    spread = z*sqrt(proportion*(1-proportion)/total+z*z/(4*total*total))/denom
    return max(0., center-spread), min(1., center+spread)


def compare_recording_qc(records: list[tuple[str, str, int, int]], *,
                         thresholds: dict[str, float]) -> tuple[list[RecordingQC], float]:
    """Each record is (dataset, recording_id, trials, rejected).

    Computes per-recording rejection prevalence with descriptive Wilson bounds.
    Disparity is max-min recording rejection rate, NOT demographic fairness.
    Wilson intervals treat trials as independent; repeated epochs often violate
    that assumption. No recording-level inferential claim is allowed.
    """
    if not records:
        raise ValueError("recording QC rows required")
    if not thresholds or any(not np.isfinite(v) or not 0 <= v <= 1 for v in thresholds.values()):
        raise ValueError("invalid dataset QC thresholds")
    seen: set[tuple[str, str]] = set()
    out: list[RecordingQC] = []
    for dataset, identifier, total, rejected in records:
        key = (dataset, identifier)
        if not dataset or not identifier or key in seen or dataset not in thresholds:
            raise ValueError("invalid or duplicate recording/dataset")
        seen.add(key)
        if not 0 <= rejected <= total or total < 1:
            raise ValueError("invalid trial counts")
        rate = rejected / total
        low, high = _wilson(rejected, total)
        out.append(RecordingQC(identifier, dataset, total, rejected, rate, low, high))
    disparity = max(v.rejection_rate for v in out)-min(v.rejection_rate for v in out)
    return out, disparity


def deterministic_json_manifest(payload: dict[str, object]) -> bytes:
    """Stable strict JSON envelope; no data upload, no unredacted identifiers."""
    import hashlib
    import json

    body = json.dumps(payload, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(body).hexdigest()
    return json.dumps({"schema_version": "1.0", "sha256": digest,
                       "payload": payload}, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")
