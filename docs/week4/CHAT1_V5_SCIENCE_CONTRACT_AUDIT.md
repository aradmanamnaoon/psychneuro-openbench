# W04 Chat 1 continuation — versioned scientific-provenance consistency gate (v5)

**Private-only preparation, 2026-10-19.** This document accompanies the additive v5 change to `receipt_v3.py`. W04 calendar begins 2026-11-05. **NO-GO** for merge, hosting, external data, dataset redistribution, manuscript claims or release. No external institutional authorization or independent root/signature exists.

## Source of truth, ancestry and retained implementation

- Original private W03 integration: `src/psychneuro/w03/{contracts,nested,service,store,vault}.py`, manual-only historical hosted run **39228198934** on the *older exact code SHA* `4eeb17845dac7641b75d9a8164f125db6c213659`; **not** W04 CI proof.
- W04 Chat1 v2 policy and SQLite queue remain in `w04/{policy_v2,queue_v2,api_hardened}.py` on upstream private branch; receipt integrity v3 plus `private_worker_v4.py` stay intact. Draft review PR #19 is unmerged.
- Dependency DAG: original synthetic registry & hash → P25 tenant/purpose/action grant → queued immutable experiment → W03 GroupKFold nested fit, DummyClassifier and sealed test → P13 four-node graph → *independent* W04 graph+run/metric crosscheck → P25-revalidated internal receipt/read → reviewer proof. Version upgrades must not silently mix W03's `w03-engine-1` or W04 `w04-p13-p25-receipt-3` contracts.

## New factual source changes

1. `src/psychneuro/w04/receipt_v3.py`: reject a P13 benchmark where the claimed deterministic `run_id` does not equal the actual W03 contract hash of `{contract, request, source, split}`; reject request fields outside W03's fixed known schema and fixed pre-response predictor allowlist. Verify source/split seeds, train/test group counts, model predictors, model-spec-only declaration, final C/test metric, three individual outer/dummy fold scores and their independently rederived mean, selected C grid and metric/unit.
2. `tests/test_w04_receipt_v3.py`: make the **test-only** four-node fixture use the actual W03 request/run hash and benchmark format, not an opaque fabricated run ID. Add 8 rehashed tampering attacks (identity, scores, seed, model grid, late features, test score, groups, method) plus one independently anchored-root negative control.
3. `tests/test_w04_synthetic_numerical_oracles_v5.py`: 5 fixed-seed analytical binary balanced-accuracy comparisons against scikit-learn, 5 fixed-seed GroupKFold vs contaminated row-wise KFold comparisons on **invented 16 groups ×6 rows**, plus a hand-calculable BA `(3/4 + 2/4)/2 = 0.625` and invalid input negatives. Always-negative binary baseline is `0.5` where both classes are present. No claim of fitted W03 behavioral result.
4. `docs/week4/CHAT1_V5_SCOPED_OBSERVED_EVIDENCE.json`: commands, interpreter/library versions, input/test SHA-256 and 500 local verification timing observations. Performance measures only the pure receipt verifier, not W03 training, hosted API latency, memory RSS or distributed load.

## Observed execution, environment, previous failure

From the local *partial source bundle only* (`/mnt/data/w04_chat1_patch`, not full GitHub checkout):

```bash
PYTHONPATH=src python -m pytest -q \
  tests/test_w04_receipt_v3.py tests/test_w04_receipt_guard_v3.py \
  tests/test_w04_atomic_worker_v4_contract.py tests/test_w04_synthetic_numerical_oracles_v5.py
# observed: 58 passed in 0.99 seconds (Python 3.13.5)
python -m compileall -q src tests
# observed: exit 0
python -m pip check
# FAILED (unrelated global environment): MoviePy 2.2.1 requires Pillow <12; installed Pillow 12.3.0
```

