"""Only fictional synthetic receipts and ephemeral test signing keys are used."""
from __future__ import annotations

import base64
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import pytest
from pydantic import ValidationError

import cryptography  # noqa: F401 - required test dependency, never skip security gate
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from psychneuro.w04 import anchor_v1 as anchor_mod

AnchorV1 = anchor_mod.AnchorV1
AnchorError = anchor_mod.AnchorError
verify_anchor = anchor_mod.verify_anchor
NOW = 1_800_000_000_000_000_000


@dataclass(frozen=True)
class Receipt:
    tenant: str = "tenant1"
    dataset: str = "w03-original-synthetic"
    purpose: str = "internal-method-validation"
    policy_revision: int = 2
    policy_sha256: str = "a" * 64
    run_id: str = "b" * 64
    provenance_root: str = "c" * 64
    receipt_sha256: str = "d" * 64


def make_anchor(*, receipt: Receipt = Receipt(), sequence: int = 7, issued: int = NOW - 10):
    private = Ed25519PrivateKey.generate()  # Test-only; never a configured signing authority.
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    raw = dict(
        key_id="offline-reviewer-1", tenant=receipt.tenant,
        dataset=receipt.dataset, purpose=receipt.purpose,
        policy_revision=receipt.policy_revision, policy_sha256=receipt.policy_sha256,
        run_id=receipt.run_id, provenance_root=receipt.provenance_root,
        receipt_sha256=receipt.receipt_sha256, sequence=sequence,
        issued_ns=issued, expires_ns=NOW + 60_000_000_000,
        signature_b64="A" * 88,
    )
    provisional = AnchorV1.model_validate(raw)
    return provisional.model_copy(update={
        "signature_b64": base64.b64encode(private.sign(provisional.signed_bytes())).decode("ascii"),
    }), public


def test_external_signature_binds_exact_receipt_and_root():
    receipt = Receipt()
    anchor, public = make_anchor(receipt=receipt)
    assert verify_anchor(anchor, receipt, pinned_public_keys={anchor.key_id: public},
                         min_sequence=7, now_ns=NOW) == receipt.provenance_root


@pytest.mark.parametrize("field,new", [
    ("tenant", "tenant2"), ("dataset", "other"), ("purpose", "redistribute"),
    ("policy_revision", 3), ("policy_sha256", "e" * 64),
    ("run_id", "e" * 64), ("provenance_root", "e" * 64),
    ("receipt_sha256", "e" * 64),
])
def test_replay_into_different_receipt_denied(field, new):
    anchor, public = make_anchor()
    altered = replace(Receipt(), **{field: new})
    with pytest.raises(AnchorError, match="bind"):
        verify_anchor(anchor, altered, pinned_public_keys={anchor.key_id: public},
                      min_sequence=7, now_ns=NOW)


def test_unsigned_rewrite_or_wrong_key_denied():
    anchor, public = make_anchor()
    altered = anchor.model_copy(update={"sequence": 8})
    for bad_anchor, bad_key in ((altered, public), (anchor, bytes([42]) * 32)):
        with pytest.raises(AnchorError, match="signature"):
            verify_anchor(bad_anchor, Receipt(), pinned_public_keys={anchor.key_id: bad_key},
                          min_sequence=7, now_ns=NOW)


def test_missing_pinned_key_or_bad_signature_denied():
    anchor, public = make_anchor()
    with pytest.raises(AnchorError, match="pinned"):
        verify_anchor(anchor, Receipt(), pinned_public_keys={}, min_sequence=7, now_ns=NOW)
    corrupt = anchor.model_copy(update={"signature_b64": "!" * 88})
    with pytest.raises(AnchorError, match="encoding"):
        verify_anchor(corrupt, Receipt(), pinned_public_keys={anchor.key_id: public},
                      min_sequence=7, now_ns=NOW)


@pytest.mark.parametrize("now,sequence,issued,expected", [
    (NOW, 8, NOW - 10, "replayed"),
    (NOW - 11, 7, NOW - 10, "future"),
    (NOW + 60_000_000_000, 7, NOW - 10, "expired"),
    (NOW, 7, NOW - 9 * 24 * 60 * 60 * 1_000_000_000, "excessive"),
])
def test_expiration_rollback_and_replay_guard(now, sequence, issued, expected):
    anchor, public = make_anchor(issued=issued)
    with pytest.raises(AnchorError, match=expected):
        verify_anchor(anchor, Receipt(), pinned_public_keys={anchor.key_id: public},
                      min_sequence=sequence, now_ns=now)


def test_strict_schema_rejects_extra_and_bool_revision():
    anchor, _ = make_anchor()
    with pytest.raises(ValidationError):
        AnchorV1.model_validate({**anchor.model_dump(), "unsigned_note": "unsafe"})
    with pytest.raises(ValidationError):
        AnchorV1.model_validate({**anchor.model_dump(), "policy_revision": True})


def test_fail_closed_without_independently_persisted_sequence_floor():
    anchor, public = make_anchor()
    for floor in (0, -1, True):
        with pytest.raises(AnchorError, match="sequence"):
            verify_anchor(anchor, Receipt(), pinned_public_keys={anchor.key_id: public},
                          min_sequence=floor, now_ns=NOW)
