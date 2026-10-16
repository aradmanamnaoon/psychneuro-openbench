# PM-09 — Day-3 engineering review, evidence and handoff

**Written:** 2026-10-16 (pulled ahead before scheduled 2026-10-17).  
**Repository:** [private PsychNeuro OpenBench](https://github.com/aradmanamnaoon/psychneuro-openbench).  
**Branch:** [pm09/versioned-config-integration-qa](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm09/versioned-config-integration-qa), based directly on [PM-08 review branch](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm08/baselines-experiment).  
**State:** SOURCE IMPLEMENTED / HOSTED VERIFICATION **BLOCKED** / NO RELEASE / NO SCIENTIFIC RESULTS.

## Review decisions

1. Preserve the rights-restricted **synthetic-only** generator, PM-05 loader and quality checks, PM-06 documentation, PM-07 participant split, and PM-08 model/metric logic. No real dataset use, model training claim, PR, merge or visibility change.
2. Use **JSON instead of YAML**, which satisfies P1-035's validated-equivalent allowance without a YAML parser dependency. [`configs/baseline.json`](../../configs/baseline.json) records version, synthetic source, seeds, split method, target/predictors, model hyperparameters, metrics and selection. [`config.py`](../../src/psychneuro/config.py) enforces exact protocol and rejects changing models/metrics/feature timing without a new version, duplicate keys, wrong types (including bool-as-int), invalid group counts or seed bounds, unexpected fields, symlink config and oversized input. Hash canonical JSON, not local file paths.
3. [`experiments.py`](../../src/psychneuro/experiments.py) now accepts `--config configs/baseline.json`, prohibits mixing a config file with ad hoc CLI seed changes and writes version/hash into the manifest's frozen `configuration`. Legacy explicit numerical arguments are retained when no config file is passed.
4. [`tests/test_experiments.py`](../../tests/test_experiments.py) adds config schema/rights denial tests, missing/invalid/duplicate JSON, simulated cross-fold leakage checks, manifest hash consistency checks, and a monkeypatched *CV-ineligible* test that confirms the runner reports no validation/test scores. **These are unexecuted test sources, not proof of correct behavior.**
5. [`docs/model-card.md`](../model-card.md) states that no model has been trained or scored for this commit, includes intended users, prohibited medical/real-data claims, error policies, leakage/selection hazards and small-group uncertainty limitations. All real/observed scores: **NOT MEASURED**. Six real source candidates remain disabled.
6. The existing [manual-only CI workflow](../../.github/workflows/ci.yml) is updated to pass the frozen configuration to the PM-08 runner. It still includes Python 3.11/3.12, full pytest suite, Ruff, strict mypy, prior synthetic pilot, source/manifest artifact SHA-256 output. Nothing triggered automatically.
7. Source and deployment guard: no background runner, no public release, no external outreach, no real participant/clinical data. The Academy is READ ONLY and was not modified.

## Traceability matrix and verification

| Original task | Artifact / action | Observed status |
| --- | --- | --- |
| [P1-035](https://app.notion.com/p/3fa977a963b281369920d38225dcc152) | [Frozen config](../../configs/baseline.json), [strict parser](../../src/psychneuro/config.py), [runner integration](../../src/psychneuro/experiments.py) | COMMITTED; source read-back pending/follow-up |
| [P1-036](https://app.notion.com/p/3fa977a963b281b4a6e7d21e3923530c) | [Integration tests](../../tests/test_experiments.py) and inherited PM-08 regressions | COMMITTED; **pytest NOT RUN** |
| [P1-037](https://app.notion.com/p/3fa977a963b281efa4e6ce411e092fdd) | [Manual workflow](../../.github/workflows/ci.yml) and GitHub commit-check inspection | **BLOCKED** — no authorized dispatch, no verified logs |
| [P1-038](https://app.notion.com/p/3fa977a963b28122b05fc0f66a234518) | [Honest model card](../model-card.md) | COMMITTED; no invented empirical scores |
| [P1-039](https://app.notion.com/p/3fa977a963b28153b47cf9a5ce45348c) | This dated decision/evidence log and next-stage handoff | COMMITTED source, verification/approval pending |

### Actual GitHub check observations

The connected GitHub API returned a real source commit checkpoint [6614722c834cdfe427bcea228fb190cee39f4714](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/6614722c834cdfe427bcea228fb190cee39f4714). For that SHA, the connector returned **`statuses=[]`** from legacy combined commit checks and **`workflow_runs=[]`** from its **PR-triggered-only** workflow-run listing. **These views do not inspect manually dispatched Actions completely** and are not evidence that CI passed, nor proof no other workflow ran. Full hosted log/artefact proof for this exact commit was **NOT AVAILABLE**.

**Actual executions this mission:** NO pytest; NO Ruff; NO mypy; NO model fitting; NO benchmark manifest or output SHA; NO comparison scores; NO authorized billable GitHub Actions time. Earlier older PM-03/PM-04 passing Actions logs do not cover this source, and PM-06, PM-07, PM-08 retained BLOCKED evidence. None of these gates may be relabeled as successes by source code presence.

GitHub Actions private runners consume the owner's included allowance and may incur charges if exhausted: [GitHub billing policy](https://docs.github.com/en/billing/concepts/product-billing/github-actions). The GitHub app exposes job/run log reads and reruns but not a **new** workflow-dispatch action. No additional MCP is required for ordinary source editing. Without explicit spending/dispatch approval or a pre-existing run ID, hosted tests cannot be certified.

## Current GO / NO-GO decision

**GO —** preserve the review branch, inspect changes, reconcile static code findings and record BLOCKED Notion evidence.

**NO-GO —** mark PM-09 Verified Done, promote to `main`, claim test passes or scientific reproducibility, publish project/results, use a real human dataset, or initiate a runner that may charge the owner's account without approval.

## Next-stage handoff

1. With explicit user permission and verified no-spend or approved budget, run the existing private [Actions workflow](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/workflows/ci.yml) on branch `pm09/versioned-config-integration-qa`; record **run URL, run ID, exact SHA, Python versions, job step logs, test counts, failures and artifact digests**. Fix observed failures via GitHub source commits, repeat verified hosted checks, preserve original failing logs. This step remains **BLOCKED**, not delegated as a coding task.
2. Only after the exact PM-06/07/08/09 dependency and verification evidence is available, evaluate [PM-10](https://app.notion.com/p/cc9f19deffdf4adebb43a831b8e7d7f1) scope in the consolidated project queue; the next mission is not yet treated as dependency-ready.
3. Keep rights and scientific restrictions unchanged. No public release or profile/website changes without separate authorization.

**Conclusion:** Source and reviewer-facing documentation are ready for examination; engineering and research outcomes remain unverified until real hosted logs exist.
