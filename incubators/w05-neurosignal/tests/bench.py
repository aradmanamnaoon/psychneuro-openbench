"""CPU/RSS benchmark: reports observed data only, not a latency SLA."""
from __future__ import annotations

import json
import platform
import statistics
import time
import tracemalloc

import numpy as np

from neurosignal.integration import run_synthetic


def main() -> None:
    observations = []
    for samples, chunk in [(1024, 64), (4096, 256), (8192, 512)]:
        for seed in range(5):
            tracemalloc.start()
            start = time.perf_counter()
            result = run_synthetic(seed=seed, samples=samples, chunk_size=chunk)
            latency_ms = (time.perf_counter() - start) * 1000
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            observations.append({"seed": seed, "samples": samples,
                                 "chunk_size": chunk, "latency_ms": latency_ms,
                                 "tracemalloc_peak_bytes": peak_bytes,
                                 "oracle_error_volts": result["stream_oracle_max_abs_error_volts"]})
    summary = []
    for samples in (1024, 4096, 8192):
        sub = [x for x in observations if x["samples"] == samples]
        summary.append({"samples": samples,
                        "median_latency_ms": statistics.median(x["latency_ms"] for x in sub),
                        "max_tracemalloc_peak_bytes": max(x["tracemalloc_peak_bytes"] for x in sub)})
    print(json.dumps({"platform": platform.platform(), "python": platform.python_version(),
                      "numpy": np.__version__, "measurements": observations,
                      "summary": summary, "limits": "tracemalloc excludes native NumPy allocations and does not equal peak RSS; warm process, n=5"}, indent=2))


if __name__ == "__main__":
    main()
