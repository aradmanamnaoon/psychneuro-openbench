# CHAT2_PRODUCT_VALIDATION_HANDOFF — W04 private P1/P13/P25

**As of 2026-10-19 (before scheduled W04 2026-11-05–11).**  
**Private dependent DRAFT:** https://github.com/aradmanamnaoon/psychneuro-openbench/pull/15  
**Branch:** `review/w04-chat2-product-20261019`  
**Implementation code freeze before this handoff:** `1b998c92af91e1f92e80b9093bee9be706556667`  
**PR base:** `review/w04-p25-private-integration-20261019` at `7c0ffd2b6779b22dbdebfc443f9827e9ba502536`; that branch is downstream of W03 `8e511988e1feecce434eb7a5c109df5ebaf4ef90`.  
**Exact W03 hosted proof (historical; NOT this head):** [Actions 39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934), tested `4eeb17845dac7641b75d9a8164f125db6c213659`, Python 3.11/3.12. **Do not transfer PASS to W04.**

## Source/evidence found

- **Chat 1 handoff** `docs/week4/CHAT1_BACKEND_HANDOFF.md`: **not found** in searched branch list, W04 preexisting reference or Notion page at inspection. Chat 1 work NOT assumed complete.
- W03 P1 grouped nested CV, immutable RunStore and P13 SHA DAG were examined in real connected repository. Existing W04 branch had P25 decisions/ledger, v1 REST, SQLite metadata job protocol, and static UI; 13 *earlier* isolated tests used shadow W03, NOT actual runner.
- Existing PR #14 is independent small reference and remains untouched/unmerged. PR #13 and W01–W03 histories preserved. No third-party deployment or branch merge.

## Exact changed-source inventory for Chat 2

- `src/psychneuro/w04/product.py`: new v2 P25 rights preview/catalog, real W03 execute adapter, v2 versioned deterministic RunResult, run compare (descriptive BA difference only), split count/graph with verification, authorized artifact export/verify/import, SQLite `w04_run_acl` with tenant and owner claim.
- `src/psychneuro/w04/rights.py`: added server-bound `Principal.tenant` field, default `local` for existing single-tenant compatibility. **Not production IAM.**
- `src/psychneuro/w04/api.py`: mounts v2 in existing app, enables `/w04/openapi.json` (declared app version 0.4.2); protects legacy v1 read/graph/export with owner claim, scopes v1 jobs by tenant + actor; no hosted OpenAPI schema generation observed.
- `src/psychneuro/w04/ui.py`: actual same-origin API-driven rights preview, run creation, two-run table, 4-node graph, artifact download/hash verify, metadata jobs. textContent-safe labels, visible focus and live status; no screenshot, browser keyboard or axe evidence.
- `apps/web/src/client.ts` + `apps/web/tsconfig.json`: strict typed TS client for v2 endpoints. This TS module is an SDK, not the served HTML's compiled bundle.
- `tests/test_w04_interop_api.py`: fixture adapted to fail-closed run ACL. `tests/test_w04_product_v2.py`: **new committed but not executed** real W03 registry-backed TestClient test for idempotency, no viewer run, cross-tenant/v1 access denial, comparison, split, graph, export, tampered receipt, wrong role, conflicting import, revoked rights.
- `compose.yaml`, `.env.example`, `infra/Dockerfile`: loopback-only host port, CPU-only non-root runtime, isolated volume and conservative resource caps. Docker build/smoke **not executed**, image digest not locked.
- `.github/workflows/w04-private-manual.yml`: manual-only Python 3.11/3.12 full suite/ruff/mypy/pip check, dependency inventory artifacts, TS SDK typecheck, local Docker smoke, advisory pip-audit; never dispatched.
- `docs/week4/CHAT2_ARCHITECTURE_AND_RUNBOOK.md`: architecture, contracts, ops, threat and migration limits.

