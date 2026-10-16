# PM-06 — Day 2 data-stage changelog and evidence

**Recorded:** 2026-10-16. **Overall status:** private REVIEW BRANCH
IMPLEMENTED / hosted CI **BLOCKED** / descriptive artifacts **NOT RUN**.
This ledger distinguishes committed source from observed execution.

## PM-06 final static CI-hardening checkpoint — 2026-10-16

- Verified official GitHub tag refs and pinned source-control actions to exact upstream commit SHAs in the [manual-only workflow](../.github/workflows/ci.yml): [actions/checkout v6](https://github.com/actions/checkout/tree/d23441a48e516b6c34aea4fa41551a30e30af803), [actions/setup-python v6](https://github.com/actions/setup-python/tree/ece7cb06caefa5fff74198d8649806c4678c61a1), and [actions/upload-artifact v4](https://github.com/actions/upload-artifact/tree/ea165f8d65b6e75b540449e92b4886f43607fa02). Tag resolution was a real GitHub API read; it does not verify runtime compatibility.
- **Existing first-party GitHub app cannot start new workflow runs:** available Actions tools permit reading run/jobs/logs and *re-running* existing jobs but provide no dispatch-new-workflow operation. Current review branch has **zero** hosted runs.
- GitHub Actions has not executed on this updated branch. Pytest, Ruff, strict mypy, Parquet integration, source-manifest exports, synthetic summary, and figure results remain **NOT RUN**. This is an explicit blocker, not a failed test.
- For user-authorized **manual** run: visit the [CI workflow](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/workflows/ci.yml), choose **Run workflow** and select branch `pm06/data-quality-provenance`. Before triggering, verify that the owner's GitHub Actions budget/available included minutes avoids unauthorized billing. Once dispatched, the connected GitHub app can retrieve the actual job logs and stored artifacts.
- The private-repo, no-publication, no-PR, no-real-data boundaries remain enforced. The next mission PM-07 is not marked Verified Done while this gate is unresolved.

## Addendum — execution-ready metadata and improved CI evidence

- [Machine-readable synthetic pilot source plan](../data/pm06-pilot-plan.json)
  explicitly distinguishes expected configuration (12 invented participants x
  20 invented trials, seed 73) from **UNEXECUTED** source hashes, test status,
  observed trial counts and artifact digests (`null` in the plan, not invented).
- Manual-only [Actions workflow](../.github/workflows/ci.yml) now uses
  Node 24-capable `checkout@v6` and `setup-python@v6` actions,
  saves pilot artifacts, prints the exact Git commit, Python version,
  dependency list, generated provenance JSON and artifact SHA-256 values
  when a real hosted run is authorized and completed.
- **NOT RUN remains unchanged** for this PM-06 branch. Private Actions can
  consume billable minutes above the repository owner's plan allowance;
  neither account remaining quota nor a zero-spend budget was verifiable
  through the available repository connector. No workflow trigger was
  used, and no new login, spending, PR or public release occurred.
  See [GitHub's billing policy](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
  and [included quotas](https://docs.github.com/en/billing/reference/product-usage-included).

## Base and preserved dependencies

- Base: [PM-05 main commit 944559a](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/944559a98386dd7c40ea9511ec9857d0714d3ca2).
- Reused [PM-05 loader](../src/psychneuro/loaders.py),
  [quality gate](../src/psychneuro/quality.py),
  [schema](../src/psychneuro/schema.py),
  [synthetic generator](../src/psychneuro/synthetic.py),
  [source registry](../data/registry.json) and [existing PM-05 tests](../tests/test_pm05_loaders.py).
- The registry is still synthetic-only: all six real OpenNeuro metadata
  candidates remain disabled. No dataset or participant file downloaded.
- Repository was verified **PRIVATE**. New work is in
  [pm06/data-quality-provenance](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm06/data-quality-provenance).
  No PR, merge, public release, or automatic CI was performed.

## Task-specific evidence

| Task | Code/doc evidence | Verification status |
| --- | --- | --- |
| [P1-022](https://app.notion.com/p/3fa977a963b281e2ba8af8edb152abe2) | [11 loader regression cases](../tests/test_loaders.py): malformed quoting, UTF-8 error, header-only empty data, ragged/extra fields, duplicate composite key, duplicate order, integer parse, infinite latency, inconsistent response, symlink refusal; [commit 8d77329](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/8d773295be233631dd51f5c4cea3adbee0d71c26) | COMMITTED, tests NOT RUN |
| [P1-023](https://app.notion.com/p/3fa977a963b281e587fbf873a567c25c) | [Manual CI workflow](../.github/workflows/ci.yml) includes Python 3.11/3.12, pytest, Ruff, strict mypy, Parquet extra, pilot export and 7-day artifacts; [commit 4322c0a](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/4322c0af1bb35d2850d50d5fb81d62d08cc7c6f5) | **BLOCKED**: no dispatch-capable authorized GitHub connector on this turn and no verified private Actions free quota; no run on PM-06 SHA |
| [P1-024](https://app.notion.com/p/3fa977a963b2811c8db5cff1549ac091) | [Deterministic descriptive exporter](../src/psychneuro/explore.py) [commit a9fb81c](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/a9fb81cdfc233d1bb9d00291e61563d90dbfa5d5), [two artifact contract tests](../tests/test_explore.py), [planned hosted invocation](pilot-exploration-protocol.md) | SOURCE COMMITTED; **NOT EXECUTED**; NO result figures/hashes |
| [P1-025](https://app.notion.com/p/3fa977a963b28172bbf4e0d6f61a89fd) | [Synthetic dataset card](data-card.md) [commit af74a12](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/af74a1216076fb7609bb2da0ff898c0a6489e77b) with real source/rights, columns, latency/leakage exclusions, misuse warnings | DOC COMMITTED, source verified; artifact results NOT RUN |
| [P1-026](https://app.notion.com/p/3fa977a963b2815d9ca2fc0a20ed9e81) | This changelog, plus GitHub commits above; will need addendum for exact CI results | COMMITTED / awaiting hosted verification evidence |

The existing loader's `ProvenanceManifest` is generated dynamically; no
fictitious raw hash, checksum, trial count, or run result has been inserted.
For generator input its raw-file hash must remain `null`. Summary, SVG and
manifest artifacts are emitted **only on actual hosted execution**.

## Verified CI read-back, but NOT for current changes

[Earlier PM-04 hosted run #38874446677](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677)
ran on commit `6f63804b5c476a689085b0ce8080452f2181d572` and completed
successfully. Its actual job log reported **80 passed in 0.13s**,
**Ruff: All checks passed!**, and **mypy: Success: no issues found in 4
source files**. Those statements apply **only to that earlier
PM-04 job**; they are not PM-05 or PM-06 verification. The current
PM-06 source commit is not covered by that run.

## Review and release gate

1. Review [loader tests](../tests/test_loaders.py), [exploration exporter](../src/psychneuro/explore.py) and the [data card](data-card.md).
2. Obtain owner-authorized hosted Actions dispatch with confirmed no unapproved
   cost; run the exact PM-06 SHA; retrieve jobs/logs/artifacts.
3. Fix any failure in a new private branch commit, then re-run and record the
   final SHA, Python versions, test counts/skips, Ruff/mypy and artifact hashes.
4. Check that the manifest's generator seed/version/source hash matches the
   archived summaries and figure and the [registry](../data/registry.json).
5. Do not merge, publish, accept real records, represent scientific results,
   or mark Notion Verified Done before these gates are completed.

**Current gate: NO-GO** for scientific result claims, release, and final
"Verified Done" status. This document logs implementation honestly, not
an approved or executed human study.
