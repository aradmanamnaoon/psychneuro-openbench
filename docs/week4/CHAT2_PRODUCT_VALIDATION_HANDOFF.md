# W04 Chat 2 — product validation and Chat 3 audit handoff

**Status:** PRIVATE DRAFT / **NO-GO** / 2026-10-19 (pre-scheduled W04 work). Original W04 Career task remains dated **2026-11-05**, `Done=unchecked`. No public deployment, merge, release, spending, human/clinical records, or outreach.

## Exact durable pointers and ancestry

PR #17 was superseded and closed **without merge** when Chat 1 advanced its head. The canonical dependent **private draft is PR #18**; its initial base is Chat 1 final head `e0a32b00843ae1346dc3382908de436b497c7cb0`. Its original one-commit overlay had `ahead=1`, `behind=0`; always inspect latest PR head before release or tests.

- Private repository: https://github.com/aradmanamnaoon/psychneuro-openbench
- **Dependent DRAFT PR:** https://github.com/aradmanamnaoon/psychneuro-openbench/pull/18, head branch `review/w04-chat2-on-chat1-final-20261019`, target `review/w04-chat1-durable-backend-20261019`. Review latest branch SHA in GitHub before doing any audit: this doc is added after the most recently inspected code SHA.
- **Clean dependent source/test overlay SHA at PR creation (not the final documentary HEAD):** `edafcb11a999b9e82733ee5cdc618a561767bb5f`. Underlying product TS origin protection code was committed `38bca3c296c9844709c9f7518e15275f1953422d`.
- Chat 1 **latest verified source/handoff:** `e0a32b00843ae1346dc3382908de436b497c7cb0`; handoff copied directly from its Git tree to `docs/week4/CHAT1_BACKEND_HANDOFF.md` along with exact policy_v2 tests and numeric oracle revisions. Previous Chat 1 source before final handoff: `8fbfb1ed27d4ac22ea46fa859951e0cd4f5b647f`.
- W03 draft PR #13 remains unmerged. Historical W03 Actions https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934 PASS applied to **W03 SHA `4eeb17845dac7641b75d9a8164f125db6c213659` only**. W04 prior #14 draft remains separate/unmerged.
- Github PR-triggered workflow query for Chat 1 original SHA and Chat 2 source SHA returned empty runs; combined status reported zero statuses. **W04 hosted QA = NOT RUN**; no CI URLs for a passed W04 check.

## Actual contents (do not confuse present code and connected behavior)

**Inherited Chat 1 v2 backend, from actual Git objects:** `policy_v2.py` (tenant-specific SQLite P25 policy, revision/retention/revocation, HMAC permit and integrity audit), `queue_v2.py` (atomic idempotent enqueue/lease/fence/cancel/resume/retry/metadata checkpoints), `api_hardened.py` (private opt-in admission/job coordination), adversarial tests and independent metric oracles. This backend is **NOT a worker** and **NOT yet wired to UI fitting**. The authoritative handoff independently reports 29 local tests against partial W03 stand-ins, Python 3.13.5, not against this complete repository, and no hosted check.

**Chat 2 integration carried from an existing private product branch:** `src/psychneuro/w04/product.py`, revised `api.py` and `rights.py`, `apps/web/src/client.ts`, `ui.py` already inherited from W04, `server.py`, Compose/loopback Docker and `test_w04_product_v2.py`. The product facade calls actual W03 `execute` with the local synthetic source registry, provides P1 run create/read/compare, P13 graph/split/export/verify/import and a tenant/owner SQLite ACL. UI is semantic HTML with an embedded JS data flow, while the TS code currently provides a **typed SDK**, not the running browser rendering implementation. Import is maintainer-only; cross-tenant/run-owner reads reject. The static **P25 v1** decision is server-controlled; **v2 durable P25 decisions are not enforced by the W03 fitting product endpoint**. This is a release-blocking integration gap, not a successfully joined three-system security flow.

**New in this PR:** `apps/web/src/science.ts` validates finite balanced accuracy and bounded groups, provides baseline and descriptive comparator with caveats, and a text alternative for ordered four-node provenance. `apps/web/tests/science.test.mjs` exercises success, self-comparison, NaN/invalid identifiers, unexpected parent ordering. `client.ts` rejects cross-origin browser destinations and non-TLS/non-loopback HTTP origins; parses only bounded W04 machine-error codes. Manual CI workflow now includes a separate TypeScript test job. No artifact is independently signed.

## Contract architecture and dependency DAG

`P25 server-side original-synthetic-only permission [v1 product; v2 separate]` → `P1 W03 ExperimentRequest` → `train-only grouped 3×2 CV / same-fold dummy` → `RunResult('w03-engine-1') and immutable RunStore` → `P13 SHA source→split→model→benchmark` → `W04 tenant-owned v2 run/compare/split/graph/export` → `browser aggregate UI and TS client`.

