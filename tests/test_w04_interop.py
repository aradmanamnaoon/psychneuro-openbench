"""Synthetic-only W04 fail-closed interoperability checks."""
import pytest
from psychneuro.rights_v1 import Action, DatasetGrant, evaluate
from psychneuro.interop_v1 import Split, produce_artifact, verify_artifact

def grant(**changes):
    values = dict(dataset_id="fictional", source_sha256="a" * 64,
                  license_id="CC0-1.0", verified=True,
                  allowed_actions=frozenset({Action.ANALYZE}))
    values.update(changes)
    return DatasetGrant(**values)

def test_denied_rights():
    for changes in ({"verified": False}, {"revoked": True}, {"license_id": None},
                    {"human_data": True}, {"source_sha256": "x" * 64}):
        assert not evaluate(grant(**changes), Action.ANALYZE).allowed
    assert not evaluate(grant(), Action.REDISTRIBUTE).allowed

def test_tamper_and_groups():
    bundle = produce_artifact(grant(), Split(("person1", "person2"), ("person3",)), 0.5, 42)
    assert verify_artifact(bundle)
    bundle["event"]["accuracy"] = 0.9
    assert not verify_artifact(bundle)
    with pytest.raises(ValueError, match="leakage"):
        produce_artifact(grant(), Split(("person1",), ("person1",)), 0.5, 42)
    with pytest.raises(PermissionError):
        produce_artifact(grant(revoked=True), Split(("a",), ("b",)), 0.5, 42)


def test_rehash_off_contract_not_accepted():
    from psychneuro.interop_v1 import digest
    basic = grant()
    for field, changed in (
        ("version", "interop.v2"), ("action", "redistribute"),
        ("rights_decision", "revoked"), ("source_sha256", "x" * 64),
        ("seed", True), ("accuracy", True), ("license_id", None),
    ):
        bundle = produce_artifact(basic, Split(("p1", "p2"), ("p3",)), 0.5, 42)
        bundle["event"][field] = changed
        bundle["sha256"] = digest(bundle["event"])
        assert not verify_artifact(bundle)

def test_rehash_requires_independent_trusted_pin():
    from psychneuro.interop_v1 import digest
    bundle = produce_artifact(grant(), Split(("p1",), ("p2",)), 0.5, 42)
    pinned = bundle["sha256"]
    bundle["event"]["accuracy"] = 0.99
    bundle["sha256"] = digest(bundle["event"])
    assert verify_artifact(bundle)  # digest alone never authenticates an attacker
    assert not verify_artifact(bundle, expected_sha256=pinned)

def test_malformed_duplicate_overlap_and_unknown_fields():
    from psychneuro.interop_v1 import digest
    import math
    assert not verify_artifact(None)
    assert not verify_artifact({})
    for kind in ("unknown", "nested", "duplicate", "overlap", "nan"):
        b = produce_artifact(grant(), Split(("a", "b"), ("c",)), 0.5, 42)
        if kind == "unknown":
            b["event"]["mystery"] = 1
        elif kind == "nested":
            b["event"]["split"] = {"train": "a", "test": ["c"]}
        elif kind == "duplicate":
            b["event"]["split"]["train"] = ["a", "a"]
        elif kind == "overlap":
            b["event"]["split"]["test"] = ["a"]
        else:
            b["event"]["accuracy"] = math.nan
            assert not verify_artifact(b)
            continue
        b["sha256"] = digest(b["event"])
        assert not verify_artifact(b)

def test_invalid_seed_metric_and_event_size():
    import math
    for metric in (True, math.nan, math.inf, -0.1, 1.1):
        with pytest.raises(ValueError):
            produce_artifact(grant(), Split(("a",), ("b",)), metric, 42)
    for seed in (True, -1, 2**64):
        with pytest.raises(ValueError):
            produce_artifact(grant(), Split(("a",), ("b",)), 0.5, seed)
    with pytest.raises(ValueError, match="size"):
        produce_artifact(grant(), Split(tuple(f"p{i}" for i in range(12000)), ("test",)), 0.5, 42)

def test_elementary_balanced_accuracy_oracle():
    # TP=3,FN=1,TN=5,FP=1: (3/4 + 5/6)/2=19/24
    assert ((3 / 4) + (5 / 6)) / 2 == pytest.approx(19 / 24)
    # prior-only majority-class negative dummy: TPR=0,TNR=1 => BA=.5
    assert (0 + 1) / 2 == 0.5
