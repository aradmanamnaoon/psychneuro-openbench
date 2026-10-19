"""Isolated SQLite integration contract; fake policy/queue/W03 are TEST DOUBLES.

Production runs must execute tests with actual repo policy_v2, queue_v2 and
W03 source; this suite alone is *not* an actual W03 fitted benchmark result.
"""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import BaseModel, ConfigDict

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from test_w04_receipt_v3 import make_record  # synthetic graph fixture only
from test_w04_receipt_v3 import v as receipt

pmod = types.ModuleType("psychneuro.w04.policy_v2")
qmod = types.ModuleType("psychneuro.w04.queue_v2")


def canonical(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(o):
    return receipt.digest(o)


class PolicyError(PermissionError):
    pass


class JobConflict(RuntimeError):
    pass


class Permit(BaseModel):
    version: str = "p25-permit-2"
    tenant: str
    dataset: str = "w03-original-synthetic"
    subject: str
    purpose: str = "internal-method-validation"
    action: str
    policy_revision: int
    policy_sha256: str
    expires_ns: int
    correlation_id: str


class PolicyStore:
    def __init__(self, path: Path, source_sha256: str):
        self.path = path
        self.source_sha256 = source_sha256
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS p25_v2_policy(tenant TEXT,dataset TEXT,"
                       "revision INTEGER,payload TEXT,sha TEXT,PRIMARY KEY(tenant,dataset))")
            payload = {"revoked": False, "retention_until_ns": 10**20,
                       "source_sha256": source_sha256,
                       "actions": ["run", "read_aggregate"], "origin": "original-synthetic"}
            db.execute("INSERT OR IGNORE INTO p25_v2_policy VALUES(?,?,?,?,?)",
                       ("tenant-A", "w03-original-synthetic", 1, canonical(payload), digest(payload)))

    def authorize(self, *, tenant, dataset, subject, role, action, purpose, correlation_id, now_ns):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT revision,payload,sha FROM p25_v2_policy WHERE tenant=? AND dataset=?",
                             (tenant, dataset)).fetchone()
        if row is None or json.loads(row[1])["revoked"] or action not in json.loads(row[1])["actions"]:
            raise PolicyError("denied")
        if role not in {"researcher", "viewer", "maintainer"} or (role == "viewer" and action == "run"):
            raise PolicyError("role denied")
        return Permit(tenant=tenant, subject=subject, action=action, policy_revision=row[0],
                      policy_sha256=row[2], expires_ns=now_ns+10**12, correlation_id=correlation_id)

    def validate_permit(self, permit, *, now_ns):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT revision,payload,sha FROM p25_v2_policy WHERE tenant=? AND dataset=?",
                             (permit.tenant, permit.dataset)).fetchone()
        if row is None or row[0] != permit.policy_revision or row[2] != permit.policy_sha256 or json.loads(row[1])["revoked"] or now_ns >= permit.expires_ns:
            raise PolicyError("stale")

    @staticmethod
    def _checked(tenant, dataset, revision, raw, sha):
        policy = json.loads(raw)
        if digest(policy) != sha:
            raise ValueError("policy corruption")
        return SimpleNamespace(**policy)

    @staticmethod
    def _verify_events(conn):
        return "0"*64

    def revoke(self):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT payload FROM p25_v2_policy WHERE tenant='tenant-A'").fetchone()
            p = json.loads(row[0]); p["revoked"] = True
            db.execute("UPDATE p25_v2_policy SET revision=2,payload=?,sha=? WHERE tenant='tenant-A'",
                       (canonical(p), digest(p)))


class QueueItem(BaseModel):
    id: str
    tenant: str
    subject: str
    dataset: str
    state: str
    fence: int
    revision: int


