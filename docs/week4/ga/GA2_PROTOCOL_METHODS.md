# GA2 — prospective protocol and methods draft, NO RESULTS
**Working title:** Integrity and Group-Leakage Controls in a Synthetic Repeated-Trial Benchmark: A Reproducibility and Falsification Protocol
**Status:** writing-only research protocol, not preregistered, peer reviewed, IRB-approved, accepted or submitted.

## Question and falsifiable propositions
For fully fictional grouped repeated binary trials, can an independently checkable workflow reliably reject participant leakage and detect modified result artifacts while preserving deterministic, internally consistent benchmark output? H1: subgroup overlap and missing assigned-person rows are rejected before fitting. H2: nested group CV prevents inner-selection access to held-out participants. H3: unauthorized, revoked or malformed P25 grants deny creation; cross-system export rejects corrupted or off-contract artifacts. H4: independently rehashed forgeries remain detectable only when the verifier possesses a genuinely trusted previously pinned digest or signature. Failure of any expected negative control falsifies its implementation claim.

## Study units/data and authorization
No recruitment, patient samples, real neuroimaging, physiological measurements or personal data. Scope is 36 entirely fictional groups × 12 trials (432 observations), generator seed 73 and split seed 42 on the documented W03 registry. The training groups number 21, held-out test groups 8 and reserved validation groups 7 (per W03 hosted record); these numbers are not proof of performance generalization. Generated CSV redistribution remains disallowed until separate explicit license review; `license=not-separately-specified` is *not* a public CC0 grant. W04 rights code accepts supplied `verified=True` and `license_id`, which is not documentary proof of license, source integrity, ethics or consent.

## Design and analysis precommitment (to execute, not asserted here)
- Prediction target: `correct` (0/1); **fixed predictors:** pre-response `difficulty`, `stimulus_condition`. No participant ID, correctness, response time or derived post-target features.
- P1 partitions at **participant** level, row-preserving per selected group; 3 outer GroupKFold, 2 inner GroupKFold; logistic `C∈{0.1,1.0}`, tie → 0.1; StandardScaler and OneHotEncoder trained only inside each fit pipeline.
- Comparator: DummyClassifier(strategy='prior') evaluated on identical outer folds. A final train-only inner selection followed by one use of sealed test yields a **descriptive** holdout score; refrain from reselection after test exposure.
- Main software acceptance: byte-preserved source/split manifest and deterministic run result; exact group disjointness; reference metric tests; adversarial provenance mismatch; negative authorization and revocation tests.
- Propose additional independent seeds 73/74/75 for generator, 42/43/44 for split, **predeclared before analysis**. This is a proposed robustness experiment, NOT RUN; 3 seeds are not independent replicate studies.
- Hold separate ablations: (A) intentional forbidden random row-wise split should be caught, (B) improper prefit scaling should be caught by sentinel, (C) omit condition predictor while retaining same folds, (D) unavailable class support yields undefined rather than imputed balanced accuracy.
- Record per-fold TP,TN,FP,FN, true-class support, selected C, train/test group counts, test scores, timing and platform versions. Do not average undefined folds silently.

## Claim/evidence grid
| Statement | Current basis | Status |
|---|---|---|
| Positive code path for W03 grouped nested CV | `src/psychneuro/w03/nested.py`; W03 earlier hosted run 39228198934 | Reported past CI only; clean current-head replication pending |
| W04 verify valid contract and reject rehashed off-schema payloads | `src/psychneuro/interop_v1.py` and `tests/test_w04_interop.py` on independent private branch | Local targeted prototype run; hosted current-head pending |
| Independent scientific predictive effect | None; fictional data, no human study | NOT CLAIMED |
| Rights/consent/revocation enforcement for humans | Caller-supplied values, no verifiable credential nor revocation subscription | BLOCKED |
| Independent signed provenance | No signing key/attestor or authenticated immutable registry | BLOCKED |

## Statistical caution
Balanced accuracy = [TP/(TP+FN) + TN/(TN+FP)]/2 for two present true classes; undefined if either support is zero. A majority-class dummy has expected illustrative balanced accuracy 0.5 only when both classes occur and it predicts one class. GroupKFold folds are mutually dependent due to overlapping training groups and repeated trials; the independent sampling unit is the person/site, not each row. No p-values, standard errors from fold SD, bootstrapped population intervals, subgroup fairness, calibration or neuroscientific causal inference are justified by present records. Clinical TRIPOD+AI remains a reporting reference only.

## Replication appendix
Review W03 unmerged branch `review/w03-current-head-additive-20261019` and independent W04 review branch. Suggested commands in a locked, fresh environment once authorized: `python -m pip install -e '.[dev,w03]'`; `python -m pytest -q`; `python -m ruff check .`; `python -m mypy --strict src/psychneuro/w03 src/psychneuro/interop_v1.py`. Confirm dependencies from exact solver/lock first; installation, lockfile reproducibility, source and fixture SHA, Windows/macOS and hosted runs need real verification. Run external `pytest` only on synthetic fixtures, and never ingest human data. Store exact branch SHA, seed and environment with logs.

## Ethics, rights and accountability
This is nonclinical synthetic software testing. No IRB approval sought or claimed; any future participant protocol requires its own institutional ethical decision. No public dataset export without separate granted distribution rights. Author responsibility includes manually verifying references, exact tool logs, rights approvals, submitted text and contradictions. **AI-assistance disclosure (draft):** “Generative AI was used to help draft software, tests, and protocol prose; the author is responsible for auditing statements and citations, executing and validating code, and approving any dissemination. No AI-generated results are represented as experimentally observed.” Protocol not intended as human subject results.
