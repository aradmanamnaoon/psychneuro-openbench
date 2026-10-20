"""Restart, tampering, tenancy and fencing tests for durable FIR checkpoints."""
import sqlite3

import numpy as np
import pytest

from neurosignal.checkpoints import CheckpointStore
from neurosignal.dsp import CausalFIR, direct_fir_oracle


def test_persist_recreate_and_compare_independent_oracle(tmp_path):
    path = tmp_path / "state.sqlite3"
    coeff = np.array([0.25, 0.5, 0.25])
    samples = np.arange(40.0).reshape(2, 20) * 1e-6
    original = CausalFIR(coeff, 2)
    first = original.process(samples[:, :9], 0)
    CheckpointStore(path).save("tenant-a", "stream-1", original)
    resumed = CheckpointStore(path).load("tenant-a", "stream-1", coeff, 2)
    second = resumed.process(samples[:, 9:], 9)
    np.testing.assert_allclose(
        np.concatenate([first, second], axis=1),
        direct_fir_oracle(coeff, samples), rtol=0, atol=1e-19,
    )
    CheckpointStore(path).save("tenant-a", "stream-1", resumed)
    with pytest.raises(ValueError, match="rollback"):
        CheckpointStore(path).save("tenant-a", "stream-1", original)
    with pytest.raises(KeyError):
        CheckpointStore(path).load("tenant-b", "stream-1", coeff, 2)
    with pytest.raises(ValueError, match="contract"):
        CheckpointStore(path).load("tenant-a", "stream-1", coeff * 2, 2)


def test_equal_position_conflict_and_corruption(tmp_path):
    path = tmp_path / "checkpoint.db"
    store = CheckpointStore(path)
    first = CausalFIR(np.array([0.5, 0.5]), 1)
    store.save("team", "signal", first)
    store.save("team", "signal", first)  # idempotent
    alternate = CausalFIR(np.array([0.2, 0.8]), 1)
    with pytest.raises(ValueError, match="conflicting"):
        store.save("team", "signal", alternate)
    with sqlite3.connect(path) as db:
        db.execute("UPDATE fir_checkpoints SET payload='{}'")
    with pytest.raises(ValueError, match="integrity"):
        store.load("team", "signal", first.coefficients, 1)


def test_invalid_stream_identity(tmp_path):
    store = CheckpointStore(tmp_path / "checkpoint.db")
    with pytest.raises(ValueError):
        store.save("", "stream", CausalFIR(np.array([1., 0.]), 1))
