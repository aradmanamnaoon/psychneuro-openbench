"""W04 deterministic local microbenchmark, prints environment and p50/p95 timings.

Performance numbers are NOT W03 model training speed or hosted API latency.
"""
from __future__ import annotations

import json
import platform
import tempfile
import time
import tracemalloc
from hashlib import sha256
from pathlib import Path

from psychneuro.w04.jobs import JobStore
from psychneuro.w04.rights import W03_INTERNAL, Action, Principal, decide


def measure(func, n: int = 200) -> dict[str, float]:
    samples = []
    tracemalloc.start()
    for _ in range(n):
        t0 = time.perf_counter_ns()
        func()
        samples.append((time.perf_counter_ns() - t0) / 1_000_000)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    samples.sort()
    return {"n": n, "p50_ms": samples[n // 2], "p95_ms": samples[int(n * .95) - 1],
            "peak_tracemalloc_bytes": peak}


def main() -> None:
    role = Principal(subject="bench", role="researcher")
    with tempfile.TemporaryDirectory() as td:
        jobs = JobStore(Path(td) / "store.sqlite")
        ids = (sha256(f"job-{i}".encode()).hexdigest() for i in range(200))
        results = {
            "environment": {"python": platform.python_version(), "machine": platform.machine(),
                            "platform": platform.platform()},
            "seed": "none; deterministic IDs only", "fixture": "internal synthetic policy + 200 unique SQLite insert IDs",
            "rights": measure(lambda: decide(W03_INTERNAL, role, Action.RUN)),
            "jobs_create": measure(lambda: jobs.create(next(ids), role.subject, correlation="bench")),
        }
        print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
