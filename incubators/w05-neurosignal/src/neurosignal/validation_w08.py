"""W08 independent deterministic DSP/PSD reference comparisons and regression gates.

No EEG-human inference; source is a seeded analytic, CC0 synthetic generator.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import numpy as np
from scipy.signal import welch

from .dsp import CausalFIR, direct_fir_oracle, fir_lowpass
from .spectral_w06 import StreamingWelch


@dataclass(frozen=True)
class ValidationEvidence:
    schema_version: str
    seed: int
    sample_rate_hz: float
    samples: int
    chunk_size: int
    waveform_sha256: str
    dominant_hz: float
    spectral_relative_l2: float
    fir_max_abs_error_volts: float
    null_max_power_v2_per_hz: float
    accepted: bool

    def json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, allow_nan=False)


def validate_synthetic(*, seed: int = 42, samples: int = 4096,
                       chunk_size: int = 127, max_psd_relative_l2: float = 1e-10,
                       max_fir_error_volts: float = 1e-16) -> ValidationEvidence:
    """Compare independently implemented streaming estimators to SciPy/shift-add.

    Frequency is bin-exact (10 Hz at 256 Hz fs / 256-sample Welch window).
    Rejection thresholds are numeric regression bounds, not clinical cutoffs.
    """
    if not 512 <= samples <= 131072 or not 1 <= chunk_size <= 8192:
        raise ValueError("samples/chunk budget out of bounds")
    if seed < 0 or not np.isfinite(max_psd_relative_l2) or not np.isfinite(max_fir_error_volts):
        raise ValueError("invalid comparison configuration")
    if max_psd_relative_l2 <= 0 or max_fir_error_volts <= 0:
        raise ValueError("positive regression tolerances required")
    fs = 256.
    t = np.arange(samples, dtype=np.float64)/fs
    rng = np.random.default_rng(seed)
    data = (12e-6*np.sin(2*np.pi*10*t)+rng.normal(0, .02e-6, samples))[None, :]
    source_digest = hashlib.sha256(data.tobytes(order="C")).hexdigest()
    streaming = StreamingWelch(fs, 1, 256)
    taps = fir_lowpass(fs, 40, 31)
    filter_ = CausalFIR(taps, 1)
    output = []
    for start in range(0, samples, chunk_size):
        block = data[:, start:start+chunk_size]
        streaming.update(block, start)
        output.append(filter_.process(block, start))
    freqs, density = streaming.result()
    ref_freqs, reference = welch(data, fs=fs, nperseg=256, noverlap=128,
                                  detrend="constant", axis=-1, scaling="density")
    if not np.array_equal(freqs, ref_freqs):
        raise AssertionError("frequency grids differ")
    denominator = np.linalg.norm(reference)
    relative = float(np.linalg.norm(density-reference)/max(denominator, np.finfo(float).tiny))
    y = np.concatenate(output, axis=1)
    oracle = direct_fir_oracle(taps, data)
    discrepancy = float(np.max(np.abs(y-oracle)))
    # Truly zero-valued signal should not develop spectral energy.
    null = StreamingWelch(fs, 1, 256)
    null.update(np.zeros((1, 512)), 0)
    null_power = float(np.max(null.result()[1]))
    peak = float(freqs[np.argmax(density[0])])
    return ValidationEvidence(
        "1.0", seed, fs, samples, chunk_size, source_digest, peak,
        relative, discrepancy, null_power,
        bool(peak == 10 and relative <= max_psd_relative_l2
             and discrepancy <= max_fir_error_volts and null_power == 0),
    )
