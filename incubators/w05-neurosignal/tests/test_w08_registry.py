import pytest

from neurosignal.registry_w08 import EvidenceRegistry


def test_registry_idempotency_tenancy_and_regression(tmp_path):
    r = EvidenceRegistry(tmp_path / "registry.sqlite")
    a = {"schema_version": "1.0", "synthetic_only": True,
         "cohort": "seed42-cc0", "metric_units": "ms", "latency_ms": 10.}
    b = {**a, "latency_ms": 11.}
    before = r.register("lab-a", a)
    assert before == r.register("lab-a", a)
    after = r.register("lab-a", b)
    assert r.compare("lab-a", before, after, metric="latency_ms")["regressed"]
    assert not r.compare("lab-a", before, after, metric="latency_ms",
                         max_relative_regression=.2)["regressed"]
    with pytest.raises(KeyError):
        r.read("lab-b", before)
    with pytest.raises(ValueError):
        r.register("lab-b", a)
    with pytest.raises(ValueError):
        r.register("lab-a", {**a, "synthetic_only": False})
    with pytest.raises(ValueError):
        r.register("lab-a", {**a, "latency_ms": float("nan")})
    other = r.register("lab-a", {**b, "cohort": "changed"})
    with pytest.raises(ValueError, match="cohort"):
        r.compare("lab-a", before, other, metric="latency_ms")


def test_registry_missing_metric_rejected(tmp_path):
    reg = EvidenceRegistry(tmp_path / "e.sqlite")
    p = {"schema_version": "1.0", "synthetic_only": True, "cohort": "a",
         "metric_units": "ms", "latency_ms": 1}
    h = reg.register("team", p)
    with pytest.raises(ValueError):
        reg.compare("team", h, h, metric="does_not_exist")
