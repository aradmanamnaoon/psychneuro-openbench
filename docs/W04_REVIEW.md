# W04 integration and adversarial release gate — private, 2026-10-19

**Status: experimental private additive patch; NOT a release candidate.** Target base: `review/w03-current-head-additive-20261019` (`8e511988e1feecce434eb7a5c109df5ebaf4ef90` at inspection). W04 begins 2026-11-05. This early implementation must not change Academy or calendar dates.

## Scoped contracts / dependency DAG

```text
Trusted synthetic registry & P25 rights review ─┐
                                                  ▼
W03 ExperimentRequest (strict) → W03 P1 source/split/nested CV → W03 RunStore (immutable)
                                        └→ W03 P13 4-node SHA DAG ↔ W04 Envelope v1
P25 Decision v1 ─→ W04 protected aggregate endpoints → accessible static explorer
                     └→ W04 SQLite job state + correlation audit (coordination only)
```

- `p25-rights-1`: immutable Pydantic dataset rights (`dataset_id`, origin, license expression, consent, reviewer, operation allowlist, expiry and revocation); refuse non-synthetic until independent registry verification/migration. Rights decisions are **not** legal clearance.
- `w04-envelope-1`: immutable SHA-256 receipt over canonical P1 report and P13 graph, preserving legacy W03 `RunStore` validation. Stored digests are **integrity only**, not proof of authorship/trusted timestamp. A trusted external root is required to detect coherent rehashing.
- `w04-v1`: private `X-Internal-Token` mapped to server-side Principals (not caller-supplied roles); same-origin UI; no tokens persisted. No multi-tenant public host, OIDC, refresh, rate limiting or secret rotation claim.
- `p25-event-1`: metadata-only append/hash ledger for server-side policy decisions and P25 CLI. Rights denial is enforced before benchmark execution and aggregate export; not a legal parser or trusted timestamp.
- `jobs`: SQLite revision CAS, deterministic caller-supplied job IDs, audit correlation, cancellation request and resumable checkpoint pointers. **No worker or actual model-fitting cancellation**; `running → cancel_requested` is cooperative protocol only. Claiming distributed job orchestration would be false.

## Reproduction and evidence boundary

After applying the `src/psychneuro/w04/` and `tests/test_w04_*` additions to the inspected W03 private branch, install using existing repo `pyproject.toml` / dependencies. Run:

```bash
python -m pytest -q tests/test_w04_rights_jobs.py tests/test_w04_interop_api.py
python -m pytest -q # full existing suite, mandatory before candidate
python -m compileall -q src/psychneuro/w04
python -m pip freeze > observed-environment.txt # private evidence only
```

**Local environment note:** 13 focused tests passed on a sandbox compatibility stand-in for W03 vault/store/models; that stand-in is NOT the actual repository and its W03 execution method raises `NotImplementedError`. The independent scientific benchmark and exact-head hosted integration remain **NOT RUN**. Python interpreter 3.13.5, installed `fastapi==0.128.2`, `pydantic==2.13.5`, `scikit-learn==1.8.0`, `pytest==9.0.2` in isolated sandbox. `ruff`, `mypy` unavailable; no lockfile or CI verification for W04.

## Threat model / priority adversarial cases

1. **License laundering**: UI or API must not accept unverified external rights fields from requester; P25 server-side W03 grant only, no raw input route.
2. **Consent withdrawal**: future human datasets fail closed; existing W03 code cannot retroactively erase receipts. Actual right-to-erasure/retention workflow **not implemented**.
3. **Participant leakage**: W03 grouped CV remains the only runnable benchmark; must separately validate group splits, duplicated rows, held-out iteration and post-response feature exclusion at exact head; W04 did not modify scientific selection.
4. **Tamper/forgery**: modified report/reordered/duplicate nodes must fail validation; coordinated rehash + root substitution remains possible without offline signature/independent trusted anchor.
5. **Job concurrency**: only one same-revision CAS transition must commit; retries preserve checkpoint pointer; actual worker cancellation, timeouts, quota, orphan recovery and lease ownership remain backlog.
6. **Auth/tenant**: secrets static, roles server-defined; tokens are still risky in a browser. No internet exposure, TLS termination, CSRF/session review or rotation tested.
7. **Storage**: W03 `runs` table and W04 `w04_jobs`/`w04_audit` tables coexist; no Alembic migrations, backup/restore or key management. Size bound for W03 immutable records, but W04 receipt parsing/cross-request quotas require tightening.
8. **Accessibility**: HTML labels, semantic tables/list and aria-live error status designed; keyboard/real browser/screen reader checks not executed. Graph shows textual edges but is not an interactive rendered DAG.

