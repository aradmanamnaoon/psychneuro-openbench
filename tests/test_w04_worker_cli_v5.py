"""CLI private operator boundary; doubles ONLY, not real W03 model execution."""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace

P = Path(__file__).parents[1] / "src/psychneuro/w04/worker_cli_v5.py"
SPEC = importlib.util.spec_from_file_location("psychneuro.w04._worker_cli_v5_tests", P)
assert SPEC is not None and SPEC.loader is not None
cli = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cli
SPEC.loader.exec_module(cli)


def _args(db: Path, registry: Path) -> list[str]:
    return ["--database", str(db), "--registry", str(registry), "--tenant", "tenant-A"]


def test_deny_keyless_and_bad_identifiers_before_imports(tmp_path, monkeypatch, capsys):
    db, registry = tmp_path/"private.sqlite", tmp_path/"registry.json"
    db.touch(mode=0o600); registry.write_text("{}")
    monkeypatch.delenv("W04_PERMIT_KEY_HEX", raising=False)
    assert cli.main(_args(db, registry)) == 2
    assert cli.main(_args(db, registry) + ["--worker", "invalid name"]) == 2
    assert cli.main(_args(db, registry) + ["--limit", "1000"]) == 2
    assert "private W04 worker" in capsys.readouterr().err


def test_deny_world_readable_db_and_missing_registry(tmp_path, monkeypatch):
    db, registry = tmp_path/"world.sqlite", tmp_path/"registry.json"
    db.touch(); db.chmod(0o644); registry.write_text("{}")
    monkeypatch.setenv("W04_PERMIT_KEY_HEX", "ab" * 32)
    assert cli.main(_args(db, registry)) == 2
    db.chmod(0o600)
    registry.unlink()
    assert cli.main(_args(db, registry)) == 2


def test_one_shot_dry_run_and_bounded_execution_with_doubles(tmp_path, monkeypatch, capsys):
    db, registry = tmp_path/"private.sqlite", tmp_path/"registry.json"
    db.touch(mode=0o600); db.chmod(0o600); registry.write_text("{}")
    monkeypatch.setenv("W04_PERMIT_KEY_HEX", "ab" * 32)
    calls: list[str] = []
    maintenance_calls: list[tuple[str, str]] = []
    fake_policy = types.ModuleType("psychneuro.w04.policy_v2")
    fake_queue = types.ModuleType("psychneuro.w04.queue_v2")
    fake_worker = types.ModuleType("psychneuro.w04.private_worker_v4")
    class PolicyStore:
        def __init__(self, path, *, permit_key):
            assert path == db and permit_key == bytes.fromhex("ab" * 32)
    class QueueStore:
        def __init__(self, path):
            assert path == db

        def reconcile_terminal(self, *, tenant: str, correlation: str) -> int:
            maintenance_calls.append((tenant, correlation))
            return 0
    class AtomicWorker:
        def __init__(self, *, database, policy, queue, registry_path):
            assert database == db and registry_path == registry
        def due(self, *, tenant, limit):
            assert tenant == "tenant-A" and 1 <= limit <= 10
            return ["id1", "id2"][:limit]
        def run_one(self, *, tenant, job_id, worker, correlation):
            calls.append(job_id)
            return SimpleNamespace(state="succeeded")
    fake_policy.PolicyStore = PolicyStore
    fake_queue.QueueStore = QueueStore
    fake_worker.AtomicWorker = AtomicWorker
    for name, module in [(fake_policy.__name__, fake_policy),
                         (fake_queue.__name__, fake_queue),
                         (fake_worker.__name__, fake_worker)]:
        monkeypatch.setitem(sys.modules, name, module)
    assert cli.main(_args(db, registry) + ["--dry-run"]) == 0
    assert calls == []
    assert maintenance_calls == []  # No maintenance writes in dry-run mode.
    assert json.loads(capsys.readouterr().out)["due"] == 1
    assert cli.main(_args(db, registry) + ["--limit", "2"]) == 0
    assert maintenance_calls == [("tenant-A", "operator-scan")]
    assert calls == ["id1", "id2"]
    assert json.loads(capsys.readouterr().out)["succeeded"] == 2
