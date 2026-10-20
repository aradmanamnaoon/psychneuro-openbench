import numpy as np
import pytest

from neurosignal.evalops import BenchmarkSpec, Segment, bootstrap_ci, preflight
from neurosignal.evaluation import ShortTimeFourier, WelchPSD, rectangular_periodogram_oracle
from neurosignal.fixtures import SyntheticReader


def rows():
    return [Segment(id=str(i), group_id=f"person{i}", recording_id=f"rec{i}",
                    start=0, stop=100, split="train" if i < 3 else "test",
                    score=.8 if i % 2 else .6) for i in range(9)]


def test_grouped_ci_and_deterministic_seed():
    spec = BenchmarkSpec(bootstrap_reps=300, seed=4)
    ci = bootstrap_ci(spec, rows())[0]
    assert ci.n_groups == 6
    assert ci.lower <= ci.mean <= ci.upper
    assert ci == bootstrap_ci(spec, rows())[0]


def test_group_leakage_blocked():
    broken = rows() + [Segment(id="dup_group", group_id="person0", recording_id="extra",
                               start=0, stop=5, split="test", score=.9)]
    assert "group split contamination" in preflight(broken).causes
    with pytest.raises(ValueError, match="leakage"):
        bootstrap_ci(BenchmarkSpec(), broken)


def test_temporal_leakage_blocked_even_distinct_group_ids():
    broken = rows() + [Segment(id="overlap", group_id="new_person", recording_id="rec0",
                               start=50, stop=110, split="test", score=.7)]
    assert "temporal window overlap across splits" in preflight(broken).causes


def test_insufficient_independent_test_groups():
    with pytest.raises(ValueError):
        bootstrap_ci(BenchmarkSpec(), rows()[:4])


def test_spectral_physics_sinusoid():
    reader = SyntheticReader(seed=8, samples=4096)
    result = WelchPSD(nperseg=256).evaluate(reader.read(0, 4096))
    hz = np.asarray(result.frequencies_hz)
    power = np.asarray(result.power_v2_per_hz[0])
    assert hz[np.argmax(power)] == pytest.approx(10.0)
    # Integral of one-sided density yields mean square energy [V^2], approximate because noise.
    assert 1e-10 < np.trapezoid(power, hz) < 1e-9
    assert result.n_segments == 31
    with pytest.raises(ValueError):
        WelchPSD(nperseg=1024).evaluate(reader.read(0, 500))


def test_oracle_parseval_and_STFT_time_alignment():
    rate = 256
    signal = np.sin(2 * np.pi * 20 * np.arange(1024) / rate) * 10e-6
    hz, density = rectangular_periodogram_oracle(signal, rate)
    assert hz[np.argmax(density)] == 20.0
    assert np.trapezoid(density, hz) == pytest.approx(np.mean(signal ** 2), rel=1e-6)
    f, t, z = ShortTimeFourier(128).evaluate(SyntheticReader(samples=512).read(64, 320))
    assert z.shape[0] == 4 and len(f) == z.shape[1]
    assert t[0] >= 64 / rate
