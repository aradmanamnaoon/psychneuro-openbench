# W04 Chat 3 — continued implementation, branch reconciliation and evidence boundary (2026-10-19)

**PRIVATE AUDIT ONLY · NO-GO · DO NOT MERGE OR DEPLOY.** This note records newly committed source and externally checked GitHub states, not imaginary successful tests. It supplements (rather than overwrites) the earlier [400-test local QA](CHAT3_EXECUTED_QA_EXACT_SOURCE_20261019.md), [66-worker-test source-limited QA](CHAT3_REAL_WORKER_INTEGRATION_QA_20261019.md) and [private browser/axe QA](CHAT3_BROWSER_ACCEPTANCE_QA_20261019.md).

## Verified incremental implementation

- The **existing** private DRAFT PR [#22](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/22) carries the work. Repository remains **private**, `main` unchanged.
- Added `tests/test_w04_sigkill_process_restart_v6.py`: POSIX subprocess runs **actual W03 synthetic fitting**, writes a postfit marker, is terminated with OS SIGKILL before publication, then fresh P25 policy/W04 queue/worker objects reopen the same SQLite DB and attempt deterministic retry. Assertions target one immutable P13/P25 artifact, one publication event, two fenced attempts, and identical run ID. This test has **NOT YET BEEN OBSERVED PASSING**. It does **not** prove host power loss, midfit continuation, durability across nodes or filesystem fsync semantics.
- Added `tests/test_w04_sqlite_backup_restore_v6.py`: SQLite online backup of completed real-fit aggregate, reopen/read after restoration, `PRAGMA integrity_check`, plus intentionally tampered restored payload refusing authorization/read. **COMMITTED, NOT YET EXECUTED**. A local online backup does not establish production disaster-recovery RTO/RPO, encryption, key custody or migration rollback.
- Added `tests/test_w04_concurrent_worker_race_v6.py`: four independent policy/queue/worker instances via ThreadPoolExecutor compete for one real synthetic job; asserts **one success / three fenced claims, one artifact, one publication event, one attempt**. **COMMITTED, NOT YET EXECUTED**; single-host threads do not model multi-node queues or adversarial infrastructure faults.
- Reconciled the most recent Chat2 `apps/web/src/science.ts`, `apps/web/tests/{client,science}.test.mjs`, and `docs/week4/CHAT2_CONTINUATION_20261019.md`: their exact Git blob SHAs **match** Chat2's updated branch. These harden reporting identity, source/split/model/benchmark graph topology, and the typed private SDK's URL/token/error boundaries. The browser UI still does **not** necessarily execute that SDK.
- Preserved the stricter Chat3 workflow with both manually requested and narrowly scoped private-branch push triggers, the pinned committed Node lockfile, separate `npm run typecheck`, `npm test`, and Python 3.11/3.12 pytest/Ruff/mypy matrix. It has **no publish, deploy, merge or upload step**.
- Safely created a **two-parent merge commit inside the draft review branch only**, after verifying Chat2's five changed file paths were preserved (four byte-identical, workflow intentionally superseded by stronger branch-scoped CI). GitHub independently reports PR #22 **mergeable**, and the head branch **0 commits behind** the current Chat2 base. **This does not merge PR #22 into its base, main, or production.**

## Exact evidence status and unfinished hard gates

| Required result | Current evidence | Gate |
| --- | --- | --- |
| Earlier W03 and W04 source-level quality checks | Historical 400-pass Python3.13 snapshot; 66-pass isolated newer-worker snapshot, nonidentical source dates | Partial; neither may be relabelled current-head PASS |
| New physical OS-kill recovery | Test source committed, no observed run | BLOCKED |
| Genuine fitted concurrency and SQLite restoration | Two test sources committed, no observed run | BLOCKED |
| Hosted exact-HEAD Python3.11, Python3.12 and TypeScript | Private Actions push-created runs report `queued` at the time of writing, no job conclusions/logs | BLOCKED |
| P13 independently authenticated source/report root | No external signer, custody or rotation evidence | BLOCKED |
| P25 human-data licence, consent/ethics and retention | Synthetic-only policy contract, no independent grants | BLOCKED; **do not enable human/third-party datasets** |
| Security, SBOM/CVE and production performance | Limited synthetic API/TestClient benchmarks and local QA; no full deployment-equivalent test or CVE clearance | PARTIAL/BLOCKED |
| Independent human scientific, security and WCAG/screen-reader review | None established; local automated axe is not human certification | BLOCKED |
| GA1–GA8 private research/career outputs | Existing narrative evidence, methods, skeptical referee, proposals, draft case study, candid admissions intelligence | PARTIAL drafts; none submitted/endorsed |

**Final decision remains NO-GO**, regardless of future passing unit tests until all independent trust, data-rights, external review and recovery gates are actually evidenced. Do not quote a numerical >=85 or >=90 release score as satisfying any hard gate when one remains failed or unevaluated.

## Immediate operator/reviewer execution commands (never claim output before execution)

```sh
python -m pytest -q tests/test_w04_sigkill_process_restart_v6.py tests/test_w04_sqlite_backup_restore_v6.py tests/test_w04_concurrent_worker_race_v6.py
python -m pytest -q
python -m ruff check .
python -m mypy --python-version 3.11 src
npm ci --prefix apps/web --ignore-scripts --no-audit --no-fund
npm run typecheck --prefix apps/web
npm test --prefix apps/web
```

Inspect [the current private Actions run list](https://github.com/aradmanamnaoon/psychneuro-openbench/actions) to tie every passing conclusion to the **actual current PR HEAD**, Python runtime, log, test count and wall clock. Never assume queued jobs will be granted runners, or spend/buy GitHub Actions capacity without an explicit separate user decision.

## Scope and ownership

Notion [single W04 Career card](https://app.notion.com/p/3fd977a963b281d29c67df3f38231508) must remain `2026-11-05`, `In Progress`, `Done=false`. The Academy is independent and read-only. PR merge, private or public deployment, human/third-party data, academic publication, outreach, upstream public contributions or payment are not authorized by a test fixture or this report. Source commit and test failures are not scientific/clinical results.
