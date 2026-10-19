# W04 Chat 3 — real synthetic P25 queue → W03 fit → P13 receipt, reviewed 19 Oct 2026

**PRIVATE only. Release: NO-GO.** This supplements [the earlier 400-test scoped QA report](CHAT3_EXECUTED_QA_EXACT_SOURCE_20261019.md); the two test runs concern **different source snapshots** and should **not** be added and claimed as a single 466-test exact-HEAD passing suite.

## Why this work was needed

The earlier Chat3 integration had a product endpoint running W03 synchronously and a fenced metadata queue, but no included executable v2 worker. The compatible Chat1 worker/provenance contract was isolated on the private branch `review/w04-chat1-atomic-worker-20261019` and absent from the integrated branch.

The verified worker integration was first assembled on the **private review-only** `review/w04-chat3-worker-integration-20261019` at commit `3c1e83292d9d241226cba33d7f94c353022b6b21`, directly descended from Chat3 PR #22 previous HEAD `06332992163cba6c869dec9b8eef2ad6449eea7d`. It was then fast-forwarded into [private draft PR #22](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/22), **not into main**, with no public PR/merge or deployment.

### Actual new code and test paths

- `src/psychneuro/w04/private_worker_v4.py`: policy-gated `AtomicWorker` with **real W03 nested scikit-learn grouped fitting** in memory; source/permit checked before fitting and at the atomic SQLite `BEGIN IMMEDIATE` publication boundary, fence/lease re-read, only one immutable P13/P25 verified artifact emitted. This is an *operator-only Python API*, not a public server endpoint. At-least-once retry repeats full training, not mid-fit checkpointing.
- `src/psychneuro/w04/receipt_v3.py` and `receipt_guard_v3.py`: strict source/run/split/model-score receipt consistency and P25 scope against W03 contract. SHA consistency is **not** third-party authentication; no external signer exists.
- `src/psychneuro/w04/worker_cli_v5.py`: one-shot private operator batch runner with bounded identifiers, synthetic-only source, private file permissions and permit key supplied out-of-band. No daemon or automatic service recovery.
- Seven new test modules: `test_w04_atomic_worker_v4_contract.py`, `test_w04_worker_v4_real_w03_integration.py`, `test_w04_real_worker_recovery_v5.py`, `test_w04_receipt_v3.py`, `test_w04_receipt_guard_v3.py`, `test_w04_worker_cli_v5.py`, `test_w04_synthetic_numerical_oracles_v5.py`.

## Independently observed QA of exact worker/core files

On Python **3.13.13**, against actual review branch `3c1e83292d9d241226cba33d7f94c353022b6b21`, with original-synthetic data, no external dataset, no publication or network:

1. Fetched current Chat3 v2 queue and unchanged shared Chat1/Chat3 P25 policy, transferred the 4 worker modules and all 7 tests from GitHub, plus current W03 service/store.
2. Compared GitHub tree native blob hashes with the actual tested local file bytes for **15/15** specified worker source/tests/queue/policy/W03 source files. **15 matched; 0 missing or divergent.** This is narrower than full repository identity.
3. Executed `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src python -m pytest -q -p no:cacheprovider` on the seven new test files. **66 passed, 120 deprecation warnings, 2.71 seconds**. The real W03 fitter/regression subset itself **16 passed** and was separately rerun after updating the current W03 service, also **16 passed**. Do not double-count repeated cases.
4. `ruff check` on all four newly imported worker/receipt Python modules: **All checks passed** (Ruff 0.17.1).
5. Strict `mypy --python-version 3.11 --no-incremental` of those 4 source modules: **Success: no issues found in 4 source files** (mypy 1.20.2).
6. Several tests use only synthetic fixtures/mock clocks. `test_w04_worker_v4_real_w03_integration.py` and `test_w04_real_worker_recovery_v5.py` execute **real grouped scikit-learn W03 fitting**; the recovery tests inject a failure *after fitting, before publication* and cancel a lease after fitting; no durable partial result becomes visible. A retry creates one authorized artifact.

## Failure modes *not* demonstrated

- **No actual physical OS SIGKILL/crash-and-restart across separately launched processes.** An attempted additional test setup could not be completed in this execution environment. In-process `RuntimeError` fault injection is not evidence of process-kill safety.
- No concurrent independent real worker executors under hostile/expired lease timing; no SQLite DB backup restore or migration/rollback/soak, signer HSM/key custody, externally attested P25 grants, third-party data, OS daemon scheduling, long-running worker monitoring, or clinical correctness.
- **Not a current complete full-repo/hosted test run.** The previous 400-pass local run was at GitHub source snapshot `b3c5563f19e988173302f462df2b871fd1d97447` before these eleven additions. Current exact-head GitHub 3.11/3.12 matrix has **not** run; no GitHub Actions workflow run exists for this merged review source.
- No independently witnessed Chromium/axe/mobile manual review or TypeScript SDK run for this new source; prior screenshots and Chat2 browser script do not validate worker operation through the product UI.

## Release epic update

**E8 changes from BLOCKED (no actual worker code) to PARTIAL (working real W03 synthetic fitted worker with durable fenced publication and fault-injection tests)**. E3/E5/E7/E11/E13 gain partial support. **E12 remains BLOCKED** due to no exact-head GitHub hosted matrix and disaster recovery. All 14 engineering epics remain below DONE, and all eight GA documents are still private substantive drafts with unfinished external corroboration/reviews.

A verified source-level and local scientific software foundation is not a licence to deploy, use external human data, publish, perform outreach, infer neuroscience or mark the 5 November 2026 W04 Career Notion task complete. **NO-GO**. Keep PR #22 DRAFT/unmerged, Status In Progress, Done false; Academy READ ONLY.
