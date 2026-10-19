"""Content-addressed scientific provenance DAG: integrity, not authenticity."""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

SHA = re.compile(r"[0-9a-f]{64}\Z")


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


@dataclass(frozen=True)
class Node:
    kind: str
    parents: tuple[str, ...]
    metadata: Mapping[str, Any]
    sha256: str


def node(kind: str, parents: Sequence[str], metadata: Mapping[str, Any]) -> Node:
    if kind not in {"source", "split", "model", "benchmark"}:
        raise ValueError("unsupported provenance node")
    if any(not SHA.fullmatch(p) for p in parents) or len(parents) != len(set(parents)):
        raise ValueError("malformed provenance parent")
    stable = {"kind": kind, "parents": list(parents), "metadata": dict(metadata)}
    return Node(kind, tuple(parents), dict(metadata), digest(stable))


def verify(nodes: Sequence[Node], root: str) -> None:
    """Reject orphan edges, reordered nodes, duplicate hashes, cycles and tampering."""
    if not SHA.fullmatch(root):
        raise ValueError("invalid root digest")
    seen: set[str] = set()
    for item in nodes:
        if item.sha256 in seen:
            raise ValueError("duplicate provenance node")
        if any(p not in seen for p in item.parents):
            raise ValueError("missing or unordered provenance parent")
        if node(item.kind, item.parents, item.metadata).sha256 != item.sha256:
            raise ValueError("provenance integrity mismatch")
        seen.add(item.sha256)
    if len(nodes) != 4 or root != nodes[-1].sha256 or root not in seen:
        raise ValueError("invalid provenance root or node count")
    if [n.kind for n in nodes] != ["source", "split", "model", "benchmark"]:
        raise ValueError("unrecognized provenance chain")
    if nodes[0].parents or nodes[1].parents != (nodes[0].sha256,):
        raise ValueError("invalid source to split edge")
    if nodes[2].parents != (nodes[1].sha256,) or nodes[3].parents != (nodes[2].sha256,):
        raise ValueError("invalid model/benchmark edges")


def make_chain(source: Mapping[str, Any], split: Mapping[str, Any], model: Mapping[str, Any], benchmark: Mapping[str, Any]) -> tuple[Node, ...]:
    a = node("source", (), source)
    b = node("split", (a.sha256,), split)
    c = node("model", (b.sha256,), model)
    d = node("benchmark", (c.sha256,), benchmark)
    chain = (a, b, c, d)
    verify(chain, d.sha256)
    return chain


def portable_chain(nodes: Sequence[Node]) -> list[dict[str, object]]:
    return [{"kind": n.kind, "parents": list(n.parents), "metadata": dict(n.metadata), "sha256": n.sha256} for n in nodes]


def verify_serialized(raw: object, root: str) -> None:
    if not isinstance(raw, list) or len(raw) != 4:
        raise ValueError("malformed provenance index")
    converted: list[Node] = []
    for entry in raw:
        if not isinstance(entry, dict) or set(entry) != {"kind", "parents", "metadata", "sha256"}:
            raise ValueError("unknown provenance fields")
        if not isinstance(entry["metadata"], dict) or not isinstance(entry["parents"], list):
            raise TypeError("invalid provenance metadata/parents")
        if not isinstance(entry["kind"], str) or not isinstance(entry["sha256"], str):
            raise TypeError("invalid provenance identity")
        if any(not isinstance(p, str) for p in entry["parents"]):
            raise ValueError("invalid provenance edge")
        converted.append(Node(entry["kind"], tuple(entry["parents"]), entry["metadata"], entry["sha256"]))
    verify(converted, root)
