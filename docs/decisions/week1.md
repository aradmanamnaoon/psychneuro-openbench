# PM-03 / P1 engineering evidence ledger

**As of 2026-10-16:** review-only draft on branch `pm03-quality-foundation`. PM-03 files have been authored as an isolated GitHub change; they have NOT been reviewed, merged or run in hosted CI. No public release was made.

## Existing prerequisite evidence
- **Real private project repository:** [psychneuro-openbench](https://github.com/aradmanamnaoon/psychneuro-openbench) (GitHub metadata verified; owner has push access).
- **PM-01 draft science contract:** [docs/spec-v0.md](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/main/docs/spec-v0.md) committed on `main` at [2103ef2](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/2103ef2e638257dd85518e6bceacf53722dd849b); author labels it **proposed, under review**.
- **PM-02 generator:** [Notion pre-repository source artifacts](https://app.notion.com/p/3fb977a963b2812a86dbd97a5012c9f8), NOT committed or tested. No verified `pyproject.toml`, generator module, package installation or v0 synthetic CSV on main as checked.
- **PM-03 mission:** [Notion record](https://app.notion.com/p/3fa977a963b2813583a9e497e2ef0519); existing staged attachments preserved.

## Actual independent GitHub changes in PM-03
- [README.md](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/README.md): clear audience, proposed workflow and nonclinical caveats, no falsely claimed live demo.
- [tests/test_synthetic.py](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/tests/test_synthetic.py): real proposed assertions for seed, schema, identity, types, inputs and RNG isolation, but the adapter is **not yet reconciled with PM-02**. Do not mark tests passing.
- [.github/workflows/cpu-tests.yml](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/.github/workflows/cpu-tests.yml): restricted CPU GitHub Actions workflow. No automatic branch push trigger or authorized PR and no CI run evidenced.
- [docs/decisions/week1.md](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/docs/decisions/week1.md): this ledger.

## Real engineering issue links
1. [#1 Schema and dataset-card validation](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/1)
2. [#2 Generator seeded/edge-case validation](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/2)
3. [#3 Participant leakage defenses](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/3)
4. [#4 Dummy and logistic baselines](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/4)
5. [#5 Provenance and rights gate](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/5)
6. [#6 Replay manifest and CI evidence](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6)

## Verification and blockers
- Commit: actual feature-branch SHA visible in GitHub branch history (this ledger cannot self-embed its own commit SHA; record separately after write).
- Python tests: **NOT RUN**; generator/API dependency missing. Generator function name/arguments in test adapter are provisional, not PM-02's verified interface.
- Hosted CPU CI: **NOT RUN**, no job ID/log/pass conclusion; private repo Actions runner entitlement and integration stage to be verified before triggering.
- Source/data rights: **synthetic-only plan**. No human records, clinical data, external datasets, model scores, downloaded data or license grant created by this mission.
- Original five requirements: P1-009 provisional committed tests; P1-010 workflow authored but hosted verification blocked; P1-011 README staged; P1-012 six real GitHub issues; P1-013 ledger committed, not final verification.

## Release / GO-NO-GO
**GO:** independent issue backlog and private branch preparation.
**NO-GO:** claims of functioning package, deterministic result, passing tests, completed PM-03, clinical/scientific reliability or public release.
**Next:** PM-02 integrates the actual typed generator on main; reconcile test adapter and README, review and merge change only with author approval for PR/merge, then run hosted CI when free usage/permissions confirmed. Record links to real run jobs before marking PM-03 Verified Done.
