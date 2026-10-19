# W04 P25 synchronous-publication race closure — 2026-10-19

**Decision: NO-GO, private draft only.** This is an implementation/evidence note, not an independent certification, hosted current-SHA test, clinical result or license grant.

## Security defect and fix

The earlier `strict_facade.run` implementation called `DurableRightsBridge.prepare_run` and verified its P25 permit **before** persisting W03 data. The subsequent `OwnerBoundRunStore` correctly made W03 run plus tenant ownership atomic, but policy revocation could still occur **between** that pre-persist check and `BEGIN IMMEDIATE`. The check and write had separate linearization points.

The strict synchronous route now calls `DurableRightsBridge.prepare_atomic_run`, returning:
1. An ordinary pre-persist (post-fit) authorization check.
2. A `before_commit(sqlite3.Connection, record)` callback invoked **inside the same SQLite write transaction** which inserts the immutable P13 run, provenance index, and tenant ACL claim.

The inside-transaction check requires:
- Authentic P25 permit HMAC under the operator-provisioned key and the exact issuer's tenant, subject, action/purpose.
- P25 event-chain and snapshot integrity, nonrevoked policy, matching revision and SHA, live permit and retention deadline.
- Exact original-synthetic source SHA (both attested source and W03 result), synthetic rights scope, policy action scope.
- No intervening revocation: SQLite `BEGIN IMMEDIATE` excludes a competing writer until commit/rollback, assuming ALL P25 mutations use the same SQLite file and transaction semantics.

Files changed: `src/psychneuro/w04/durable_bridge.py`, `product.py`, `strict_facade.py`; `tests/test_w04_strict_security_unified.py` gains (a) actual W03 real synthetic fitting in a nonpersistent buffer, then policy revocation before writer admission, asserting **zero durable run+owner rows**; (b) digest substitution denial under a writer lock. Existing strict endpoint tests also exercise cross-tenant duplicate identities, denied unsigned imports, catalog contract, and non-inline CSP.

**Safety boundary:** This closes the *synchronous strict route* publication gap. The separate `private_worker_v4.py` already has an independently implemented lock-scoped P25+fenced publish check; these are two distinct execution paths. In-fit preemption, distributed multi-DB atomicity and legal rights are not proven. The callback uses the existing P25 internal verifier primitives; a later refactor should expose a stable versioned transaction-guard API.

## Observed verification, distinctly scoped

- **Hosted ancestor audit base SHA `c8b7d871d2d3f389b62888df97277a56e559c940`:** [GitHub run 39288865774](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39288865774) **completed SUCCESS**, with Python 3.11, Python 3.12 and TypeScript jobs successful. Earlier audit handoff reports 491 Python tests plus Ruff/mypy success on this **ancestor only**. This run does NOT test this fix or the unified worker/UI overlay.
- **Unified client/science source set:** four Git blob IDs matched local files; Node 22.16.0 and global TypeScript 5.8.3: `tsc -p apps/web/tsconfig.build.json`, no-emit typecheck, and **11 Node unit tests PASS**. Neither real HTTP nor Python rights transactions were executed by that TypeScript test.
- **New P25 callback, new Python tests, merged authenticated worker/UI and strict CSP** have NOT been executed as a complete exact-HEAD Python 3.11/3.12/Docker/Chromium suite. An attempted private-source staging in an isolated sandbox timed out; it is **not** a PASS/FAIL for the source itself.

## Reviewer acceptance / reproduction

```sh
# From a clean private checkout pinned to the exact current PR #24 head:
python -m pip install -e '.[dev,benchmark,w03,ui,parquet]'
python -m pytest -q tests/test_w04_strict_security_unified.py tests/test_w04_worker_routes_v5.py
python -m pytest -q
python -m ruff check .
python -m mypy --python-version 3.11 src
python -m mypy --python-version 3.12 src
npm ci --prefix apps/web --ignore-scripts --no-audit --no-fund
npm run typecheck --prefix apps/web
npm test --prefix apps/web
# Afterwards: isolated browser keyboard/axe, Docker DB backup+restore,
# SIGKILL worker recovery and measured load/security/rights review.
```

Original career mission: 2026-11-05–11; `In Progress`; `Done=false`. Academy unaffected. Do not merge/publicly deploy/submit or claim W04 release until all independently verified hard gates meet the original rubric.
