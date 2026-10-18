# PM-07 — Participant-held-out split design (synthetic v0)

**Status:** implemented in the private PM-07 review branch; source committed, **tests/hosted CI NOT RUN**. PM-06 integration remains unverified. This is a software-evaluation contract, not evidence of research performance or approval to ingest human data.

## Target and scientific claim

- **Prediction unit:** one fictional two-choice trial. The binary outcome `correct` is the target available only *after* response.
- **Generalization unit:** an **entire previously unseen synthetic participant**, not an individual trial or session. The intended claim is only that a model trained on fictional participants predicts correctness for *different fictional participants generated under the same simulation process*. No human, clinical, cognitive, inter-lab or domain-shift claim is permitted.
- **Permitted predictors:** `stimulus_condition` and `difficulty`, declared pre-response. The existing `validate_predictor_columns` guard is mandatory when features are assembled downstream. Group IDs, session/trial keys, trial order, outcome, `response`, and `response_time_ms` are forbidden predictors.
- **Source rights:** a `LoadedDataset` from the registry-gated, quality-checked PM-05 loader, carrying synthetic-only rights and an exact canonical CSV SHA-256. PM-07 performs a fresh quality, source-card and digest validation before splitting. Six catalogued real-source candidates remain disabled.

## Frozen group assignment: `participant-shuffle-v1`

1. Obtain unique `participant_id` values *within the single validated dataset*, sorting lexicographically for an input-order-independent group list. This is participant identity, **not** a globally unique `session_id`: the generator repeats `session-01` for every participant.
2. Shuffle that sorted list with a **local** `random.Random(split_seed)`, with validated integer seed `0..2**64-1`; do not change the process-wide RNG.
3. Freeze the **outer test set first**: `max(2, ceil(N_subjects/5))` subjects (about 20%).
4. From the remaining subjects freeze validation: `max(2, ceil(N_remaining/4))` subjects (about 20% of the original dataset).
5. Remaining participants are training. **Require at least five training groups**, two validation groups and two test groups. With the default proportions, nine unique participants are the minimum. A smaller source yields an explicit `ValueError` rather than a row-level fallback or fabricated evaluation. There is no outcome-aware or label-stratified allocation.
6. All rows of a participant follow the same assigned partition; row indices refer to the input `LoadedDataset.records` tuple. The returned `GroupSplit` carries distinct sorted group lists, exact row-index tuples and source identity.

For the *defined default generator configuration* of 24 fictional participants × 20 trials each, the **expected group counts** are 14 train / 5 validation / 5 test, approximately 280/100/100 trial rows. These are **contract calculations**, not measured execution results; the actual data may not yet have been generated or tested in hosted CI.

## Reproducibility and tamper checks

`GroupSplit.assignment_sha256` is the SHA-256 of UTF-8 canonical compact JSON containing `algorithm`, `dataset_id`, `source_sha256`, `seed`, and the three sorted participant lists (`sort_keys=True`, ASCII JSON, stable separators). Because indices depend on the canonical dataset row order, indices are also retained and checked against the source checksum. Timestamp, job URL, path and wall-clock time are excluded from the deterministic assignment digest.

`validate_group_split(data, split)` rechecks source identity/rights, verifies disjoint subject sets and a complete subject universe, recomputes the seeded assignment, confirms each row index appears *exactly once* and is mapped to its correct participant, and rejects a changed digest. The validator is **not** a cryptographic signature or protection against malicious source code changes; it detects accidental contamination and manifest inconsistency under a trusted code environment.

The split seed, source SHA, algorithm identifier, group lists and indices must be stored in the future PM-08/09 experiment manifest before fitting any model. Freeze the split *before* exploring labels or metrics. Re-running many split seeds to choose the best held-out accuracy invalidates the held-out test.

## Leakage and contamination risk register

| Risk | Fail-closed rule or mitigation |
| --- | --- |
| Same participant contributes multiple dependent trials | Assign by `participant_id` globally across sessions; never split by row |
| Session label shared between different participants | Never group solely by `session_id`; session is nested within participant |
| Different sessions of the *same* participant go to different partitions | All sessions inherit the participant assignment |
| Duplicate trial ID or repeated trial order within subject/session | PM-05 quality validation rejects before assignment |
| Missing, changed, duplicate or cross-partition subject memberships | Validate exact subject sets and rederive membership deterministically |
| Duplicate, missing or wrongly assigned indices | Validate full row coverage and original participant-to-row mapping |
| Post-response feature (`response`, latency) or outcome-derived mean | Only pre-response allowlisted inputs; prohibit leakage-producing aggregations |
| Feature scaling, encoding, imputation, class weighting fitted to all records | Fit inside **training-only** fold pipelines in PM-08 |
| Selecting seeds, models or thresholds using test metrics | Lock split and modeling choices before outer test, evaluate test once |
| Different synthetic source or reordered/tampered CSV | Revalidate dataset card, canonical SHA-256 and split digest |
| Class imbalance or single-class folds despite valid group splits | Eligibility checks before any metric; no silent stratification claim |
| Related subjects/sites not encoded by `participant_id` | Outside v0; real data needs identity/site/family grouping and privacy review |

## Evaluation handoff and failure behavior

- The training set alone may be used for five-fold `GroupKFold` inner comparisons when the group count and class coverage are valid. Each training fold must have disjoint participants, with preprocessing fitted only to its training side.
- The **separate validation** set may be used for one documented final candidate/threshold decision; it must not train the final model before that decision. The untouched test subjects remain sealed until model selection and configuration are frozen.
- `GroupShuffleSplit`/`GroupKFold` semantics are established in [scikit-learn documentation](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data). The PM-07 implementation uses only Python standard-library assignment primitives; it does not install scikit-learn or claim stratification.
- If validation/test classes are missing or any fold lacks sufficient independent groups, mark scoring **ineligible / undefined** with a reason; never manufacture a finite statistic or silently change seed or split.
- See [evaluation protocol](evaluation-protocol.md) for the fixed task, metrics, dummy baseline, logistic baseline and sampling caveats.

## Verification and release boundary

The [PM-07 regression tests](../tests/test_splits.py) specify deterministic assignment, partition coverage, session nesting, input hash, invalid seeds, insufficient group count and multiple injected contamination cases. **These tests have not been executed on the PM-07 commit**; a file's presence is not a test pass. The inherited [PM-06 review branch](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm06/data-quality-provenance) likewise awaits authorized hosted CI.

**GO:** private implementation and review. **NO-GO:** benchmark accuracy claims, scientific findings, real data, public release or marking PM-07 Verified Done without actual hosted execution and code/CI read-back.

**Original requirements:** [P1-027](https://app.notion.com/p/3fa977a963b281deb919d1244bf6b5a4), [P1-028](https://app.notion.com/p/3fa977a963b281f9a790efff33fd489c), [P1-029](https://app.notion.com/p/3fa977a963b2818c851cda1c77887e0e).
