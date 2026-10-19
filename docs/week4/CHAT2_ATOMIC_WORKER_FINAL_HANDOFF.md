# W04 Chat 2 final execution and Chat 3 independent audit handoff

**Review state:** PRIVATE DEPENDENT DRAFT; **NO-GO**. Prepared 2026-10-19 for scheduled W04 mission 2026-11-05–11, not represented as a completed future week. The sole existing Career W04 Notion card remains dated **2026-11-05**, **In Progress**, `Done=false`; independent Academy unchanged. No public release, external pull request, human/clinical data, spending, deployment, research claim, contact or merge.

## Exact source pointers

- **Current canonical Chat 2 dependent private DRAFT:** https://github.com/aradmanamnaoon/psychneuro-openbench/pull/23
- **Branch:** `review/w04-chat2-atomic-worker-ui-20261019`
- **Last implementation source commit checked before this documentation-only addition:** `2c75ba831c78e310a74c5d337b05f79e0340d288`; obtain the later full HEAD with `git rev-parse HEAD` before signing any validation. A documentation commit changes HEAD without rerunning tests.
- **PR base:** Chat 2 draft #18, `review/w04-chat2-on-chat1-final-20261019`, at `24c57af06f62f514fda93cc53dc60d23ccd47578` when #23 was created; comparison originally **ahead 1 / behind 0**. Do not merge #18/#19/#22/#23, cherry-pick independent Chat 3 without review or alter original W03 PR #13.
- Related historical draft #19 (Chat 1 actual atomic worker) is **not merged**. Chat 3 independent draft #22 targets an earlier Chat 2 snapshot and is divergent; its independent ownership patches and GA1–GA8 scholarship packet require reviewer reconciliation against this latest worker branch.

## Implemented software

1. Reused **real** W03 participant-group-disjoint, train-only nested-CV logistic/dummy benchmark and deterministic `RunResult` + four-node P13 provenance. `psychneuro.w03.service.execute` now accepts a typed `RunSink` protocol in place of a concrete RunStore, preserving its existing public call contract and optional `before_persist` revocation boundary.
2. Integrated **Chat 1's existing** `private_worker_v4.py`, `receipt_v3.py`, `worker_cli_v5.py` and numerical oracle tests on the real Chat 2 code without rewriting their original science. Worker staging stays in memory until **one SQLite BEGIN IMMEDIATE** transaction rechecks P25 revocation/source/purpose, worker lease fence, W03/P13 integrity and result receipt before atomic publish. An in-flight scikit-learn fit cannot be interrupted; cancellation fences out publication, and resume restarts fitting instead of restoring optimizer state.
3. Added **authenticated private v3 REST** in `worker_routes_v5.py`: `POST /w04/v3/jobs`, `GET /w04/v3/jobs/{id}`, `POST /w04/v3/jobs/{id}/cancel`, `POST /w04/v3/jobs/{id}/resume`, `GET /w04/v3/jobs/{id}/receipt`. Strict P25 v2 policy, typed request and machine-error boundaries, server-side tenant/owner role decisions. Identity is **operator-provisioned static internal token only**, **not** multi-user production IAM. Job idempotency is bounded by owner/key/request SHA. Wrong source/role/tenant and revoked grants deny.
4. Accessible `ui.py` now queues, reads status, cancels, resumes and exports **real durable v3 jobs**. V1 fake metadata-job buttons were replaced, and strict facade no longer removes real v3 panel. UI also retains independent synchronous original synthetic run, P13 graph, descriptive real-model/dummy table, split metadata, download and receipt verification; untrusted text uses DOM `textContent`, long `<pre>` wraps on mobile and source code does not embed the bearer token. TypeScript client adds typed job and receipt methods. The real worker is deliberately **operator-run**, not started with a public/browser REST request.
5. Private CPU-only Compose and manual-only CI are present. `.env.example` keeps **separate** operator token/P25 key; workbench uses loopback `127.0.0.1:18080`, 1 CPU, 768MiB, non-root user, no public bind, read-only root/cap drop. **Docker image was NOT built/smoked in this session**.
6. Added `benchmarks/w04_sbom.py` to write an installed-package **CycloneDX 1.5 inventory**, **not a security/vulnerability attestation**. Manual CI includes fixed Python 3.11/3.12 pytest/Ruff/mypy, reproducible `npm ci` and TS unit checks, W04 OpenAPI 0.4.3 export with SHA, in-process benchmark and pip-freeze/CBOM artifacts (7-day retention), container smoke and **explicit opt-in** pip-audit advisory job. GitHub Actions was **not triggered** because paid/private runner entitlement and spending-free execution were not independently established. No SBOM artifact/scan from CI is claimed.
7. `scripts/w04_browser_audit.py` contains a reproducible loopback Playwright Chromium plus axe WCAG A/AA acceptance script, now extended to exercise the real fenced worker queue/cancel/resume/receipt. Screenshots are optional due observed headless Chromium crash under full-page capture on the test sandbox. Final amended script AST parsed successfully, but no exact-final-file runtime replay took place.