Versioned product endpoints: `/w04/v2/catalog`, `rights/preview`, `runs`, `runs/{id}/split`, `runs/{id}/graph`, `runs/{id}/artifact`, `artifacts/verify`, `artifacts/import`, `compare`. Existing product FastAPI is configured `version='0.4.0'` and `openapi_url='/w04/openapi.json'`; **generation, schema diff and client-to-spec conformance were not executed**. Chat 1's separate private hardened app is configured `version='0.4.2'` with OpenAPI disabled. Versioned `W04_FORBIDDEN`, `W04_INVALID`, `W04_NOT_FOUND`, `W04_CONFLICT` exist for v2 domain failures; FastAPI defaults are not yet fully normalized. Never describe static internal X-Internal-Token identities as production sessions/IAM.

## Evidence observed locally during Chat 2 (not hosted)

- Local machine: AMD EPYC 9V74 80-Core Processor (reported CPU descriptor), Node **v22.16.0**, global TypeScript compiler **5.8.3**, Python **3.13.5**. Full W04 source checkout was inaccessible to local shell because the private GitHub remote is not resolvable; a subset of new TS source was authored and executed in an isolated working directory. Do not claim full exact-head build.
- `tsc -p apps/web/tsconfig.build.json` on the isolated newly authored `science.ts`: **exit 0**. Local built JS and `node --test apps/web/tests/science.test.mjs`: **4 passed, 0 failed** (observed TAP output). The isolated folder did **not** include `client.ts` from the private repo; hence exact full `client.ts` type check = **NOT RUN**.
- Actual second microbenchmark via `node benchmarks/measure_w04_science.mjs` on compiled isolated science helper: **n=10,000**, warmup 1,000, concurrency 1, median **1.141 µs**, p95 **2.383 µs**, process RSS sample **32,735,232 bytes**. See `benchmarks/w04_chat2_science_20261019.csv`. Per-call `performance.now()` sampling overhead dominates tiny operations. These are **presentation-helper timings only**, NOT API latency, HTTP throughput, model run capacity, worker recovery or browser paint; no statistical confidence bound.
- Python integration/pytest, W03 scientific oracle on full tree, Ruff, mypy 3.11/3.12, installation lock validation, Docker Compose smoke, SBOM, CVE scan, real API latency, accessibility audit with browser/axe/screen reader, keyboard tour and mobile viewport, persisted job worker crash/replay: **NOT RUN on this branch**.
- No rendered UI screenshot or verified live walkthrough exists. UI visually plausible on source inspection is **NOT an accessibility certification**.

## Safe private demo and rollback (NOT EXECUTED)

```sh
cp .env.example .env
python -c 'import secrets; print(secrets.token_urlsafe(48))'
# Set fresh secret W04_PRIVATE_TOKEN in the untracked .env file; do not commit or log it.
docker compose --env-file .env build
docker compose --env-file .env up -d
curl -fsS http://127.0.0.1:18080/health
# Never bind the host port to 0.0.0.0 or supply human/clinical data.
docker compose --env-file .env down
```

Service is configured for host loopback, one CPU, ~768MiB, named SQLite volume, nonroot container, restricted caps and read-only root filesystem; image and Python transitive dependencies are **not digest/hashes locked**. Verify `.env` exists and volume ownership before use. For rollback stop Compose, back up SQLite volume, restore prior branch/image; **no automatic destructive DB downgrade**. Chat 1 v2 tables and W04 run ACL use create-if-absent/version guards, not a rehearsed migration framework. No deployed service/public port/real users.

## Threat model and adversarial matrix

| Scenario | Observed implementation | Chat 2 exact-head evidence |
|---|---|---|
| Missing/wrong internal token | FastAPI maps operator-provisioned opaque token server-side | Existing Python tests only; combined NOT RUN |
| Viewer writes, cross-tenant/owner reads/compare/export | Product ACL + fail-closed domain checks; separate v2 policy ledger | Existing Python tests only; combined NOT RUN |
| P25 revoked/expired grants, permit forgery/replay | Chat 1 v2 policy tests/validation | v2 NOT bound to live fitting route |
| Corrupted P13 node, mutated receipt, imported conflict | W03 store/graph verification and W04 envelope checks | Existing tests only; independent end-to-end NOT RUN |
| Stale lease/cancel/resume/idempotency | Chat 1 fenced metadata queue tests | No real worker or stage-boundary compute check |
| Malformed source/participant overlap/preprocessing leakage | W03 source, split, GroupKFold and metric oracle | No full-tree exact-head replay |
| Browser token exfiltration | New TS SDK rejects cross-origin/browser and off-loopback HTTP origins | Exact integrated browser NOT RUN; inline legacy JS CSP remains weak |
| Large requests, secret logging, corrupt DB rollback | Limited W03 schema and SQLite checks | No load/negative integration/backup restore |

