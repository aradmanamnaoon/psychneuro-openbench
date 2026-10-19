"""W03 synthetic-only quality and adversarial gates; no external participant data."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from psychneuro.w03.api import create_app
from psychneuro.w03.contracts import ExperimentRequest, RunResult
from psychneuro.w03.nested import nested_grouped_benchmark, validate_isolation
from psychneuro.w03.store import ConflictError, RunStore
from psychneuro.w03.vault import digest, make_chain, portable_chain, verify_serialized


@dataclass(frozen=True)
class FictionalTrial:
    participant_id: str
    difficulty: float
    stimulus_condition: str
    correct: int


def trials() -> tuple[FictionalTrial, ...]:
    # Explicit deterministic software-only scenario; each subject supplies 12 rows.
    return tuple(FictionalTrial(f"fictional-{p:02d}", (i % 4) / 5,
                                 "left" if i % 2 else "right", int(i % 3 != 0))
                 for p in range(36) for i in range(12))


def groups(rows: tuple[FictionalTrial, ...]) -> tuple[list[int], list[int]]:
    return ([i for i, row in enumerate(rows) if int(row.participant_id[-2:]) < 27],
            [i for i, row in enumerate(rows) if int(row.participant_id[-2:]) >= 27])


def test_manifest_forbids_timing_leak_and_unbounded_compute() -> None:
    assert ExperimentRequest().outer_folds == 3
    for payload in [
        {"predictors": ["correct", "difficulty"]},
        {"predictors": ["difficulty", "response_time_ms"]},
        {"n_participants": 10000},
        {"generator_seed": -1},
        {"outer_folds": 10},
        {"extra_field": "untrusted"},
    ]:
        with pytest.raises(ValidationError):
            ExperimentRequest.model_validate(payload)


def test_nested_grouped_cv_repeatability_and_reference_baseline() -> None:
    rows = trials()
    fit, heldout = groups(rows)
    first = nested_grouped_benchmark(rows, fit, heldout)
    second = nested_grouped_benchmark(rows, fit, heldout)
    assert first == second
    assert len(first.outer_scores) == len(first.dummy_scores) == 3
    assert all(0 <= v <= 1 for v in (*first.outer_scores, *first.dummy_scores))
    assert first.final_c in (0.1, 1.0)
    assert 0 <= first.test_score <= 1


def test_contamination_sentinel_rejects_duplicate_and_cross_group() -> None:
    rows = trials()
    train, test = groups(rows)
    with pytest.raises(ValueError, match="row contamination"):
        validate_isolation(rows, train, [train[0], *test[1:]])
    with pytest.raises(ValueError, match="participant contamination"):
        validate_isolation(rows, [*train[1:], test[0]], test[1:])
    with pytest.raises(ValueError, match="noninteger"):
        validate_isolation(rows, [True, *train[1:]], test)


def sample_record() -> dict[str, object]:
    nodes = make_chain({"source_sha256": "a" * 64, "rights": "internal-synthetic-only"},
                       {"split_sha256": "b" * 64}, {"score": 0.5, "result_sha256": digest({"score": 0.5})})
    return {"run_id": "c" * 64, "provenance_root": nodes[-1].sha256,
            "nodes": portable_chain(nodes), "rights": "internal-synthetic-only",
            "result": {"score": 0.5}}


def test_vault_tampering_wrong_root_and_missing_parents_fails() -> None:
    record = sample_record()
    verify_serialized(record["nodes"], record["provenance_root"])
    bad = json.loads(json.dumps(record["nodes"]))
    bad[0]["metadata"]["source_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="integrity"):
        verify_serialized(bad, record["provenance_root"])
    bad = json.loads(json.dumps(record["nodes"]))
    bad[1]["parents"] = []
    with pytest.raises(ValueError, match="parent|integrity"):
        verify_serialized(bad, record["provenance_root"])
    with pytest.raises(ValueError, match="root"):
        verify_serialized(record["nodes"], "0" * 64)


def test_sqlite_idempotency_conflict_reopen_and_tamper(tmp_path: Path) -> None:
    file = tmp_path / "private" / "runs.sqlite3"
    store = RunStore(file)
    record = sample_record()
    store.put(record)
    store.put(record)
    assert RunStore(file).get(record["run_id"]) == record
    changed = dict(record)
    changed["result"] = {"score": 0.6}
    with pytest.raises(ValueError, match="result provenance digest"):
        store.put(changed)
    alternate = sample_record()
    chain = make_chain({"source_sha256": "a" * 64, "rights": "internal-synthetic-only"},
                       {"split_sha256": "b" * 64}, {"score": 0.6, "result_sha256": digest({"score": 0.6})})
    alternate["nodes"] = portable_chain(chain)
    alternate["provenance_root"] = chain[-1].sha256
    alternate["result"] = {"score": 0.6}
    with pytest.raises(ConflictError):
        store.put(alternate)
    with sqlite3.connect(file) as conn:
        tampered = json.loads(conn.execute("SELECT payload FROM runs").fetchone()[0])
        tampered["nodes"][2]["metadata"]["score"] = 0.7
        conn.execute("UPDATE runs SET payload=?", (json.dumps(tampered),))
    with pytest.raises(ValueError, match="integrity"):
        store.get(record["run_id"])


def test_api_contract_auth_validation_and_retrieval(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from psychneuro.w03 import api

    def fake_execute(req: ExperimentRequest, registry: Path, store: RunStore) -> RunResult:
        result = RunResult(run_id="c" * 64, source_sha256="a" * 64,
                           split_sha256="b" * 64, provenance_root=sample_record()["provenance_root"],
                           n_train_groups=20, n_test_groups=8,
                           outer_balanced_accuracy=0.5,
                           dummy_outer_balanced_accuracy=0.5,
                           test_balanced_accuracy=0.5, selected_c=0.1)
        record = sample_record()
        # construct a new provenance chain for the new response, preserving its hash
        response = result.model_dump(mode="json")
        unsigned = {k: v for k, v in response.items() if k != "provenance_root"}
        chain = make_chain({"source_sha256": "a" * 64, "rights": "internal-synthetic-only"},
                           {"split_sha256": "b" * 64}, {"result_sha256": digest(unsigned)})
        record["nodes"] = portable_chain(chain)
        record["provenance_root"] = chain[-1].sha256
        result = result.model_copy(update={"provenance_root": chain[-1].sha256})
        record["result"] = result.model_dump(mode="json")
        store.put(record)
        return result

    monkeypatch.setattr(api, "execute", fake_execute)
    app = create_app(db_path=tmp_path / "runs.sqlite3", registry_path=tmp_path / "registry.json",
                     internal_token="a-private-test-token-123456")
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "internal-only"}
    assert client.post("/v1/runs", json={}).status_code == 403
    token = {"X-Internal-Token": "a-private-test-token-123456"}
    assert client.post("/v1/runs", json={"n_participants": 999}, headers=token).status_code == 422
    created = client.post("/v1/runs", json={}, headers=token)
    assert created.status_code == 200, created.text
    rid = created.json()["run_id"]
    assert client.get(f"/v1/runs/{rid}").status_code == 403
    assert client.get(f"/v1/runs/{rid}", headers=token).json() == created.json()
    assert len(client.get(f"/v1/runs/{rid}/provenance", headers=token).json()["nodes"]) == 3
    assert client.get(f"/v1/runs/{'0'*64}", headers=token).status_code == 404
    assert client.get("/v1/runs/bad-id", headers=token).status_code == 422


def test_repository_integration_with_real_registry(tmp_path: Path) -> None:
    """On the target repo, use its actual rights-checked loader; do not mock science."""
    from psychneuro.w03.service import execute

    registry = Path(__file__).resolve().parents[1] / "data" / "registry.json"
    if not registry.exists():
        pytest.skip("real checked-in registry unavailable in standalone sandbox copy")
    store = RunStore(tmp_path / "run.sqlite3")
    one = execute(ExperimentRequest(), registry, store)
    two = execute(ExperimentRequest(), registry, store)
    assert one == two
    assert store.get(one.run_id) is not None
    assert one.n_train_groups >= 6 and one.n_test_groups >= 2


def test_partial_group_rows_fail_but_entire_validation_group_can_be_reserved() -> None:
    rows = trials()
    train, test = groups(rows)
    with pytest.raises(ValueError, match="missing rows"):
        validate_isolation(rows, train[:-1], test)
    # An entire independent group may be omitted as the validation cohort.
    excluded = {i for i in train if rows[i].participant_id == "fictional-02"}
    validate_isolation(rows, [i for i in train if i not in excluded], test)


def test_sqlite_provenance_sidecar_tamper_and_missing_index_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "provenance.sqlite3"
    store = RunStore(path)
    record = sample_record()
    store.put(record)
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT ordinal, kind FROM provenance_index ORDER BY ordinal").fetchall()
        assert rows == [(0, "source"), (1, "split"), (2, "model"), (3, "benchmark")]
        conn.execute("UPDATE provenance_index SET node_sha256=? WHERE ordinal=2", ("0" * 64,))
    with pytest.raises(ValueError, match="sidecar integrity"):
        RunStore(path).get(record["run_id"])
    with pytest.raises(ValueError, match="sidecar integrity"):
        RunStore(path).put(record)
    with sqlite3.connect(path) as conn:
        conn.execute("DELETE FROM provenance_index")
    with pytest.raises(ValueError, match="sidecar integrity"):
        RunStore(path).get(record["run_id"])


def test_sqlite_atomic_conflict_preserves_prior_lineage(tmp_path: Path) -> None:
    path = tmp_path / "atomic.sqlite3"
    original = sample_record()
    store = RunStore(path)
    store.put(original)
    other = json.loads(json.dumps(original))
    other["result"]["score"] = 0.8
    with pytest.raises(ValueError):
        RunStore(path).put(other)
    assert RunStore(path).get(original["run_id"]) == original
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM provenance_index").fetchone()[0] == 4
