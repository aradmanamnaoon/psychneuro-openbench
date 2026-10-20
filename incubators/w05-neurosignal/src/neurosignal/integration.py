"""P2 -> P26 -> P14 isolated, explicit synthetic-only interoperability proof."""
from __future__ import annotations

from typing import Any

import numpy as np

from .contracts import canonical_sha
from .dsp import direct_fir_oracle, fir_lowpass
from .evalops import BenchmarkSpec, Segment, bootstrap_ci
from .evaluation import WelchPSD
from .fixtures import SyntheticReader
from .pipeline import GraphSpec, PreprocessingGraph, StepSpec


def run_synthetic(seed: int = 42, samples: int = 4096, chunk_size: int = 333) -> dict[str, Any]:
    """Not human/clinical data; demo scores are invented constants for CI-contract exercise."""
    if not (0 <= seed < 2**32) or samples < 512 or not 1 <= chunk_size <= 2048:
        raise ValueError("invalid bounded synthetic experiment")
    with SyntheticReader(seed=seed, samples=samples) as reader:
        spec = GraphSpec(seed=seed, steps=(
            StepSpec(op="average_reference"),
            StepSpec(op="amplitude_qc", threshold_uv=100),
            StepSpec(op="lowpass_fir", cutoff_hz=45, taps=31)))
        graph = PreprocessingGraph(spec, reader.metadata.sample_rate_hz, len(reader.metadata.channels))
        pieces: list[np.ndarray] = []
        provenance: list[dict[str, object]] = []
        for start in range(0, samples, chunk_size):
            raw_chunk = reader.read(start, min(start + chunk_size, samples))
            transformed, trace = graph.process(raw_chunk)
            pieces.append(transformed.as_array())
            provenance.append({"start": start, "stop": transformed.stop,
                               "traces": [t.model_dump() for t in trace]})
        full = np.concatenate(pieces, axis=1)
        # Independent P26 numeric oracle, using raw full-length input and direct convolution.
        raw = reader.read(0, samples).as_array()
        referenced = raw - np.mean(raw, axis=0, keepdims=True)
        oracle = direct_fir_oracle(fir_lowpass(256.0, 45, 31), referenced)
        max_error = float(np.max(np.abs(full - oracle)))
        if max_error > 1e-17:
            raise AssertionError(f"P26 streaming FIR disagrees with independent oracle: {max_error}")
        last_chunk = reader.read(0, samples)
        from .contracts import Chunk
        transformed_chunk = Chunk(recording_id=last_chunk.recording_id, start=0,
                                  sample_rate_hz=last_chunk.sample_rate_hz,
                                  channel_names=last_chunk.channel_names, volts=full.tolist())
        spectrum = WelchPSD(nperseg=256).evaluate(transformed_chunk)
        # Artificial group-scored records, used ONLY to validate the P14 protocol implementation.
        segments = [Segment(id=f"g{i}", group_id=f"fictional-{i}",
                            recording_id=f"fictional-r{i}", start=0, stop=128,
                            split="train" if i < 4 else "test", score=0.55 + 0.03 * (i % 4))
                    for i in range(12)]
        ci = bootstrap_ci(BenchmarkSpec(seed=seed, bootstrap_reps=500), segments)[0]
        frequency = np.asarray(spectrum.frequencies_hz)
        dominant = float(frequency[np.argmax(spectrum.power_v2_per_hz[0])])
        return {
            "contract_version": "1.0", "synthetic_only": True, "seed": seed,
            "source_sha256": reader.metadata.rights.content_sha256,
            "sample_rate_hz": reader.metadata.sample_rate_hz,
            "samples": samples, "chunk_size": chunk_size, "channels": len(reader.metadata.channels),
            "dominant_frequency_hz": dominant,
            "stream_oracle_max_abs_error_volts": max_error,
            "confidence_interval_fictional": ci.model_dump(),
            "transforms_sha256": canonical_sha(provenance),
            "spectrum_sha256": canonical_sha(spectrum.model_dump()),
            "spectrum_quantized_sha256": canonical_sha(
                {"frequencies_hz": spectrum.frequencies_hz,
                 "power_v2_per_hz": np.round(
                     np.asarray(spectrum.power_v2_per_hz), 18).tolist()}),
            "QC": sorted({flag for item in provenance for step in item["traces"]
                          for flag in step["qc_flags"]}),
            "disclaimer": "Synthetic signal and fictional score CI; no claims about humans or generalization",
        }
