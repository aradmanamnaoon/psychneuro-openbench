"""P25-permissioned facade for internal P13 receipt issuance and verification.

Unlike receipt_v3's pure content checksum verifier, this interface REFUSES
unauthorized uses and requires a live policy store / permit on each operation.
The caller must authenticate the permit holder (no direct browser exposure).
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from .anchor_v1 import AnchorV1
from .receipt_v3 import P13P25Receipt, ReceiptError, issue_receipt, verify_receipt


class PermitLike(Protocol):
    version: str
    tenant: str
    dataset: str
    subject: str
    purpose: str
    action: str
    policy_revision: int
    policy_sha256: str


class PolicyLike(Protocol):
    def validate_permit(self, permit: PermitLike, *, now_ns: int | None = None) -> None: ...


def _check_scope(permit: PermitLike, *, tenant: str, subject: str, action: str) -> None:
    if (permit.version != "p25-permit-2" or permit.tenant != tenant
            or permit.subject != subject or permit.dataset != "w03-original-synthetic"
            or permit.purpose != "internal-method-validation" or permit.action != action):
        raise ReceiptError("permit scope mismatch")


def export_authorized(record: dict[str, Any], *, policy: PolicyLike,
                      permit: PermitLike, tenant: str, subject: str,
                      now_ns: int | None = None) -> P13P25Receipt:
    """Aggregate ONLY; caller is responsible for transport and secure recipient ACL."""
    _check_scope(permit, tenant=tenant, subject=subject, action="export_aggregate")
    policy.validate_permit(permit, now_ns=now_ns)
    envelope = issue_receipt(record, tenant=tenant, policy_revision=permit.policy_revision,
                             policy_sha256=permit.policy_sha256)
    # Revocation detected after potentially expensive graph validation.
    policy.validate_permit(permit, now_ns=now_ns)
    return envelope


def import_authorized(receipt: P13P25Receipt, *, policy: PolicyLike,
                      permit: PermitLike, tenant: str, subject: str,
                      trusted_root: str | None,
                      now_ns: int | None = None) -> dict[str, Any]:
    """No import/persistence side effects; reauthorize any subsequent operation."""
    _check_scope(permit, tenant=tenant, subject=subject, action="read_aggregate")
    policy.validate_permit(permit, now_ns=now_ns)
    if receipt.policy_revision != permit.policy_revision:
        raise ReceiptError("receipt came from an obsolete policy revision")
    record = verify_receipt(receipt, tenant=tenant,
                            expected_policy_sha256=permit.policy_sha256,
                            trusted_root=trusted_root)
    policy.validate_permit(permit, now_ns=now_ns)
    return record


def import_authorized_anchored(
    receipt: P13P25Receipt,
    *,
    anchor: "AnchorV1",
    pinned_public_keys: Mapping[str, bytes],
    min_sequence: int,
    policy: PolicyLike,
    permit: PermitLike,
    tenant: str,
    subject: str,
    now_ns: int | None = None,
) -> dict[str, Any]:
    """Independently signed aggregate import validation without persistence.

    Both the key mapping and nonrollback sequence floor MUST originate from a
    separately authenticated operator-controlled channel; never deserialize
    them from the receipt, anchor, user request or same application database.
    This still cannot prove legal dataset-use rights. Import/persistence
    remains the caller's independently authorized responsibility.
    """
    from .anchor_v1 import verify_anchor

    _check_scope(permit, tenant=tenant, subject=subject, action="read_aggregate")
    policy.validate_permit(permit, now_ns=now_ns)
    if receipt.policy_revision != permit.policy_revision:
        raise ReceiptError("receipt came from an obsolete policy revision")
    pinned_root = verify_anchor(
        anchor, receipt,
        pinned_public_keys=pinned_public_keys,
        min_sequence=min_sequence, now_ns=now_ns,
    )
    record = verify_receipt(
        receipt, tenant=tenant,
        expected_policy_sha256=permit.policy_sha256,
        trusted_root=pinned_root,
    )
    # A rights revocation during asymmetric crypto/content verification wins.
    policy.validate_permit(permit, now_ns=now_ns)
    return record
