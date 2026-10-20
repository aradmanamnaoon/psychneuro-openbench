import hashlib
import json

import pytest

from neurosignal.validation_w08 import validate_synthetic


@pytest.mark.parametrize("chunk", [1, 7, 127, 256, 1000])
def test_independent_oracle_and_chunk_invariance(chunk):
    outcome = validate_synthetic(seed=42, samples=2048, chunk_size=chunk)
    assert outcome.accepted
    assert outcome.dominant_hz == 10
    assert outcome.spectral_relative_l2 < 1e-10
    assert outcome.fir_max_abs_error_volts < 1e-16
    assert outcome.null_max_power_v2_per_hz == 0
    assert outcome.waveform_sha256 == validate_synthetic(
        seed=42, samples=2048, chunk_size=13
    ).waveform_sha256
    evidence = json.loads(outcome.json())
    assert len(evidence["waveform_sha256"]) == hashlib.sha256().digest_size * 2


def test_adversarial_regression_gate_and_input_budget():
    with pytest.raises(ValueError):
        validate_synthetic(samples=4096, chunk_size=0)
    with pytest.raises(ValueError):
        validate_synthetic(samples=4096, chunk_size=1024, max_psd_relative_l2=-1)
    result = validate_synthetic(seed=42, max_psd_relative_l2=1e-30,
                                max_fir_error_volts=1e-30)
    assert result.accepted is False


def test_seed_changes_source_digest():
    a = validate_synthetic(seed=42, samples=1024)
    b = validate_synthetic(seed=43, samples=1024)
    assert a.waveform_sha256 != b.waveform_sha256