CSP currently permits inline script/style; no production identity federation, TLS reverse proxy, rate-limit/quotas, systematic log redaction, signed provenance trust anchor, cross-tenant namespace isolation, independent legal authorization or SBOM/scanning proof. **NO PUBLIC/HUMAN DATA.**

## Release epics E1–E14 — observed status

| Epic | State | Why |
|---|---|---|
| E1 UI/P1 integration | PARTIAL | Browser static source + real W03 v2 run API; no live browser E2E |
| E2 P13 explorer/import/export | PARTIAL | Four-node source view and hash receipt checks; no independent root signature |
| E3 job cancel/resume | PARTIAL | v2 queue exists, browser uses v1 metadata protocol; no fitted-job worker |
| E4 Docker/CI/artifact | PARTIAL | Source configs and manual matrix; no Docker/hosted run, lock/SBOM |
| E5 rights P25 | PARTIAL | v2 server-side durable policy exists but fitting uses v1 |
| E6 science oracles | PARTIAL | W03 historical tests and Chat 1 isolated metric oracle; no combined run |
| E7 schema/persistence | PARTIAL | SQLite v2 tables and old run ACL; migrations/rollback unproven |
| E8 worker recovery | BLOCKED | No actual worker binding/restarted training equivalence |
| E9 browser/API/SDK | PARTIAL | Versioned routes and TypeScript SDK; no exact OpenAPI generation/browser |
| E10 performance | PARTIAL | Only synthetic TS presentation-helper benchmark; no API/load/RSS of worker |
| E11 adversarial QA | PARTIAL | Source/tests exist; exact combined execution not observed |
| E12 hosted QA/release | BLOCKED | W04 hosted runs absent; no security scan |
| E13 three-project E2E | BLOCKED | P25 v2 permit not tied to W03 P1 fitting and P13 envelope |
| E14 reviewer artifacts | PARTIAL | This handoff, branch/PR/CPU CSV, architecture; no screenshots/host proof |

**GA1–GA8 are not concluded by Chat 2.** Existing `docs/week4/W04_RESEARCH_CAREER.md` is a draft evidence packet, not published work. Chat 3 should independently verify 8–15 methods sources, the ethics/methods appraisal and claims, skrub contribution status (no unauthorized upstream PR), official academic program eligibility and funding, one-page UNSENT collaboration proposal, public-proof case study drafts, skeptical referee methods and remaining factual-approval ledger. No correspondence, submissions, applications, publication or endorsements were performed.

## Chat 3 mandatory independent gate checklist

1. Check exact **PR #17 HEAD** and dependency/merge-base against **Chat 1 final HEAD**, W03 #13, isolated #14; do not merge without explicit approval. Ensure all latest Chat 1 policy sources and tests are present.
2. Execute `python -m pytest -q`, `python -m ruff check .`, `python -m mypy --python-version 3.11 src`, plus Python 3.12; fix source/test failures and rerun on the **same SHA**. TypeScript `npm install` then `npm run test --prefix apps/web` with a new committed lockfile if an approved network environment exists; check exact TS source `client.ts`.
3. Independently run actual positive P25 v2 permit → persisted queued job → real W03 train-only split/fitting → P13 receipt → browser export → offline verified root. Current branch does **not** support full gate. Add separately authorized worker with cancellation points, stale-fence protections and revocation checks.
4. Negative tests: cross-tenant same run ID, viewer artifact/rights denial, revoked source, forged permit, stale lease after worker crash, tampered receipts/graph/checkpoint, interrupted/restarted equivalence, replay idempotency, SQL migrations and rollback.
5. Local-only Docker Compose migration/load/backup/restore, dependency inventory/SBOM and approved scans, measured CPU API p50/p95 and memory with realistic sample sizes. Do not infer large-scale behavior from 36 fictional participants.
6. Actual keyboard/focus/contrast/axe/screen-reader/reduced-motion/mobile walkthrough, captured screenshots and recorded browser build; remove inline CSP exception before considering production. Verify browser never embeds tokens in source, storage, URL, error reporting or export.
7. Run private hosted CI **only after checking owner permission and zero-spend runner entitlement**; otherwise keep BLOCKED. Preserve logs and artifact SHA. Do not treat historical W03 PASS as W04 proof.
8. Preserve original sole Career calendar date **2026-11-05** and `Done=unchecked`, Academy untouched at 40h/week, total daily focused learner time ≤10h. Audit GA tasks with primary URLs and owner authorization. Release requires ≥85/100 plus ALL factual/data-rights/security/independent-review gates.

**Final disposition: NO-GO for hosted/public use, research inference or claim of complete three-system execution.**
