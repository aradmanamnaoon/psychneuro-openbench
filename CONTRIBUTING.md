# Contributing to PsychNeuro OpenBench (PRIVATE PRE-RELEASE)

**Status: written on a private PM-16 feature branch, not a call for public
contributions.** Only existing authorized repository collaborators may
review/internalize these instructions. Do not make the repository public,
create a public fork or PR, invite external contributors, send unsolicited
outreach, publish a release, or spend paid runner minutes without specific
owner approval. This file is the proposed contribution policy; it has
**not** passed a live contributor onboarding session or clean hosted CI.

## Mission and research integrity

This nonclinical reproducibility workbench uses **original invented two-choice
behavioral trials**. Permitted research-software changes must make source
rights, grouped holdouts, pre-response features, fixed baseline protocol,
seed provenance and honest uncertainty *more* auditable. We do not solicit
patient information, real participant datasets, protected research records,
clinical predictions, fake human-subject claims or scraped inputs. Metadata
for external OpenNeuro candidates is **not** a right to download/ingest.
Read [v0 contract](docs/spec-v0.md), [dataset policy](docs/license-policy.md),
[PM-16 reproduction ledger](docs/reproducibility.md) and
[release gates](docs/release-gates.md).

## The actual repository layout (source-checked 2026-10-17)

- `src/psychneuro/`: original synthetic generation,
  rights-checked `loaders.py`/`registry.py`, grouped
  `experiments.py`, repeated `pipeline.py`, strict
  `reporting.py`, bounded `workflow.py`, and UX/privacy
  utilities. These APIs are not a validated medical product.
- `configs/baseline.json`: fixed prespecified v1 model/metric/split
  protocol, canonical input SHA and protected feature timing.
- `data/registry.json`: only original synthetic generator enabled; human
  dataset entries are disabled metadata.
- `tests/`: grouped split, pipeline, loader, report, application and PM-15
  deployment-preflight specifications. **A test file existing does not mean
  it passed current SHA CI.**
- `app.py`: source-only Streamlit private UI, with three distinct permitted
  modes: model-free preview, validated PM-10 report inspection and explicit
  bounded original synthetic benchmark execution. **No hosted URL exists.**
- `.github/workflows/ci.yml`: manual-only private Linux Actions matrix
  for Python 3.11/3.12. A clean run must be approved and its logs linked.
- `docs/`: tutorial, usage constraints, scientific contracts,
  reproducibility methods, security/privacy audit and dated changelogs.
- `pyproject.toml`: typed Python package and dev/benchmark/ui optional
  dependencies. `requirements.txt` carries PM-15 candidate direct runtime
  pins, not a complete tested lock.
- `LICENSE` and `NOTICE`: Apache-2.0 for original project source and
  attribution; not automatically for datasets, assets or dependencies.

## Internal issue triage and reporting quality

