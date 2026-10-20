"""W07 synthetic EEG artifact QC and event-locked ERP, in physical volts.

Thresholds are channel-wise peak absolute voltage and peak-to-peak amplitude.
Epochs are rejected as a whole when any channel fails; boundary epochs omitted.
No ocular/muscle classification and no clinical decision support.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ERPResult:
    event_count: int
    retained: int
    rejected: int
    out_of_bounds: int
    time_seconds: np.ndarray
    mean_volts: np.ndarray
    sem_volts: np.ndarray
    rejected_event_indices: tuple[int, ...]


def artifact_mask(volts: np.ndarray, *, absolute_uv: float = 120,
                  peak_to_peak_uv: float = 180) -> np.ndarray:
    """Return channel x epoch boolean mask of rejected epochs.

    Requires (epochs, channels, samples); no automatic interpolation.
    """
    x = np.asarray(volts, dtype=np.float64)
    if x.ndim != 3 or not all(x.shape) or not np.isfinite(x).all():
        raise ValueError("finite epochs x channels x samples required")
    if not 0 < absolute_uv < 1e6 or not 0 < peak_to_peak_uv < 1e6:
        raise ValueError("invalid artifact threshold in microvolts")
    peak = np.max(np.abs(x), axis=-1)
    spread = np.ptp(x, axis=-1)
    return (peak > absolute_uv * 1e-6) | (spread > peak_to_peak_uv * 1e-6)


def event_locked_erp(volts: np.ndarray, events: list[int], fs: float, *,
                     pre_samples: int, post_samples: int,
                     absolute_uv: float = 120,
                     peak_to_peak_uv: float = 180) -> ERPResult:
    """Align events at integer sample zero with [event-pre,event+post) epochs."""
    x = np.asarray(volts, dtype=np.float64)
    if x.ndim != 2 or not all(x.shape) or not np.isfinite(x).all():
        raise ValueError("finite channels x samples required")
    if not np.isfinite(fs) or fs <= 0 or pre_samples < 1 or post_samples < 1:
        raise ValueError("invalid sample clock or window")
    if len(set(events)) != len(events) or any(type(e) is not int for e in events):
        raise ValueError("unique integer event indices required")
    valid = [(i, e) for i, e in enumerate(events)
             if e - pre_samples >= 0 and e + post_samples <= x.shape[1]]
    out_of_bounds = len(events) - len(valid)
    length = pre_samples + post_samples
    rejected_ids: list[int] = []
    kept: list[np.ndarray] = []
    for i, event in valid:
        epoch = x[:, event-pre_samples:event+post_samples]
        if artifact_mask(epoch[None, :, :], absolute_uv=absolute_uv,
                         peak_to_peak_uv=peak_to_peak_uv).any():
            rejected_ids.append(i)
        else:
            kept.append(epoch)
    if not kept:
        raise ValueError("no accepted epochs after QC; do not generate an ERP")
    stack = np.stack(kept, axis=0)
    mean = stack.mean(axis=0)
    sem = (stack.std(axis=0, ddof=1) / np.sqrt(len(kept))
           if len(kept) >= 2 else np.full_like(mean, np.nan))
    return ERPResult(event_count=len(events), retained=len(kept),
                     rejected=len(rejected_ids), out_of_bounds=out_of_bounds,
                     time_seconds=np.arange(-pre_samples, post_samples)/fs,
                     mean_volts=mean, sem_volts=sem,
                     rejected_event_indices=tuple(rejected_ids))


def minmax_downsample(volts: np.ndarray, max_bins: int = 256) -> np.ndarray:
    """Preserve extrema for visual trace; max 2*max_bins output points."""
    x = np.asarray(volts, dtype=np.float64)
    if x.ndim != 1 or not x.size or not np.isfinite(x).all():
        raise ValueError("finite single-channel trace required")
    if not 1 <= max_bins <= 8192:
        raise ValueError("invalid display bin budget")
    pieces = np.array_split(x, min(max_bins, len(x)))
    return np.asarray([v for segment in pieces for v in (segment.min(), segment.max())])
