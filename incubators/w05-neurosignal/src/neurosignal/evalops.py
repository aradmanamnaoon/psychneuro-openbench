"""P14: typed benchmark DSL, participant/temporal isolation and group confidence intervals."""
from __future__ import annotations

from collections import defaultdict
from typing import Literal

import numpy as np
from pydantic import Field, model_validator

from .contracts import LeakageDecision, StrictModel


class Segment(StrictModel):
    id: str = Field(min_length=1)
    group_id: str = Field(min_length=1)
    recording_id: str = Field(min_length=1)
    start: int = Field(ge=0)
    stop: int = Field(gt=0)
    split: Literal["train", "validation", "test"]
    score: float = Field(ge=0, le=1)
    stratum: str = "all"

    @model_validator(mode="after")
    def ordered(self) -> Segment:
        if self.stop <= self.start:
            raise ValueError("empty or reversed segment")
        return self


class SliceDefinition(StrictModel):
    name: str = Field(min_length=1)
    stratum: str = Field(min_length=1)
    min_groups: int = Field(default=3, ge=2)


class BenchmarkSpec(StrictModel):
    version: Literal["1.0"] = "1.0"
    outcome: Literal["bounded_accuracy", "bounded_detection_rate"] = "bounded_accuracy"
    unit_of_independence: Literal["group_id"] = "group_id"
    seed: int = 42
    bootstrap_reps: int = Field(default=500, ge=100, le=20000)
    confidence: float = Field(default=0.95, gt=0.5, lt=1)
    slices: tuple[SliceDefinition, ...] = (SliceDefinition(name="overall", stratum="all"),)


class CI(StrictModel):
    slice_name: str
    mean: float
    lower: float
    upper: float
    n_groups: int
    repetitions: int


def preflight(rows: list[Segment]) -> LeakageDecision:
    causes: list[str] = []
    if not rows:
        causes.append("empty benchmark")
    if len(set(x.id for x in rows)) != len(rows):
        causes.append("duplicate segment id")
    split_by_group: dict[str, set[str]] = defaultdict(set)
    by_recording: dict[str, list[Segment]] = defaultdict(list)
    for row in rows:
        split_by_group[row.group_id].add(row.split)
        by_recording[row.recording_id].append(row)
    if any(len(parts) > 1 for parts in split_by_group.values()):
        causes.append("group split contamination")
    for segments in by_recording.values():
        sorted_segments = sorted(segments, key=lambda s: s.start)
        for i, current in enumerate(sorted_segments):
            for nxt in sorted_segments[i + 1:]:
                if nxt.start >= current.stop:
                    break
                if current.split != nxt.split:
                    causes.append("temporal window overlap across splits")
                    break
    train = {x.group_id for x in rows if x.split == "train"}
    test = {x.group_id for x in rows if x.split == "test"}
    if len(train) < 2 or len(test) < 2:
        causes.append("fewer than two independent groups in train/test")
    return LeakageDecision(accepted=not causes, causes=tuple(dict.fromkeys(causes)),
                           train_groups=len(train), test_groups=len(test))


def bootstrap_ci(spec: BenchmarkSpec, rows: list[Segment]) -> list[CI]:
    verdict = preflight(rows)
    if not verdict.accepted:
        raise ValueError("leakage preflight failed: " + "; ".join(verdict.causes))
    out: list[CI] = []
    for index, definition in enumerate(spec.slices):
        subset = [r for r in rows if r.split == "test" and
                  (definition.stratum == "all" or r.stratum == definition.stratum)]
        grouped: dict[str, list[float]] = defaultdict(list)
        for row in subset:
            grouped[row.group_id].append(row.score)
        if len(grouped) < definition.min_groups:
            raise ValueError(f"slice {definition.name}: insufficient independent groups")
        means = np.array([np.mean(vals) for _, vals in sorted(grouped.items())])
        rng = np.random.default_rng(spec.seed + index)
        draws = rng.integers(0, len(means), (spec.bootstrap_reps, len(means)))
        reps = np.mean(means[draws], axis=1)
        alpha = 1 - spec.confidence
        low, high = np.quantile(reps, [alpha / 2, 1 - alpha / 2])
        out.append(CI(slice_name=definition.name, mean=float(means.mean()),
                      lower=float(low), upper=float(high), n_groups=len(means),
                      repetitions=spec.bootstrap_reps))
    return out
