import numpy as np
import pytest
from scipy.signal import lfilter

from neurosignal.dsp import CausalFIR, direct_fir_oracle, fir_lowpass, synchronize_sample
from neurosignal.fixtures import SyntheticReader
from neurosignal.integration import run_synthetic
from neurosignal.pipeline import GraphSpec, PreprocessingGraph, StepSpec


@pytest.mark.parametrize("chunk_size", [1, 7, 64, 256, 333, 999])
def test_chunk_boundary_independent(chunk_size):
    x = SyntheticReader(samples=2048, seed=3).read(0, 2048).as_array()
    h = fir_lowpass(256, 40, 31)
    filt = CausalFIR(h, x.shape[0])
    pieces = [filt.process(x[:, n:n + chunk_size], n)
              for n in range(0, x.shape[1], chunk_size)]
    assert np.allclose(np.concatenate(pieces, axis=1), direct_fir_oracle(h, x), atol=1e-18)
    assert np.allclose(np.concatenate(pieces, axis=1), lfilter(h, [1], x), atol=1e-18)


def test_checkpoint_restore_and_duplicate_rejection():
    x = np.ones((2, 30))
    f = CausalFIR(np.array([.25, .5, .25]), 2)
    a = f.process(x[:, :10], 0)
    recovered = CausalFIR.restore(f.checkpoint())
    b = recovered.process(x[:, 10:], 10)
    assert np.allclose(np.concatenate([a, b], axis=1), direct_fir_oracle(f.coefficients, x))
    with pytest.raises(ValueError, match="clock discontinuity"):
        recovered.process(x[:, :2], 0)
    corrupt = f.checkpoint()
    corrupt["zi"] = [[0]]
    with pytest.raises(ValueError):
        CausalFIR.restore(corrupt)


def test_timestamp_synchronization():
    assert synchronize_sample(1_000_000_000, 1_500_000_000, 256) == 128
    with pytest.raises(ValueError):
        synchronize_sample(1_000_000_000, 1_500_000_000, 257)
    with pytest.raises(ValueError):
        synchronize_sample(100, 99, 256)


def test_reference_properties_and_amplitude_flags():
    reader = SyntheticReader(samples=256)
    graph = PreprocessingGraph(GraphSpec(steps=(StepSpec(op="average_reference"),
                                               StepSpec(op="amplitude_qc", threshold_uv=1))),
                               256, 4)
    processed, trace = graph.process(reader.read(0, 256))
    assert np.max(np.abs(processed.as_array().mean(axis=0))) < 1e-19
    assert trace[1].qc_flags
    assert trace[1].input_sha256 == trace[1].output_sha256


def test_mismatch_and_gap_rejected():
    reader = SyntheticReader(samples=256)
    graph = PreprocessingGraph(GraphSpec(steps=(StepSpec(op="scale", multiplier=2),)), 256, 4)
    with pytest.raises(ValueError):
        graph.process(reader.read(1, 20))
    out, _ = graph.process(reader.read(0, 10))
    assert out.start == 0
    with pytest.raises(ValueError):
        graph.process(reader.read(12, 16))


@pytest.mark.parametrize("seed", [0, 13, 42, 999])
def test_integrated_three_systems(seed):
    a = run_synthetic(seed, samples=1024, chunk_size=77)
    b = run_synthetic(seed, samples=1024, chunk_size=319)
    assert a["dominant_frequency_hz"] == pytest.approx(10.0)
    assert a["stream_oracle_max_abs_error_volts"] < 1e-17
    assert a["spectrum_quantized_sha256"] == b["spectrum_quantized_sha256"]
    assert a["confidence_interval_fictional"] == b["confidence_interval_fictional"]
