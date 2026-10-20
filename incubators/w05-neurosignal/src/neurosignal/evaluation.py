"""P2 spectral plugin API and independent frequency-domain sanity checks."""
from __future__ import annotations

from typing import Protocol

import numpy as np
from scipy.signal import stft, welch

from .contracts import Chunk, SpectralResult


class SpectralPlugin(Protocol):
    name: str
    def evaluate(self, chunk: Chunk) -> SpectralResult: ...


class WelchPSD:
    name = "welch_v1"

    def __init__(self, nperseg: int = 256, overlap: int | None = None):
        if nperseg < 16 or nperseg > 32768:
            raise ValueError("invalid window size")
        if overlap is not None and not (0 <= overlap < nperseg):
            raise ValueError("invalid overlap")
        self.nperseg = nperseg
        self.overlap = overlap

    def evaluate(self, chunk: Chunk) -> SpectralResult:
        x = chunk.as_array()
        if x.shape[1] < self.nperseg:
            raise ValueError("insufficient samples: no implicit window shortening")
        ov = self.overlap if self.overlap is not None else self.nperseg // 2
        hz, power = welch(x, fs=chunk.sample_rate_hz, nperseg=self.nperseg,
                          noverlap=ov, axis=-1, detrend="constant", scaling="density")
        segments = 1 + (x.shape[1] - self.nperseg) // (self.nperseg - ov)
        return SpectralResult(metric=self.name, frequencies_hz=hz.tolist(),
                              power_v2_per_hz=power.tolist(), n_segments=segments)


class ShortTimeFourier:
    name = "stft_v1"

    def __init__(self, nperseg: int = 128):
        if not 16 <= nperseg <= 32768:
            raise ValueError("invalid STFT length")
        self.nperseg = nperseg

    def evaluate(self, chunk: Chunk) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if chunk.stop - chunk.start < self.nperseg:
            raise ValueError("insufficient samples")
        f, t, z = stft(chunk.as_array(), fs=chunk.sample_rate_hz, nperseg=self.nperseg,
                       noverlap=self.nperseg // 2, boundary=None, padded=False, axis=-1)
        return f, t + chunk.start / chunk.sample_rate_hz, z


def rectangular_periodogram_oracle(signal_volts: np.ndarray, rate: float) -> tuple[np.ndarray, np.ndarray]:
    """Independent single-window FFT (not a Welch reference with overlapping Hann windows)."""
    x = np.asarray(signal_volts, dtype=np.float64)
    if x.ndim != 1 or x.size < 2 or rate <= 0:
        raise ValueError("invalid oracle input")
    x = x - np.mean(x)
    spectrum = np.fft.rfft(x)
    density = (np.abs(spectrum) ** 2) / (rate * len(x))
    if len(x) % 2 == 0:
        density[1:-1] *= 2.0
    else:
        density[1:] *= 2.0
    return np.fft.rfftfreq(len(x), 1 / rate), density
