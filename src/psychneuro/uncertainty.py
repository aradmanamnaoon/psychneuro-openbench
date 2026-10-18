"""Bounded descriptive uncertainty across preregistered synthetic seed repeats.

One replicate = one independently seeded synthetic cohort, not an individual
trial or participant. Intervals are conditional on the toy generator only.
"""
from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class ScoreSummary:
    n_repeats: int
    mean: float | None
    sample_sd: float | None
    standard_error: float | None
    ci95_low: float | None
    ci95_high: float | None
    ci_method: str | None
    interpretation: str


def _t975_approx(df: int) -> float:
    """Cornish-Fisher t(.975, df) approximation, not an exact quantile."""
    if df < 4:
        raise ValueError("CI requires at least five independent repeats")
    z = 1.959963984540054
    v = float(df)
    return (
        z
        + (z**3 + z) / (4 * v)
        + (5 * z**5 + 16 * z**3 + 3 * z) / (96 * v**2)
        + (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * v**3)
    )


def summarize_scores(scores: Sequence[float]) -> ScoreSummary:
    """Return descriptive mean/SE and optional *nominal* t interval.

    The standard error is SD/sqrt(n), using replicate-level variability.
    A 95% interval is reported only for >=5 complete, finite valid repeats.
    Assumptions (independent seeds, approximately Gaussian repeat means) are
    NOT proven. No p-value, efficacy or real-population claim is warranted.
    """
    if any(
        type(score) not in (int, float)
        or not math.isfinite(score)
        or not (0.0 <= score <= 1.0)
        for score in scores
    ):
        raise ValueError("repeat scores must be finite numeric values within [0, 1]")
    n = len(scores)
    note = (
        "Descriptive synthetic-seed variability only; not a participant-level "
        "CI, significance test or evidence of population generalization."
    )
    if n == 0:
        return ScoreSummary(0, None, None, None, None, None, None, note)
    mean = statistics.fmean(scores)
    if n == 1:
        return ScoreSummary(n, mean, None, None, None, None, None, note)
    sd = statistics.stdev(scores)
    se = sd / math.sqrt(n)
    if n < 5:
        return ScoreSummary(n, mean, sd, se, None, None, None, note)
    radius = _t975_approx(n - 1) * se
    # Do not clip the symmetric t interval; clipping changes its interpretation.
    return ScoreSummary(
        n, mean, sd, se, mean - radius, mean + radius,
        "nominal_95pct_student_t_cornish_fisher_approximation", note,
    )


def summary_dict(scores: Sequence[float]) -> dict[str, object]:
    return asdict(summarize_scores(scores))
