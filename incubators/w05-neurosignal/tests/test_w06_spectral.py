"""W06 scientific correctness and adversarial regressions."""
import numpy as np
import pytest
from scipy.signal import welch

from neurosignal.paired_w06 import paired_stratified_ci
from neurosignal.spectral_w06 import StreamingWelch, multitaper_density


@pytest.mark.parametrize("step", [1, 13, 77, 256, 511])
def test_streaming_matches_scipy_welch(step):
    fs = 256
    t = np.arange(4096)/fs
    x = np.stack([10e-6*np.sin(2*np.pi*10*t), 5e-6*np.cos(2*np.pi*20*t)])
    estimator = StreamingWelch(fs, 2, 256, 128)
    for at in range(0, x.shape[1], step):
        estimator.update(x[:, at:at+step], at)
    freq, observed = estimator.result()
    reference_f, reference = welch(x, fs=fs, nperseg=256, noverlap=128,
                                   axis=-1, detrend="constant", scaling="density")
    np.testing.assert_allclose(freq, reference_f, rtol=0, atol=0)
    np.testing.assert_allclose(observed, reference, rtol=1e-12, atol=1e-26)
    assert freq[np.argmax(observed[0])] == 10
    assert estimator._tail.shape[1] < 256
    assert estimator.segments == 31


def test_streaming_invalid_inputs_and_minimum():
    s = StreamingWelch(200, 1, 32)
    with pytest.raises(ValueError):
        s.result()
    with pytest.raises(ValueError, match="discontinuous"):
        s.update(np.ones((1, 10)), 1)
    with pytest.raises(ValueError):
        s.update(np.array([[np.nan]]), 0)
    s.update(np.ones((1, 10)), 0)
    with pytest.raises(ValueError):
        s.update(np.ones((1, 3)), 9)


def test_multitaper_frequency_and_physical_units():
    fs = 256
    n = 1024
    t = np.arange(n)/fs
    x = (8e-6*np.sin(2*np.pi*16*t))[None,:]
    freq, density = multitaper_density(x, fs)
    assert abs(freq[np.argmax(density[0])] - 16) <= 0.5
    power = np.trapezoid(density[0], freq)
    assert power == pytest.approx((8e-6)**2/2, rel=0.08)
    with pytest.raises(ValueError):
        multitaper_density(x*np.nan, fs)


def test_stratified_pairing_reproducible_and_null():
    left = {f"sub{i}": ("a" if i<4 else "b", 0.7+i/100) for i in range(8)}
    right = {k: (stratum, val-.05) for k,(stratum,val) in left.items()}
    a = paired_stratified_ci(left,right,seed=27)
    b = paired_stratified_ci(left,right,seed=27)
    assert a == b
    assert a.mean_difference == pytest.approx(.05)
    assert a.lower == pytest.approx(.05)
    assert a.upper == pytest.approx(.05)
    null = paired_stratified_ci(left,left,seed=27)
    assert null.mean_difference == 0
    with pytest.raises(ValueError):
        paired_stratified_ci(left, {**right,"extra":("a",.5)})
    with pytest.raises(ValueError):
        paired_stratified_ci(left,{k:("wrong",v) for k,(_,v) in right.items()})


def test_synthetic_psd_api_tenant_and_peak(monkeypatch):
    from fastapi.testclient import TestClient

    from neurosignal.service import app

    monkeypatch.setenv("NEUROSIGNAL_LOCAL_TOKEN", "w06-test-token")
    monkeypatch.setenv("NEUROSIGNAL_LOCAL_TENANT", "w06-lab")
    client = TestClient(app)
    req = {"seed": 42, "samples": 2048, "chunk_size": 77,
           "idempotency_key": "w06-psd-key"}
    url = "/v1/spectral/synthetic"
    assert client.post(url, json=req).status_code == 401
    good = {"Authorization": "Bearer w06-test-token", "X-Tenant": "w06-lab"}
    assert client.post(url, json=req, headers={**good, "X-Tenant": "evil"}).status_code == 403
    response = client.post(url, json=req, headers=good)
    assert response.status_code == 200
    result = response.json()
    assert result["synthetic_only"] is True
    assert result["unit"] == "V^2/Hz"
    assert len(result["channels"]) == 4
    power = result["power_v2_per_hz"][0]
    assert result["frequencies_hz"][int(np.argmax(power))] == pytest.approx(10.0)
    assert client.post(url, json={**req, "samples": 9000}, headers=good).status_code == 422
    page = client.get("/").text
    assert 'id="psd-channel"' in page and 'id="psd-plot"' in page
