"""PM-14 hosted-only, opt-in CPU/memory profiling of ONE synthetic pipeline run.

NOT executed by ChatGPT. Run only in an authorized, budget-approved private
GitHub Actions job; published source/fixtures are never benchmark measurements.
No participant rows or machine/user identity are saved to the metrics output.
"""
from __future__ import annotations

import argparse
import json
import platform
import time
import tracemalloc
from pathlib import Path
from typing import Any

from .workflow import Scenario, run_scenario

PROFILE_PROTOCOL = "pm14-synthetic-small-perf-v1"


def measure_small_synthetic_run(project_root: Path) -> dict[str, Any]:
    """Profile a strictly fixed single seeded 24x20 synthetic cohort.

    Python's tracemalloc does NOT track all native NumPy/scikit-learn memory.
    Linux ru_maxrss is process-wide peak, not an isolated scenario peak. Wall
    and CPU timings fluctuate with runner load; not promises or benchmarks
    without exact hosted logs and repetition.
    """
    scenario = Scenario(
        generator_seed=73, n_participants=24,
        trials_per_participant=20, repeats=1,
    )
    baseline = 0
    peak_rss: int | None = None
    if platform.system() == "Linux":
        import resource

        baseline = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if tracemalloc.is_tracing():
        raise RuntimeError("cannot isolate allocation profiling: tracemalloc already active")
    tracemalloc.start()
    cpu_start = time.process_time()
    wall_start = time.perf_counter()
    try:
        report = run_scenario(scenario, project_root)
        wall_seconds = time.perf_counter() - wall_start
        cpu_seconds = time.process_time() - cpu_start
        _current, traced_peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if platform.system() == "Linux":
        import resource

        peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {
        "measurement_protocol": PROFILE_PROTOCOL,
        "measurement_state": "measured_in_current_process_not_externally_verified",
        "source_policy": "synthetic-original",
        "python_version": platform.python_version(),
        "scenario": {
            "generator_seed": 73,
            "split_seed": 42,
            "fictional_participants": 24,
            "trials_per_fictional_participant": 20,
            "repeats": 1,
            "trial_budget": 480,
        },
        "wall_seconds": round(wall_seconds, 6),
        "process_cpu_seconds": round(cpu_seconds, 6),
        "python_tracemalloc_peak_bytes": traced_peak,
        "linux_process_peak_rss_kib_before": baseline if peak_rss is not None else None,
        "linux_process_peak_rss_kib_after": peak_rss,
        "eligibility_status": report["status"],
        "n_eligible": report["n_eligible"],
        "n_requested": report["n_requested"],
        "report_sha256": report["report_sha256"],
        "caveats": [
            "tracemalloc does not capture all native allocations",
            "Linux ru_maxrss is process-wide peak, not isolated run delta",
            "one hosted observation cannot justify caching or performance claims",
            "no person-level data, measurements or external datasets used",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure bounded synthetic CPU/memory")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = measure_small_synthetic_run(Path(__file__).resolve().parents[2])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        "Synthetic profiling artifact written; wall/process CPU seconds and "
        "peak allocation/RSS stored under the requested hosted output path."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
