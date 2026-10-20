"""P26: exact-boundary streaming causal FIR, synchronization and independent oracle."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.signal import firwin, lfilter


def fir_lowpass(sample_rate_hz: float, cutoff_hz: float, taps: int = 65) -> np.ndarray:
    if not (0 < cutoff_hz < sample_rate_hz / 2) or taps < 3 or taps % 2 != 1:
        raise ValueError("cutoff must be below Nyquist; taps must be odd >=3")
    return np.asarray(firwin(taps, cutoff_hz, fs=sample_rate_hz), dtype=np.float64)


@dataclass
class CausalFIR:
    coefficients: np.ndarray
    channels: int
    _zi: np.ndarray = field(init=False, repr=False)
    next_sample: int = 0

    def __post_init__(self) -> None:
        self.coefficients = np.asarray(self.coefficients, dtype=np.float64)
        if (self.coefficients.ndim != 1 or len(self.coefficients) < 2 or self.channels < 1
                or not np.all(np.isfinite(self.coefficients))):
            raise ValueError("invalid FIR coefficients or channels")
        self._zi = np.zeros((self.channels, len(self.coefficients) - 1))

    def process(self, data: np.ndarray, start: int) -> np.ndarray:
        block = np.asarray(data, dtype=np.float64)
        if (block.ndim != 2 or block.shape[0] != self.channels or block.shape[1] == 0
                or not np.all(np.isfinite(block))):
            raise ValueError("invalid or nonfinite block")
        if start != self.next_sample:
            raise ValueError("clock discontinuity: duplicate, dropped or out-of-order block")
        out, self._zi = lfilter(self.coefficients, [1.0], block, axis=1, zi=self._zi)
        self.next_sample += block.shape[1]
        return np.asarray(out)

    def checkpoint(self) -> dict[str, object]:
        return {"version": 1, "next_sample": self.next_sample, "zi": self._zi.tolist(),
                "coefficients": self.coefficients.tolist(), "channels": self.channels}

    @classmethod
    def restore(cls, obj: dict[str, object]) -> CausalFIR:
        if obj.get("version") != 1:
            raise ValueError("unknown checkpoint schema")
        state = cls(np.asarray(obj["coefficients"], dtype=np.float64), int(obj["channels"]))
        zi = np.asarray(obj["zi"], dtype=np.float64)
        if zi.shape != state._zi.shape or not np.all(np.isfinite(zi)):
            raise ValueError("checkpoint shape or numeric corruption")
        state._zi = zi.copy()
        state.next_sample = int(obj["next_sample"])
        if state.next_sample < 0:
            raise ValueError("negative checkpoint position")
        return state


def synchronize_sample(clock_start_ns: int, event_timestamp_ns: int,
                       sample_rate_hz: float, max_error_samples: float = 0.25) -> int:
    """Align timestamps using integer ns origin; reject instead of silently interpolating."""
    if clock_start_ns < 0 or event_timestamp_ns < clock_start_ns or sample_rate_hz <= 0:
        raise ValueError("invalid clock origin, time, or sample rate")
    relative = (event_timestamp_ns - clock_start_ns) * sample_rate_hz / 1e9
    nearest = round(relative)
    if abs(relative - nearest) > max_error_samples:
        raise ValueError("event timestamp ambiguous relative to sample clock")
    return nearest


def direct_fir_oracle(coefficients: np.ndarray, signal: np.ndarray) -> np.ndarray:
    """Independent O(N*K) shift-and-add reference (not scipy.signal.lfilter)."""
    x = np.asarray(signal, dtype=np.float64)
    h = np.asarray(coefficients, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError("expect channels x samples")
    y = np.zeros_like(x)
    for lag, weight in enumerate(h):
        if lag >= x.shape[1]:
            break
        y[:, lag:] += float(weight) * x[:, :x.shape[1] - lag]
    return y
