# W04 Chat 2 — executed QA and performance appendix (2026-10-19)

**Private draft PR #18, still NO-GO.** Evidence pertains to a reconstructed sandbox, not an exact-head hosted CI run.

## Executed checks

Environment: Python 3.13.13, FastAPI 0.148.0, scikit-learn 1.6.1, Intel Xeon @ 2.60 GHz. Source was reconstructed from private GitHub files; not a complete clone. Commands:

```bash
PYTHONPATH=src python3 -m pytest -q --ignore=tests/test_app.py --ignore=tests/test_pm14.py --ignore=tests/test_contributor_docs.py --ignore=tests/test_deployment.py --ignore=tests/test_pm17_patch.py
# 293 passed, 1 skipped, 238 warnings, 4.56 s
PYTHONPATH=src python3 -m mypy --python-version 3.11 src
# Success: no issues in 47 source files (sandbox)
PYTHONPATH=src python3 -m pytest -q tests/test_w04_precommit_revoke.py
# 1 passed; real W03 fit then revoke P25 before persistence, SQLite runs=0
```

The five excluded modules require Streamlit, documentation or upstream fixture files that were absent in the reconstructed sandbox. Python 3.11/3.12 themselves were **not run**. Ruff `check src` passed in the sandbox after automatic import fixes; some resulting import-only source changes are not in GitHub, so **PR-head Ruff PASS is NOT claimed**. Historical W03 hosted CI applies only to W03's tested SHA. No W04 Actions run was triggered.

## Actual private in-process API microbenchmark

[Measured CSV](../../benchmarks/w04_private_http_observed_20261019.csv). Single concurrency, five warmups per endpoint, 36 fictional groups ×12 trials, seed 73/split 42. No real users, clinical data, network traffic or hosted API.

| Route | Samples | Median | p95 |
|---|---:|---:|---:|
| Health baseline | 100 | 1.8425 ms | 2.7490 ms |
| Protected run read | 100 | 25.0860 ms | 36.8878 ms |
| Protected P13 graph | 100 | 53.8868 ms | 75.2479 ms |
| Protected receipt export | 60 | 77.7566 ms | 88.6305 ms |

Measured peak process RSS 201,976 KiB; one synthetic fit took 0.1758 s (one observation, not a fit-time distribution). Policy audit history grows during this ordered test; P25 chain-verification overhead needs separate profiling. This is NOT browser paint, throughput under concurrent external traffic, or worker capacity proof.

## Integrated code and limitations

Actual P25 v2 grant/source digest → grouped W03 nested CV → post-fit rights recheck → immutable P13 result is testable. Added `tests/test_w04_precommit_revoke.py`; corrected legacy fixture expectations so an unclaimed historical run is **403** until explicitly assigned to a tenant owner. Browser source and API code are private, but keyboard/axe/screen-reader/visual audit remains **NOT RUN**. Metadata queue cancellation does not interrupt model fitting. No production IAM, signer-root trust, public data grant, independent legal verification, worker checkpoint recovery, migration rollback drill, Docker smoke, dependency lock/SBOM/CVE scan or W04 hosted matrix run.

**E1–E7, E9–E11, E13–E14 PARTIAL; E8 and E12 BLOCKED. Release NO-GO.** Chat 3 must independently audit exact PR head, real worker, browser accessibility, hosted Python/TS and all legal gates. Career W04 original date 2026-11-05, Done unchecked; Academy read-only. GA1–GA8 drafts are not external scientific outcomes.
