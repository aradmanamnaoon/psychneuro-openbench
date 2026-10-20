"""W06 paired, group-stratified bootstrap; independent groups are resampling units."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PairedCI:
    mean_difference: float
    lower: float
    upper: float
    groups: int
    strata: int
    resamples: int


def paired_stratified_ci(left: dict[str, tuple[str, float]],
                         right: dict[str, tuple[str, float]], *,
                         seed: int = 42, resamples: int = 1000,
                         confidence: float = 0.95) -> PairedCI:
    """Paired deltas mean(left-right); bootstrap independently within each stratum.

    Each key is an independent subject/group, never an overlapping epoch.
    Stratum membership must be identical across paired runs. Estimand is an
    equal-group pooled difference, preserving observed stratum proportions.
    """
    if not left or left.keys() != right.keys():
        raise ValueError("paired groups must match exactly")
    if resamples < 100 or not 0.5 < confidence < 1:
        raise ValueError("invalid bootstrap specification")
    strata: dict[str, list[float]] = defaultdict(list)
    for group in sorted(left):
        a_stratum, a = left[group]
        b_stratum, b = right[group]
        if not a_stratum or a_stratum != b_stratum:
            raise ValueError("paired stratum mismatch")
        if not np.isfinite(a) or not np.isfinite(b):
            raise ValueError("nonfinite paired outcome")
        strata[a_stratum].append(float(a-b))
    if any(len(vals) < 2 for vals in strata.values()):
        raise ValueError("at least two independent groups per stratum required")
    rng = np.random.default_rng(seed)
    samples = np.zeros(resamples, dtype=np.float64)
    n = len(left)
    for group in sorted(strata):
        v = np.asarray(strata[group])
        draws = rng.integers(0, len(v), size=(resamples, len(v)))
        samples += v[draws].sum(axis=1)/n
    margin = (1-confidence)/2
    low, high = np.quantile(samples, [margin, 1-margin])
    return PairedCI(mean_difference=float(np.mean([left[k][1]-right[k][1] for k in left])),
                    lower=float(low), upper=float(high), groups=n,
                    strata=len(strata), resamples=resamples)
