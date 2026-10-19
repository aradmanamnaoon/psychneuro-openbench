"""Fail-closed scoped-P25 bridge tests with test-only synthetic evidence."""
from __future__ import annotations

import hashlib
import importlib
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1] / "src"
sys.path.insert(0, str(ROOT))
guard = importlib.import_module("psychneuro.w04.receipt_guard_v3")
export_authorized = guard.export_authorized
import_authorized = guard.import_authorized
ReceiptError = importlib.import_module("psychneuro.w04.receipt_v3").ReceiptError
make_record = importlib.import_module("test_w04_receipt_v3").make_record


@dataclass(frozen=True)
class Permit:
    version: str = "p25-permit-2"
    tenant: str = "tenant-A"
    dataset: str = "w03-original-synthetic"
    subject: str = "researcher"
    purpose: str = "internal-method-validation"
    action: str = "export_aggregate"
    policy_revision: int = 2
    policy_sha256: str = hashlib.sha256(b"independent-policy").hexdigest()


class LocalPolicy:
    def __init__(self):
        self.validations = 0
        self.revoked = False
        self.revoke_after = None

    def validate_permit(self, permit, *, now_ns=None):
        self.validations += 1
        if self.revoked or self.validations == self.revoke_after:
            raise PermissionError("revoked or expired")


def test_export_read_reauthorize_and_no_implicit_public_export():
    policy = LocalPolicy()
    write = Permit()
    record = make_record()
    receipt = export_authorized(record, policy=policy, permit=write,
                                tenant="tenant-A", subject="researcher")
    assert policy.validations == 2
    read = replace(write, action="read_aggregate")
    assert import_authorized(receipt, policy=policy, permit=read, tenant="tenant-A",
                             subject="researcher", trusted_root=receipt.provenance_root) == record
    assert policy.validations == 4
    with pytest.raises(ReceiptError):
        export_authorized(record, policy=policy, permit=read,
                          tenant="tenant-A", subject="researcher")
    with pytest.raises(ReceiptError):
        import_authorized(receipt, policy=policy, permit=write, tenant="tenant-A",
                          subject="researcher", trusted_root=receipt.provenance_root)
    with pytest.raises(ReceiptError):
        export_authorized(record, policy=policy, permit=replace(write, action="redistribute"),
                          tenant="tenant-A", subject="researcher")


def test_revoke_on_second_check_fails_closed():
    policy = LocalPolicy()
    policy.revoke_after = 2
    with pytest.raises(PermissionError):
        export_authorized(make_record(), policy=policy, permit=Permit(),
                          tenant="tenant-A", subject="researcher")
    assert policy.validations == 2


def test_revoke_between_import_validation_and_delivery():
    policy = LocalPolicy()
    receipt = export_authorized(make_record(), policy=policy,
                                permit=Permit(), tenant="tenant-A", subject="researcher")
    policy.revoke_after = 4
    with pytest.raises(PermissionError):
        import_authorized(receipt, policy=policy, permit=replace(Permit(), action="read_aggregate"),
                          tenant="tenant-A", subject="researcher", trusted_root=receipt.provenance_root)


def test_foreign_identity_or_policy_revision_is_rejected():
    p = LocalPolicy()
    receipt = export_authorized(make_record(), policy=p, permit=Permit(),
                                tenant="tenant-A", subject="researcher")
    checks = p.validations
    with pytest.raises(ReceiptError):
        import_authorized(receipt, policy=p, permit=replace(Permit(), action="read_aggregate", tenant="tenant-B"),
                          tenant="tenant-A", subject="researcher", trusted_root=receipt.provenance_root)
    assert p.validations == checks
    with pytest.raises(ReceiptError):
        import_authorized(receipt, policy=p, permit=replace(Permit(), action="read_aggregate", policy_revision=3),
                          tenant="tenant-A", subject="researcher", trusted_root=receipt.provenance_root)
    with pytest.raises(ReceiptError):
        export_authorized(make_record(), policy=p, permit=replace(Permit(), version="p25-permit-1"),
                          tenant="tenant-A", subject="researcher")
