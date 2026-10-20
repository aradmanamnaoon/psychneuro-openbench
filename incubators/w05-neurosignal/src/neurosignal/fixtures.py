"""Explicit synthetic only; deterministic multi-channel EEG with labeled events."""
from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np

from .contracts import Channel, Chunk, Event, Recording, Rights, bytes_sha


@dataclass
class SyntheticReader:
    """Seeded array is private to this in-memory synthetic reader; reads are bounded slices."""

    seed: int = 42
    samples: int = 8192
    sample_rate_hz: float = 256.0
    channels: int = 4

    def __post_init__(self) -> None:
        if self.samples < 64 or self.channels < 2 or self.sample_rate_hz <= 0:
            raise ValueError("invalid synthetic fixture dimensions")
        rng = np.random.default_rng(self.seed)
        t = np.arange(self.samples, dtype=np.float64) / self.sample_rate_hz
        # Known 10/20-Hz analytical components in volts, with independently seeded noise.
        self._data = np.stack([
            (20 + i) * 1e-6 * np.sin(2 * np.pi * 10 * t + i * np.pi / 4)
            + 3e-6 * np.sin(2 * np.pi * 20 * t)
            + rng.normal(0, 0.7e-6, self.samples)
            for i in range(self.channels)
        ])
        mem = io.BytesIO()
        np.save(mem, self._data, allow_pickle=False)
        sha = bytes_sha(mem.getvalue())
        self.metadata = Recording(
            recording_id=f"synthetic-{self.seed}-{self.samples}",
            sample_rate_hz=self.sample_rate_hz,
            samples=self.samples,
            channels=tuple(Channel(name=f"EEG{i + 1}") for i in range(self.channels)),
            events=tuple(Event(sample=i, code="fictional_stim") for i in range(256, self.samples, 512)),
            rights=Rights(source_uri="generated:seeded-sine", data_license="CC0-1.0-synthetic",
                          permission_verified=True, is_synthetic=True,
                          allow_analysis=True, content_sha256=sha),
        )

    def read(self, start: int, stop: int) -> Chunk:
        if not (0 <= start < stop <= self.metadata.samples):
            raise ValueError("unbounded or invalid chunk")
        arr = self._data[:, start:stop]
        return Chunk(recording_id=self.metadata.recording_id, start=start,
                     sample_rate_hz=self.sample_rate_hz,
                     channel_names=tuple(c.name for c in self.metadata.channels),
                     volts=arr.tolist())

    def close(self) -> None:
        pass

    def __enter__(self) -> SyntheticReader:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
