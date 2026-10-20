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


def test_synthetic_artifact_api_security_and_provenance(monkeypatch):
    from fastapi.testclient import TestClient

    from neurosignal.service import app

    monkeypatch.setenv("NEUROSIGNAL_LOCAL_TOKEN", "w07-secure-test")
    monkeypatch.setenv("NEUROSIGNAL_LOCAL_TENANT", "lab")
    client = TestClient(app)
    payload = {"seed": 42, "samples": 2048, "chunk_size": 128,
               "idempotency_key": "w07-test-key"}
    route = "/v1/artifacts/synthetic"
    assert client.post(route, json=payload).status_code == 401
    headers = {"Authorization": "Bearer w07-secure-test", "X-Tenant": "lab"}
    assert client.post(route, json=payload, headers={**headers, "X-Tenant": "other"}).status_code == 403
    response = client.post(route, json=payload, headers=headers)
    assert response.status_code == 200
    result = response.json()
    assert result["synthetic_only"] is True
    assert result["license"] == "CC0-1.0-synthetic"
    assert len(result["trace_volts_minmax"]) == 256
    assert result["erp"]["retained"] >= 1
    assert client.post(route, json={**payload, "samples": 8193}, headers=headers).status_code == 422


def test_recording_qc_differences_and_manifest():
    import hashlib
    import json

    from neurosignal.qc_w07 import compare_recording_qc, deterministic_json_manifest

    rows, spread = compare_recording_qc(
        [("syntheticA", "r1", 10, 0), ("syntheticB", "r2", 10, 10)],
        thresholds={"syntheticA": 0.1, "syntheticB": 0.2})
    assert spread == 1
    assert rows[0].above_threshold is False
    assert rows[1].above_threshold is True
    assert 0 <= rows[0].wilson_low <= rows[0].wilson_high <= 1
    assert 0 <= rows[1].wilson_low <= rows[1].wilson_high <= 1
    manifest = json.loads(deterministic_json_manifest({"seed": 42, "license": "CC0"}))
    body = json.dumps(manifest["payload"], sort_keys=True,
                      separators=(",", ":")).encode()
    assert manifest["sha256"] == hashlib.sha256(body).hexdigest()
    with pytest.raises(ValueError):
        compare_recording_qc([("A", "x", 1, 2)], thresholds={"A": 0.5})
    with pytest.raises(ValueError):
        deterministic_json_manifest({"invalid": float("nan")})
