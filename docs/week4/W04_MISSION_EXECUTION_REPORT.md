# W04 mission execution and independent release gate — 2026-10-19

**Authoritative task:** https://app.notion.com/p/3fd977a963b281d29c67df3f38231508  
**Original W04 mission date:** November 5–11, 2026. **Card state:** Preserve Planned and `Done=false`, W04 implementation is early preparatory work, not finished. **Academy:** read-only.  
**Repositories inspected:** https://github.com/aradmanamnaoon/psychneuro-openbench (private), specific W03 HEAD `8e511988e1feecce434eb7a5c109df5ebaf4ef90`; https://github.com/skrub-data/skrub/issues/2340 (open contribution proposal).  
**Safety:** Original fictional synthetic records and local aggregate metadata only; **NO human or medical subject data.** No public PR, merge, deploy, scholarship application, outreach or publication performed. Branch `review/w04-p25-private-integration-20261019` created without changing protected W03 branch. No evidence of paid compute spending.

## Inspectable dependency DAG

`trusted synthetic registry` → `P25 authorized dataset-rights decision` → `W03 P1 fixed split + group-nested CV` → `W03 SQLite immutable run` → `P13 four-node SHA DAG` → `W04 envelope import/export/verification` → `private FastAPI / accessible-source HTML viewer`; rights decisions and manual job transitions → `W04 metadata audit ledger + SQLite revision CAS`. This is an **interface-level integrated source design** with isolated tests: W04 has NOT yet been executed against actual W03 code.

## Actual new patch inventory

- `src/psychneuro/w04/rights.py` — versioned P25 types and deny-by-default policy, expiry, revocation, role restrictions and synthetic-only grants.
- `src/psychneuro/w04/ledger.py` — append and independently anchored verification for metadata policy event ledger; explicit caveat that SHA alone is not a signature.
- `src/psychneuro/w04/cli.py` — P25 CLI for local rights JSON with bounded input, exit-code-denial and ledger verification.
- `src/psychneuro/w04/interop.py` — immutable `w04-envelope-1` serializer/verifier around W03 four-node graph.
- `src/psychneuro/w04/jobs.py` — durable SQLite CAS state and audit correlation, cooperative checkpoint status; no worker.
- `src/psychneuro/w04/api.py` — versioned FastAPI with server-side role, W03 execution adapter, rights audit, graph, import/export, jobs and hard-coded private boundary.
- `src/psychneuro/w04/ui.py` — static semantic HTML run comparer / provenance graph text, no server-side UI secrets.
- `src/psychneuro/w04/server.py` and `infra/Dockerfile` — local-only demo candidates; build/unpinned-image security gates untested.
- `.github/workflows/w04-private-manual.yml` — **not executed**, workflow_dispatch only, Python 3.11/3.12 intended after review/billing authorization.
- `tests/test_w04_rights_jobs.py`, `tests/test_w04_interop_api.py`, `tests/test_w04_server.py` — 13 focused local tests **passed with a shadow W03 stand-in**, not the real W03 branch.
- `benchmarks/measure_w04.py`, `docs/W04_REVIEW.md`, `docs/W04_RESEARCH_CAREER.md`, `README_W04_PATCH.md` — measured microbenchmark, architecture/release notes and GA deliverables.

## Reproducible local commands and observed results

```
PYTHONPATH=/mnt/data/_w04_shadow:/mnt/data/w04_patch/src python -m pytest -q /mnt/data/w04_patch/tests
# 13 passed in 0.83s, Python 3.13.5, pytest 9.0.2
PYTHONPATH=/mnt/data/_w04_shadow:/mnt/data/w04_patch/src python -m compileall -q /mnt/data/w04_patch/src/psychneuro/w04
# exit 0
```

The `_w04_shadow` modules are *test-only stand-ins*, excluded from the deliverable ZIP; their W03 execute raises NotImplementedError. This command must **never** be described as the integrated P1 model benchmark. Installed packages: FastAPI 0.128.2; Pydantic 2.13.5; scikit-learn 1.8.0; NumPy 2.3.5; httpx 0.28.1; pytest 9.0.2. Ruff and mypy were absent. Actual W03 repo could not be cloned into the sandbox because outbound DNS/network access failed; the repo was inspected via connected GitHub connector instead.

Observed **single-process** CPU microbenchmark, n=200 each, Python 3.13.5 Linux x86_64:

| Isolated operation | p50 latency | p95 latency | traced Python peak | Qualification |
|---|---:|---:|---:|---|
| P25 `decide` (synthetic static policy) | 0.004165 ms | 0.006993 ms | 5,704 B | no I/O, not network service |
| SQLite `JobStore.create` | 3.083333 ms | 5.679023 ms | 263,536 B | local temporary SQLite, not concurrent load |

`benchmarks/measure_w04.py` and `W04_performance_observed.json` capture method/value; these are not clinical, request-server p95, actual memory RSS or scaling guarantees. No experiment metric newly measured.

## Engineering E1–E14 evidence status

