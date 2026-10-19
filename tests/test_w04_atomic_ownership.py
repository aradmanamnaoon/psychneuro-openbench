"""Adversarial W03/P13 + W04/P25 atomic ownership tests (synthetic only)."""
from __future__ import annotations

import sqlite3
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

from psychneuro.w03.store import RunStore
from psychneuro.w03.vault import digest, make_chain, portable_chain
from psychneuro.w04.product import OwnerBoundRunStore, TenantRunACL
from psychneuro.w04.rights import Principal

ALICE = Principal(subject="alice", tenant="lab-a", role="researcher")
BOB = Principal(subject="bob", tenant="lab-b", role="researcher")


def _synthetic_record() -> dict[str, Any]:
    run_id = sha256(b"fictional-group-run").hexdigest()
    source = sha256(b"fictional-only-fixture").hexdigest()
    split = sha256(b"participant-disjoint-fixture").hexdigest()
    result = {
        "schema_version": "w03-engine-1",
        "run_id": run_id, "source_sha256": source, "split_sha256": split,
        "rights": "internal-synthetic-only",
        "n_train_groups": 21, "n_test_groups": 8,
        "outer_balanced_accuracy": 0.5, "dummy_outer_balanced_accuracy": 0.5,
        "test_balanced_accuracy": 0.5, "selected_c": 0.1,
    }
    chain = make_chain(
        {"source_sha256": source},
        {"split_sha256": split},
        {"model_spec_only": True},
        {"result_sha256": digest(result)},
    )
    return {
        "run_id": run_id, "provenance_root": chain[-1].sha256,
        "nodes": portable_chain(chain), "rights": "internal-synthetic-only",
        "result": {**result, "provenance_root": chain[-1].sha256},
    }


def _setup(path: Path) -> tuple[RunStore, TenantRunACL]:
    return RunStore(path), TenantRunACL(path)


def _counts(path: Path) -> tuple[int, int, int]:
    with sqlite3.connect(path) as db:
        return tuple(
            int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in ("runs", "provenance_index", "w04_run_acl")
        )


def test_atomic_success_replay_and_foreign_owner_denied(tmp_path: Path) -> None:
    path = tmp_path / "atomic.sqlite"
    runs, acl = _setup(path)
    record = _synthetic_record()
    alice = OwnerBoundRunStore(runs, acl, ALICE)
    alice.put(record)
    alice.put(record)
    assert runs.get(record["run_id"]) == record
    assert _counts(path) == (1, 4, 1)
    acl.check(record["run_id"], ALICE)
    with pytest.raises(PermissionError):
        acl.check(record["run_id"], BOB)
    with pytest.raises(PermissionError):
        OwnerBoundRunStore(runs, acl, BOB).put(record)
    assert _counts(path) == (1, 4, 1)


def test_owner_claim_failure_rolls_back_run_and_all_provenance(tmp_path: Path) -> None:
    path = tmp_path / "rollback.sqlite"
    runs, acl = _setup(path)
    record = _synthetic_record()
    with sqlite3.connect(path) as db:
        db.execute(
            "CREATE TRIGGER reject_claim BEFORE INSERT ON w04_run_acl "
            "BEGIN SELECT RAISE(ABORT, 'injected owner write failure'); END"
        )
    with pytest.raises(sqlite3.IntegrityError, match="injected owner"):
        OwnerBoundRunStore(runs, acl, ALICE).put(record)
    assert _counts(path) == (0, 0, 0)
    assert runs.get(record["run_id"]) is None


def test_unowned_historical_run_requires_audited_migration(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite"
    runs, acl = _setup(path)
    record = _synthetic_record()
    runs.put(record)
    with pytest.raises(PermissionError, match="migration"):
        OwnerBoundRunStore(runs, acl, ALICE).put(record)
    assert _counts(path) == (1, 4, 0)


def test_corrupt_data_cannot_claim_owner(tmp_path: Path) -> None:
    path = tmp_path / "tampered.sqlite"
    runs, acl = _setup(path)
    record = _synthetic_record()
    record["result"]["test_balanced_accuracy"] = 0.99
    with pytest.raises(ValueError):
        OwnerBoundRunStore(runs, acl, ALICE).put(record)
    assert _counts(path) == (0, 0, 0)


def test_run_and_acl_cannot_span_nonatomic_databases(tmp_path: Path) -> None:
    runs = RunStore(tmp_path / "runs.sqlite")
    acl = TenantRunACL(tmp_path / "owner.sqlite")
    with pytest.raises(ValueError, match="same SQLite file"):
        OwnerBoundRunStore(runs, acl, ALICE).put(_synthetic_record())