## Actual observed tests — provenance and limitations

| Environment and scope | Observed result | Caveat |
|---|---|---|
| Remote in-process reconstructed checkout, Python 3.13.13 (earlier integration content) | **376 pytest PASS**, Ruff 0, mypy targeting 3.11 **52 source files PASS** | SHA-equivalent source reconstruction for tested files, not GitHub-hosted exact-final HEAD; before latest UI/SDK/workflow edits |
| Real W03 Chat 1 atomic worker subset, Python 3.13 | **17 PASS** | Actual scikit-learn fits in two seeds; not test doubles |
| Strict v3 API enqueue, cross-tenant, viewer denial, idempotency, cancellation, fresh-permit resume, operator-run real W03 model, revoked graph/receipt, Python 3.13 | **2 new tests PASS** | Test-specific rights are fictional fixtures; current integrated source subsequently adds browser/CI files |
| TypeScript 5.9.3, npm locked installation, Node 20/22 local runs | **4 tests PASS; build/typecheck PASS** | Includes typed v3 client contract compilation after source changes; unit tests primarily scientific helpers |
| Loopback Chromium and axe after amended v3 UI, synthetic test grant | **Observed v2 run→P13 receipt, v3 queue→cancel→resume→trusted worker fit→P13/P25 receipt, 0 page errors, 0 automated axe WCAG A/AA findings, no document overflow at 1280px or 375px** | Last successful browser replay used a non-screenshot copy of the script and tested source from the dependent branch. Not a manual screen-reader audit or accessibility certification |
| In-process TestClient HTTP, Python 3.13.13, Intel Xeon 2.60GHz, 36 fictional participants, concurrency 1 | Real observed CSV `benchmarks/w04_http_20261019_cpu_testclient.csv`: n=100 health median 1.816ms/p95 2.6504ms; n=100 authorized P1 read median 23.6287ms/p95 46.3925ms; n=100 P13 graph 56.5754ms/p95 74.723ms; n=60 artifact export 76.3042ms/p95 86.6828ms | Historical previous product snapshot; **not** network/browser performance or v3 worker throughput |
| Native Python 3.11.17 clean interpreter, remote sandbox | Interpreter + environment dependencies installed; full pytest **TIMED OUT**, targeted pytest **TIMED OUT** without a conclusive result | Remote sandbox overloaded/recycled. **NOT PASS** |
| Native Python 3.12.15 clean interpreter | Interpreter installed, no trustworthy full tests before sandbox recycled | **NOT RUN** |
| Hosted Actions, Docker, pip-audit, external root signature/manual screen reader | **NO hosted W04 runs** at checked commit, Docker engine unavailable in session, scans/manual a11y **NOT RUN** | **BLOCKING** |

**Performance caveat:** all figures are bounded single-process synthetic tests; no confidence interval, concurrency scaling, tail-at-capacity estimate, patient/clinical diagnostic claim or human cohort inference. 36 fictional participants cannot support “large-scale” inference.

## Architecture and hard constraints

P25 operator-installed synthetic-only signed permit (short TTL, per-tenant policy SHA and source SHA) → authenticated P1 experiment request → fenced v2 durable job → trusted one-shot v5 worker → **real** W03 grouped nested-CV → in-memory P13 source/split/model/benchmark DAG → **atomic** P25 revocation+lease+receipt+artifact+job state commit → P25-scoped aggregate read/typed browser UI → P13/P25 receipt export and independent checksum validation. Other legacy v1/v2 endpoints remain for W01–W03 private compatibility; they must NOT be misconstrued as v3 worker operations.

Browser accessibility: keyboard focus, form labels, semantic table, live errors and status, text graph metadata, reduced-motion styling, long-hash wrapping; automated axe WCAG A/AA no findings on one fixture is **not** proof of assistive-technology coverage. Interop error bodies are bounded `w04-error-2`. Untrusted metadata never becomes HTML via string concatenation.

Security and scientific budgets: CPU-only ≤1 CPU/768MiB Compose source config (not yet smoke-tested), one W03 synthetic approved fixture (24–80 fictional participants; 8–40 invented trials), 3 outer/2 inner grouped CV, no GPU, no human/clinical data, no third-party-accessible endpoints. Publication/release must still require independently authenticated rights grants, production IAM/session controls, rate-limits/quotas, external authenticated provenance anchor, supply-chain audit, independently validated 3.11/3.12 hosted matrix and rollback rehearsal.

