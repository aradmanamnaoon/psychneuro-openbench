# PM-07 — Prespecified synthetic correctness evaluation protocol

**Status:** design frozen for private engineering review, **no model training or held-out scoring performed**. This is a prespecified methods contract, not a results report. PM-08 will implement the model/metric runner.

## Research question and estimand

**Question:** Can a transparent model use *pre-response* synthetic task conditions to predict the invented binary trial-correctness outcome for fictional participants not present in its training data, under this generator's distribution?

- One row is one synthetic two-choice trial; target `y = correct ∈ {0, 1}`.
- Training features (`X`): only `difficulty` (bounded synthetic scalar) and `stimulus_condition` (left/right). Enforce the repository's `validate_predictor_columns` allowlist **at feature-construction time**, including against later transformations.
- Prohibit `response`, `response_time_ms`, outcome aggregates, trial order, session/participant/trial IDs, generator seed, inferred labels, diagnosis and any post-outcome value. A response is mathematically tied to correctness in this fixture, so including it would trivialize scoring.
- Independent generalization unit: fictional `participant_id`. Repeated rows per participant **are not independent replicates**.

## Prespecified partitions and use of data

Use only a rights-approved `LoadedDataset` from PM-05 and the deterministic [`participant-shuffle-v1` split](split-design.md), with split seed **42** unless a preregistered configuration explicitly overrides it *before looking at outcomes*. Freeze `source_sha256`, membership SHA-256, sorted group IDs and exact row indices in the run manifest.

| Partition | Intended proportion of distinct subjects | Permitted use |
| --- | --- | --- |
| Training | About 60% | Fit transformers/models; internally compare five grouped CV folds |
| Validation | About 20% | Prespecified selection or stopping/threshold check, **never** test reporting |
| Test | About 20% | Final, one-time score for the frozen method only |

All training-only modeling/cross-validation folds must group by `participant_id`. Five-fold grouped CV is allowed only with **at least five training participants** *and* sufficient class support in each train/evaluation fold for any requested metric. If a fold cannot support a metric, the run is ineligible; do not resplit based on labels or change seed until a desired result emerges.

Preprocessing (e.g. scalar normalization, one-hot vocabulary) is fitted to the **training subfold** during CV and is applied without refitting to that subfold's validation data. After the model/hyperparameters are chosen from training CV and/or the dedicated validation participants, fit the frozen final pipeline on the authorized training pool under an explicitly documented policy. The **test set must never be used** for feature selection, scaling, imputation, class balance adjustments, hyperparameter tuning, decision thresholds or model choice. PM-08 must resolve and record whether the final fit uses train only or train+validation *before* test access; do not choose retrospectively.

## Fixed model comparison and selection

1. **Dummy baseline:** `DummyClassifier(strategy="prior")` (probability prior from **training labels only**); apply one explicit hard-label threshold policy to both models, e.g. `argmax` with documented tie-breaking. Train-only prior must be recomputed per CV fold.
2. **Logistic baseline:** `LogisticRegression(solver="lbfgs", C=1.0, max_iter=1000, random_state=42)`, with a fold-fitted `ColumnTransformer` (`StandardScaler` on `difficulty`, `OneHotEncoder(handle_unknown="ignore")` for condition). Freeze binary threshold **0.5** for probability of label 1, with any threshold change treated as a newly prespecified experiment.
3. Both pipelines use **identical persisted folds** and identical allowable feature/label rows. The dummy must not receive label statistics from validation/test.

**Selection:** primary ranking on *mean valid training-CV balanced accuracy* using the same grouped folds. The separate validation set is an independent prespecified check; if model choice uses it, state that explicitly and do not reuse validation as unbiased test. If ties occur, select dummy (simpler model) deterministically. No post-hoc search over seeds, folds, subject filters or model variants.

The project's current `pyproject.toml` has **no sklearn dependency**; the scikit-learn requirement and actual runner belong to PM-08, not an implicit claim about what PM-07 executes.

## Metrics fixed before observing any held-out outcome

