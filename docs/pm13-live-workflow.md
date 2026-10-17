# PM-13 — User-facing real synthetic workflow, bounded scenarios and honest uncertainty

**Recorded 2026-10-17. Status: PRIVATE SOURCE IMPLEMENTED; NO HOSTED EXECUTION OR REAL OUTPUT VERIFIED.** This is NOT a successful benchmark, scientific paper, publicly usable browser application, deployed service, or validated release. PM-10/11/12 remain `Blocked` on remote CI; this mission is independent source-only preparation atop their private latest branch.

## Project purpose and rights

PsychNeuro OpenBench is a nonclinical behavioral ML benchmarking workbench for psychology methods students, computational neuroscience analysts and ML reproducibility reviewers. A useful output must preserve data ownership/right-to-use, no pre-response target leakage, participant-separated training/validation/test, explicit baseline selection, descriptive uncertainty and exact source/experiment/export lineage. All active data remain wholly **original synthetic**. No web fetch, patient data, raw human upload, external participant ingestion, profiles or publication.

## Requirements-to-implementation

| Old requirement | Code delivered | What remains unverified |
| --- | --- | --- |
| **P1-053 actual data loader -> model -> report in UI** | [`src/psychneuro/workflow.py`](../src/psychneuro/workflow.py) calls EXISTING `run_pipeline`, which calls `run_experiment`, `load_dataset` (synthetic only), group-disjoint train/CV/test and fixed dummy/logistic estimators, then `validate_report` and `build_bundle`. [`app.py`](../app.py) runs only on explicit form submission, stores report in session state, clears stale evidence on error, and reuses original chart/table/export sections. No parallel mock inference path. | **NOT RUN in an actual private browser**; source code path exists, behavior unverified |
| **P1-054 permitted scenario settings** | Frozen-only seed 73/101; fictional cohort participants 24/30; 20 trials each; repeats 1/3/5; locked group split seed 42 and 5 training-only CV folds. <=3,000 fictional trials across all repeats per execution; full model/predictor/metric/selection protocol inherited unchanged from `configs/baseline.json`. Scenario-specific SHA-256 is recalculated from the exact source JSON, so no false claim that modified input matches the default config hash. | Actual safe wallclock/memory/accessibility QA **NOT RUN** |
| **P1-055 descriptive uncertainty chart** | [`src/psychneuro/explorer.py`](../src/psychneuro/explorer.py) emits interval rows only when original report has >=5 eligible repeats and non-null interval bounds. UI plots unclipped nominal approximate t intervals and means with textual limitations and exact-point numerical table; for <5 eligible cohorts displays **N/A, not zero-width bars**. Doesn't recompute intervals based on filtered displayed points, declare significance, or treat synthetic seeds as human participants. | Real in-app chart and screen-reader/keyboard/browser checks **NOT RUN** |
| **P1-056 safe reproducibility downloads** | In-app generated report and uploaded PM-10 mode feed the existing strict `build_bundle` to return `report.json`, `report.md`, `artifact-manifest.json`. Source rights, configuration checksum, seed list, held-out score status, experimental manifest and SHA-256 file checks recorded. No participant-level raw trial records, name, contacts, clinical IDs, or timing signals exported from the original synthetic generator. Export self-hash is NOT an independent CI attestation. | No actual PM-13 generated artifact or independent hash verification exists yet. |

## Exact algorithmic and ethical boundary

**Scenario selection is exploratory.** User settings are fixed by explicit form submission *before* running a new synthetic-cohort experiment. Do not reinterpret repeated results or select the best seed as a confirmatory discovery. Models remain exactly `dummy_prior` and `logistic_regression`, target correct, predictors difficulty/stimulus_condition (available before response). Training-only participant-disjoint GroupKFold selects a policy, and held-out test labels are evaluated only after model selection. The selected-policy score is the score of the selected baseline, not a newly independently trained third estimator. Per-repeat trial rows and repeated CV folds do not count as independent human observations.

**Uncertainty:** 1 repeat -> no SE or CI, 3 repeats -> descriptive sample SD/SE only and no 95% CI, 5 eligible repeats -> nominal approximate Student-t CI across *fictional simulation seeds*. Ineligible repeats never imputed. Nominal symmetric intervals may extend beyond 0..1 and are not cropped; no p-values, winner claims, clinical efficacy, human generalization or external validity.

**Privacy/data rights:** User cannot choose external data source or supply raw human records; only a valid original-synthetic report can be uploaded, and the bounded live mode uses the synthetic-only rights-gated `data/registry.json`. Report checksums detect inconsistency, not maliciously fabricated values or author identity. Do not represent an uploaded file as *independently verified CI* without matching run logs and artifacts.

## New source, tests, and CI