class QueueStore:
    def __init__(self, path: Path):
        self.path = path
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS w04_v2_jobs("
                       "id TEXT PRIMARY KEY,tenant TEXT,subject TEXT,dataset TEXT,idem TEXT,"
                       "payload_sha TEXT,state TEXT,revision INT,fence INT,attempts INT,"
                       "lease_until INT,next_attempt INT,checkpoint_stage TEXT,checkpoint_sha TEXT,"
                       "result_sha TEXT,worker TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS w04_v2_audit("
                       "seq INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT,tenant TEXT,revision INT,"
                       "event TEXT,actor TEXT,correlation TEXT,at_ns INT)")

    @staticmethod
    def _identifier(s):
        if not s or not s.replace("-", "").replace("_", "").isalnum() or len(s) > 80:
            raise ValueError("invalid identifier")
        return s

    def get(self, *, tenant, job_id, subject, maintainer=False):
        with sqlite3.connect(self.path) as db:
            r = db.execute("SELECT id,tenant,subject,dataset,state,fence,revision FROM w04_v2_jobs "
                           "WHERE id=? AND tenant=?", (job_id, tenant)).fetchone()
        if r is None or (r[2] != subject and not maintainer):
            raise JobConflict("not authorized")
        return QueueItem(id=r[0], tenant=r[1], subject=r[2], dataset=r[3], state=r[4], fence=r[5], revision=r[6])

    def claim(self, *, tenant, job_id, worker, correlation, lease_ns, now_ns):
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            r = db.execute("SELECT state,lease_until FROM w04_v2_jobs WHERE id=? AND tenant=?",
                           (job_id, tenant)).fetchone()
            if r is None or not (r[0] == "queued" or r[0] == "running" and r[1] <= now_ns):
                raise JobConflict("not claimable")
            db.execute("UPDATE w04_v2_jobs SET state='running',fence=fence+1,revision=revision+1,"
                       "attempts=attempts+1,lease_until=?,worker=? WHERE id=?",
                       (now_ns+lease_ns,worker,job_id))
        return self.get(tenant=tenant, job_id=job_id, subject=worker, maintainer=True)

    def fail(self, *, tenant, job_id, worker, fence, correlation, now_ns):
        with sqlite3.connect(self.path) as db:
            r = db.execute("SELECT state,worker,fence FROM w04_v2_jobs WHERE id=?", (job_id,)).fetchone()
            if r != ("running",worker,fence):
                raise JobConflict("stale")
            db.execute("UPDATE w04_v2_jobs SET state='queued',next_attempt=?,lease_until=0 WHERE id=?",
                       (now_ns+1_000_000_000,job_id))

    def cancel(self, job_id):
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE w04_v2_jobs SET state='cancelled',fence=fence+1,lease_until=0 WHERE id=?",(job_id,))


pmod.PolicyStore, pmod.PolicyError, pmod.Permit = PolicyStore, PolicyError, Permit
pmod.canonical, pmod.digest = canonical, digest
qmod.QueueStore, qmod.QueueItem, qmod.JobConflict = QueueStore, QueueItem, JobConflict
w03 = types.ModuleType("psychneuro.w03")
w03.__path__ = []
contracts = types.ModuleType("psychneuro.w03.contracts")


class ExperimentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    generator_seed: int
    split_seed: int
    n_participants: int
    trials_per_participant: int
    outer_folds: int
    inner_folds: int
    predictors: tuple[str, str]


contracts.ExperimentRequest = ExperimentRequest
@pytest.fixture
def env(tmp_path, monkeypatch):
    # Never contaminate the real suite: test-double injections live only
    # inside this fixture, and worker uses a private alias, not production name.
    monkeypatch.setitem(sys.modules, "psychneuro.w04.policy_v2", pmod)
    monkeypatch.setitem(sys.modules, "psychneuro.w04.queue_v2", qmod)
    monkeypatch.setitem(sys.modules, "psychneuro.w03.contracts", contracts)
    worker_name = "psychneuro.w04._worker_v4_contract_testonly"
    filename = SRC / "psychneuro/w04/private_worker_v4.py"
    spec = importlib.util.spec_from_file_location(worker_name, filename)
    assert spec is not None and spec.loader is not None
    worker_mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, worker_name, worker_mod)
    spec.loader.exec_module(worker_mod)
    db = tmp_path / "shared.sqlite"
    record = make_record()
    p = PolicyStore(db, record["result"]["source_sha256"])
    q = QueueStore(db)
    calls = []

    def fake_w03(request, registry_path, sink):
        calls.append(request)
        sink.put(record)
        return SimpleNamespace(run_id=record["run_id"],
                               source_sha256=record["result"]["source_sha256"])

    agent = worker_mod.AtomicWorker(database=db, policy=p, queue=q,
                                    registry_path=tmp_path / "registry.json", execute=fake_w03,
                                    source_preflight=lambda *_: record["result"]["source_sha256"])
    return agent,p,q,db,calls


