"""P2 causal preprocessing graph; rights and deterministic transform lineage."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from pydantic import Field, model_validator

from .contracts import Chunk, StrictModel, TransformTrace, canonical_sha
from .dsp import CausalFIR, fir_lowpass


class StepSpec(StrictModel):
    op: Literal["average_reference", "amplitude_qc", "lowpass_fir", "scale"]
    threshold_uv: float | None = Field(default=None, gt=0)
    cutoff_hz: float | None = Field(default=None, gt=0)
    taps: int = Field(default=65, ge=3, le=4097)
    multiplier: float | None = None

    @model_validator(mode="after")
    def valid(self) -> StepSpec:
        if self.op == "amplitude_qc" and self.threshold_uv is None:
            raise ValueError("threshold_uv is required")
        if self.op == "lowpass_fir" and self.cutoff_hz is None:
            raise ValueError("cutoff_hz is required")
        if self.op == "scale" and (self.multiplier is None or not np.isfinite(self.multiplier)):
            raise ValueError("finite multiplier required")
        return self


class GraphSpec(StrictModel):
    version: Literal["1.0"] = "1.0"
    seed: int = 42
    steps: tuple[StepSpec, ...] = ()


@dataclass
class PreprocessingGraph:
    spec: GraphSpec
    sample_rate_hz: float
    channels: int
    _filters: dict[int, CausalFIR] = field(default_factory=dict, init=False)
    next_sample: int = 0

    def __post_init__(self) -> None:
        if self.channels < 1 or self.sample_rate_hz <= 0:
            raise ValueError("invalid graph shape")
        for i, step in enumerate(self.spec.steps):
            if step.op == "lowpass_fir":
                self._filters[i] = CausalFIR(
                    fir_lowpass(self.sample_rate_hz, float(step.cutoff_hz), step.taps),
                    self.channels)

    def process(self, chunk: Chunk) -> tuple[Chunk, tuple[TransformTrace, ...]]:
        if chunk.sample_rate_hz != self.sample_rate_hz or len(chunk.channel_names) != self.channels:
            raise ValueError("rate/channel mismatch")
        if chunk.start != self.next_sample:
            raise ValueError("chunk overlap/gap/out of order")
        arr = chunk.as_array()
        traces: list[TransformTrace] = []
        for i, step in enumerate(self.spec.steps):
            before = canonical_sha(arr.tolist())
            flags: tuple[str, ...] = ()
            if step.op == "average_reference":
                if self.channels < 2:
                    raise ValueError("average reference requires >=2 channels")
                arr = arr - np.mean(arr, axis=0, keepdims=True)
            elif step.op == "amplitude_qc":
                flagged = np.where(np.max(np.abs(arr), axis=1) > float(step.threshold_uv) * 1e-6)[0]
                flags = tuple(f"amplitude_exceeded:{chunk.channel_names[j]}" for j in flagged)
                # Flag only; never quietly mutate/remove samples.
            elif step.op == "lowpass_fir":
                arr = self._filters[i].process(arr, chunk.start)
            elif step.op == "scale":
                arr = arr * float(step.multiplier)
            traces.append(TransformTrace(op=step.op, config_sha256=canonical_sha(step.model_dump()),
                                         input_sha256=before,
                                         output_sha256=canonical_sha(arr.tolist()), qc_flags=flags))
        self.next_sample = chunk.stop
        return Chunk(recording_id=chunk.recording_id, start=chunk.start,
                     sample_rate_hz=chunk.sample_rate_hz, channel_names=chunk.channel_names,
                     volts=arr.tolist()), tuple(traces)