## E1–E14 and reviewer gates

| Epic | Evidence state |
|---|---|
| E1 browser P1 benchmark | IMPLEMENTED, local Chromium positive path observed; no manual screen-reader evidence |
| E2 P13 DAG/read/export/verify | IMPLEMENTED and local positive/tamper cases tested; no external authenticity anchor |
| E3 real create/cancel/resume/recovery | REAL queue/fence/cancel/resume tested; model fitting is restarted, not optimizer-checkpointed; crash recovery fail injection not fully independently measured |
| E4 Compose and package inventory | CONFIGURED, Docker not executed; dependency SBOM script authored, not independently scanned |
| E5 P25 tenant/source rights | REAL durable v2 gate and negative cases observed on synthetic fixture; not a legal rightsholder attestation |
| E6 scientific oracle | REAL W03 and 2-seed worker integration test PASS on Python 3.13; clinical/large-scale inference forbidden |
| E7 durable migrations/rollback | Create-if-absent SQLite and atomic worker tables; upgrade/restore rehearsal absent |
| E8 true worker recovery | Partial: at-least-once fenced worker, fresh cancellation and replay; independent crash-and-lease experiments outstanding |
| E9 OpenAPI/typed SDK | FastAPI strict 0.4.3 and TS client built, hosted OpenAPI file generation configured, not observed on current HEAD |
| E10 measured capacity | Bounded TestClient CSV exists; no concurrency/load/cross-process v3 memory study |
| E11 adversarial E2E | Strong local tests and scripted positive browser; no external independent reviewer |
| E12 hosted/release | BLOCKED: exact-HEAD W04 Actions jobs and security scan never run |
| E13 full P25→P1→P13→UI→artifact | Positive private original-synthetic integration observed; signed trust anchor, production ACL/IAM and independent audit remain BLOCKED |
| E14 evidence handoff | THIS durable SHA-linked report plus earlier CHAT1/CHAT2 handoffs; review decision **NO-GO** |

## Instructions for Chat 3

1. Independently compare exact HEAD of **#23** with #18, #19 and existing independent Chat 3 #22. Preserve all previous branches; **do not** merge or publish. Resolve Chat 3 atomic ACL fixes onto this v3 worker rather than creating a third competing queue/product.
2. Independently run Python 3.11 and 3.12 complete pytest, Ruff, mypy, TS locked build/test, negative producer-tenant collision/revocation/during-fit, corrupted receipt, signed root tamper, stale fence, SQLite crash/recover, Docker/backup restore. Hosted job names/links may be reported only after actually observed; compare `GITHUB_SHA` exactly.
3. Run `npm ci --prefix apps/web`, `npm test --prefix apps/web`, install `playwright==1.64.0` with Chromium headless shell, run `PYTHONPATH=src python scripts/w04_browser_audit.py` on loopback. Optionally `--screenshots` with sufficient memory. In addition, independent human keyboard/VO/TalkBack/NVDA and viewport audit.
4. Generate and inspect `/w04/openapi.json`, CI package SBOM, optional security report after owner confirms private runner costs/permissions. No `0 CVEs` statement without scan.
5. Verify data provenance and P25 consent/license independently; SHA/permit-only integrity is not legal authority. No real human data allowed in this release gate. GA1–GA8 research/career deliverables in independent Chat3 #22 remain DRAFT; verify primary literature, 8–15 citations, funding/eligibility, truthful academic outreach drafts before *any* user-approved external action.
6. Keep **only** original W04 Career date **2026-11-05**, Status `In Progress`, Done unchecked; Academy is read-only 40h/week, combined daily human focus ≤10h. No duplicated calendar days. Require all hard scientific/security/hosted/independent acceptance gates before declaring GO.

### Private setup/rollback (documented, NOT executed here)

```bash
cp .env.example .env
# Fill TWO independent 32+ character randomly generated values:
# W04_PRIVATE_TOKEN, W04_P25_PERMIT_KEY. NEVER commit .env.
docker compose --env-file .env build
# Install a P25 grant with the operator-only command in a private environment
# for the EXACT synthetic generator/source configuration. No auto-grants.
docker compose --env-file .env up -d
curl -fsS http://127.0.0.1:18080/health
docker compose --env-file .env down
# Back up private SQLite volume before any destructive migration;
# no automatic schema downgrade or destruction of user data.
```

**Final independent release decision: NO-GO**, even though private synthetic positive paths and locally reconstructed Python 3.13/browser tests now demonstrate meaningful implementation.
