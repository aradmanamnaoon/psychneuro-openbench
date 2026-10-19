"""Offline Ed25519 validation of independently issued W04 P13/P25 root anchors.

This module verifies an external authority's signature; it DOES NOT issue
trust, sign receipts, decide dataset rights, or store private signing keys.
The trust-key mapping and minimum sequence must arrive from an independently
controlled, authenticated channel, not the receipt or its SQLite database.
Use a fresh P25 authorization before and after verification and any import.
"""
from __future__ import annotations

import base64
import binascii
import hmac
import json
import re
import time
from collections.abc import Mapping
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

DOMAIN = b"PsychNeuro-OpenBench/W04/P13P25/anchor-v1\n"
MAX_VALIDITY_NS = 7 * 24 * 60 * 60 * 1_000_000_000
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class AnchorError(ValueError):
    """The external attestation did not satisfy authenticity/scope/freshness."""


class ReceiptBinding(Protocol):
    tenant: str
    dataset: str
    purpose: str
    policy_revision: int
    policy_sha256: str
    run_id: str
    provenance_root: str
    receipt_sha256: str


class AnchorV1(BaseModel):
    """Signed, canonical, scope-bound receipt metadata, not a permission grant."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    version: Literal["w04-anchor-1"] = "w04-anchor-1"
    key_id: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,80}$")
    tenant: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,80}$")
    dataset: Literal["w03-original-synthetic"] = "w03-original-synthetic"
    purpose: Literal["internal-method-validation"] = "internal-method-validation"
    policy_revision: int = Field(ge=1)
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    run_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    provenance_root: str = Field(pattern=r"^[0-9a-f]{64}$")
    receipt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    sequence: int = Field(ge=1)
    issued_ns: int = Field(ge=0)
    expires_ns: int = Field(ge=1)
    signature_b64: str = Field(min_length=88, max_length=88)

    def signed_bytes(self) -> bytes:
        """Domain-separated, deterministic byte sequence for offline verification."""
        raw = self.model_dump(mode="json", exclude={"signature_b64"})
        return DOMAIN + json.dumps(
            raw, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")


def verify_anchor(
    anchor: AnchorV1,
    receipt: ReceiptBinding,
    *,
    pinned_public_keys: Mapping[str, bytes],
    min_sequence: int,
    now_ns: int | None = None,
) -> str:
    """Verify independently pinned Ed25519 signature and exact receipt context.

    A monotonically increasing `min_sequence` is meaningful ONLY when persisted
    and integrity-protected outside the importable artifact. Verification alone
    cannot establish lawful data access or third-party stewardship.
    """
    if (not isinstance(anchor, AnchorV1) or isinstance(min_sequence, bool) or
            not isinstance(min_sequence, int) or min_sequence < 1):
        raise AnchorError("invalid anchor or minimum externally pinned sequence")
    current_ns = time.time_ns() if now_ns is None else now_ns
    if isinstance(current_ns, bool) or not isinstance(current_ns, int) or current_ns < 0:
        raise AnchorError("invalid verification clock")
    if (anchor.sequence < min_sequence or anchor.issued_ns > current_ns or
            current_ns >= anchor.expires_ns or anchor.expires_ns <= anchor.issued_ns or
            anchor.expires_ns - anchor.issued_ns > MAX_VALIDITY_NS):
        raise AnchorError("expired, future, replayed or excessive-validity anchor")
    fields = (
        "tenant", "dataset", "purpose", "policy_revision", "policy_sha256",
        "run_id", "provenance_root", "receipt_sha256",
    )
    for field in fields:
        actual = getattr(receipt, field, None)
        expected = getattr(anchor, field)
        if isinstance(expected, str):
            if not isinstance(actual, str) or not hmac.compare_digest(expected, actual):
                raise AnchorError("anchor does not bind to this exact receipt")
        elif type(actual) is not int or actual != expected:
            raise AnchorError("anchor does not bind to this exact receipt")
    for field in ("policy_sha256", "run_id", "provenance_root", "receipt_sha256"):
        if not _SHA256_RE.fullmatch(getattr(anchor, field)):
            raise AnchorError("malformed SHA-256 binding")
    key_bytes = pinned_public_keys.get(anchor.key_id)
    if not isinstance(key_bytes, bytes) or len(key_bytes) != 32:
        raise AnchorError("no valid independently pinned public key")
    try:
        signature = base64.b64decode(anchor.signature_b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise AnchorError("malformed anchor signature encoding") from exc
    if len(signature) != 64:
        raise AnchorError("malformed Ed25519 signature length")
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise AnchorError("Ed25519 verifier dependency unavailable") from exc
    try:
        Ed25519PublicKey.from_public_bytes(key_bytes).verify(signature, anchor.signed_bytes())
    except (InvalidSignature, ValueError) as exc:
        raise AnchorError("untrusted anchor signature") from exc
    return anchor.provenance_root
