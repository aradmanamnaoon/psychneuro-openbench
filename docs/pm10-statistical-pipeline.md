# PM-10 — Statistical pipeline, repeated seeds and guarded errors (PRIVATE)

**2026-10-17 status: SOURCE IMPLEMENTED, ALL PM-10 TESTS AND BENCHMARK EXECUTION NOT RUN.** This document is a design/validation checklist, not observed research output. Previous PM-08 and PM-09 verification remains blocked. Repository must remain private until explicit release approval.

## Exact dataset -> scored report flow

1. Validate the fixed `configs/baseline.json` contract via `load_baseline_config`. It permits only the original, invented two-choice behavioral task, its preregistered two pre-response features and two baseline classifiers.
2. In `psychneuro.pipeline`, choose **five** repeats by default with generator seeds 73–77 and split seeds 42–46, fixed **before** looking at any held-out results. Each repeat regenerates a separate synthetic cohort; the same fictional participant IDs across repeats do **not** refer to the same real individuals.
3. Each repeat calls the existing provenance-validated `run_experiment`: fresh training-only folds, participant-disjoint CV, train-only preprocessing and model selection; after selection, the two prespecified models are scored once on that repeat's held-out fictional participants.
4. `run_experiment` reuses the selected candidate's **single existing held-out prediction batch** to compute predeclared `stimulus_condition` slice diagnostics. No tuning uses these slices.
5. `pipeline` collects both fixed-model scores and the **CV-selected policy** score separately. Only `status=ok` repeats contribute; all ineligible repeats are recorded and excluded, never imputed as zero. A report is `incomplete` when any configured repeat is ineligible. Unexpected results/rights violations cause a hard error, not a fabricated report.
6. For each balanced accuracy and macro F1 score, compute mean, sample SD (`ddof=1`) and SD / sqrt(number of **eligible synthetic cohort repeats**). A nominal 95% Student-t interval is emitted **only for >=5 valid repeats** using the documented Cornish-Fisher approximate t quantile. No CI is emitted for 0–4 valid repeats, and SE is null for 0–1. No estimate is imputed for missing samples. Do not construe the interval as uncertainty about human populations, a participant-level CI or a hypothesis test.
7. Fixed subgroup labels are `left` and `right` for pre-response stimulus condition. Each requires >=10 independent fictional participants **and** >=30 trial rows, as well as both outcome classes; otherwise report `status=suppressed`, reason, and `metrics=null`. The default five-person test holdout per repeat is thus suppressed on purpose. No small-cell superiority claims.

## Execution interface (configured but NOT executed)

Install only approved free open-source package dependencies on an authorized hosted runner, never on the reviewer's device. Once free hosted capacity/dispatch is authorized, the manual GitHub Actions workflow is set up to call:

```sh
python -m psychneuro.pipeline --config configs/baseline.json --registry data/registry.json --repeats 5 --output-dir artifacts/pm10
```

On successful complete execution, `artifacts/pm10/report.json` will contain a version, strict input configuration and checksum, source/split/experiment hashes, per-repeat eligibility and selected baseline, guarded slice diagnostics, actual numeric summary only for eligible synthetic repeats, and a canonical `report_sha256`. The report hash is deterministic **for the recorded run inputs/runtime**, not a cryptographic proof of research validity. No such report or benchmark result is currently claimed to exist.

## Statistical and leakage limitations

- Seed-distinct pseudo-random synthetic cohorts are **simulation repeats**, not independent human studies. Pseudo-random seeds alone do not prove statistical independence. Approximate t intervals assume sufficiently independent and roughly well-behaved replicate scores; five repeats is a small sample and the approximation has not been calibrated. There is no p-value or significance declaration.
- Balanced accuracy and macro F1 are constrained to [0,1]. A symmetric t interval can go outside [0,1]; it is left unclipped and labeled *nominal* rather than misrepresenting truncated bounds as a calibrated interval. The t quantile is a numerical approximation, not SciPy's exact inverse CDF.
- CV folds inside a repeat share training participants, so **fold scores are never incorrectly treated as independent repeats**. Trial rows inside participants likewise do not increase inferential sample size. Fixed-model and selected-policy means answer different questions.
- Changing seed count, report settings or interpretation in response to held-out results would bias evaluation. Repeat list and model-selection policy must be frozen before actual execution. This pipeline does not conduct multiplicity-adjusted model comparisons or estimate clinical, biological, causal or external validity.
- Grouped CV and fit-only-on-training policies follow [scikit-learn's data-leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html) and [GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html). Standard error is descriptive across synthetic cohorts; no patient-level resampling is attempted.

## Verification and review gate

| Check | Evidence needed | Current finding |
| --- | --- | --- |
| Files present, branch derived from PM-09 | Read-back GitHub blobs and commits | Source written; reread needed |
| CI pytest and adversarial tests | Logs for **exact PM-10 branch SHA** on Python 3.11/3.12 | **NOT RUN** |
| Strict type/lint QA | Remote mypy/Ruff output | **NOT RUN** |
| Real synthetic repeat results | Archived actual `report.json`, sha256 and true eligibility counts | **NOT RUN** |
| No source/data-rights change | Registry remains synthetic only; no real subject data | Source design checks, runtime NOT RUN |
| Release gate | Formal quality evidence and fresh owner approval | **NO-GO** |

Source files: `src/psychneuro/pipeline.py`, `uncertainty.py`, `slices.py`, integration into `experiments.py`, and `tests/test_uncertainty.py`. The manual-only workflow is at `.github/workflows/ci.yml`. Continue PM-09/PM-08 hosted verification before declaring PM-10 complete. Next dependency-ready mission must be chosen only after these acceptance checks.