| Epic | Status | Actual evidence and missing release gate |
|---|---|---|
| E1 Multi-dataset benchmark + run comparison UI | **PARTIAL** | W03 single synthetic dataset adapter and W04 semantic run comparison UI source; no second rights-cleared dataset, actual browser or real P1 run |
| E2 P13 explorer / export / integrity | **PARTIAL** | W04 graph text, envelope import/export, negative tamper test on stand-in; no external anchor and live W03 import run |
| E3 cancellation / checkpoint / rights / trace | **PARTIAL** | Job CAS and audit/cancel/resume *protocol* tests; no worker/model execution cancellation |
| E4 Docker/cloud/CI export | **PARTIAL** | Container and manual CI source, report envelope; Docker build, cloud, security scans and transitive locks not done |
| E5 P25 core/CLI/API | **PARTIAL** | Rights parser/policy decisions, CLI, ledger, API authorization on isolated stand-in; not a legal grant evaluator with signed contracts |
| E6 scientific oracle/robustness/leakage | **PARTIAL** | Math oracle in docs, historical W03 grouped test provenance; W04 multiple seeds/ablations/independent baseline not executed |
| E7 schema/DB/rights lineage | **PARTIAL** | Versioned strict schemas and private SQLite policy-event chain; consent lifecycle, migrations, verified license provenance absent |
| E8 durable jobs/concurrency/retry | **PARTIAL** | Local CAS race/transition tests; true distributed scheduler, retries, restart replay and queue backpressure absent |
| E9 browser/API/SDK E2E | **PARTIAL** | HTTP TestClient routes and static a11y-oriented HTML; no generated TS SDK, real keyboard/browser E2E |
| E10 performance load/latency/memory | **PARTIAL** | n=200 local microbenchmark only; no stress/resource caps or model performance |
| E11 adversarial permissions/security | **PARTIAL** | Negative role/data-origin/hash cases; no pen test, multi-tenant proof, signed secret management, key rotation |
| E12 hosted CI/lock/deploy/rollback | **BLOCKED** | Existing W03 CI passed in past, W04 CI is not run, Docker unbuilt; no hash-pinned transitive lock or production rollback test |
| E13 real three-system interoperability | **BLOCKED** | Additive W03 imports and W04 contract tests on stand-in; actual P1→P13→P25 full run **not executed** |
| E14 reviewer-grade evidence | **PARTIAL** | Architecture, scoped test logs, numeric microbenchmark, source appraisal, no independent reviewer acceptance |

## Academic/career GA1–GA8 evidence status

| Epic | Status | Evidence and gaps |
|---|---|---|
| GA1 8–15 true literature studies | **DONE (source matrix draft)** | 12 verifiable publisher/DOI primary methodological/technical publications, limitations and links in `docs/W04_RESEARCH_CAREER.md`; not a systematic review |
| GA2 method/ethics manuscript prep | **DONE (draft)** | Methods-first title/abstract/claim matrix/AI disclosure; no results, no submission |
| GA3 maintainer-valued upstream contribution | **PARTIAL** | Existing skrub #2340 and private previous test-backed example inspected; no new upstream PR or full skrub build |
| GA4 3–5 academic/funding candidates | **DONE (research memo)** | Official 5 institutions/teams, clear closed Finnish deadline and admission caveats; personal eligibility unverified |
| GA5 concrete collaboration proposal/outreach | **DONE (unsent drafts)** | Inria MIND 1-page technical proposal and individualized **UNSENT** message; no collaborator response |
| GA6 case study/CV/story asset | **DONE (drafts)** | Evidence-scoped private CV bullet and educational script; nothing published |
| GA7 critical peer review/replication | **DONE (draft)** | Five major skeptical objections and negative control replication targets; not executed independent review |
| GA8 source/impact/decision ledger | **DONE (private audit draft)** | Current artifact states, approvals and stretch backlog recorded; future results not asserted |

'**DONE (draft)**' above means only the *specified written draft* exists, **not** a completed research programme, externally recognized contribution or W04 release gate. No epic is fully released.

## Non-negotiable next review order

1. Apply the patch to the *inspected* W03 private source branch and run real import/runner+TestClient, source/split checks, negative rights tests and exact SHA; do not overwrite earlier branches.
2. Independent reviewer validates rights/legal interpretation, group holdout/no leaked predictors and reported result schema; record source roots externally if authenticity is expected.
3. Execute local browser keyboard and screen-reader walkthrough, 2-user tenant isolation and true worker abort/restart equivalent results; all failures remain blocked.
4. Pin transitive package hashes and base container digest, add evaluated vulnerability scanner (no arbitrary scanning claims), run Docker smoke and strict mypy/Ruff.
5. Request explicit approval for private hosted runner minutes and new **draft** PR; never merge, deploy, publish, contact researchers or spend money unreviewed.

## Reviewer decision

**NO-GO.** The current W04 patch proves limited engineering exercises locally, not a validated cross-repository deployment. Official W04 card remains **Planned**, due **2026-11-05**, Done unchecked. Carry unfinished E1–E14 into the week without claiming completion. W04 career/engineering work suggested 24 hours is a planning target, not an override of the independent Academy's 40h/week or 10h/day focused cap. Reminder: learner R course; optional original videos 3/week (no auto-post).