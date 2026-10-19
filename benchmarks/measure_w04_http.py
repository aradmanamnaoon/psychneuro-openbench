"""Private in-process W04 HTTP benchmark; no external endpoints or human data.

Reports measured latency distributions, not hosted throughput or browser paint.
"""
from __future__ import annotations

import csv
import os
import platform
import resource
import statistics
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

import fastapi
import sklearn
from fastapi.testclient import TestClient

from psychneuro.w03.contracts import ExperimentRequest
from psychneuro.w04.durable_bridge import source_sha256
from psychneuro.w04.policy_v2 import PolicyRecord, PolicyStore
from psychneuro.w04.rights import Principal
from psychneuro.w04.strict_facade import create_strict_app

TOKEN = "synthetic-only-benchmark-token-000000000001"
KEY = b"synthetic-only-internal-benchmark-permit-key-not-for-hosting"
REQUEST = ExperimentRequest(generator_seed=73, split_seed=42,
                            n_participants=36, trials_per_participant=12)


def measure(name: str, operation: Callable[[], None], n: int) -> dict[str, object]:
    for _ in range(5):
        operation()
    times: list[float] = []
    begin = time.perf_counter()
    for _ in range(n):
        start = time.perf_counter_ns()
        operation()
        times.append((time.perf_counter_ns() - start) / 1_000_000)
    elapsed = time.perf_counter() - begin
    ordered = sorted(times)
    return {
        "operation": name, "n": n, "warmup": 5, "concurrency": 1,
        "median_ms": round(statistics.median(ordered), 4),
        "p95_ms": round(ordered[max(0, (95 * n + 99) // 100 - 1)], 4),
        "observed_requests_per_second": round(n / elapsed, 2),
        "peak_process_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def main() -> None:
    output = Path(os.getenv("W04_BENCHMARK_OUTPUT", "/tmp/w04-private-http-benchmark.csv"))
    registry = Path(__file__).resolve().parents[1] / "data" / "registry.json"
    with tempfile.TemporaryDirectory() as temporary:
        db = Path(temporary) / "test.sqlite"
        rights = PolicyStore(db, permit_key=KEY)
        rights.install(PolicyRecord(
            tenant="local", source_sha256=source_sha256(REQUEST, registry),
            actions=frozenset({"run", "read_aggregate", "export_aggregate"}),
            attestation_ref="benchmark-fictional-fixture-reviewed-v1",
            retention_until_ns=10**20,
        ), operator="benchmark")
        app = create_strict_app(db_path=db, registry_path=registry,
                                credentials={TOKEN: Principal(
                                    tenant="local", subject="benchmark", role="researcher")},
                                policy=rights)
        client = TestClient(app)
        headers = {"X-Internal-Token": TOKEN}
        started = time.perf_counter()
        run = client.post("/w04/v2/runs", headers=headers,
                          json=REQUEST.model_dump(mode="json", exclude={"predictors"}))
        if run.status_code != 201:
            raise RuntimeError(f"fixture run failed with HTTP {run.status_code}")
        fit_seconds = time.perf_counter() - started
        run_id = run.json()["run_id"]

        def make(path: str, auth: bool = True) -> Callable[[], None]:
            def call() -> None:
                response = client.get(path, headers=headers if auth else {})
                if response.status_code != 200:
                    raise RuntimeError(f"HTTP {response.status_code} on benchmark path")
            return call

        rows = [
            measure("health_baseline", make("/health", False), 100),
            measure("authorized_run_read", make(f"/w04/v2/runs/{run_id}"), 100),
            measure("authorized_p13_graph", make(f"/w04/v2/runs/{run_id}/graph"), 100),
            measure("authorized_artifact_export",
                    make(f"/w04/v2/runs/{run_id}/artifact"), 60),
        ]
        for row in rows:
            row.update({
                "python": platform.python_version(),
                "fastapi": fastapi.__version__,
                "scikit_learn": sklearn.__version__,
                "cpu": (Path("/proc/cpuinfo").read_text().split("model name\t: ")[1].splitlines()[0]
                        if Path("/proc/cpuinfo").is_file() and "model name\t: "
                        in Path("/proc/cpuinfo").read_text() else platform.processor()),
                "synthetic_participants": 36, "seed": 73, "split_seed": 42,
                "one_model_fit_seconds": round(fit_seconds, 4),
                "caveat": "in-process TestClient only; not browser/network/hosted load",
            })
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(output.read_text())


if __name__ == "__main__":
    main()
