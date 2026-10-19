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
