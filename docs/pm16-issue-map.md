# PM-16 — Private issue map, labels and newcomer entry points

**2026-10-17 | PRIVATE project evidence, NOT a public invitation.**
The repository was inspected through the connected GitHub account.
Issues below are **real** private GitHub issues, not imagined candidates.
The newly created issue was read back and verified OPEN with the
`good first issue` label. This does not authorize outreach, new users,
public PRs, merges or repository publicity.

## Verified issue index

| Issue | Actual scope | Contributor suitability | Status at audit |
| --- | --- | --- | --- |
| [#1 — Validate synthetic trial schema and dataset-card invariants](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/1) | Core input quality/schema contract | Specialized underlying v0 behavior and integration | Existing; do NOT relabel as trivial |
| [#2 — Seeded synthetic generator determinism and edge cases](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/2) | Scientific generator regression coverage | Requires API and numerical semantics | Existing; not relabeled |
| [#3 — Prevent participant leakage in held-out evaluation](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/3) | Grouped split research integrity | High-risk methodology | Existing; not relabeled |
| [#4 — Reproducible DummyClassifier and logistic baseline comparison](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/4) | Fixed real baseline training/held-out scores | Requires ML and validation knowledge | Existing; not relabeled |
| [#5 — Fail-closed data provenance registry](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/5) | Permissions, synthetic-only registry and validation | Rights/privacy sensitive | Existing; not relabeled |
| [#6 — Canonical manifest and browser-reviewable CI evidence](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6) | Source/env/manifest hashes and legitimate host proof | Requires advanced reproducibility, quota and scientific review | Existing; not relabeled |
| [#7 — Add an offline-only relative Markdown link checker](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/7) | Small, deterministic documentation regression test | **Genuinely bounded beginner-friendly Python/pytest, no model training** | **Created and verified OPEN, label `good first issue`** |

### Evidence and duplicate check for #7

Before creating #7, an actual GitHub issue search returned only six existing
v0 issues and no matches for **link checker**, **documentation** or
**good first issue**. #7 is narrowly scoped to offline relative-link checking
in Markdown documentation, not to generator scientific invariants, model
metrics, external dataset reuse, deployment or an already completed
feature. Acceptance describes exact local-path/line error reporting and
positive/negative test fixtures; external HTTP links are explicitly NOT
fetched. Host test status remains **NOT RUN** until a separately approved
GitHub Actions execution proves success for the submitted change.

An internal issue template being present on this private PM-16 branch does
not make it available in GitHub's live issue chooser yet: GitHub requires
templates on the **default branch**, currently `main`. Owner-approved
PR/merge and CI are still missing. #7 was created by an authorized existing
private GitHub write tool, **not** via a public form or outreach.

## Current prepared templates (source only)

- [Synthetic research-software bug template](../.github/ISSUE_TEMPLATE/bug_report.md):
  sanitized synthetic reproduction, actual SHA, expected/observed,
  no human participant payload.
- [Bounded improvement template](../.github/ISSUE_TEMPLATE/improvement.md):
  duplicate search, small acceptance criteria, rights/science conditions,
  truthful `NOT RUN` flags.
- [Issue chooser config](../.github/ISSUE_TEMPLATE/config.yml): no external
  company/maintainer contact list or PR invitation.
- [PR review template](../.github/PULL_REQUEST_TEMPLATE.md): source/test/rights
  and reviewer gates but **no PR created or authorized**.
- [CONTRIBUTING](../CONTRIBUTING.md): genuine private repository paths,
  contributor instructions, issue response/security guidance and explicit
  owner-approval boundaries.

## How to review a future first issue honestly

Only already authorized private collaborators can see this list. Review
small issues by exact file/branch diff, require synthetic-only input and
a meaningful fail-before/pass-after test, and record `NOT RUN` without
linkable hosted proof. The AI engineer may author fixes privately under
explicit mission scope, while the owner reviews permission-sensitive
actions. Do not ask the owner to perform coding or local CLI work.

**Gate: GO for private issue hygiene and source review; NO-GO for
public contributor recruitment, hosted test success or merge.**
