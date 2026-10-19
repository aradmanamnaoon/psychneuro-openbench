"""Independent W03/P13 digest and P25 relationship verifier for private aggregate receipts.

This deliberately does not trust W03's own verification implementation. A hash
is an *integrity checksum*, not a digital signature or an authorization grant.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_KINDS = ("source", "split", "model", "benchmark")
_MAX_BYTES = 250_000


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


class ReceiptError(ValueError):
    """Invalid version, corrupted graph, unsupported scope or cross-system identity."""


class P13P25Receipt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    schema_version: Literal["w04-p13-p25-receipt-3"] = "w04-p13-p25-receipt-3"
    tenant: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,80}$")
    dataset: Literal["w03-original-synthetic"] = "w03-original-synthetic"
    purpose: Literal["internal-method-validation"] = "internal-method-validation"
    export_scope: Literal["aggregate-internal-only"] = "aggregate-internal-only"
    policy_revision: int = Field(ge=1)
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    run_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    provenance_root: str = Field(pattern=r"^[0-9a-f]{64}$")
    record: dict[str, Any]
    receipt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def verify_record(record: Mapping[str, Any]) -> tuple[str, str]:
    """Recompute every P13 edge and verify W03 run/result/source relationships.

    Strictly accepts W03's currently published *four-node linear DAG* and no
    other artifact kind. Upgrading the scientific contract requires v4.
    """
    if set(record) != {"run_id", "provenance_root", "nodes", "rights", "result"}:
        raise ReceiptError("unknown W03 report fields")
    if len(canonical(record)) > _MAX_BYTES:
        raise ReceiptError("excessive W03 report size")
    root, run_id = record["provenance_root"], record["run_id"]
    if not isinstance(root, str) or not _SHA.fullmatch(root):
        raise ReceiptError("malformed root")
    if not isinstance(run_id, str) or not _SHA.fullmatch(run_id):
        raise ReceiptError("malformed run identifier")
    if record["rights"] != "internal-synthetic-only":
        raise ReceiptError("unsupported rights declaration")
    nodes = record["nodes"]
    if not isinstance(nodes, list) or len(nodes) != 4:
        raise ReceiptError("expected exactly four P13 nodes")
    parent: str | None = None
    for index, item in enumerate(nodes):
        if not isinstance(item, dict) or set(item) != {"kind", "parents", "metadata", "sha256"}:
            raise ReceiptError("unknown P13 node fields")
        kind, parents, metadata, sha = (item[k] for k in ("kind", "parents", "metadata", "sha256"))
        if kind != _KINDS[index] or not isinstance(metadata, dict):
            raise ReceiptError("unexpected P13 node ordering or metadata")
        if not isinstance(parents, list) or parents != ([] if parent is None else [parent]):
            raise ReceiptError("missing, cyclic, or out-of-order P13 edge")
        if not isinstance(sha, str) or not _SHA.fullmatch(sha):
            raise ReceiptError("malformed node SHA")
        if digest({"kind": kind, "parents": parents, "metadata": metadata}) != sha:
            raise ReceiptError("tampered P13 node")
        parent = sha
    if parent != root:
        raise ReceiptError("P13 root mismatch")
    result = record["result"]
    if not isinstance(result, dict) or set(result) != {
        "schema_version", "run_id", "source_sha256", "split_sha256", "provenance_root",
        "rights", "n_train_groups", "n_test_groups", "outer_balanced_accuracy",
        "dummy_outer_balanced_accuracy", "test_balanced_accuracy", "selected_c"
    }:
        raise ReceiptError("unexpected W03 result fields")
    if result["schema_version"] != "w03-engine-1" or result["rights"] != record["rights"]:
        raise ReceiptError("unsupported scientific result version/rights")
    if result["run_id"] != run_id or result["provenance_root"] != root:
        raise ReceiptError("W03 run/root relationship mismatch")
    if nodes[0]["metadata"].get("source_sha256") != result["source_sha256"]:
        raise ReceiptError("P13 source/result disagreement")
    if nodes[1]["metadata"].get("split_sha256") != result["split_sha256"]:
        raise ReceiptError("P13 split/result disagreement")
    if nodes[2]["metadata"].get("selected_c") != result["selected_c"]:
        raise ReceiptError("P13 model/result disagreement")
    if nodes[3]["metadata"].get("result_sha256") != digest({k: v for k, v in result.items()
                                                              if k != "provenance_root"}):
        raise ReceiptError("P13 benchmark/result digest mismatch")
    # W03 assigns run_id FROM request + original source + split; a content-hash
    # chain by itself does not prove that the run identity is internally valid.
    # Rechecking it also detects incorrectly rebound archived aggregate reports.
    benchmark_metadata = nodes[3]["metadata"]
    request = benchmark_metadata.get("request")
    benchmark = benchmark_metadata.get("benchmark")
    model = nodes[2]["metadata"]
    source = nodes[0]["metadata"]
    split = nodes[1]["metadata"]
    if not isinstance(request, dict) or set(request) != {
        "generator_seed", "split_seed", "n_participants", "trials_per_participant",
        "outer_folds", "inner_folds", "predictors"
    }:
        raise ReceiptError("missing or unsupported W03 experiment request")
    if (type(request["generator_seed"]) is not int or
            type(request["split_seed"]) is not int or
            type(request["n_participants"]) is not int or
            type(request["trials_per_participant"]) is not int or
            request["outer_folds"] != 3 or request["inner_folds"] != 2 or
            request["predictors"] != ["difficulty", "stimulus_condition"] or
            not 0 <= request["generator_seed"] < 2**64 or
            not 0 <= request["split_seed"] < 2**64 or
            not 24 <= request["n_participants"] <= 80 or
            not 8 <= request["trials_per_participant"] <= 40):
        raise ReceiptError("invalid W03 source/split/frozen predictors")
    expected_run_id = digest({"contract": "w03-engine-1", "request": request,
                              "source": result["source_sha256"],
                              "split": result["split_sha256"]})
    if expected_run_id != run_id:
        raise ReceiptError("W03 deterministic run identity mismatch")
    if (source.get("seed") != request["generator_seed"] or
            source.get("rights") != "internal-synthetic-only" or
            split.get("seed") != request["split_seed"] or
            split.get("train_groups") != result["n_train_groups"] or
            split.get("test_groups") != result["n_test_groups"] or
            model.get("predictors") != request["predictors"] or
            model.get("model_spec_only") is not True or
            model.get("trained_model_bytes_hash") is not None):
        raise ReceiptError("W03 node evidence contradicts source/split/model declaration")
    if not isinstance(benchmark, dict) or set(benchmark) != {
        "outer_scores", "dummy_outer_scores", "outer_selected_c", "final_c",
        "sealed_test_balanced_accuracy", "metric", "unit"
    }:
        raise ReceiptError("incomplete benchmark provenance metadata")
    if (benchmark["metric"] != "balanced_accuracy" or
            benchmark["unit"] != "fictional_participant" or
            benchmark["final_c"] != result["selected_c"] or
            benchmark["sealed_test_balanced_accuracy"] != result["test_balanced_accuracy"]):
        raise ReceiptError("prespecified metric or final holdout mismatch")
    scores = benchmark["outer_scores"]
    dummy = benchmark["dummy_outer_scores"]
    choices = benchmark["outer_selected_c"]
    if (not all(isinstance(x, list) and len(x) == 3 for x in (scores, dummy, choices)) or
            any(type(x) not in (int, float) or not 0 <= x <= 1
                for x in [*scores, *dummy]) or
            any(type(x) not in (int, float) or x not in (0.1, 1.0)
                for x in choices) or
            abs(sum(scores)/3 - result["outer_balanced_accuracy"]) > 1e-12 or
            abs(sum(dummy)/3 - result["dummy_outer_balanced_accuracy"]) > 1e-12):
        raise ReceiptError("fold metrics disagree with the reported mean or model grid")
    for field in ("source_sha256", "split_sha256"):
        value = result[field]
        if not isinstance(value, str) or not _SHA.fullmatch(value):
            raise ReceiptError("malformed source/split SHA")
    if (type(result["n_train_groups"]) is not int or type(result["n_test_groups"]) is not int
            or result["n_train_groups"] < 1 or result["n_test_groups"] < 1):
        raise ReceiptError("invalid group accounting")
    for field in ("outer_balanced_accuracy", "dummy_outer_balanced_accuracy",
                  "test_balanced_accuracy"):
        if type(result[field]) not in (float, int) or not 0 <= result[field] <= 1:
            raise ReceiptError("invalid reported metric")
    if type(result["selected_c"]) not in (float, int) or result["selected_c"] not in (0.1, 1.0):
        raise ReceiptError("invalid prespecified model")
    return run_id, root


def issue_receipt(record: Mapping[str, Any], *, tenant: str,
                  policy_revision: int, policy_sha256: str) -> P13P25Receipt:
    """Caller MUST verify a fresh P25 read/export permit separately before issue."""
    run_id, root = verify_record(record)
    fields = {"schema_version": "w04-p13-p25-receipt-3", "tenant": tenant,
              "dataset": "w03-original-synthetic", "purpose": "internal-method-validation",
              "export_scope": "aggregate-internal-only", "policy_revision": policy_revision,
              "policy_sha256": policy_sha256, "run_id": run_id,
              "provenance_root": root, "record": dict(record)}
    receipt = P13P25Receipt.model_validate({**fields, "receipt_sha256": digest(fields)})
    if len(canonical(receipt.model_dump(mode="json"))) > _MAX_BYTES:
        raise ReceiptError("excessive receipt size")
    return receipt


def verify_receipt(receipt: P13P25Receipt, *, tenant: str,
                   expected_policy_sha256: str, trusted_root: str | None = None) -> dict[str, Any]:
    """Integrity and tenant-binding only; caller MUST recheck current P25 ACL.

    Supplying an independently stored trusted_root provides tamper detection;
    neither this record nor SHA-256 alone provides signer authenticity.
    """
    raw = receipt.model_dump(mode="json")
    if len(canonical(raw)) > _MAX_BYTES:
        raise ReceiptError("excessive receipt size")
    payload = {k: v for k, v in raw.items() if k != "receipt_sha256"}
    if not hmac.compare_digest(receipt.receipt_sha256, digest(payload)):
        raise ReceiptError("receipt checksum mismatch")
    if receipt.tenant != tenant or not hmac.compare_digest(receipt.policy_sha256,
                                                            expected_policy_sha256):
        raise ReceiptError("foreign tenant or stale policy")
    run_id, root = verify_record(receipt.record)
    if (run_id != receipt.run_id or root != receipt.provenance_root or
            (trusted_root is not None and root != trusted_root)):
        raise ReceiptError("P13/P25 identity or trusted-root mismatch")
    return receipt.record