The first new numerical oracle run observed **5 failures, 53 passed** due to an error in the *new test fixture*: the labels were accidentally expanded from 96 to 576. Corrected fixture to `labels[groups]`, reran and observed 58 passed. Failures preserved in the reported history, not hidden. Python 3.13.5, pytest 9.0.2, NumPy 2.3.5, scikit-learn 1.8.0, Pydantic 2.13.5, FastAPI 0.128.2, Linux x86_64. New source+test file SHA-256 values are in the machine-readable evidence JSON; check against the GitHub commit before reproducing.

**Unexecuted:** complete GitHub checkout tests; real W03 registry → fit → score → P13 → P25 SQLite worker; full Python 3.11/3.12 matrix; Ruff/mypy (not installed here); actual key custody, CI, Docker build, browser accessibility, E2E cancellation/restart and migration rollback. No eligible claim of these being passed. Old historical W03 success does not substitute for current commit CI. Stand-in worker tests and graph consistency checks cannot certify model fitting, license authorization or signer authenticity.

## QA boundaries and threats

- **Integrity vs authenticity:** a malicious actor controlling all records can build mutually consistent hashes and even an internally consistent `run_id`. Without separately held trusted root and independent signer/attestor key, this is NOT proof of origin, human consent, data license or performed model training. Trust anchor/signed receipts remain BLOCKED.
- **Permissions:** P25 grants are strictly synthetic-only, operator-controlled, versioned and revocable; code Apache-2.0 license never grants rights to generated or third-party datasets. Public redistribution remains DENY; no human sources enabled. P25 HMAC key/identity and audit root need real security management.
- **Scientific leakage:** prespecified `difficulty` and `stimulus_condition` only; reaction time/correct cannot be input predictors. Existing W03 grouped train/test/inner/outer partition logic unchanged. This v5 verifies the report's *declarations*, not the fact that training followed them; real runner integration and held-out group evidence still need execution.
- **Uncertainty:** correlated subject-fold scores are not independent samples, and selecting the best-performing configuration and reporting naïve fold CIs introduces optimistic bias. Future work: evaluate prespecified seeds and null permutations with group-aware assessment, separated tuning/locked held-out subjects, report sample sizes and baselines without invented p-values or population generalization.
- **Performance and concurrency:** isolated 500-iteration pure verifier timing is not p95 production HTTP, workload throughput, model latency or RAM footprint. Queue fencing works at final atomic publication boundaries; sklearn fit cannot be interrupted or resumed mid-fit by this package.

## Handoff and release decision

Chat 2 should consume the updated receipt v3 verifier, then perform real W03 runner/registry/P25 v2+Queue v2 integration with a working full private checkout. The strict W03 benchmark contract may cause previously accepted *toy/malformed* reports to be rejected; this is intentional and requires version review before product integration. Run real fixture/timing CI against the precise head SHA, test revocation during model fit and canceled-worker output rollback, review all cross-user reads and hidden privileged routes. Do not merge, publish, host publicly, use human/clinical data or approve the week until hard gates pass.

| Required E | State | New evidence and still-blocked gate |
|---|---|---|
| E2 P13 graph/transport | PARTIAL | stronger run/metric consistency + rehashed corruption tests, no externally held anchor or actual imported run |
| E3 worker/cancel/permissions | PARTIAL | inherited atomic worker and mock tests, no actual W03 fit/cancel replay |
| E5 P25 rights | PARTIAL | inherited strict v2 authorization, attestation independence and real run rights unverified |
| E6 scientific oracles | PARTIAL | 5-seed scikit-learn/group tests and null controls; no full W03 model-run verification |
| E7 schema/DB/lineage | PARTIAL | source-only verifier; schema migration and real DB rollback unverified |
| E8 concurrency/durable retries | PARTIAL | existing queue/worker source; multiworker real crash/retry unverified |
| E11 adversarial/security | PARTIAL | coordinated hash-rewrite negative regression tests; real IAM/pen test/signing blocked |
| E13 integrated P1/P13/P25 | PARTIAL | contract alignment by code review; actual integrated fitted workload not run |

Keep sole existing Career W04 Thursday card 2026-11-05, Done unchecked; preserve Academy 40h/week, max 10 focused human hours/day, existing R reminder and optional videos. **NO-GO.**