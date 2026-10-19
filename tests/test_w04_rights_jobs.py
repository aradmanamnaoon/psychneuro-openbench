from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date
from hashlib import sha256
from pathlib import Path

import pytest

from psychneuro.w04.jobs import JobStore, RevisionConflict
from psychneuro.w04.rights import W03_INTERNAL, Action, DatasetRights, Principal, decide

RESEARCHER = Principal(subject="researcher", role="researcher")
VIEWER = Principal(subject="viewer", role="viewer")


def test_internal_policy_denies_export_data_and_viewer_execute() -> None:
    assert decide(W03_INTERNAL, RESEARCHER, Action.RUN).allowed
    assert not decide(W03_INTERNAL, VIEWER, Action.RUN).allowed
    assert not decide(W03_INTERNAL, RESEARCHER, Action.EXPORT_DATA).allowed
    assert decide(W03_INTERNAL, VIEWER, Action.READ_AGGREGATE).allowed
    assert not decide(W03_INTERNAL, VIEWER, Action.EXPORT_AGGREGATE).allowed


@pytest.mark.parametrize("origin,consent", [("human", "unknown"), ("human", "documented"), ("third-party", "documented")])
def test_unapproved_non_synthetic_denied(origin: str, consent: str) -> None:
    rights = DatasetRights(dataset_id="external", origin=origin,
                           license_expression="CC-BY-4.0", consent=consent,
                           verified_by="asserted-reviewer", approved_actions=frozenset({Action.RUN}))
    assert not decide(rights, RESEARCHER, Action.RUN).allowed


def test_revocation_and_expiry() -> None:
    changed = W03_INTERNAL.model_copy(update={"revoked": True})
    assert decide(changed, RESEARCHER, Action.RUN).reason == "revoked"
    changed = W03_INTERNAL.model_copy(update={"expires_on": date(2026, 1, 1)})
    assert decide(changed, RESEARCHER, Action.RUN, today=date(2026, 10, 19)).reason == "expired"
    changed = W03_INTERNAL.model_copy(update={"verified_by": None})
    assert decide(changed, RESEARCHER, Action.RUN).reason == "no_review"


def test_job_lifecycle_cancel_resume_checkpoint(tmp_path: Path) -> None:
    job_id = sha256(b"synthetic-job").hexdigest()
    store = JobStore(tmp_path / "jobs.sqlite")
    a = store.create(job_id, "researcher", correlation="trace-1")
    assert store.create(job_id, "researcher", correlation="trace-1") == a
    b = store.advance(job_id, expected_revision=a.revision, target="running", actor="researcher", correlation="trace-1")
    assert b.attempts == 1
    c = store.advance(job_id, expected_revision=b.revision, target="cancel_requested", actor="researcher", correlation="trace-1", checkpoint="batch-3")
    d = store.advance(job_id, expected_revision=c.revision, target="cancelled", actor="researcher", correlation="trace-1")
    e = store.advance(job_id, expected_revision=d.revision, target="queued", actor="researcher", correlation="trace-2")
    f = store.advance(job_id, expected_revision=e.revision, target="running", actor="researcher", correlation="trace-2")
    g = store.advance(job_id, expected_revision=f.revision, target="succeeded", actor="researcher", correlation="trace-2", checkpoint="final-artifact-sha")
    assert (g.state, g.checkpoint, g.attempts) == ("succeeded", "final-artifact-sha", 2)
    assert len(store.audit(job_id)) == 7
    with pytest.raises(RevisionConflict):
        store.advance(job_id, expected_revision=f.revision, target="failed", actor="researcher", correlation="trace-2")
    assert JobStore(store.path).get(job_id) == g


def test_concurrent_cas_single_winner(tmp_path: Path) -> None:
    job_id = sha256(b"race").hexdigest()
    store = JobStore(tmp_path / "jobs.sqlite")
    store.create(job_id, "researcher", correlation="race")

    def start(_: int) -> bool:
        try:
            store.advance(job_id, expected_revision=0, target="running", actor="researcher", correlation="race")
            return True
        except RevisionConflict:
            return False

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(start, range(12)))
    assert sum(results) == 1
    assert store.get(job_id).revision == 1
    with pytest.raises(RevisionConflict):
        store.create(job_id, "different", correlation="race")


def test_fail_before_success_without_checkpoint(tmp_path: Path) -> None:
    job_id = sha256(b"checkpoint").hexdigest()
    store = JobStore(tmp_path / "jobs.sqlite")
    store.create(job_id, "researcher", correlation="id")
    job = store.advance(job_id, expected_revision=0, target="running", actor="researcher", correlation="id")
    with pytest.raises(RevisionConflict):
        store.advance(job_id, expected_revision=job.revision, target="succeeded", actor="researcher", correlation="id")


def test_rights_ledger_event_chain_tamper_detection(tmp_path: Path) -> None:
    import sqlite3

    from psychneuro.w04.ledger import LedgerStore

    ledger = LedgerStore(tmp_path / "audit.sqlite")
    first = ledger.append(event_type="permission_evaluated", dataset_id="w03-original-synthetic",
                          action="run", allowed=True, actor_pseudonym="researcher", correlation_id="trace-1")
    second = ledger.append(event_type="revoked", dataset_id="w03-original-synthetic",
                           action="run", allowed=False, actor_pseudonym="maintainer", correlation_id="trace-2")
    assert ledger.verify(trusted_root=second)[0] == 2
    with pytest.raises(ValueError, match="independent anchor"):
        ledger.verify(trusted_root=first)
    with sqlite3.connect(ledger.path) as db:
        db.execute("UPDATE w04_rights_ledger SET event_json=? WHERE seq=1", ('{}',))
    with pytest.raises(ValueError):
        ledger.verify()


def test_w04_cli_rights_and_audit(tmp_path, capsys):
    from psychneuro.w04.cli import main
    from psychneuro.w04.rights import W03_INTERNAL
    rights = tmp_path / "rights.json"
    ledger = tmp_path / "ledger.sqlite"
    rights.write_text(W03_INTERNAL.model_dump_json(), encoding="utf-8")
    assert main(["review-rights", "--rights", str(rights), "--action", "run",
                 "--role", "viewer", "--ledger", str(ledger)]) == 3
    assert main(["review-rights", "--rights", str(rights), "--action", "run",
                 "--role", "researcher", "--ledger", str(ledger)]) == 0
    assert main(["verify-ledger", "--ledger", str(ledger)]) == 0
    stdout = capsys.readouterr().out
    assert '"allowed":false' in stdout and '"allowed":true' in stdout
    assert '"records": 2' in stdout
