# Reproducibility — private synthetic benchmark (PM-16)

**Evidence cut-off: 2026-10-17. This is a source-audited procedure, NOT a
completed clean-runner experiment.** Source came from the private
`pm15/private-host-preflight` head
`c13bd8b57c1727bfa90663ed9d14c97b38b4017e`. The PM-16 branch inherits
those files. On the parent branch, GitHub Actions reported **zero branch-specific
runs**. No current PM-10–16 scientific score, checksum, dependency-resolution,
CI log, fresh app screenshot or hosted replay is certified here. Old verified
PM-03/PM-04 generator-only runs cannot be reused to certify this pipeline.

## Question and scientific boundary

PsychNeuro OpenBench is a nonclinical software workbench for studying how
originally invented two-choice behavioral trial records can be validated,
split by *fictional participant*, trained on with two fixed ML baselines and
audited. It is for psychology methods students, computational neuroscience
researchers and ML reproducibility reviewers. **No actual participant/patient
data, clinical inference, licensed third-party dataset import or empirical
neuroscience result is authorized.** The dataset registry explicitly denies
external human sources. Post-response `response_time_ms`, `correct` target
and observed response are not pre-response predictors.

## Inputs and frozen protocol, checked against repository source

| Source file | Role / invariant |
| --- | --- |
| [`configs/baseline.json`](../configs/baseline.json) | Versioned frozen generator and model contract: seed, cohort size, trial count, five training CV folds, fixed dummy-prior and logistic regression models, balanced accuracy/macro F1; model selection by training-only CV |
| [`data/registry.json`](../data/registry.json) | `deny_external_sources_by_default`; `psychneuro-synthetic-v0` enabled; external human metadata entries not downloadable/ingestible |
| [`src/psychneuro/pipeline.py`](../src/psychneuro/pipeline.py) | Calls real original-synthetic rights-gated experiment code per seeded cohort, reports eligibility and nominal repeat-level uncertainty; `--repeats 5` |
| [`src/psychneuro/workflow.py`](../src/psychneuro/workflow.py) | PM-13 in-app-equivalent bounded generator/loader/model/report runner, seed 73, 24 fictional participants, 20 trials and 5 repeats by default |
| [`src/psychneuro/reporting.py`](../src/psychneuro/reporting.py) | Validates exact synthetic report version, seed order, rights, metrics, summary, SHA; exports deterministic JSON/Markdown/lineage manifest; source self-hash is **not** a signed provenance claim |
| [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | Configured manual-only Python 3.11/3.12 runner including pytest, Ruff, mypy, PM-06 exploration, PM-08 baseline, PM-10 report, PM-11 exports, PM-12 replay, PM-13 exact file comparison and PM-15 direct-package install checks |
| [`requirements.txt`](../requirements.txt) | Candidate direct runtime pins only; transitive dependency lock/hashes and private-host build **unverified** |

The `cv_selected_policy` reuses the selected baseline's **held-out**
metrics. It is not independently fitted as a third estimator. Synthetic
cohort repeats, not individual trial rows, are the uncertainty unit.
Unscorable repeats stay in the denominator, never imputed as zeros.

## Hosted-only reproduction procedure and provenance requirements

All commands below are **transcribed from committed source and intended for a
future explicitly authorized hosted job**. They are NOT commands run by this
assistant or a list of tasks delegated to the project owner. No local Python,
Node, CLI, Docker, IDE, Work or Codex was used in PM-16.

1. Confirm the exact private GitHub branch/commit to verify. The candidate
   for this mission is `pm16/repro-docs-contributor-onboarding`. Keep the
   repository private. The release owner must separately authorize private
   Actions quota/spending before any new runner job is started. Do not change
   `main`, open a PR, deploy, publish, invite reviewers or grant host OAuth
   permissions without explicit approval.
2. GitHub's browser can dispatch a `workflow_dispatch` workflow **only when
   its workflow file also exists on the default branch**, which is true for
   the existing `.github/workflows/ci.yml`. In the ordinary GitHub website
   open **Actions → Synthetic and loader CPU quality gates (manual only) →
   Run workflow**, select the precise candidate branch (not `main`), leave
   `profile_small_synthetic` **false** unless extra profiling spend was
   separately approved, then review the resulting exact SHA and job logs.
   **No such PM-16 run has been started here.**
3. The existing YAML's hosted steps below are the exact installed-check and
   scientific pipeline commands. Each runs in an isolated GitHub Actions
   Linux checkout; the workflow matrix uses Python **3.11 and 3.12**. Manual
   reproduction in another environment may differ due to unpinned transitive
   dependencies; it is *not* independently verified by this guide.

### Exact hosted quality and installation steps (configured, NOT RUN)

```sh
python -m pip install --disable-pip-version-check -e '.[dev,parquet,benchmark,ui]'
python -m pip install --disable-pip-version-check -r requirements.txt
python -m pip check
python -m pip freeze --disable-pip-version-check
python -m pytest -q
python -m ruff check .
python -m mypy src
```

The installation is **not** a full bitwise lock: `requirements.txt` pins only
the direct app/runtime packages, and `pyproject.toml` permits version ranges
for test, Parquet and library dependencies. `pip freeze` from each successful
hosted run must be archived/linked as environment evidence; it cannot by itself
prove that all artifact bytes replay on later interpreters/platforms.

### Exact experiment/export/checksum commands (configured, NOT RUN)

These are the current YAML commands, in execution order and with the exact
checked-in file paths. Do not interpret their presence as a passing test.

```sh
python -m psychneuro.explore --seed 73 --participants 12 --trials-per-participant 20 --registry data/registry.json --output-dir artifacts/pm06
python -m psychneuro.experiments --config configs/baseline.json --registry data/registry.json --output-dir artifacts/pm08
sha256sum configs/baseline.json artifacts/pm08/manifest.json
python -m psychneuro.pipeline --config configs/baseline.json --registry data/registry.json --repeats 5 --output-dir artifacts/pm10
sha256sum artifacts/pm10/report.json
python -m psychneuro.reporting --input artifacts/pm10/report.json --output-dir artifacts/pm11
python -m compileall -q app.py
sha256sum artifacts/pm11/report.json artifacts/pm11/report.md artifacts/pm11/artifact-manifest.json
python -m psychneuro.reporting --input artifacts/pm10/report.json --output-dir artifacts/pm12/recheck
cmp artifacts/pm11/report.json artifacts/pm12/recheck/report.json
cmp artifacts/pm11/report.md artifacts/pm12/recheck/report.md
cmp artifacts/pm11/artifact-manifest.json artifacts/pm12/recheck/artifact-manifest.json
python -m psychneuro.workflow --generator-seed 73 --participants 24 --trials 20 --repeats 5 --output-dir artifacts/pm13
cmp artifacts/pm10/report.json artifacts/pm13/report.json
cmp artifacts/pm11/report.md artifacts/pm13/report.md
cmp artifacts/pm11/artifact-manifest.json artifacts/pm13/artifact-manifest.json
sha256sum artifacts/pm13/*.json artifacts/pm13/*.md
```

**Eligibility matters:** The PM-10 and PM-13 runners return a nonzero exit code
on an `incomplete` report. Do not silently skip a step, rerun and pick the
best seeds, or replace ineligible outcomes. Log a scientific blocker instead.

### What makes a claim reproducible

Capture *actual* source commit SHA, workflow URL/run ID, date, OS, Python
version, exact resolved packages, stdout/stderr, right-to-use registry
state, fixed config digest, generator/split seed order, held-out group-split
hashes and all `report.json`, `report.md` and `artifact-manifest.json`
checksums. The CI workflow is configured to archive PM-10/11/13 artifacts
for seven days **only on actual success**. Note that present
`artifact-manifest.json` deliberately leaves `source_commit_sha` and
`ci_run_id` null; do not fill those using guesses or equate a report
self-digest with verified Actions provenance. Compare independent run logs
and archival checksums outside the report.

| Gate | Evidence needed to mark PASS | Current status |
| --- | --- | --- |
| Exact branch Python 3.11/3.12 | Both real jobs and successful pytest/Ruff/mypy | **NOT RUN / BLOCKED** |
| Package dependencies | Successful pip install/check and frozen versions, license/security review | **NOT RUN / BLOCKED** |
| Original synthetic inputs | Rights-approved generator/registry and recorded canonical source SHA | SOURCE REVIEW ONLY |
| Group split and leakage | Real unmocked checks, no cross-participant leakage, post-response fields excluded | HOSTED VERIFICATION BLOCKED |
| PM-10/11/12/13 artifact replay | Real `cmp` output and archived JSON/MD/manifest hashes | **NOT RUN / BLOCKED** |
| Browser/app | Private app signed-in and signed-out smoke; actual charts/downloads | **NO LIVE URL / BLOCKED** |
| Repeat-level uncertainty | Actual eligible/ineligible cohort count; CI only when defined | **NO MEASURED VALUES** |
| Permissions | Explicit owner/host/CI/public release approvals | **NOT GRANTED** |

## Interpretation pitfalls and ethical limits

- **No human subjects:** Fictional cohorts are generated by the project; score
  values cannot estimate true cognitive traits, human effect sizes, diagnosis or
  generalization.
- **Leakage:** Evaluating multiple trials from the same fictional participant
  with row-level randomized splits would be invalid. Test/train grouping is
  participant-based. Predictions must not consume reaction time or response.
- **No cherry-picking:** Predeclare seeds and all runs; keep ineligible
  denominators visible; do not filter repeats to recompute intervals.
- **Uncertainty:** Fewer than five eligible independent synthetic cohorts
  means no nominal CI. For sufficient repeats, the approximation describes
  variability over the simulator's seeds only, never an inferential guarantee.
- **Data rights:** Apache-2.0 covers project software, not unapproved
  external datasets or real participant data.
- **Privacy and supply chain:** No raw human upload, API secret, free-tier
  spending, private host linking or public distribution is authorized.
  Direct version pins are not a signed or complete dependency lock.

## Link to existing evidence and next gate

- Previously verified synthetic generator-only work on earlier commits:
  [PM-03/04 Actions #38864568384](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38864568384).
  **Historical only**, not CI evidence for PM-10–16.
- [PM-10 pipeline method](pm10-statistical-pipeline.md),
  [PM-11 reporting](pm11-report-exports.md),
  [PM-12 UI smoke](pm12-explorer-smoke.md),
  [PM-13 bounded workflow](pm13-live-workflow.md),
  [PM-14 accessibility/error/performance](pm14-a11y-errors-performance.md),
  [PM-15 host preflight](pm15-host-runbook.md) and [release gate](release-gates.md).
- [GitHub's official manual workflow documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow),
  [scikit-learn grouped cross-validation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html)
  and [common leakage pitfalls](https://scikit-learn.org/stable/common_pitfalls.html).

**GO:** Private source review of this reproducibility procedure.
**NO-GO:** Claiming a clean hosted replay, actual scores, complete dependency
lock, empirically validated neuroscience result, deployed app or public release.

## PM-01–16 remediation: bounded private CI identity sidecar (SOURCE ONLY)

New private remediation source adds an evidence-producing step to the
**existing manual-only workflow**, not a new or automatic Actions trigger.
The future runner, *after passing* pytest/Ruff/mypy and all PM10/11/13
synthetic artifact comparisons, is configured to execute:

```sh
mkdir -p artifacts/verification
python -m pip freeze --disable-pip-version-check > artifacts/verification/resolved-dependencies.txt
python -m psychneuro.attestation --output artifacts/verification/ci-evidence.json
cat artifacts/verification/ci-evidence.json
```

Only an actual GitHub-hosted run with `GITHUB_ACTIONS=true`, the exact
private repository ID, valid 40-character commit SHA and numeric run ID
will produce the sidecar. It independently checks both reports' eligible
state and compares genuine PM10/11/13 JSON/Markdown/manifest bytes and
records SHA-256 of the exact resolved dependency list. GitHub's workflow
will retain the sidecar and dependency freeze for seven days **only after
the run really succeeds**. A CI environment variable or self-reported
digest is not a cryptographic signature; verify the run's exact commit,
steps, uploaded artifacts and API status separately.

Also, `src/psychneuro/config.py` now independently reconstructs a
report-embedded frozen v1 protocol digest and rejects arbitrary
self-rehashed claims of different config/seed/dimensions. The repeated
pipeline normalizes exported slice/confusion-matrix fields to JSON-native
types for reliable read-back. These changes are version-preserving
research software safeguards; none has yet passed exact-branch pytest,
mypy, Ruff or an executed benchmark.

**Recorded PM-01–16 remediation status: NO CURRENT REMEDIATION CI RUN.**
See the [full gate ledger](pm01-pm16-gap-closure.md), not an
invented Actions URL or a guessed accuracy/CPU value.
