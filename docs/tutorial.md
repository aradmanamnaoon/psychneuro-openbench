# First-user walkthrough — PsychNeuro OpenBench (private pre-release)

**Status: SOURCE WALKTHROUGH, NOT A VERIFIED LIVE DEMO (2026-10-17).**
No screenshot, deployment, completed UI test, measured score or participant
dataset is available or implied. Examples below explain what the existing
source code *intends* to do when the private app is run on an authorized host.
GitHub Actions remains manual-only; check actual run logs before trusting a
result or claiming these controls function in a browser.

## What problem is this solving?

Two machine-learning models can score the same behavioral trials yet be
scientifically incomparable: one might accidentally share participants between
training and testing, include reaction times that occur *after* the response,
or use a dataset without clear reuse rights. PsychNeuro OpenBench is being
built to help psychology methods students, computational neuroscience
researchers and ML reproducibility reviewers inspect those choices instead
of trusting a single attractive accuracy number.

**Only completely invented two-choice trial data are allowed today.** This is
a nonclinical software exercise, not a diagnostic product, evidence about
humans, or an authorized human-participant study.

## Workflow A — Explore original synthetic trials, no model training

1. Open the private Streamlit app only after a trusted host and browser QA
   have been approved. The intended startup shows **PsychNeuro OpenBench**,
   a nonclinical banner, **Navigation** and **Permitted data source**.
2. Keep source **Original synthetic preview (no model scores)** and choose
   **Synthetic preview** in the navigation control.
3. Choose an allowed **Toy generator seed** (73, 74 or 75), **Fictional
   participants** (6, 12 or 24) and **Trials per fictional participant** (8 or 20).
   There is no file upload or Run button in this preview mode.
4. Read the static table of the first 12 fictional rows. It contains only:
   fictional participant ID, trial order, artificial cue (left/right) and
   difficulty (unitless). Response correctness and latency are deliberately
   absent because they are not pre-response predictors.
5. Note the synthetic source SHA-256 and **synthetic-original** rights label.
   These identify generator output, **not** human evidence or hosted test
   authenticity. Opening the Results page in this mode shows no scores.

**What to expect:** no charted performance and no report download. Preview
controls do not modify the frozen model, split or experiment configuration.

## Workflow B — Run an actual synthetic-only grouped benchmark in the app

**Prerequisites:** private approved compute and a valid checked-in synthetic
registry/configuration. No paid hosting, login or launch is approved by this
tutorial; it is a source-level review guide.

1. Select **Run bounded synthetic benchmark (in-app)** in **Permitted data
   source**. A form appears in the sidebar with explicit submit control.
2. Default settings are **first generator seed 73**, **24 fictional participants
   per cohort**, **20 trials per participant**, **5 predetermined cohorts**.
   Choices are deliberately restricted: seed 73/101; participants 24/30;
   20 trials each; 1/3/5 repeats; **maximum 3,000 artificial trial rows per
   submitted operation**. There is no field for patient data or external files.
3. Select **Run synthetic benchmark** *once* to begin the synchronous
   original-synthetic loader -> group-held-out split -> fixed dummy/logistic
   baselines -> held-out metrics -> repeat summary flow. The page must not
   start training on initial render or after unrelated control changes.
4. When execution genuinely completes, the app retains the last **submitted**
   scenario and its validated-format PM-10 report in session state. It must
   not relabel prior scores as belonging to an edited but unsubmitted form.
   Failed runs clear prior results and show a human-actionable error.
5. Select **Results and charts** and choose **Balanced accuracy** or
   **Macro F1** (both unitless between 0 and 1). Select baseline models and
   predeclared repeat points to display; the **CV-selected policy** is the
   training-CV choice, *not* a third fitted estimator.
6. Interpret the static table, *not just colored chart marks*. Every plotted
   score must appear in the table with repeat/model/score. The **full-report**
   summary does not change when filtering visible points.
7. If there are **fewer than five eligible fictional cohort repeats**, the
   nominal 95% interval is **N/A**. With at least five, the view shows actual
   approximate Student-t interval bounds from the original synthetic summary
   beside their exact values in a static table. A line can extend outside
   0..1: it is deliberately not clipped. **No human-population CI, significance,
   causation, medical use or winner claim is justified**.
