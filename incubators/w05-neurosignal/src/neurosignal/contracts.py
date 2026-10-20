"""Versioned, fail-closed data, event and lineage contracts for synthetic/research EEG."""
from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any, Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SignalUnit(StrEnum):
    VOLT = "V"
    MICROVOLT = "uV"

    @property
    def to_volts(self) -> float:
        return 1.0 if self is SignalUnit.VOLT else 1e-6


class Channel(StrictModel):
    name: str = Field(min_length=1, max_length=128)
    kind: Literal["eeg", "eog", "ecg", "misc"] = "eeg"
    native_unit: SignalUnit = SignalUnit.VOLT
    bad: bool = False


class Event(StrictModel):
    sample: int = Field(ge=0)
    code: str = Field(min_length=1, max_length=64)
    duration_samples: int = Field(default=0, ge=0)


class Rights(StrictModel):
    source_uri: str = Field(min_length=1, max_length=2048)
    data_license: str = Field(min_length=1, max_length=128)
    permission_verified: bool = False
    is_synthetic: bool = False
    allow_analysis: bool = False
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def gate(self) -> Rights:
        if not self.is_synthetic and not (self.permission_verified and self.allow_analysis):
            raise ValueError("real data denied: verified source/license and permission required")
        if self.is_synthetic and not self.allow_analysis:
            raise ValueError("synthetic fixture must permit analysis")
        return self


class Recording(StrictModel):
    contract_version: Literal["1.0"] = "1.0"
    recording_id: str = Field(min_length=1, max_length=128)
    sample_rate_hz: float = Field(gt=0, le=100000)
    samples: int = Field(gt=0)
    channels: tuple[Channel, ...] = Field(min_length=1)
    events: tuple[Event, ...] = ()
    rights: Rights
    clock_start_ns: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_metadata(self) -> Recording:
        if len({c.name for c in self.channels}) != len(self.channels):
            raise ValueError("duplicate channels")
        if any(e.sample >= self.samples or e.sample + e.duration_samples > self.samples for e in self.events):
            raise ValueError("event out of bounds")
        return self


class Chunk(StrictModel):
    contract_version: Literal["1.0"] = "1.0"
    recording_id: str
    start: int = Field(ge=0)
    sample_rate_hz: float = Field(gt=0)
    channel_names: tuple[str, ...]
    volts: list[list[float]]

    @model_validator(mode="after")
    def validate_shape(self) -> Chunk:
        if len(self.volts) != len(self.channel_names) or not self.volts:
            raise ValueError("channel mismatch")
        n = len(self.volts[0])
        if n == 0 or any(len(x) != n for x in self.volts):
            raise ValueError("invalid samples")
        if not all(np.isfinite(v) for row in self.volts for v in row):
            raise ValueError("nonfinite signal")
        return self

    @property
    def stop(self) -> int:
        return self.start + len(self.volts[0])

    def as_array(self) -> np.ndarray:
        return np.asarray(self.volts, dtype=np.float64)


class TransformTrace(StrictModel):
    op: str
    config_sha256: str
    input_sha256: str
    output_sha256: str
    qc_flags: tuple[str, ...] = ()


class SpectralResult(StrictModel):
    metric: str
    frequencies_hz: list[float]
    power_v2_per_hz: list[list[float]]
    n_segments: int = Field(gt=0)
    qc_flags: tuple[str, ...] = ()


class LeakageDecision(StrictModel):
    accepted: bool
    causes: tuple[str, ...]
    train_groups: int = Field(ge=0)
    test_groups: int = Field(ge=0)


def canonical_sha(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def bytes_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
