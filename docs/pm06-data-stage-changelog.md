# PM-06 — Day 2 data-stage changelog and evidence

**Recorded:** 2026-10-16. **Overall status:** private REVIEW BRANCH
IMPLEMENTED / hosted CI **BLOCKED** / descriptive artifacts **NOT RUN**.
This ledger distinguishes committed source from observed execution.

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
