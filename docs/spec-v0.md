# PsychNeuro OpenBench — v0 vertical-slice and reproducibility contract

**Status:** PM-01 research contract, proposed freeze for implementation; **initial GitHub draft under human review; no release or test claims**. 
**Date:** 2026-10-16. **Traceability:** PM-01 / P1-001..004.
**Canonical repository path:** `docs/spec-v0.md`.
**Product:** nonclinical reproducible ML benchmarking for lawful tabular behavioral-trial datasets, with future optional neuroscience-derived features.
## 1. Purpose, intended readers, success definition
Users: psychology methods students, psychology lab research assistants, computational neuroscience data analysts, and ML reproducibility reviewers. Use case: import a permitted, trial-level task, reject invalid or contaminated evaluation setups, compare transparent statistical/ML baselines under identical subject-held-out folds, export evidence another lab can replay. A success is a verifiable *contract and later working synthetic v0 pipeline*, not high test accuracy or a clinical claim.
## 2. In-scope v0 vertical slice
Exactly one fully synthetic binary outcome classification task, modeling trial correctness from **pre-response task conditions**. Dataset generator creates synthetic subjects, sessions, trials and categorical/continuous task features with fully declared generating parameters and fixed seed. Dataset contents must be labeled synthetic on every generated card and report. No actual participant recruitment or physiological records. No dataset download in v0.
Proposed flow: generate a synthetic, rights-clear task table → validate schema and provenance → create immutable participant-group train/validation/test assignments → fit train-only preprocessing → evaluate constant/prior DummyClassifier and logistic regression with exactly matched folds → report balanced accuracy, macro F1, raw confusion counts, sample/group counts, prevalence and uncertainty status → export a canonical JSON run manifest and a human-readable HTML/Markdown summary.
Not in v0: EEG/MEG/fMRI preprocessing; medical images; neural network/GPU training; personalized or clinical inference; intervention; cognitive diagnosis; live experiment collection; participant uploads; real-world efficacy claims; deployment or public release.
## 3. User stories and acceptance evidence
- **US1 (RA):** When I submit a synthetic CSV, the importer validates required columns, types, unique `(dataset_id, participant_id, session_id, trial_id)` keys, and missing value policy, so corrupted records cannot slip into a benchmark. Test: good fixture accepted; missing/duplicate/invalid fixtures rejected with line/column errors.
- **US2 (reviewer):** I can see distinct held-out participants and split manifest before scores. Test: group intersection between any train/val/test = empty; injected cross-split duplicate participant fails closed.
- **US3 (student):** I can compare DummyClassifier to LogisticRegression evaluated on the same untouched held-out records, metrics and seed. Test: split digests exactly equal; metrics defined and bounded, with no silent undefined values.
- **US4 (methods reviewer):** I can inspect immutable input rights, transformation, versions and scoring settings. Test: missing license/legal basis, SHA-256 or source declaration blocks acceptance.
- **US5 (replicator):** I can reproduce a run or report any mismatch. Test: identical input+config+locked environment and seed give matching fold memberships and canonical outputs under declared numeric tolerance; any changed source checksum is visible and replay fails safe.
## 4. v0 trial schema (normative contract)
CSV UTF-8, exactly one row per trial, with companion dataset card JSON.
Required: `dataset_id` (nonempty string), `participant_id` (opaque synthetic string), `session_id` (opaque synthetic string), `trial_id` (opaque synthetic string), `trial_order` (positive integer unique within subject/session), `stimulus_condition` (known enum declared in card), `difficulty` (finite numeric pretrial feature), `correct` (binary integer 0 or 1). All fields MUST have declared types; reject NaN/Inf, unknown labels, negative/zero order, duplicate keys, missing group identity. All fields used for training must be documented as available *before* the response being predicted.
Excluded from features in v0: `correct` (target), `participant_id`, `session_id`, `trial_id`, raw free text, timestamps, response time measured after the trial, treatment/diagnosis/demographic data, and any post-outcome derived feature. Keep IDs in provenance/splits only. Avoid exporting raw personal identifiers. Schema is NOT declared BIDS-certified.
Companion dataset card fields: `schema_version`, `dataset_id`, `title`, `source_kind=synthetic`, `source_url_or_generator`, `generator_revision`, `source_sha256`, `rights_basis=synthetic-original`, `usage_limitations`, `synthetic=true`, `generator_seed`, `n_participants`, `n_sessions`, `n_trials`, `field_definitions`, `target_definition`, `feature_availability`, `transforms`. Reject incomplete cards. Never label invented participants as clinical research subjects.
## 5. Evaluation design and leakage defenses
Unit of generalization: previously unseen `participant_id` within this *synthetic generator*, not people in the real world. Generate a persisted, deterministic outer held-out test split of participant IDs (target \~20%, exact groups/count recorded). The fixed held-out test is untouched through selection. Remaining groups feed training/validation via group-respecting CV; default 5 folds only when group count supports it, otherwise fail explicitly. Use deterministic, seeded assignment. Do NOT claim perfect stratification while grouping when class balance prevents it. An empty or single-class test fold returns an explicit ineligible/undefined metric status, never a fabricated finite score.
All imputation, scaling, one-hot encoding, feature selection, hyperparameter selection and model fitting occur inside each training fold. The external test is evaluated exactly once per frozen candidate decision. No target/per-subject aggregate or post-response feature in predictors. Verify no `participant_id` overlaps across outer or inner folds; reject if present. Set synthetic-source hashes and known labels before splits. All model comparisons use identical splits.
Baselines: (1) DummyClassifier with prior or most_frequent configured explicitly; (2) LogisticRegression with deterministic solver, fixed max_iter, frozen regularization; no auto tuning on test. Report balanced accuracy, macro F1, confusion matrix, prevalence, sample and group counts; flag undefined cases. Nontrivial uncertainty is group-level: for later implementation, bootstrap held-out participants with declared repetitions and seed, resampling **groups**, never individual trials; if insufficient groups or degenerate class coverage report `uncertainty_unavailable` and why. No p-value or confidence interval claims without measured runs.
## 6. Reproducibility and manifest contract
Each run MUST persist: `run_id`, input dataset card + SHA-256 bytes, generator code revision/seed, schema_version, code commit SHA, environment/dependency lock digest, host OS/Python/library versions, deterministic controls, model hyperparameters, exact sorted participant IDs/fold assignments (synthetic only), fold digests, preprocessing graph config, metric implementation/version, aggregate counts, per-fold results, warnings, failed gates, and time recorded separately from digest. No secrets or network credentials.
Canonical JSON uses stable key order, stable float serialization/version policy, normalized paths, UTF-8 and SHA-256; **timestamps, job URLs, run-specific UUIDs and host paths must not enter the deterministic digest**. Same pinned environment+inputs+seed ⇒ exact split and manifest digest, and numeric metrics within 1e-12 in a fixed runner; across different versions/hardware report tolerances rather than claim bit-for-bit identity. Every run can be traced to original synthetic generator/card; never silently mutate input on load.
## 7. Rights, nonclinical boundary and security
First milestone uses original **synthetic** fixtures only. Real datasets later require per-dataset license or explicit permission, immutable version/DOI where possible, meaningful consent/ethics assessment, privacy audit, and authorization to download/process/share. A software license does not grant data usage rights. Do not copy GPL tool code without an explicit dependency/license review. Refuse identifiable patient data, clinical labels intended for diagnosis or PHI; v0 has no actual participants, diagnosis, prognosis, or treatment guidance. Guard against filename traversal, unbounded uploads, formula injection in exported tabular files, dependency risks and report HTML injection when engineering begins. No medical-device or clinical-use representations.
## 8. Implementation boundary and gates (not evidence of execution)
G0 **Repo**: `psychneuro-openbench` exists with approved visibility and protected main; `docs/spec-v0.md` committed. Present status BLOCKED — authenticated connector lacks repo creation.
G1 **Schema**: valid 24-subject × 20-trial synthetic fixture (\~480 rows) loads with deterministic card, duplicate/missing/invalid fixtures fail closed; subject/session/trial semantics validated. This is a planned fixture size, **not generated measurements**.
G2 **Leakage**: at least 4 intentionally contaminated fixtures rejected; cross-partition subject intersection exactly zero and prefit/post-response feature checks fail.
G3 **Baselines**: both models use identical fold manifest, dummy result present, class counts and metric ranges checked, insufficient-group/single-class fixtures handled.
G4 **Rerun**: two actual hosted runs on a pinned runtime reproduce fold/manifest digests, numeric tolerance documented, changed hash rejected.
G5 **Rights**: synthetic-only dataset card complete and no real data or PII present; future real adapter denied by default.
G6 **Hosted CI**: verified GitHub Actions logs for schema/leakage/metric/reproducibility tests on a repository commit; report run URL, SHA, conclusion and failures; never infer pass from a workflow file alone.
G7 **GO/NO-GO**: GO for code implementation after dedicated repo and v0 rights+schema review. NO-GO for public release, real-data ingestion or scientific performance claims until tested, approved and explicitly authorized.
## 9. Risks and assumptions
- User demand and proposed task success rates are **hypotheses**, not interviews or market validation.
- Synthetic random data demonstrates software mechanics, not cognitive neuroscience predictive usefulness or out-of-distribution performance.
- Repeated trials make row-random splitting misleading; subject-level assignment is mandatory; site/dataset holdout is later scope.
- Confidence intervals from only a few held-out participants may be unstable; report limitations rather than precision.
- Standard GitHub-hosted runners may be free for public repos per GitHub docs, but repository visibility, Actions rights, quota and actual runs must be verified before execution.
- Potential future link to the user’s Holdout-Ledger/CohortSeal by ideas or optional interfaces, **not copy/paste or merging them without review**.
## 10. Sources and decision trail
- Existing software: [PsychoPy](https://github.com/psychopy/psychopy), [jsPsych](https://github.com/jspsych/jsPsych), [OpenSesame](https://github.com/open-cogsci/OpenSesame), [MNE](https://github.com/mne-tools/mne-python), [NeuroKit](https://github.com/neuropsychology/NeuroKit), [Nilearn](https://github.com/nilearn/nilearn).
- [sklearn data leakage](https://scikit-learn.org/stable/common_pitfalls.html) and [grouped CV](https://scikit-learn.org/stable/modules/cross_validation.html).
- [BIDS](https://bids-specification.readthedocs.io/) reference; v0 is not BIDS certified.
- [OpenNeuro data terms](https://docs.openneuro.org/faq), for later separate dataset gate.
- [GitHub Actions runners](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job).
- Original requirement pages: [Original Notion requirement](https://app.notion.com/p/3fa977a963b281b694cbf7abd6c8059b), [Original Notion requirement](https://app.notion.com/p/3fa977a963b28197aec2e18fb6d232a8), [Original Notion requirement](https://app.notion.com/p/3fa977a963b28173ba3acb8c91fa2119), [Original Notion requirement](https://app.notion.com/p/3fa977a963b28149b312cead66f53777).

## 11. 2026-10-17 implementation reconciliation (non-normative addendum)

The *frozen v0 scientific requirements above remain unchanged*. The original
PM-01 text was written before this repository existed. **Its G0 statement
that GitHub repository creation is still blocked is historical, not current.**
The owner subsequently created a private
[PsychNeuro OpenBench repository](https://github.com/aradmanamnaoon/psychneuro-openbench).
PM-02 through PM-04 have real archived historical source/hosted QA evidence,
while PM-05 through PM-16 contain substantial private implementations but
still lack successful current-branch hosted integration, scored reports and
browser/security review. No proof of human, clinical or real cohort validity
has emerged, and PM-01's five user hypotheses remain untested research
hypotheses. The normative v0 requirements for immutable code/environment
provenance, rights and test/validation gates still apply.

A source-only remediation now adds [the PM-01–16 gate ledger](pm01-pm16-gap-closure.md)
and prepares CI-generated identity/dependency/artifact checks. It does not
constitute a successful runner, an approved change of scientific protocol or
a public product release. Preserve the frozen baseline settings unless
a separately reviewed new protocol version is deliberately accepted.