**No model-fitted checkpoint or worker was added.** The UI metadata job controls are not a cancellation or resume of W03 training. The P25 grant and P13 receipts are neither legal grants nor signatures.

## Observed validation (do not overstate)

1. **Source inspection:** repo confirmed PRIVATE; branch ancestry W04 preparatory HEAD 3 commits ahead of W03 branch, exact commit refs above; PR #15 created PRIVATE DRAFT and no merge. GitHub status check for W04 commit **not executed**. No runner minutes triggered.
2. **Exact remote W04 browser inline JS:** fetched from committed `ui.py` and syntax-checked with a JS parser (`new Function`) → **PASS syntax only**; accessibility and DOM functional runtime **NOT tested**.
3. **Local *separate prototype* (not exact GitHub SHA):** local TypeScript interface compiled with global `tsc` and JS syntax checked by Node; does **not** certify committed TS SDK nor browser workflow. `py_compile` on a local independent adaptation of product module succeeded, not a connected W03 full import run.
4. **Local ACL microbenchmark attempt:** timed out, **no valid new p50/p95/RSS CSV**. The inherited pre-Chat2 rights/jobs microbenchmark is on preparatory code, not this head.
5. **Hosted W04 Python tests, Ruff/mypy, container smoke, security scan, SBOM, CI artifact URL, Playwright/axe, screen reader, full scientific replay, actual API latency and browser critical path:** **NOT RUN/BLOCKED**. No screenshots or workflows to archive. No actual vulnerability count can be asserted.

## Run/check commands for independent reviewer (not claims of execution)

```bash
# In an authorized isolated checkout of the exact private PR #15 HEAD:
python -m pip install -e '.[dev,benchmark,w03,ui,parquet]'
python -m pytest -q tests/test_w04_product_v2.py tests/test_w04_interop_api.py
python -m pytest -q
python -m ruff check .
python -m mypy --python-version 3.11 src
# Repeat Python matrix on 3.12, compare exact SHA and dependency inventory.
npm install --prefix apps/web --no-package-lock --no-save --ignore-scripts typescript@5.8.3
apps/web/node_modules/.bin/tsc -p apps/web/tsconfig.json
cp .env.example .env
# set a NEW high-entropy W04_PRIVATE_TOKEN in .env; do not commit or log it
docker compose --env-file .env build
docker compose --env-file .env up -d
curl --fail http://127.0.0.1:18080/health
docker compose --env-file .env down
```

Backend OpenAPI is declared FastAPI app `version=0.4.2`, `openapi_url=/w04/openapi.json`. **Actual generated schema and TS/Python schema parity checks are not executed**. Existing Pydantic Python client models are reused. TS SDK is manually typed, **not generated from OpenAPI**; drift remains possible. No transitive lock or verified SBOM.

## E1–E14 coverage — code submitted is not independently verified

| Epic | Assessment | Evidence / outstanding |
|---|---|---|
| E1 | PARTIAL | API run and two-run UI; one rights-cleared synthetic dataset only, real browser absent |
| E2 | PARTIAL | P13 DAG list and hash-envelope verify/export; signer authenticity absent |
| E3 | PARTIAL | Tenant-scoped job metadata; actual worker cancellation/restart BLOCKED |
| E4 | PARTIAL | Compose/Docker/manual CI source; build/smoke/locks BLOCKED |
| E5 | PARTIAL | Reused P25 fail-closed policy; legal review/revocation lifecycle BLOCKED |
| E6 | BLOCKED at Chat2 head | historical W03 grouped baseline exists; no new exact-head oracle/multiseed CI |
| E7 | PARTIAL | SQLite ACL table; versioned numbered migrations and fully atomic run+ACL absent |
| E8 | BLOCKED | no durable computational worker, stale-lease retry or backpressure implementation |
| E9 | PARTIAL | browser HTML + TS typed SDK and real API contract; no actual browser E2E |
| E10 | BLOCKED | no valid new p50/p95/throughput/RSS measurements |
| E11 | PARTIAL | committed negative TestClient cases, tenant guard; not executed at exact head |
| E12 | BLOCKED | manual-only CI defined, no hosted dispatch/observed results/rollback |
| E13 | PARTIAL code / BLOCKED proof | actual W03 execute call connected to P25/P13 in source, but unexecuted end-to-end |
| E14 | PARTIAL | draft PR, architecture, runbook, this evidence ledger; independent review absent |

