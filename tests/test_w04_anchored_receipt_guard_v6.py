"""Synthetic-only tests of signed-anchor + P25 guarded offline import.

Policy is a TEST DOUBLE; these cases cannot certify externally issued signing
keys, independent root custody or rights to any real data.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from test_w04_anchor_v1 import NOW, make_anchor
from test_w04_receipt_v3 import make_receipt

from psychneuro.w04.anchor_v1 import AnchorError
from psychneuro.w04.receipt_guard_v3 import import_authorized_anchored
from psychneuro.w04.receipt_v3 import ReceiptError


class TestPolicy:
    __test__ = False

    def __init__(self, *, revoke_after_first: bool = False) -> None:
        self.calls = 0
        self.revoke_after_first = revoke_after_first

    def validate_permit(self, permit, *, now_ns=None) -> None:
        self.calls += 1
        if self.revoke_after_first and self.calls >= 2:
            raise PermissionError("test-only P25 revocation")


def _permit(receipt):
    return SimpleNamespace(
        version="p25-permit-2",
        tenant=receipt.tenant, dataset=receipt.dataset,
        subject="researcher", purpose=receipt.purpose,
        action="read_aggregate", policy_revision=receipt.policy_revision,
        policy_sha256=receipt.policy_sha256,
    )


def _import(receipt, anchor, key, policy):
    return import_authorized_anchored(
        receipt, anchor=anchor, pinned_public_keys={anchor.key_id: key},
        min_sequence=7, policy=policy, permit=_permit(receipt),
        tenant=receipt.tenant, subject="researcher", now_ns=NOW,
    )


def test_signed_original_synthetic_receipt_requires_two_live_policy_checks():
    receipt = make_receipt(73)
    anchor, public = make_anchor(receipt=receipt)
    policy = TestPolicy()
    record = _import(receipt, anchor, public, policy)
    assert record["run_id"] == receipt.run_id
    assert policy.calls == 2


def test_signed_root_rejects_wrong_external_public_key_before_returning_record():
    receipt = make_receipt(73)
    anchor, _ = make_anchor(receipt=receipt)
    policy = TestPolicy()
    with pytest.raises(AnchorError, match="signature"):
        _import(receipt, anchor, bytes([17]) * 32, policy)
    assert policy.calls == 1


def test_revocation_during_signature_validation_prevents_return():
    receipt = make_receipt(73)
    anchor, public = make_anchor(receipt=receipt)
    policy = TestPolicy(revoke_after_first=True)
    with pytest.raises(PermissionError, match="revocation"):
        _import(receipt, anchor, public, policy)
    assert policy.calls == 2


def test_obsolete_policy_revision_rejected_before_asymmetric_verification():
    receipt = make_receipt(73)
    anchor, public = make_anchor(receipt=receipt)
    old = _permit(receipt)
    old.policy_revision += 1
    policy = TestPolicy()
    with pytest.raises(ReceiptError, match="obsolete"):
        import_authorized_anchored(
            receipt, anchor=anchor,
            pinned_public_keys={anchor.key_id: public}, min_sequence=7,
            policy=policy, permit=old, tenant=receipt.tenant,
            subject="researcher", now_ns=NOW,
        )
    assert policy.calls == 1
