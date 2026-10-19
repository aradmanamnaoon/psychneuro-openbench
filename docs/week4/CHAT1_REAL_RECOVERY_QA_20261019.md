# W04 Chat 1 — real synthetic-fitting post-fit failure and cancellation review

**Date:** 2026-10-19. **Repository private.** Source for this review is the unchanged previous typed/format-tested worker commit `db3b63b72d12853bd5b9956369cdb32a8e9bb3fd`, plus [new fault-injection integration test](../../tests/test_w04_real_worker_recovery_v5.py), test blob `b69861e7bd5b4252db614aadc47973f07b9541d2`. Tests executed in an isolated Python 3.13.13 environment against GitHub-blob-matched W03/W04 modules; this is **not** GitHub-hosted CI.

## What was actually executed

- Two new tests invoke the **real W03 sklearn nested GroupKFold model fitter**, not a mocked score or substituted experiment result.
- **Test 1 — simulated post-fit exception:** after real W03 `execute()` emits its in-memory result but BEFORE SQLite publication, an injected RuntimeError stops the first attempt; the SQLite artifact table remains empty and the job is in queued/retry state. After bounded backoff, a fresh worker claim triggers real fitting again and publishes exactly one authorized result; the deterministic scientific `run_id` matches the first in-memory run. No partial report is visible before success.
- **Test 2 — cancellation after real fit but before commit:** after W03 `execute()` completes, a real `QueueStore.cancel` call revokes the running lease/fence. The stale worker's subsequent attempted publication raises `JobConflict` and the artifact table remains empty. After acknowledging cancellation and obtaining a fresh scoped P25 `run` permit, a new attempt completes real fitting and publishes one result matching the earlier in-memory `run_id`.
- **Explicit limitation:** this is in-process fault injection at a precisely chosen boundary, NOT an actual OS process crash/SIGKILL, GPU interruption, worker-overlap stress test, arbitrary mid-sklean fitting checkpoint, or independent right-to-use attestation.

## Final observed checks for this test-only addition

| Check | Evidence |
|---|---|
| New actual W03-fitter tests | **2 passed**, 80 warnings, 2.12 s on initial run |
| All staged W03/W04 tests together | **94 passed**, 241 warnings, 3.61 s after fixing import formatting |
| Ruff 0.17.1 | **PASS** — `ruff check --no-cache src tests` (staged subset and narrow FastAPI declarative dependency rule) |
| mypy 1.20.2 | **PASS** — strict Python 3.11 typing for 30 staged source files |
| Compilation | **PASS** — `python -m compileall -q src tests` |

The prior [base QA report](CHAT1_QA_REPLAY_20261019.md) separately records real synthetic fitted scores for seeds 73 and 101; each model balanced accuracy was **0.50**, the same as the dummy baseline **0.50**, and the held-out score **0.50**. No clinical or predictive improvement is claimed.

## Remaining release blockers

Actual process-kill and replay across a clean operating-system process; multi-worker and persisted SQLite corruption/rollback soak; complete exact-head GitHub 3.11/3.12 hosted pytest/Ruff/mypy; third-party independent security review, externally anchored P13 signing/trusted root, independently validated P25 rights and legal/ethics clearance for any non-synthetic dataset, browser and Docker proof. The single W04 Career Notion task remains dated 2026-11-05, In Progress, Done unchecked. **NO-GO; no merge, public action, manuscript submission, deployment or communication**.
