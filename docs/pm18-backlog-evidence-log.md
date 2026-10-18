# PM-18 — Real issue backlog, traceability, and internal daily evidence log
**Date:** 2026-10-18. AI-assisted engineering audit; user reviewer. Existing PM-17 and PM-19–21 source and GitHub records were read. **NOT** a public milestone or executed workflow success claim.

## Source-level weakness ledger (not user reports)
| Priority | Identifiable gap/why this matters | Action and acceptance | Actual tracking |
| --- | --- | --- | --- |
| **P0** | PM17 branch lacks exact-SHA hosted workflow proof. Without execution, authored split/metric/tests and exports are hypotheses about code behavior, not verified acceptance. | Run manual Python 3.11/3.12 pytest/Ruff/mypy, dependency resolution, exact expected artifacts on candidate commit, record all failures and artifact hashes. | Existing [#6](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6). No duplicate created. |
| **P0** | No hosted app URL. Cannot validate authentication, mobile, keyboard, NVDA/VoiceOver, invalid inputs, cross-session privacy or real crash cases. | Only after approved private hosting and exact SHA CI, execute B01–B20 with genuine dated results/defects and sanitized screenshots. | Created private [#8](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/8) |
| **P0** | Synthetic export data license unspecified in registry though repo source code says Apache-2.0. This is a documentation/permission decision, not proof of illegality. | Record actual data ownership/rights and intended distribution decision; update cards/registry/tests consistently with owner approval, never reinterpret external metadata license as consent. | Created private [#9](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/9) |
| **P0** | Human sources are known only as snapshot metadata without reviewed row schema, rights/secondary-analysis authorization and source file hashes. | Leave human ingestion disabled; permit only after independent ethics/rights, variable, BIDS and provenance audit. | Existing [#5](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/5) |
| **P1** | A checksum in downloadable JSON is not cryptographic host-run identity, and user may mistake seed-based intervals for human CI. | Explicitly distinguish artifact checksum from CI attestation, independent subject count from rows and simulation interval from human inference; verify report/help text and any real browser state. | [PM19 audit](pm19-independent-qa-2026-10-18.md), [#6](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6) |
| **P1** | Existing long-lived PM06–17 branches are not all merged into main, making README/default install inconsistent with advanced source. | Review exact target diff, preserve private history, require current-branch hosted CI before integration; no public PR or main merge in this audit. | [Private review branch](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/review/pm19-pm21-independent-gates-20261018) |

The entries are **source/metadata observations**, not observed interviews, third-party usage failures or actual UI bugs.

## Evidence and dated activity
- **2026-10-16:** Prior hosted PM-02 one-off [run 38863471313](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313) successful (31 pytest, Ruff, mypy). Prior hosted PM-04 final [run 38874446677](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677) successful (80 pytest, Ruff, mypy on 4 files). **Not equivalent to PM17 CI.**
- **2026-10-17:** PM-17 private source/patch branch `ba4bafcdf4ffa3e76b927139ac23e753d0546074` [commit](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/ba4bafcdf4ffa3e76b927139ac23e753d0546074); patch is not upstream accepted or tested.
- **2026-10-18:** Independent PM-19, PM-20, PM-21 evidence reports [private commit](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/595b6372faa9bb5c5234dd3f5368db777d39b59c), Notion pages updated to **Blocked**, release **NO-GO**.
- **2026-10-18:** Two new private issues [#8](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/8), [#9](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/9); deduplicated overlap with [#5](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/5) and [#6](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6).
- **2026-10-18:** [Internal engineering case study](case-study.md), [unsent outreach drafts](pm18-outreach-drafts.md), [consent-aware questionnaire](pm18-feedback-instrument.md) and this traceability ledger committed as source-only results. No host CI/web session.

## Human review decision log
- **Accepted for private drafting:** user authorized continued PM-18–21 implementation and review. This is not verified quality signoff.
- **Current release decision:** **NO-GO** because PM-18/19 gates, exact-candidate CI and private browser validation do not pass.
- **External contacts:** 0 sent, 0 responses, 0 interviews, 0 endorsements, 0 collaborators secured as a result of PM-18.
- **Actual PM18 implementation:** internal drafts, protocol, issues, case study and ledger exist. Real expert feedback or public case-study success is not achieved.
- **Public actions:** 0 tag, 0 release, 0 visibility changes, 0 deployment, 0 personal website/LinkedIn/Hugging Face changes, 0 third-party PRs. No Week-2 task creation.
- **Next permitted independent action:** obtain *actual* exact SHA hosted CI, or continue review-only source edits. Hosted private browser check requires safe, appropriately authorized deployment. A UI screenshot or script alone is not proof.

**Status:** PM-18 needs independent hosted proof and prerequisite PM-17 verification before `Verified Done`. Mark **Blocked** with private source evidence, not `Verified Done`.
