"""Synthetic PyNWB regression for per-channel scaling; no participant data."""
import hashlib
from datetime import UTC, datetime

import numpy as np
import pytest

from neurosignal.adapters import NWBReader
from neurosignal.contracts import Rights


def test_nwb_channel_conversion_and_offset(tmp_path):
    pynwb = pytest.importorskip("pynwb")
    from pynwb.ecephys import ElectricalSeries

    nwb = pynwb.NWBFile(
        session_description="synthetic numerical units test",
        identifier="synthetic-nwb-channel-gains",
        session_start_time=datetime(2025, 1, 1, tzinfo=UTC),
    )
    device = nwb.create_device(name="simulator")
    group = nwb.create_electrode_group(
        name="sim", description="simulated", location="none",
        device=device,
    )
    for _ in range(2):
        nwb.add_electrode(x=0.0, y=0.0, z=0.0, imp=float("nan"),
                          location="synthetic", filtering="none", group=group)
    electrodes = nwb.create_electrode_table_region(region=[0, 1], description="both")
    data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    series = ElectricalSeries(
        name="ElectricalSeries", data=data, electrodes=electrodes,
        rate=200.0, starting_time=0.0, conversion=1e-6,
        channel_conversion=np.array([1.0, 10.0]), offset=2e-9,
    )
    nwb.add_acquisition(series)
    path = tmp_path / "generated.nwb"
    with pynwb.NWBHDF5IO(str(path), "w") as io:
        io.write(nwb)
    rights = Rights(
        source_uri="generated:synthetic-nwb", data_license="CC0-1.0-synthetic",
        is_synthetic=False, permission_verified=True, allow_analysis=True,
        content_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    with NWBReader(path, tmp_path, rights, "synthetic") as reader:
        assert reader.metadata.samples == 3
        assert reader.metadata.sample_rate_hz == 200.0
        actual = reader.read(1, 3).as_array()
    expected = (data[1:3] * np.array([1e-6, 10e-6]) + 2e-9).T
    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-15)