def req(agent, seed=73):
    module = sys.modules[agent.__class__.__module__]
    return module.Request(version="w04-worker-request-4", generator_seed=seed,split_seed=42,
                              n_participants=36,trials_per_participant=12)


def submit(agent, key="key-A", request=None):
    return agent.submit(tenant="tenant-A", subject="researcher", role="researcher",
                        idempotency_key=key,request=request or req(agent),correlation="corr-1",now_ns=100)


def run(agent, job_id, now=200, worker="worker-A"):
    return agent.run_one(tenant="tenant-A", job_id=job_id, worker=worker,
                         correlation="corr-2",lease_ns=20_000_000_000,now_ns=now)


def test_atomic_commit_restart_read_and_duplicate_delivery(env):
    a,p,q,db,calls = env
    item = submit(a)
    assert submit(a).id == item.id
    assert a.due(tenant="tenant-A",now_ns=150) == [item.id]
    finished = run(a,item.id)
    assert finished.state == "succeeded"
    assert len(calls) == 1
    receipt_obj = a.read(tenant="tenant-A",subject="researcher",role="researcher",
                         job_id=item.id,correlation="read",now_ns=300)
    assert receipt_obj.run_id == make_record()["run_id"]
    with pytest.raises(JobConflict):
        run(a,item.id)
    assert a.due(tenant="tenant-A",now_ns=400)==[]
    again = type(a)(database=db,policy=p,queue=q,
                                    registry_path=Path("registry"),execute=lambda *_: None,
                                    source_preflight=lambda *_: make_record()["result"]["source_sha256"])
    assert again.read(tenant="tenant-A",subject="researcher",role="researcher",
                      job_id=item.id,correlation="read",now_ns=400).run_id == receipt_obj.run_id
    with sqlite3.connect(db) as c:
        assert c.execute("SELECT count(*) FROM w04_v4_artifacts").fetchone()[0] == 1
        assert c.execute("SELECT checkpoint_stage FROM w04_v2_jobs WHERE id=?",(item.id,)).fetchone()[0] == "persisted"


def test_cancel_during_fit_never_publishes(env):
    a,_p,q,db,_calls=env
    item=submit(a)
    def cancelling(*args):
        q.cancel(item.id)
        args[2].put(make_record())
        r=make_record()
        return SimpleNamespace(run_id=r["run_id"],source_sha256=r["result"]["source_sha256"])
    a.execute=cancelling
    with pytest.raises(JobConflict):
        run(a,item.id)
    with sqlite3.connect(db) as c:
        assert c.execute("SELECT count(*) FROM w04_v4_artifacts").fetchone()[0]==0
    assert q.get(tenant="tenant-A",job_id=item.id,subject="researcher").state=="cancelled"


def test_revocation_while_fitting_denies_publication(env):
    a,p,_q,db,_calls=env
    item=submit(a)
    def revoking(*args):
        p.revoke()
        args[2].put(make_record())
        r=make_record()
        return SimpleNamespace(run_id=r["run_id"],source_sha256=r["result"]["source_sha256"])
    a.execute=revoking
    with pytest.raises(PolicyError):
        run(a,item.id)
    with sqlite3.connect(db) as c:
        assert c.execute("SELECT count(*) FROM w04_v4_artifacts").fetchone()[0]==0
    with pytest.raises(PolicyError):
        submit(a,key="other")


def test_source_sha_wrong_denied_rollback(env):
    a,_p,_q,db,_calls=env
    item=submit(a)
    with sqlite3.connect(db) as c:
        row=c.execute("SELECT payload FROM p25_v2_policy WHERE tenant='tenant-A'").fetchone()
        payload=json.loads(row[0]); payload["source_sha256"]="f"*64
        c.execute("UPDATE p25_v2_policy SET payload=?,sha=?",(canonical(payload),digest(payload)))
    with pytest.raises(PolicyError):
        run(a,item.id)
    with sqlite3.connect(db) as c:
        assert c.execute("SELECT count(*) FROM w04_v4_artifacts").fetchone()[0]==0