## Science reference oracle and acceptance

The predefined dummy baseline's binary **balanced accuracy** is `(TPR+TNR)/2`; if two classes are present and all outputs predict one class, TPR and TNR sum to 1, hence exact BA=0.5. This is a mathematical oracle for the dummy, **not** evidence that logistic regression's expected BA is 0.5 across randomized datasets. For real W03 execute, compare unchanged source/split/seed/hash; reject run if schema, group IDs, isolated inner folds or rights differ. Do not infer population confidence intervals from three dependent CV folds. No claims for real psychology, neuroscience, medicine or calibrated risk.

## Milestone gate, budget and rollback

- **M1:** W04 rights/read-only provenance/receipt + tests on actual W03 branch. One small CPU, no human data.
- **M2:** actual P1→P13→P25 synthetic execute with W04 API/TestClient and signed external test anchor; lock and exact SHA CI (requires approval if runner minutes may incur charges).
- **M3:** sandbox browser keyboard/screen-reader checks, load/memory, worker checkpoints and fault injection.
- **M4:** multi-dataset rights-signed registry, third-party contracts/legal review, server-side auth/multi-tenant and hosted private demo.

Estimated *human* budget target: 4–6h code review, 2–3h scientific QA, 1–2h career drafting in W04; Academy remains 40h/week in separate read-only workspace, all actual human focused hours capped at 10/day across both; defer stretch backlog instead of exceeding cap. Reminder: continue R course; optional 3 original educational videos/week, no auto-post.

**Rollback:** no existing W03 file is changed by the patch; exclude W04 additions/disable W04 service. Existing W03 SQLite `runs` are retained; `w04_*` tables may be archived only after backup and approval. No destructive migrations, no release tag, no public PR.


## Additional implementation delta (local snapshot, 2026-10-19)

- Added `src/psychneuro/w04/ledger.py`: SQLite append-only policy event metadata and independently anchored root comparison. Exposes maintainer-only `/w04/v1/rights/ledger`; decisions emit policy events before protected action (including denied ones). No PII/real consent forms stored.
- Added `cli.py` executable as `python -m psychneuro.w04.cli` for explicit operator-supplied local policy JSON, expiry/revocation review and ledger verification. **A supplied policy file is not proof of license**; CLI operator reviews it separately.
- Added `server.py`, source-only review `infra/Dockerfile` and `.github/workflows/w04-private-manual.yml`. No Docker build/cloud deployment or hosted CI run has been observed. Workflow is manual-only to avoid surprise private runner charges; dependencies are direct constraints only, no transitive hash lock or secure base digest.
- `tests/test_w04_server.py` asserts missing server token refuses launch. `tests/test_w04_rights_jobs.py` now tests CLI, SQLite tamper, conflict and transition semantics. **Local focus status: 13 passed**, Python 3.13.5, pytest 9.0.2 on W03 stand-in. Not a real W03 integration or actual Python 3.11/3.12 evidence.
- `benchmarks/measure_w04.py` measured 200 local rights decisions p50 **0.004165 ms**, p95 **0.006993 ms**, tracemalloc peak **5,704 bytes**, and 200 local SQLite job creations p50 **3.083333 ms**, p95 **5.679023 ms**, tracemalloc peak **263,536 bytes**. Platform Linux x86_64, Python 3.13.5; see `W04_performance_observed.json` outside this repo patch. This is a **single-process microbenchmark**, no model fitting, concurrency/load test, process RSS measure or statistical stability claim.
- Scientific literature and GA1–GA8: [W04_RESEARCH_CAREER.md](W04_RESEARCH_CAREER.md); 12 publisher/DOI-linked publications, 5 official academic pathways, an unsent lab-specific proposal, skeptical review and rights ethics text. No outreach/publication/application conducted.
