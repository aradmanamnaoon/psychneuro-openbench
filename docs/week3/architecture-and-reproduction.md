# W03 P1/P13 private integrated architecture and review

Prepared 2026-10-19 for W03 29 Oct–4 Nov. P13 is a reusable source package inside private P1, not a standalone release. All data remain fictional, internal-use only.

## Six-module interaction
1. contracts.py: bounded strict Pydantic v2 model; only prereponse difficulty and stimulus_condition. Reject unknown request keys, forbidden predictor columns, excessive experiment sizes, invalid seeds.
2. service.py: use existing rights-checked load_dataset, create_group_split and validate_group_split. Check registry synthetic-only and no separate public data export licence. Training sees existing train partition only.
3. nested.py: outer GroupKFold(3), inner GroupKFold(2); inner search logistic-regression C in (0.1,1.0), tie C=0.1; fresh scaler/encoder per training fold; dummy-prior on identical outer folds. Frozen final C before one-time heldout test. Fail closed on undefined binary class support and any same-participant crossover.
4. vault.py: canonical SHA-256 source -> split -> benchmark nodes with parent-edge integrity; result hash bound into benchmark node.
5. store.py: immutable idempotent aggregate SQLite run record, content-hash integrity rechecked on retrieval, 250KB record cap, conflict on same ID with differing bytes. No raw participant data stored.
6. api.py: FastAPI factory with a required internal secret (20+ characters), 403 unauthorized, 422 invalid input, 404 unknown digest, 409 run-ID conflict. POST /v1/runs; GET /v1/runs/{id}; GET /v1/runs/{id}/provenance; /health returns only internal-only. API accepts no file paths/URLs or external data.

## Reviewer verification commands
For authorized CI review, Python 3.11/3.12: python -m pip install -e '.[dev,benchmark,w03]' ; python -m pytest -q ; python -m ruff check . ; python -m mypy src. W03 workflow is MANUAL ONLY and not dispatched; a configured job is not observed CI. Direct optional dependency ranges are in pyproject.toml; full hash-locked transitive environment remains backlog.

Default generator seed=73, split seed=42, 36 fictional participants *12 fabricated trials; 3 outer/2 inner participant-grouped CV. Fixed pre-response features and dummy baseline. Expected negative gates: same participant and duplicate row index fail, modified provenance content invalidates digest, repeated request yields equal SHA/run, API schema/auth and SQLite restart checks. Actual local sandbox tests (Python 3.13.5, pytest 9.0.2, numpy 2.3.5, sklearn 1.8.0, pydantic 2.13.5, FastAPI 0.128.2, httpx 0.28.1): 6 PASSED and 1 SKIPPED on an isolated candidate copy; temporary existing-metrics scaffold was used ONLY for local import compatibility. The skipped real-repository integration MUST run later. No hosted exact-SHA tests or Ruff/mypy have run.

## Scientific, security and rights limits
This cannot infer human-population validity or clinical use. Fold means are synthetic software diagnostics; confidence interval and p-value NOT estimated. SHA-256 alone is not signer authentication; SQLite is not protected against fully rewritten coherent records by an adversary. Single internal token is NOT multiuser access control. Public host TLS, OAuth, rotation, rate-limiting, proxy request cap, authenticated provenance signature, concurrency/queue, migrations/Postgres, screen-reader/mobile browser testing and independent security review remain NOT RUN. Source code Apache-2.0 is not a separately authorized licence for generated exports; six external OpenNeuro human datasets disabled. Do not mark W03 Complete until 85/100 with every safety gate satisfied.

No PR, merge, public deployment, paid CI run, personal-data collection or Academy edit has been authorized or performed.
