# Research-software use cases (synthetic-only; PM-16)

**2026-10-17 — SOURCE-BASED EXAMPLES ONLY. No live app, executed current
benchmark, human-participant dataset, paper, external adopter, interview,
performance result or screenshot has been verified.** The examples describe
bounded capabilities committed to the private GitHub branch, not field-tested
usage. Refer to [the first-user walkthrough](tutorial.md) for intended UI
controls and [the reproducibility ledger](reproducibility.md) for exact
hosted commands and acceptance gates.

## 1. Teach why participant-level splitting matters

**Audience:** psychology methods student, statistics educator or reproducible
ML course tutor. **Question:** If each fictional participant makes multiple
responses, how can a model avoid seeing the same person's trials in training
and test partitions?

- **Source workflow:** use original `psychneuro.synthetic` two-choice
  generator with rights-gated loader and the grouped split/experiment path in
  `src/psychneuro/experiments.py`. The PM-08/10 pipeline records split IDs,
  group assignments, training CV model scores and one held-out evaluation.
- **What the student can inspect:** versioned `configs/baseline.json`,
  original-synthetic source manifest, cohort seed, group partition checksum,
  dummy-prior versus logistic-regression baselines, ineligible split reasons.
- **Appropriate conclusion:** “This implementation is designed to keep
  fictional participant groups separate”; **not** “The code has proven
  generalization to real human participants.” Runtime proof remains gated by
  fresh hosted tests and recorded exact-commit outputs.

**Expected output if genuinely executed:** synthetic-only report JSON with
per-repeat split/source digests, completeness status, fixed metrics and any
defined uncertainty. **Current actual output from this PM-16 branch: none.**

## 2. Examine leakage from features measured after the response

**Audience:** computational neuroscience trainee or behavioral-task
software reviewer. **Question:** Can a model be built without unintentionally
using observed response or reaction time to predict correctness?

- **Source workflow:** inspect the frozen `configs/baseline.json` feature
  list: only synthetic stimulus condition and difficulty are permitted
  predictors, with binary correctness as the target. UI synthetic preview
  deliberately omits correctness, response and reaction time columns.
- **What can be checked:** source validator feature timing, mock negative
  tests, and fresh unmocked CI evidence before making verified leakage
  claims. Displayed chart metrics must derive from held-out outcomes after
  training-only model selection.
- **Appropriate conclusion:** The feature set is **intended** to prevent
  post-response leakage; absence of a real current-commit CI run means the
  behavior is not independently verified.

## 3. Compare a naive model and a fixed logistic baseline

**Audience:** ML reproducibility analyst. **Question:** Does a baseline
comparison preserve the distinction between fixed candidate models and a
selection rule picked on training folds?

- **Source workflow:** original-synthetic PM-10 pipeline reports dummy-prior
  and logistic regression, plus a `cv_selected_policy` row that reuses the
  chosen trained baseline's held-out metrics. Metric controls are limited
  to balanced accuracy and macro F1 (unitless 0–1).
- **Uncertainty:** fixed 1/3/5 synthetic-cohort repeats in the UI scenario
  mode. Approximate interval rows are only available when **at least five
  eligible** simulated cohort repeats exist. With fewer, show N/A.
- **Appropriate conclusion:** No best-seed selection, p-value, claim of
  superior real-world prediction, clinical finding or causation is licensed
  by simulator outcomes.

**Live chart and accuracy result:** unavailable; no screenshot included.

## 4. Check source rights and reject an unauthorized data upload

**Audience:** open-science software maintainer or research data steward.
**Question:** Can a tool refuse human datasets and still demonstrate
provenance-aware experimentation?

- **Source workflow:** `data/registry.json` has a deny-external-by-default
  policy. The original fictional trial generator is the only enabled source;
  listed external neuroscience candidates are disabled metadata, never
  download or ingest authorization. The UI accepts only an original-format
  PM-10 report JSON (maximum 2 MB), not arbitrary CSV/Parquet/person records.
- **Expected rejection:** malformed, oversized, wrong-version, duplicate-key,
  unsupported-rights or self-digest-inconsistent reports show human-readable
  rejection guidance and must not create charts or downloads.
- **Privacy caveat:** UI validation occurs **after** a file has been received
  by the host, so no user should upload actual participant data. Host-level
  retention/authentication/privacy still require independent testing.

## 5. Review whether two independently generated reports replay byte-for-byte

**Audience:** computational methods lab, package reviewer or source-code
auditor. **Question:** Do the same locked synthetic inputs produce identical
report JSON, Markdown and provenance manifest under a controlled environment?

- **Source workflow:** [reproducibility guide](reproducibility.md) lists the
  configured exact PM-10 pipeline, PM-11 export, PM-12 re-export, and PM-13
  in-app-equivalent run commands. The manual-only GitHub Actions YAML
  compares JSON/Markdown/manifest bytes with `cmp` and records SHA-256.
- **Reviewer evidence requirement:** the exact SHA of both Python jobs,
  resolved dependency versions, real stdout/stderr and archived artifacts.
  A SHA inside the report cannot independently prove author identity or
  an actual GitHub Actions run.
- **Current outcome:** **BLOCKED** pending hosted approval/CI and artifact
  read-back. No checksum values or performance scores have been invented.

## 6. Accessibility and reproducible error states in a fictional demo

**Audience:** accessibility advocate, methods teacher or research software QA
reviewer. **Question:** Can score charts be understood without color alone or
without an enabled training run?

- **Source workflow:** PM-14 added visible keyboard guidance and static
  tables for fictional previews, scores and interval bounds alongside
  Altair charts, plus generic safe error messages that do not echo uploaded
  file contents. The controlled, synchronous in-app Run form is separate
  from the no-training preview.
- **Expected tests:** tab/focus, screen-reader status/labels, contrast,
  320–1440px and 200% zoom, private auth and cross-session access according
  to the [PM-15 20-case smoke plan](pm15-browser-smoke.md).
- **Current evidence:** static source and test specifications only.
  No WCAG conformance, working mobile UI or actual screen-reader session
  is claimed.

## Who this is not for (yet)

This is NOT a clinical decision tool, individual cognitive trait estimator,
neuroimaging pipeline, real participant-data processing service, randomized
clinical trial, externally validated ML benchmark or publicly accessible
hosted research demo. Do not upload patient/human/third-party datasets or
solicit external users before owner approval and verified privacy/release
gates. Apache-2.0 covers project-authored software; dataset licenses and
consent need separate case-by-case assessment.

**Next proof needed:** Exact-commit private hosted tests, artifact hashes,
a real approved private browser smoke test and scientific/rights review.