| Role | Metric | Computation / reporting convention |
| --- | --- | --- |
| **Primary** | Balanced accuracy | Average recall across the **two true classes**, using pooled trial predictions; report only when both 0 and 1 occur in evaluated truth |
| Secondary | Macro F1 | Arithmetic mean of class-0 and class-1 F1 with fixed `labels=[0, 1]`; report undefined-class warnings explicitly |
| Audit | Confusion matrix | Raw 2×2 **integer** counts ordered true/predicted `[0, 1]`; no normalization in the canonical output |
| Audit | Class prevalence | Actual count and proportion of each truth class for *each* evaluated partition |
| Audit | Sizes and composition | Participant count, session count, row count, per-subject trial count distribution and label support |
| Optional diagnostic | Per-participant performance | Descriptive only; clearly flag participants with missing classes, never treat trial rows as independent subjects |

Balanced accuracy's pooled-trial point estimate may overweight participants with more rows; report subject counts and per-participant descriptive summaries alongside it. It estimates behavior *in this synthetic task distribution*, not human cognition. **Do not select models using the held-out test metric**.

**Undefined metric policy:** if a partition has no rows, only one truth class, invalid labels/predictions, or insufficient grouping, mark `metric_status="undefined"`, include a machine-readable reason, omit the point estimate (`null`), and fail the relevant acceptance gate. Do not replace undefined with 0, 0.5 or NaN. A missing prediction class with both truth classes present can yield F1=0 for that class, but it must be accompanied by its confusion count and warning. Explicitly report any classifier fitting error, convergence warning or out-of-range score.

## Uncertainty, sample-size and leakage limitations

- Report group count separately from row count. **480 trials from 24 fictional participants are not 480 independent subjects.**
- With the standard 24-subject design, the holdout is only **five participants by construction**. That is too small to present a stable generalization interval or make strong effect claims; a precise-looking confidence interval would be misleading.
- No individual-trial IID bootstrap. A future exploratory interval, **only if predeclared and if enough independent participants exist**, can bootstrap held-out **participants as clusters**, carrying along all their trials, with a fixed documented seed/repetitions and a check that resamples contain both classes. Clearly report number of usable replicates and cluster count. Otherwise `uncertainty_status="unavailable"` and reason (e.g. "only five held-out participants").
- Do not claim statistical significance from one split or use p-values without a justified sampling model, preregistered hypothesis and sufficient group count.
- A one-generator synthetic fixture cannot validate a real neuroscience or psychology effect, domain shift, institutional generalization, calibration, fairness or clinical efficacy.
- Class balance is **not guaranteed** in grouped splits. Assess eligibility for observed partitions without retrying splits to optimize the class mix.
- Multiple code fixes guided by test outcomes consume the holdout's informational budget; do not repeatedly benchmark the test during PM-08/PM-09.

## Future PM-08/09 minimum artifacts and acceptance gates

- Executable **dummy and logistic** pipelines with no prohibited features or leakage of validation/test statistics.
- Same versioned `GroupSplit` for both baselines: source SHA-256, subject lists, index lists, split seed, algorithm version, assignment SHA-256, training-only CV folds and fold digests.
- Per-fold metrics and final trial/participant/group counts; confusion matrices and class coverage; explicit undefined statuses and convergence warnings.
- Full configuration and pinned Python/scikit-learn versions, fit-time transform provenance, dependencies, code commit and host CI run URL.
- At least one **actual GitHub-hosted** Python 3.11/3.12 test + Ruff + strict mypy run on the exact commit after cost and dispatch authorization; do not count older PM-04 jobs as PM-07 proof.
- Tests that try intentionally contaminated subjects, duplicated indices, post-response predictors and single-class evaluations.
- Results report **ONLY if executed**; current code/docs constitute protocol and unexecuted tests, not score results.

**GO:** implement a private baseline runner later using the fixed protocol. **NO-GO:** public benchmark/research-success or performance claims until reproducibility, scientific, rights and hosted-test checks pass.

## Methodological sources

- [scikit-learn: GroupShuffleSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html) — split size is measured in **groups**, not rows.
- [scikit-learn: GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html) — nonoverlapping group folds, enough groups required.
- [scikit-learn: common pitfalls and data leakage](https://scikit-learn.org/stable/common_pitfalls.html) — preprocessing must be learned on training data only.
- [Project scientific contract](spec-v0.md), [dataset card](data-card.md), [split design](split-design.md).
- [Original P1-030 requirement](https://app.notion.com/p/3fa977a963b28170a6b0f716f9f183a0).
