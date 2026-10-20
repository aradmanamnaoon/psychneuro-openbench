"""W06: bounded-memory streaming Welch and vectorized multitaper density in V²/Hz.

Only complete fixed-length windows are analyzed. Shared overlap samples are
buffered; partial trailing windows are excluded, matching scipy.signal.welch
with identical window, detrend, overlap and average conventions.
"""
from __future__ import annotations

import numpy as np
from scipy.signal.windows import dpss


class StreamingWelch:
    def __init__(self, sample_rate_hz: float, channels: int, nperseg: int = 256,
                 overlap: int | None = None):
        self.fs = float(sample_rate_hz)
        self.channels = channels
        self.n = nperseg
        self.overlap = nperseg // 2 if overlap is None else overlap
        if not np.isfinite(self.fs) or self.fs <= 0 or channels < 1 or nperseg < 16:
            raise ValueError("invalid clock, channels or segment length")
        if not 0 <= self.overlap < self.n:
            raise ValueError("invalid segment overlap")
        self.hop = self.n - self.overlap
        self.window = np.hanning(self.n + 1)[:-1]
        self._tail = np.empty((channels, 0), dtype=np.float64)
        self._sum = np.zeros((channels, self.n // 2 + 1), dtype=np.float64)
        self.segments = 0
        self.next_sample = 0

    def update(self, block: np.ndarray, start: int) -> None:
        x = np.asarray(block, dtype=np.float64)
        if x.ndim != 2 or x.shape[0] != self.channels or x.shape[1] < 1:
            raise ValueError("expected nonempty channels x samples")
        if start != self.next_sample or not np.isfinite(x).all():
            raise ValueError("discontinuous or nonfinite samples")
        self.next_sample += x.shape[1]
        pending = np.concatenate((self._tail, x), axis=1)
        # At most one input block plus one incomplete window is resident.
        count = 0 if pending.shape[1] < self.n else 1 + (pending.shape[1]-self.n)//self.hop
        if count:
            offsets = np.arange(count) * self.hop
            for at in offsets:
                frame = pending[:, at:at+self.n]
                centered = (frame - frame.mean(axis=1, keepdims=True)) * self.window
                transformed = np.fft.rfft(centered, axis=1)
                density = np.abs(transformed)**2 / (self.fs * np.sum(self.window**2))
                if self.n % 2 == 0:
                    density[:, 1:-1] *= 2
                else:
                    density[:, 1:] *= 2
                self._sum += density
            self.segments += count
            pending = pending[:, count*self.hop:]
        self._tail = pending.copy()
        if self._tail.shape[1] >= self.n:
            raise AssertionError("unbounded tail")

    def result(self) -> tuple[np.ndarray, np.ndarray]:
        if not self.segments:
            raise ValueError("not enough complete windows")
        return np.fft.rfftfreq(self.n, 1/self.fs), self._sum/self.segments


def multitaper_density(data: np.ndarray, sample_rate_hz: float,
                       nw: float = 3.0, tapers: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """Equal-weight DPSS multitaper, one-sided power density, mean-detrended.

    No adaptive eigenspectrum weighting, jackknife confidence bands or
    local line-component rejection are claimed. Output (channels, frequencies).
    """
    x = np.asarray(data, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] < 16 or not np.isfinite(x).all():
        raise ValueError("finite channels x samples required")
    if not np.isfinite(sample_rate_hz) or sample_rate_hz <= 0 or not 1 < nw < x.shape[1]/2:
        raise ValueError("invalid sample rate or time bandwidth")
    if not 1 <= tapers <= int(2*nw)-1:
        raise ValueError("taper count exceeds concentration rule")
    windows = dpss(x.shape[1], nw, Kmax=tapers, sym=False)
    centered = x-x.mean(axis=1, keepdims=True)
    transformed = np.fft.rfft(centered[:,None,:]*windows[None,:,:], axis=-1)
    density = np.abs(transformed)**2 / (sample_rate_hz*np.sum(windows**2, axis=1)[None,:,None])
    if x.shape[1] % 2 == 0:
        density[...,1:-1] *= 2
    else:
        density[...,1:] *= 2
    return np.fft.rfftfreq(x.shape[1], 1/sample_rate_hz), density.mean(axis=1)