8. On **Reports and lineage**, inspect original report SHA-256 and source
   provenance; download **PM-10 JSON report**, **PM-11 Markdown report** and
   **PM-11 artifact lineage manifest**. These contain synthetic source/model
   metadata and hashes, not raw trial-level response data. Exported checksums
   are internal consistency checks, not proof of Actions provenance.
9. Select **Discard session benchmark results** to clear retained in-app
   results. No new trial dataset is uploaded or stored by that operation.

**Boundary:** A scenario selected *after* observing results is exploratory;
do not select the best seed or call this a confirmatory comparison.

## Workflow C — Review an already executed PM-10 report

1. Select **Uploaded PM-10 report (results)** under permitted source.
2. Upload **only** an original, unmodified, <=2 MB `report.json` from
   an independently checked private PM-10 synthetic-only run. Do not upload
   CSV, Parquet, participant data, medical records or third-party data.
3. A malformed, empty, rights-uncleared, unsupported, oversized or
   checksum-inconsistent file is refused with a safe recovery message.
   Nothing is plotted or exported on failure. A report with eligibility
   gaps displays the denominator and suppresses unavailable points.
4. For a structurally valid artifact, inspect the metric/interval tables and
   download the full original reproducibility bundle. Filtering plots never
   alters the exported report. Compare source commit, Actions log and artifact
   hashes externally: **a self-consistent JSON is not an authenticated run**.

## Reading the four key terms

| Term | Plain-English meaning and limit |
| --- | --- |
| Participant-held-out | Each invented participant belongs to only one partition within a repeat. This guards against row leakage, but does not demonstrate human generalization. |
| Balanced accuracy | Average recall across the two binary outcome classes, a score from 0 to 1. |
| Macro F1 | Average F1 over the two classes, also from 0 to 1. |
| Nominal 95% interval | Approximate uncertainty across independent *synthetic cohort seeds* under the selected generator; not a statistical guarantee about actual people. |

## Keyboard and nonvisual walkthrough

The navigation radio, data-source selector, permitted seed/count selectors,
Run/discard buttons, model/repeat multiselects, and download buttons have
visible labels in source. Intended keyboard path is **Tab/Shift+Tab** and
**Enter/Space** for native Streamlit controls; do not assume this works until
tested in a real private browser. Chart title/captions explain axes and units,
and static tables show numeric alternatives. The error messages contain
explicit text, not just color. Screen-reader announcements, focus restoration,
contrast, 200% zoom, small screens and downloadable-file controls are
**NOT VERIFIED**. No screenshots have been created or embedded.

## Troubleshooting

| Screen message or symptom | Meaning | Expected next action |
| --- | --- | --- |
| No result artifact / no in-app run yet | No permitted, executed report loaded | Choose the authorized source and submit the synthetic-only form, or upload a genuine PM-10 report |
| Input rejected: malformed or invalid | File is not an unmodified valid PM-10 JSON report | Recover original source export; don't edit scores/renormalize input |
| Unapproved original-synthetic source | The file may contain other data, unsupported rights, or unexpected metadata | Do not upload it; no external or human dataset is approved |
| Integrity check failed | Uploaded payload's canonical SHA differs from its content | Compare the original Actions artifact SHA and provenance |
| Registry unavailable or unsafe | Synthetic-only registry must be present to execute | Host/repo maintainer must restore the checked-in registry; no user dataset workaround |
| Benchmark did not complete | Results and downloads are unavailable for that attempt | Inspect approved private CI/test logs before claiming any scores |
| Ineligible repeat / N/A uncertainty | Required folds/scores or independent seeded cohorts are insufficient | Treat as unavailable, not zero; do not silently replace repeats |
| No results for chosen model/repeat filters | These filters select no eligible recorded points | Select original eligible repeats; never fabricate points |

## Source-only acceptance and continuing work

The private code provides a UI path, frozen schemas and exported evidence.
**No browser screenshots, hosted test logs, memory/CPU measurements, real
benchmark scores, empirical scientific outcomes, external dataset permissions
or public site exist as proof for PM-14.** Refer to
[PM-14 accessibility and resilience log](pm14-a11y-errors-performance.md),
[PM-13 methodology](pm13-live-workflow.md), and
[release gates](release-gates.md) before any wider use. A genuine hosted
run, human assistive-tech test and explicit owner permission are required for
public deployment or public success claims.