## Chat 3 independent audit — mandatory order

1. Fetch PR #15 exact current head and this handoff; independently review diffs, compare with W03 PR #13 and W04 ref #14; **read any later Chat 1 handoff if it appears** before resolving backend contracts.
2. Check real W03/P13/P25 registered synthetic job end-to-end against actual code, 3.11/3.12 and real W04 ACL fixtures; investigate any test/type failures before CI. Verify no tenant bypass through *any* v1/v2 route and no owner-claim loss on crash. Test revoked/expired rights, wrong role, corrupted graph/index, tampered receipt, replay/race, sealed test leakage and invariant checks.
3. Review OpenAPI schema and TS client parity; cover dynamic errors/rate limits, no secret leaks, CSP inline-script allowance, browser-auth model. Confirm `w04-error-2` errors are not complete for FastAPI validation or v1 routes.
4. After independent cost/billing permission check, optionally authorize **manual** hosted Actions dispatch. Keep exact SHA, job URLs and artifacts. Run real Docker smoke, Playwright/axe keyboard/screen-reader/motion walkthrough and resource limits, no third-party deployment.
5. Measure CPU-only P1 duration, API p50/p95 with n/concurrency/seeds/hardware, memory and hostile workload, and real restart/cancel feasibility. Do not conflate old 36 fictional IDs with scale evidence.
6. Audit GA1–GA8 existing W04 research/career appendix *independently*: scientific studies, rights/publication claims, funding/eligibility sources, outreach draft, ethics/critical reviewer report; no submission, contact, public profile edit or research findings without separate consent. One W04 original 2026-11-05 Career card only; no Academy changes.
7. Release decision **NO-GO** until independent threshold, rights/legal clearance, authentication, actual browser security/accessibility proof, numerics and owner signoff. Do not merge or publish from this PR.

**Operator approvals not present:** GitHub Actions runner spend/dispatch, real private host, public deployment, publication, external reviewers or outreach. All remain blocked. **Done remains unchecked.** Academy remains separate 40h/week; learner-focused work <=10 h/day total. R-course reminder only; three original videos/week optional, not claimed completed.


## Post-handoff security and contract correction (private review only)

After the original handoff was recorded at commit `285569d7e265c704810669ae1b210d2925885c6e`, two additive implementation changes were made:
- `src/psychneuro/w04/product.py` now calls an injected persistent P25 audit callback for each v2 protected authorization verdict, including denied decisions; code change commit `d1f6a4591f039c7bee78c9eea156474ef65ebdd5`.
- `src/psychneuro/w04/api.py` now binds that callback to the preexisting metadata `LedgerStore` (fail closed when auditing fails); code change commit `be34e787ec6049f7bee072ec00df65aec57b9b77`.
- Added `tests/test_w04_acl_contract.py` at commit `260304253bff44919a440496e7f1d7f8194573a2` with concurrent ownership claim, schema-path and static accessibility assertions; **test source only, NOT run**.
- Consequently, the earlier recorded `1b998c92...` code freeze is historical. The **latest pre-handoff-update source/test SHA** is `260304253bff44919a440496e7f1d7f8194573a2`. The final documentation-only commit follows this note. Neither SHA has exact-code hosted tests, lint, Docker, browser, accessibility or performance results.
- The private PR is still a draft, all external release and hosted-run safety gates remain NO-GO.

**Reviewer note:** The previous independent Chat 3 report in the W04 card predates these Chat 2 code changes. That report cannot serve as independent validation of this branch. A separate exact-code review and no-spend authorization are needed before any hosted action.
