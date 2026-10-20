import pytest
from pydantic import ValidationError

from neurosignal.contracts import Channel, Chunk, Event, Recording, Rights, SignalUnit
from neurosignal.fixtures import SyntheticReader


def test_synthetic_metadata_checksum_is_stable():
    a, b = SyntheticReader(seed=44), SyntheticReader(seed=44)
    assert a.metadata.rights.content_sha256 == b.metadata.rights.content_sha256
    assert a.read(3, 9).as_array().shape == (4, 6)
    assert SignalUnit.MICROVOLT.to_volts == 1e-6


@pytest.mark.parametrize("start,stop", [(-1, 5), (0, 0), (7, 6), (0, 999999)])
def test_slice_fails_closed(start, stop):
    with pytest.raises(ValueError):
        SyntheticReader().read(start, stop)


def test_real_data_needs_explicit_rights():
    with pytest.raises(ValidationError):
        Rights(source_uri="https://example.org/x.edf", data_license="unknown",
               content_sha256="0" * 64, is_synthetic=False, allow_analysis=True)


def test_duplicate_channel_and_invalid_event_rejected():
    rights = SyntheticReader().metadata.rights
    with pytest.raises(ValidationError):
        Recording(recording_id="bad", sample_rate_hz=100, samples=10,
                  channels=(Channel(name="Fp1"), Channel(name="Fp1")), rights=rights)
    with pytest.raises(ValidationError):
        Recording(recording_id="bad", sample_rate_hz=100, samples=10,
                  channels=(Channel(name="Fp1"),), events=(Event(sample=10, code="x"),), rights=rights)


def test_nonfinite_chunk_denied():
    with pytest.raises(ValidationError):
        Chunk(recording_id="x", start=0, sample_rate_hz=256,
              channel_names=("Cz",), volts=[[float("nan")]])
