# PM-08 — Synthetic grouped baseline experiment (private engineering review)

**Status: SOURCE COMMITTED; PYTEST / RUFF / MYPY / HOSTED MODEL EXECUTION NOT RUN.** No measured results, clinical claims, human subjects or publication claims are made. PM-06 and PM-07 hosted evidence is still blocked. This protocol should be read alongside [split design](split-design.md) and [evaluation protocol](evaluation-protocol.md).

## Intent and fixed task

Predict **invented binary trial correctness** from only the pre-response `difficulty` and `stimulus_condition` fields. Independent unit is the fictional `participant_id`, not trials or globally repeated `session_id` labels. All source records pass existing synthetic registry, data-rights, SHA-256, schema and quality gates; no external dataset downloads or real-data adapters are included.

The canonical v0 configuration is *proposed*, not an executed observation:

- Generator seed **73**; **24** fictional participants × **20** invented trials.
- Split seed **42**; 14 train / 5 dedicated validation / 5 held-out test *participants* under `participant-shuffle-v1`.
- Exactly five training-only `GroupKFold` folds. Each training fold and its validation fold have disjoint fictional participant IDs and complete nonoverlapping training-row coverage.
- Two candidates fixed in advance: `DummyClassifier(strategy="prior")` and `ColumnTransformer(StandardScaler(difficulty), OneHotEncoder(stimulus_condition)) → LogisticRegression(solver="lbfgs", C=1.0, max_iter=1000, random_state=42)`.
- All fitting, one-hot category discovery, scaling, class-prior estimation and candidate selection use only **training** rows. Fold preprocessors are *freshly refitted* on fold-training rows. Selection is by average valid **training CV balanced accuracy**, with deterministic tie preference for dummy. The independent dedicated validation set is reported as diagnostic only. **Final fit uses train only** (not train+validation). The held-out test is accessed only after selecting the candidate using CV. Both *prespecified* candidates are scored once on the same held-out participants for audit; test metrics cannot choose the model or parameters.
- No threshold search or class stratification. The dummy uses its majority-class hard-label policy; logistic uses sklearn's default decision rule for binary hard prediction, equivalent to threshold 0.5 on the positive-class posterior. Do not compare probability calibration or make biological generalization claims.

**Metrics:** `score_binary` computes a fixed-class 2×2 confusion matrix ([0,1]), class support, prediction prevalence, true positive prevalence, balanced accuracy and macro F1. It refuses missing/noninteger labels (including bool), invalid predictions and shape mismatch; empty or single-class truth returns `status="undefined"` with `None` rather than fabricated 0/NaN. The runner marks an ineligible CV and *never touches held-out test metrics* when any training fold or candidate lacks required support.

**Important limitation:** The default test uses only **five invented participants**, not 100 independent observations. Participant bootstrap uncertainty is explicitly **unavailable**; do not use trial-row bootstrap confidence intervals or p-values.

## Artifacts and exact run interface

- [Binary scoring implementation](../src/psychneuro/metrics.py); negative tests in [`test_pm08_experiments.py`](../tests/test_pm08_experiments.py).
- [Training-only sklearn baselines](../src/psychneuro/baselines.py) with explicit NumPy array adapter for heterogeneous pre-response columns. No third-party imports are required until an estimator is created.
- [Runner](../src/psychneuro/experiments.py) with `ExperimentConfig`, `run_experiment` and a command-line entry point. Input must be `SyntheticConfig`; the external dataset registry entries stay disabled.
- [Manual GitHub Actions workflow](../.github/workflows/ci.yml) builds optional dependency `.[benchmark]`, performs the **full** inherited pytest/Ruff/strict mypy suite, executes one synthetic pilot and one benchmark per Python version, prints and archives the JSON manifest for seven days. This workflow is **not automatically triggered**.
- The resulting `manifest.json`, **if and only if executed**, includes generator parameters, rights/source SHA, participant-held-out assignment and digest, global-row-index grouped CV fold digests, each model's per-fold class/metric diagnostics, training CV means, model-selection decision, validation/test results, status/reasons, library/Python versions, source commit from `GITHUB_SHA` where available, an explicit confidence-interval limitation and canonical SHA-256. It contains invented IDs only, no actual participants.
- `manifest_sha256` hashes deterministic JSON fields (but does not include itself); host paths, wall-clock timestamps and workflow URLs are excluded. A different scikit-learn/Python version or code SHA can legitimately change the checksum. It is not a tamper-proof signature.

When an **authorized hosted runner** is used, its planned entry point is:

`python -m psychneuro.experiments --seed 73 --participants 24 --trials-per-participant 20 --split-seed 42 --registry data/registry.json --output-dir artifacts/pm08`

The runner requires the repository-installed optional `benchmark = ["scikit-learn>=1.5,<2"]`; this is a free, open-source Python dependency, not a paid API. A new installation to the reviewer's device is not required, and neither is an additional ChatGPT MCP. No install or execution has occurred in this chat.

## Verification gates: exact distinction between code and results

| Gate | Source implementation | Verified execution |
| --- | --- | --- |
| Binary metric edge cases and boundedness | Code + tests committed | **NOT RUN** |
| Dummy prior and logistic hyperparameters | Code + tests committed | **NOT RUN** |
| Train-only CV and group-level overlap prevention | Code + tests committed | **NOT RUN** |
| Deterministic manifest round-trip and source identity | Code + tests committed | **NOT RUN** |
| Invalid fold, missing/single label, forbidden feature leakage | Code + tests committed | **NOT RUN** |
| Python 3.11/3.12, Ruff, strict mypy, actual pilot and manifest hashes | Manual-only workflow configured | **BLOCKED pending explicit cost/dispatch approval** |

Successful prior PM-03/PM-04 CI runs cover **older code**, not these files. The repository remains private, no PR/merge, no API spending, no public research results. The held-out test itself should not be evaluated repeatedly while debugging model quality. A preliminary hosted quality run can check source/tests and unit synthetic assertions; any interpretive performance analysis must honor the locked protocol and one-shot evaluation boundary.

## User review gate and next mission

**GO:** review the source and authorize hosted tests only after confirming a zero-spend private Actions quota/budget and the exact requested branch. **NO-GO:** Verified Done, publication, benchmark validity or the next mission's verified dependency until PM-06/PM-07/PM-08 source and current hosted test evidence are reconciled.

Next: [PM-09](https://app.notion.com/p/3fa977a963b281f8b05dccf23de8ecf7) (configuration versioning, integration QA, model card, CI), *after* actual hosted validation. Engineering-only documentation work can be done in advance but not marked independently verified.

**Primary-methodology sources:** [scikit-learn data leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html), [sklearn GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html), [sklearn balanced accuracy](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html), [sklearn pipeline](https://scikit-learn.org/stable/modules/compose.html).