- `src/psychneuro/workflow.py`: `Scenario`, `_scenario_baseline` with canonical SHA-256 changed-input accounting, guarded `run_scenario` delegating to existing PM-10 runner, bounded hosted-CI equivalent entrypoint `python -m psychneuro.workflow --output-dir artifacts/pm13`.
- `src/psychneuro/explorer.py`: adds explicit third source mode and `nominal_uncertainty_intervals` function, while retaining PM-12 preview/upload defaults and selectors.
- `app.py`: submit-only sidebar form, session-state cache of last *submitted* scenario, error clears, explicit discard, original PM-12 model/repeat charts and PM-11 downloads reused plus new uncertainty figure. No code runs in background on page load.
- `tests/test_workflow.py`: unit/edge tests for exact default configuration digest, distinct scenario digests, invalid/bool/out-of-budget inputs, missing rights-gated registry, null CIs for 0..4 repeats, selected/missing-repeat chart rows, export no raw sensitive fields, and **one true unmocked integration test** of the original grouped synthetic pipeline. Mock scores in *other tests* are test fixtures, NOT measured results. **All tests NOT RUN.**
- `.github/workflows/ci.yml`: still MANUAL ONLY, per Python 3.11/3.12 runs complete pytest, Ruff, strict mypy, original PM-10 pipeline report, PM-11 export, then the PM-13 real original-synthetic UI-equivalent runner; checks report JSON/Markdown/manifest byte-for-byte with `cmp` and archives results for seven days if successful. **No PM-13 CI run or artifact exists at this time.**

## Extra PM-13 upload/export boundary

The inherited PM-11 uploaded-report pathway now additionally rejects unknown
top-level keys, baseline configuration fields, repeat fields, slice fields and
slice metrics, and refuses injected interpretation strings or malformed/unsafe
repeat reason text before any JSON/Markdown/manifest export. This avoids
preserving arbitrary unexpected metadata such as a `patient_email` field even
when an attacker recomputes a self-checksum. It is an allowlist boundary, **not
proof of input authenticity or a complete PII/content audit**. In-app generation
does not use personal input data, raw participant records or response latencies.

An adversarial regression in `tests/test_workflow.py` rehashes a malicious
uploaded-looking report and expects a hard validation error. This regression
is **written but NOT RUN**, and further actual browser and security checks
remain required before hosting or public release.

## GO / NO-GO QA checklist

- [x] New branch derived directly from exact PM-12 private head and original source intact.
- [x] Source, scenario safety policy, interval view, executable UI path, tests, CLI-equivalent integration and CI instructions committed.
- [ ] Exact PM-13 commit GitHub Actions run logs on Python 3.11 AND 3.12; complete pytest, Ruff, mypy — **NOT RUN**.
- [ ] Real `artifacts/pm13/{report.json,report.md,artifact-manifest.json}` present with true per-repeat scores and source hash; identical `cmp` to PM-10/11 — **NOT RUN**.
- [ ] Actual private Streamlit app launch and test clickable controls, real model run, null intervals and five-repeat intervals, downloads, invalid upload/discard, 200% zoom, keyboard, screen reader, narrow screen — **NOT RUN**.
- [ ] Scientific/statistical/code/data-rights/release gate signed off; permission for any PR/public deployment/release — **NOT AUTHORIZED**.

**Current GO:** Private source review. **Current NO-GO:** Verified Done status, any empirical scientific/performance claim, public release, new collaborations based on claimed results, site/profile changes and dependent mission advancement. Private GitHub Actions may consume paid or limited quota and no verified workflow-dispatch action is exposed through the connected GitHub plugin; no workflow was dispatched, no charges approved or incurred here.

## Provenance / version change log

- Parent: PM-12 private branch [pm12/explorer-controls-smoke](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm12/explorer-controls-smoke), head `b69b41f141f9f54e40866c9eaba2478cb59918c2`.
- Branch: `pm13/live-synthetic-workflow`; latest commit SHA recorded in the [consolidated PM-13 Notion record](https://app.notion.com/p/3fa977a963b28124bfb6d37ec767de07) after GitHub read-back.
- Package stays `0.1.0.dev0`; no release, new public artifact, publication, PR or page changes.
- [PM-10 specification](pm10-statistical-pipeline.md), [PM-11 report provenance](pm11-report-exports.md), [PM-12 browser control matrix](pm12-explorer-smoke.md) remain the parent baselines.

**Next dependent work:** Determine the next consolidated mission *only when* the PM-10 through PM-13 hosted and scientific acceptance gates are resolved. The user is the human reviewer; no coding is handed off.

## Primary guidance

- [scikit-learn data leakage warnings](https://scikit-learn.org/stable/common_pitfalls.html), [GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html).
- [Streamlit form submit semantics](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form_submit_button); [Streamlit testing](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
