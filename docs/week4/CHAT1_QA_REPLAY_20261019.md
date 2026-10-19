# W04 Chat1 reproducible scientific/backend QA — 2026-10-19

**Private source/test code commit:** `db3b63b72d12853bd5b9956369cdb32a8e9bb3fd`, dependent [draft PR #19](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/19). This report itself is a subsequent documentation-only commit. **Status: NO-GO for merge/release.**

## Actual execution and observed results

The checked scientific test subset comprised **40** exact GitHub tracked files, including W03 synthetic registry, GroupKFold/nested CV source, W04 P25 SQLite rights/queue, P13 verifier, fenced worker, associated FastAPI endpoints, test sources and narrow Ruff config. The committed 16 changed files have exact Git blob SHA matches to the passing isolated checkout. This is **not** a complete repository checkout.

| Check | Actual observed result | Scope |
|---|---|---|
| Python | 3.13.13 | Linux private isolated runtime |
| Pytest | **92 passed, 161 warnings in 3.04 seconds** | All staged W03 and W04 tests, including real P1→P13→P25 fitted synthetic training and P25 revocation/rights negative tests |
| Ruff 0.17.1 | **PASS** | `ruff check --no-cache src tests` on staged subset; FastAPI declarative `Depends()` B008 intentionally scoped to two API modules |
| mypy 1.20.2 | **PASS, 30 source files** | `mypy --no-incremental --cache-dir=/tmp/w04_mypy_final --strict --python-version 3.11 src` |
| Python compilation | **PASS** | `python -m compileall -q src tests` |
| Dependency consistency | **PASS** | `python -m pip check` within isolated environment |

The earlier broader local run on a larger but ultimately non-exact checkout reported 455 tests passing; **do not relabel that run as exact-head verification**. An initial source-only full suite reported 11 missing-document/fixture failures, followed by 452 passes on a repaired but not byte-perfect workspace. This report deliberately promotes **only the 92 exact-code tests** to observed source-sha-attached evidence.

## Real model outcomes (original synthetic data ONLY)

| Synthetic generator seed | Run ID (SHA-256) | Source SHA-256 | train/test groups | Outer balanced accuracy | Dummy outer | Held-out balanced accuracy |
|---|---|---|---|---:|---:|---:|
| 73 | `b4a0f38b4c3302c56a1e75151813dc0bada8c1f95b45269eee9fe0914ba16844` | `bc6f7b672193d4c4b4af13d1df25964454d3216d6e5c4b3c9c9c6099363412b8` | 21/8 | 0.5 | 0.5 | 0.5 |
| 101 | `efdd5c9151343531162cc8e963272805f36aadd46a2e3179346178f42af4f925` | `c092716486a21bcc485f4516ca13f2f0f18ecb87136a7a10e249ae045d153164` | 21/8 | 0.5 | 0.5 | 0.5 |

Both persisted once under a P25-scoped aggregate read permit; source checks and P13 independent graph verification passed. Original synthetic data had 36 participant groups ×12 fictional trials, fixed pre-response predictor allowlist (`difficulty`, `stimulus_condition`), outer GroupKFold 3 and inner GroupKFold 2. These are a **software sanity check**, not a clinical result, population inference, or proof of model value. **Neither model improves on the 0.50 dummy baseline.** No significance test, clinical inference, human dataset reuse, or public redistribution is justified.

P13 internal root hashes: seed 73 `2579eb8213827b0fd434f3339f11b7651ca545562852d6a8742bd97fd11b38d2`; seed 101 `913dbe00e98fae4e4221270c7dc52f22b79dda2c00b129cf450e3d87b84fc1aa`. SHA-256 detects independent corruption only with a securely retained trusted root; it does not authenticate an attacker who controls the full archive. Code license is NOT a human-data license.

## Observed toolchain versions

- pytest: 8.3.5
- pydantic: 2.13.3
- fastapi: 0.148.0
- httpx: 0.28.1
- scikit_learn: 1.6.1
- numpy: 2.3.5
- ruff: 0.17.1
- mypy: 1.20.2

## Remaining strict release blockers

1. Python 3.11/3.12 matrix, complete current-GitHub 45-source repository test suite and hosted Actions **NOT RUN** for this commit. Existing manual-only workflow source is configured but no GitHub-hosted result is claimed; no paid CI was dispatched.
2. No independent P25 legal/data-steward source-rights attestation or production authentication/key custody, no public or human data.
3. P13 graph has no externally anchored signed root. SHA/checksum consistency is not a signature.
4. Real fit interruption/restart equivalence, multi-worker crash/rollback/provenance forgery soak, browser accessibility, Docker and production deployments remain **BLOCKED/NOT RUN**.
5. No independent third-party research/security review. Work is an AI-assisted private engineering slice.

**Release decision: NO-GO**. W04 Career Notion date 2026-11-05, Status In Progress, Done unchecked; no Academy changes, external publication or communication.