Before suggesting a new ticket, search [existing repo issues](https://github.com/aradmanamnaoon/psychneuro-openbench/issues)
including **closed** ones and read scope/dependencies. Broad v0 issues
already exist for data validity, generator invariants, leakage prevention,
baseline metrics, rights and canonical manifest. Add specific subproblem
evidence to the matching issue rather than creating duplicates.

A useful authorized issue needs: one observable expected behavior or user
problem; affected file/API; original-synthetic minimal reproduction or
documented non-run status; exact branch/SHA; a **bounded** acceptance test;
data/privacy implications; scientific limitation; and any dependency/CI
permission gate. Never paste log tokens, credentials, names/emails of
participants, medical details or raw human data.

**Labels:** `good first issue` is only appropriate for a self-contained
documentation or test-quality task with a small, clear diff; not a task to
change scientific model selection, upload real data, audit hosting security,
rewrite grouped splits or assert empirical results. Use existing repository
label names only; check application of each label in the issue read-back.
Labeling a private issue does not authorize external invitations. A
`blocked` status must be explicit when it depends on unapproved host spend.

## Internal contribution and code review flow

1. Confirm that you are already authorized to read/write this private
   repository. New users and external PRs require owner approval; none is
   requested by this policy.
2. Choose an existing discrete private issue. Define scope, acceptance
   evidence, touched paths and data-rights boundary before changes.
3. For source changes keep versioned seed/split/model/metric protocols
   frozen unless a separate scientific version and review is approved.
   No row-based leakage, post-response predictors, cherry-picked runs,
   made-up metrics, CI IDs, screenshots, reviewers or endorsements.
4. Write focused tests for negative/edge inputs; use original synthetic
   fixtures and keep mock metrics clearly labeled **test-only**. Do not
   mutate real/human rights policy or load external data as a workaround.
5. Keep docs honest about whether source code was committed, a test was
   **NOT RUN**, a log was actually observed, or a browser actually worked.
   Update README/changelog only with exact evidence and limitation links.
6. Source authors and reviewers may use the configured command sequence
   in [the hosted reproducibility guide](docs/reproducibility.md), but
   **no ChatGPT local CLI or automatic GitHub Actions execution is
   authorized by this document**. Private hosted runs may cost money.
7. A PR requires separate explicit owner permission. Until then, commit
   changes only on an approved private branch and give the owner
   exact source/commit references for review; do not merge/tag/deploy.
   A passing test on an older SHA is not a passing test for the proposed
   diff.

## Minimum review rubric (reviewer checks the actual changed code)

- **Scope:** one issue, code paths and documentation accurate, no invented
  capabilities or public-facing claims.
- **Scientific design:** participant group boundaries preserved,
  training-only model selection, no test-label leakage, no unauthorized
  predictor/time feature.
- **Dataset rights:** original synthetic only, registry fail-closed and
  no personal/PHI or prohibited redistribution.
- **Reproducibility:** exact config/seed/run identity, deterministic digest,
  negative/ineligible tests, no "best seed" selection, no fake CI proof.
- **Software quality:** type safety, subprocess/dependency/bounds/security,
  input validation, error messages, licenses and notices where relevant.
- **Accessibility:** keyboard/labels/chart data alternatives, missing or
  malformed input states, browser testing only if actually run.
- **Evidence and approvals:** hosted pytest/Ruff/mypy and artifact hashes
  from exact SHA, or clear **BLOCKED/NOT RUN**; no unapproved spend or public
  activity.
- **Documentation and review:** user-facing limitations, maintainable small
  diff, linked issue, reproducibility notes, original authorship.

A reviewer can request changes, defer scientific claims, or reject unsafe
inputs even when tests pass. **Do not self-approve your own code**, and do not
interpret an AI-authored test specification as successful independent review.
No fixed response-time promise is made; issue response timing depends on
actual authorized maintainer availability. Labels and priorities do not
create a service-level agreement.

## Security issue response policy

Treat credentials, abuse vectors, private-repo access leaks, harmful data
uploads and dependency-vulnerability findings as potentially sensitive.
**Do not disclose exploit steps, secrets, third-party contact details or
raw datasets in public issues.** A repository collaborator can use an
existing private issue for sanitized, non-exploitable observations, but
confidential exploit details belong in a separately approved private
security reporting channel. No official external vulnerability intake,
bug bounty, paid reward or incident response team is represented.

## When this file becomes active

The default GitHub branch is `main`, while these new issue/PR templates and
policy are written on `pm16/repro-docs-contributor-onboarding`.
**GitHub will not offer the templates in its UI until they are present on
the default branch**, which needs a separately approved PR/merge. This
policy alone does not authorize that step. The repo must stay PRIVATE
until [all release gates](docs/release-gates.md) are satisfied and
publication separately approved.

**Current GO:** read-only private reviewer/onboarding documentation.
**NO-GO:** claim tested contributor workflow, launch public community or
accept PRs/issue submissions from unauthenticated outsiders.
