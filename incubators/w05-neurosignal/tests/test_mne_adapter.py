import hashlib

import numpy as np
import pytest

from neurosignal.adapters import MNEReader
from neurosignal.contracts import Rights


def test_fif_lazy_units_events_license_checksum(tmp_path):
    mne = pytest.importorskip("mne")
    fs = 200
    t = np.arange(600) / fs
    expected = np.stack((10e-6 * np.sin(2 * np.pi * 12 * t),
                         5e-6 * np.sin(2 * np.pi * 15 * t)))
    info = mne.create_info(["F3", "F4"], fs, ch_types="eeg")
    raw = mne.io.RawArray(expected, info, verbose=False)
    raw.set_annotations(mne.Annotations(onset=[1.0], duration=[.1], description=["stim"] ))
    path = tmp_path / "synthetic_raw.fif"
    raw.save(path, overwrite=True, verbose=False)
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    rights = Rights(source_uri="generated:mne-fif", data_license="CC0-1.0-synthetic",
                    is_synthetic=False, permission_verified=True, allow_analysis=True,
                    content_sha256=checksum)
    with MNEReader(path, tmp_path, rights, "synthetic-fif") as reader:
        assert reader._raw.preload is False
        assert reader.metadata.sample_rate_hz == fs
        assert len(reader.metadata.events) == 1
        assert reader.metadata.events[0].sample == 200
        assert reader.metadata.events[0].duration_samples == 20
        assert np.allclose(reader.read(10, 70).as_array(), expected[:, 10:70], atol=1e-12)
        with pytest.raises(ValueError):
            reader.read(-1, 500)
    with pytest.raises(ValueError, match="checksum"):
        MNEReader(path, tmp_path, rights.model_copy(update={"content_sha256": "0" * 64}), "bad")


def test_root_escape_denied(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    safe = tmp_path / "safe"
    safe.mkdir()
    badfile = outside / "x.edf"
    badfile.write_text("not an EDF")
    rights = Rights(source_uri="generated:bad", data_license="synthetic", is_synthetic=False,
                    permission_verified=True, allow_analysis=True,
                    content_sha256=hashlib.sha256(badfile.read_bytes()).hexdigest())
    with pytest.raises(ValueError, match="approved data root"):
        MNEReader(badfile, safe, rights, "denied")


def test_fif_annotation_origin_nonzero_first_sample(tmp_path):
    """Regression: MNE stores raw.first_time in annotations; map back to local samples."""
    mne = pytest.importorskip("mne")
    data = np.zeros((1, 500), dtype=float)
    raw = mne.io.RawArray(data, mne.create_info(["Cz"], 100, ch_types="eeg"),
                          first_samp=10_000, verbose=False)
    raw.set_annotations(mne.Annotations(onset=[1.0], duration=[0.1], description=["evt"]))
    path = tmp_path / "offset_raw.fif"
    raw.save(path, overwrite=True, verbose=False)
    rights = Rights(source_uri="generated:nonzero-first", data_license="CC0-1.0-synthetic",
                    is_synthetic=False, permission_verified=True, allow_analysis=True,
                    content_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    with MNEReader(path, tmp_path, rights, "offset") as reader:
        assert reader._raw.first_samp == 10_000
        assert len(reader.metadata.events) == 1
        assert reader.metadata.events[0].sample == 100
        assert reader.metadata.events[0].duration_samples == 10
