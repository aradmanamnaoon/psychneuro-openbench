# PM-03 evidence and decision ledger — 2026-10-16

**Status: private implementation branch; review required; no hosted execution result.** This is an actual GitHub file, not the historical Notion-only draft. The mission is not yet Verified Done.

## Changes verified in GitHub
- Main repository [psychneuro-openbench](https://github.com/aradmanamnaoon/psychneuro-openbench) exists and is **private**.
- PM-01 [docs/spec-v0.md](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/main/docs/spec-v0.md) was committed in [2103ef2](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/2103ef2e638257dd85518e6bceacf53722dd849b). Spec expressly says proposed and under human review.
- PM-02 actual typed [generator](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/main/src/psychneuro/synthetic.py), [tests](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/main/tests/test_synthetic.py), [pyproject](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/main/pyproject.toml), [schema](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/main/docs/data-schema.md) and manual [CI workflow](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/main/.github/workflows/ci.yml) now exist on main after PM-02 commits.
- PM-03 first private branch commit: [29055e2](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/29055e2aca4224bbeba1a6f41981f50b8a2c53df). It was authored **before** PM-02's generator landed, using provisional interfaces and is preserved only as history.
- PM-03 updated integration branch [pm03-quality-foundation](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm03-quality-foundation) now incorporates PM-02 main without modifying main. It *preserves* PM-02's existing `tests/test_synthetic.py` and replaces the provisional test with `tests/test_synthetic_pm03.py` using the verified `generate_trials(SyntheticConfig(...))` API.
- Updated [README](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/README.md) adds browser-only *review* navigation, real issue links, seed scientific caveats, installation-free demo plan and release boundary.
- Updated [CI workflow](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/.github/workflows/ci.yml) preserves PM-02 manual-only, pytest/Ruff/mypy gates and extends the CPU Python matrix to 3.11/3.12. Previous duplicate `cpu-tests.yml` draft is absent from updated branch tip.
- [PM-03 supplemental tests](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/tests/test_synthetic_pm03.py): field order/CSV, seeds/digests, dataset-card provenance, mutation and validation error paths, generated latency/feature timing, safe identifier constraints.

## Six REAL GitHub issues
1. [#1 Schema and card](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/1)
2. [#2 Seeded generator](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/2)
3. [#3 Leakage](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/3)
4. [#4 Transparent baselines](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/4)
5. [#5 Rights](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/5)
6. [#6 Replay and CI](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6)

## Tests, CI and scientific rights
- **Tests authored, NOT run.** No pytest assertion-count/pass claim and no real GitHub Actions job ID or logs. GitHub combined commit status may be empty even if a workflow is defined; inspect actual run jobs after execution.
- CI remains `workflow_dispatch`-only because private Actions quota and possible billing have not been authorized. The feature-branch changes are **not merged to main**, and a PR has not been opened.
- **Synthetic-only.** No external participants/PHI, dataset download, clinical evaluation, benchmark results, scientific adoption or open-source license claim. Distinguish synthetic data rights from undecided software source-license policy.
- Repo self-commit SHA cannot be placed inside the same commit without changing it; the current exact integrated commit SHA and readback belong in the Notion PM-03 mission evidence field after write.

## Gate and next task
**GO:** review standalone private issue list, code/document QA additions, and PM-02 API compatibility. **NO-GO:** mark PM-03 Verified Done or claim passing tests until a real GitHub Actions CPU job has been authorized, run and audited (commit SHA, run URL, job conclusion, failing assertions included). Subsequent branch integration into main requires human review/approval of PR/merge. After PM-03 evidence, proceed to a dependency-ready later research-software mission.