def test_cross_user_and_tenant_denied(env):
    a,_p,_q,_db,_calls=env
    item=submit(a)
    run(a,item.id)
    with pytest.raises(JobConflict):
        a.read(tenant="tenant-A",subject="intruder",role="researcher",job_id=item.id,correlation="x",now_ns=300)
    with pytest.raises(JobConflict):
        a.read(tenant="tenant-B",subject="researcher",role="researcher",job_id=item.id,correlation="x",now_ns=300)


def test_corrupt_immutable_request_prevents_fitting(env):
    a,_p,_q,db,calls=env
    item=submit(a)
    with sqlite3.connect(db) as c:
        c.execute("UPDATE w04_v4_requests SET payload='{}' WHERE id=?",(item.id,))
    with pytest.raises(ValueError):
        run(a,item.id)
    assert calls==[]


def test_concurrent_submit_returns_one_job(env):
    a,_p,_q,db,_calls=env
    with ThreadPoolExecutor(max_workers=6) as pool:
        submitted=list(pool.map(lambda _: submit(a),range(15)))
    assert len({x.id for x in submitted})==1
    with sqlite3.connect(db) as c:
        assert c.execute("SELECT count(*) FROM w04_v4_requests").fetchone()[0]==1
    with pytest.raises(JobConflict):
        submit(a,request=req(a,74))


def test_expired_lease_fences_old_worker(env):
    a,_p,q,_db,calls=env
    item=submit(a)
    original=q.claim(tenant="tenant-A",job_id=item.id,worker="old",correlation="a",lease_ns=1000,now_ns=200)
    recovered=run(a,item.id,now=2000,worker="new")
    assert recovered.state=="succeeded"
    assert recovered.fence>original.fence
    assert len(calls)==1


def test_migration_denied_and_default_predictor_allowlist(env):
    a,p,q,db,_calls=env
    req_module = sys.modules[a.__class__.__module__]
    with pytest.raises(ValueError):
        req_module.Request(version="w04-worker-request-4",generator_seed=73,split_seed=42,
                           n_participants=36,trials_per_participant=12,
                           predictors=("reaction_time","stimulus_condition")).w03_payload()
    with sqlite3.connect(db) as c:
        c.execute("UPDATE w04_v4_meta SET version='100'")
    with pytest.raises(ValueError):
        type(a)(database=db,policy=p,queue=q,
                                registry_path=Path("registry"),execute=a.execute,
                                source_preflight=lambda *_: make_record()["result"]["source_sha256"])


def test_atomic_rollback_if_audit_insert_fails_after_artifact_insert(env):
    """Crash/injected SQLite ABORT cannot orphan a successful report/queue state."""
    a,_p,_q,db,calls = env
    item = submit(a,key="abort-test")
    with sqlite3.connect(db) as con:
        con.execute("CREATE TRIGGER stop_publish BEFORE INSERT ON w04_v2_audit "
                    "WHEN NEW.event='published_v4' BEGIN SELECT RAISE(ABORT,'fault injected'); END")
    with pytest.raises(sqlite3.IntegrityError, match="fault injected"):
        run(a,item.id)
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT count(*) FROM w04_v4_artifacts").fetchone()[0] == 0
        row = con.execute("SELECT state,checkpoint_stage,result_sha FROM w04_v2_jobs "
                          "WHERE id=?",(item.id,)).fetchone()
        assert row == ("queued",None,None)
    assert len(calls) == 1  # fitting occurred; publication rolled back


def test_immutable_artifact_checksum_checked_on_read(env):
    a,_p,_q,db,_calls = env
    item = submit(a,key="tamper-test")
    run(a,item.id)
    with sqlite3.connect(db) as con:
        con.execute("UPDATE w04_v4_artifacts SET payload='{}' WHERE id=?",(item.id,))
    with pytest.raises(ValueError, match="corrupted"):
        a.read(tenant="tenant-A",subject="researcher",role="researcher",
               job_id=item.id,correlation="tamper",now_ns=400)
