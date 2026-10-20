"""W07 regression tests: artifact, alignment, units, and trace extrema."""
import numpy as np
import pytest

from neurosignal.artifacts_w07 import artifact_mask, event_locked_erp, minmax_downsample


def test_artifact_thresholds_strict_and_channels():
    x = np.zeros((3, 2, 20))
    x[0, 0, 3] = 121e-6
    x[1, 1, 5] = -95e-6
    x[1, 1, 6] = 95e-6
    rejected = artifact_mask(x, absolute_uv=120, peak_to_peak_uv=180)
    assert rejected.tolist() == [[True, False], [False, True], [False, False]]
    with pytest.raises(ValueError):
        artifact_mask(x * np.inf)


def test_erp_alignment_rejection_boundaries_and_sem():
    rate = 100.0
    x = np.zeros((2, 700))
    events = [5, 100, 300, 500, 695]
    for position in [100, 300, 500]:
        x[0, position+3] = 12e-6
    x[1, 300] = 200e-6  # Reject exactly one otherwise valid event
    r = event_locked_erp(x, events, rate, pre_samples=20, post_samples=30)
    assert (r.event_count, r.retained, r.rejected, r.out_of_bounds) == (5, 2, 1, 2)
    assert r.rejected_event_indices == (2,)
    assert r.time_seconds[20] == 0
    assert r.time_seconds[23] == pytest.approx(.03)
    assert r.mean_volts[0, 23] == pytest.approx(12e-6)
    np.testing.assert_allclose(r.sem_volts, 0, atol=1e-20)


def test_null_guard_and_minmax_preserves_spike():
    with pytest.raises(ValueError, match="no accepted"):
        event_locked_erp(np.zeros((1, 100)), [0], 100, pre_samples=20, post_samples=20)
    signal = np.zeros(1000)
    signal[443] = 4
    signal[444] = -3
    reduced = minmax_downsample(signal, 32)
    assert reduced.size <= 64
    assert max(reduced) == 4
    assert min(reduced) == -3
