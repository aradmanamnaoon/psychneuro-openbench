# PsychNeuro OpenBench — private development and public-release gates

**Decision recorded 2026-10-16:** Keep this GitHub repository **PRIVATE while the research-software platform is incomplete**. Visibility changes are *never* automatic. Once development and quality gates pass, the owner reviews the evidence and separately authorizes making it public.

## Mandatory release conditions

- [ ] **Functional research product:** the approved v0 user workflow works end-to-end on a lawful/synthetic dataset, not just a generator. Frozen participant-group splits, no post-response predictor leakage, DummyClassifier/logistic baselines, reproducibility manifest, reports and usable reviewer documentation all implemented.
- [ ] **Engineering evidence:** hosted CI jobs succeed on release candidate commit(s), including reproducibility/negative/leakage tests, static analysis, packaging/install checks, and actual log links. CI passing on an older branch is not release-candidate validation.
- [ ] **Scientific integrity:** no empirical claims inferred from toy fixtures; split policy and uncertainty/undefined metrics are scrutinized; source/rights ledger and known limitations are clear.
- [ ] **Data, security, privacy:** only licensed or original synthetic sources; no PHI or secrets; risk audit for ingestion/report rendering, dependency issues and artifact provenance.
- [ ] **Documentation and usability:** comprehensive README, install/reviewer pathways, changelog, architecture, examples, reproducibility instructions and release notes match the ACTUAL implemented state; screenshots/demo only if really captured/hosted.
- [ ] **Legal:** decide, review and add an explicit code license (if intending open source); review dependency and dataset licenses separately.
- [ ] **External review:** owner reviews exact links, tests, sample results and unresolved blockers. If outreach/feedback is desired, it needs specific approval; no invented reviewers or endorsements.
- [ ] **Explicit publication authorization:** owner approves a specific action to switch repository visibility to public and any tag, release, website/profile update, package publication or external announcement separately.

## What is allowed before the gate

Private GitHub commits, branches, issues, Notion evidence, rights research, independent hosted test runs within authorized budget, and internal documentation. No visibility modification is required for any of these.

## Current known limitations

- The validated main-line artifact is a bounded, wholly fictional trial generator/validator—not an end-to-end ML benchmark.
- Hosted verification on 2026-10-16: [31 pytest passes + Ruff + strict mypy](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313) for the specific verified code state; this is not a release validation.
- The former `pm-02/synthetic-foundation` conflicting API is **resolved for engineering**: [ADR-0001](decisions/pm02-reconciliation.md) adopts the CI-verified `main` v0 schema and preserves the alternate branch only as historical experimental code. It was not merged. Any later multi-session or congruency feature requires a versioned migration and hosted test evidence.
- `pm03-quality-foundation` contains independent supplemental tests/documentation whose integration needs real verification.
- No software-source license has been granted. **Apache-2.0 is the documented preference, not a selected or granted license**; the owner still controls that decision. See [rights log](license-policy.md).
- Private-repository GitHub Actions minutes can be limited or billable; never enable expensive recurring tasks or overages without the owner's approval.

**Decision rule:** a schedule, a completed README, or a passing toy test suite cannot by itself flip the repository public. Only a completed quality review **plus explicit owner authorization** may do so.
