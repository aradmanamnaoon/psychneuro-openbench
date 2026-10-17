# PM-12 — Private browser research explorer: source-only QA evidence

**Status at 2026-10-17: IMPLEMENTED SOURCE, HOSTED VERIFICATION BLOCKED.**
No PM-12 GitHub Actions run, passing pytest, screenshot, actual benchmark score, deployed browser application or real CI-artifact reproduction is claimed. Repo remains private. Package version is **unchanged: `0.1.0.dev0`**; this is a pre-release implementation delta, not a release.

## Product intent and preserved scientific contract

PsychNeuro OpenBench is a nonclinical, reproducibility-first behavioral research software project for methods students, computational neuroscience analysts and ML reviewers. Core safeguards remain: lawful source rights, participant-held-out splits, pre-response predictors only, training-only CV selection, synthetic-cohort repeat uncertainty and small-cell suppression. No patient/human dataset is used or approved. A self-checksum in uploaded JSON is a consistency check, not independent execution provenance or CI proof.

**Dependencies:** PM-10 held-out statistical pipeline + PM-11 validation/exports are present in reviewed private source but BOTH remain BLOCKED on actual hosted execution. PM-12 is intentionally implemented as an independent private source branch, not declared dependency-ready/Verified Done.

## Original task coverage

| Task | Private implementation | Verification status |
| --- | --- | --- |
| P1-048 source selector + demo | [`app.py`](../app.py) sidebar switches between **original-synthetic pre-response preview** and **uploaded PM-10 report**. [`explorer.py`](../src/psychneuro/explorer.py) uses only the existing `generate_trials` + `dataset_card` rights checks with three approved seeds, bounded cohort sizes and <=1000 generated rows. Only preview columns are synthetic participant ID, trial order, artificial difficulty and stimulus condition. No response/latency/correctness/held-out scores. | Source checked; automated/hosted UI NOT RUN |
| P1-049 model comparison | Prespecified `dummy_prior`, `logistic_regression` and CV-selected policy, metric selector (balanced accuracy/macro F1), repeat selector. Source data exclusively come from `parse_report` + `validate_report` via `filter_report_scores`. Empty/ineligible points suppressed, no post-hoc split or fitting. Original report's full-repeat SE/nominal CI always separated from visual filters. | No authentic PM-10 score artifact yet; no measured comparison |
| P1-050 smoke tests | [`tests/test_app.py`](../tests/test_app.py): bounded deterministic toy preview, rights and pre-response-only columns, valid and malformed inputs, duplicate/unknown filters, result subset semantics, repeat-ineligible omission, AppTest navigation, empty mode, upload rejection, synthetic test-fixture accepted path and download controls. | **WRITTEN, NOT RUN**; not browser/screen-reader QA |
| P1-051 hosted reproducibility | [manual-only workflow](../.github/workflows/ci.yml) installs free optional UI group, performs all pytest / mypy / Ruff, generates actual PM-10 and PM-11 reports, reproduces PM-11 exports in `artifacts/pm12/recheck` and byte-compares `report.json`, `report.md`, `artifact-manifest.json`. | Branch-specific Actions run list: **ZERO**, logs/artifact measurements: **NOT AVAILABLE** |
| P1-052 Day-4 delta | This file, [PM-11 spec](pm11-report-exports.md), [PM-10 spec](pm10-statistical-pipeline.md), private README, exact review branch SHA and consolidated Notion PM-12 evidence record. | Version NOT BUMPED; **NO-GO** until verification |

## PM-12 browser/smoke acceptance matrix

| ID | Scenario | Expected behavior | Automated spec | Real browser/host |
| --- | --- | --- | --- | --- |
| S01 | Cold app start / Overview | Original-synthetic default, disclaimers; no model results/download | `test_app_starts_with_original_synthetic_preview_without_heldout_results` | NOT RUN |
| S02 | Switch to synthetic preview + allowed seed/cohort/trial controls | Deterministic rights-cleared invented data and only pre-response fields, max preview size enforced | `test_preview_bounded_deterministic_original_synthetic_only` | NOT RUN |
| S03 | Invalid/bool/excessive preview controls via function | Fail closed | `test_preview_rejects_unapproved_or_unsafe_parameters` | NOT RUN |
| S04 | Results page while in preview mode | Accurate no-report empty state, no score chart | `test_app_navigation_to_results_requires_real_artifact` | NOT RUN |
| S05 | Change to report source, no upload | Clear empty state, no chart/export | `test_app_upload_mode_empty_state_is_explicit` | NOT RUN |
| S06 | Malformed/foreign/oversize input | Refuse without score or downloadable outputs | `test_app_rejects_corrupt_uploaded_report_without_downloads`; inherited `tests/test_reporting.py` | NOT RUN |
| S07 | PM-10 synthetic-only consistent report upload | Displays exact artifact SHA, rights, eligibility; **external CI still unverified** | `test_app_uploaded_fixture_exposes_real_input_only_and_comparison_controls` (fixture only) | NOT RUN on actual report |
| S08 | Filter fixed models and repeats; change metric | Every shown point derives from selected eligible PM-10 test result; no refit or significance | `test_comparison_points_remain_original_noninvented_values` and invalid-choice tests | NOT RUN |
| S09 | Ineligible repeat, empty model list and nil CI | Withheld values, N/A/empty controls, no imputation or invented model performance | `test_artifact_comparison_incomplete_run_withheld` and empty-selector tests | NOT RUN |
| S10 | Full-report uncertainty next to filtered points | Clearly separated all-eligible summary, no recalculated interval from chosen repeats | `test_full_report_uncertainty_not_recomputed_after_selection` | NOT RUN |
| S11 | JSON, Markdown, lineage download | Same entire input (not subset) and reproducible export SHA-256/byte sizes | inherited `tests/test_reporting.py`, AppTest fixture path and CI recheck | NOT RUN |
| S12 | Keyboard, labels, screen readers, touch, viewport scaling | Accessible controls, sequential focus, no color-only encoding, chart data table alternative, no clipping | Source design only; review documented | **NOT RUN**; needs actual private hosted UI and assistive-tech checks |
| S13 | Actual hosted CI against exact commit | pytest, Ruff, strict mypy, all prior CI steps, actual PM-10 JSON, PM-11 exports and byte-match on Python 3.11/3.12 | workflow configured | **NOT RUN** |

### Manual hosted/browser validation plan (not yet executed)

After independent approval of the private runner and no unexpected charges, exercise S01-S13 using a PRIVATE authorized host. Check small and wide viewports, keyboard Tab/Enter, high zoom, screen-reader navigation, chart text alternatives, upload errors, and all three downloaded file hashes. Cross-check commit SHA, actual workflow run URLs, artifact names, full `sha256sum` output, eligibility counts, original synthetic rights and that numeric chart tables match original JSON. Do not pass the gate on fixture-only `AppTest` assertions.

## Deliberate implementation boundaries

1. The synthetic preview **never writes or scores held-out experiment data**. Preview controls are distinct from the frozen PM-10 predeclared seed rule, grouped test split, feature protocol and training-only model selector.
2. All report-source result comparisons are **read-only selections** over exact PM-10 outputs and inherit the fail-closed PM-11 validator. User selection changes only visibility, not reported CI/pipeline results. No winner ranking or significance claims.
3. The summary table refers to all originally eligible simulated cohorts even if the displayed comparison is narrowed to one repeat or one model; its title explicitly explains this.
4. The browser is a **source implementation**, not a deployed hosted app. No real personal/participant data collection, authentication, network push, paid service, public visibility or external URL change was performed.
5. `AppTest` simulates a Streamlit page and widgets; it does not establish browser layout, screen-reader access, color contrast or live-server security. Real browser checks are separate.

## Release-readiness gate: NO-GO

- [x] PM-12 source committed on a private branch descended from PM-11 exact head, with baseline/PM-10/11 files preserved.
- [x] Deterministic preview and strictly source-derived comparison/filter code committed.
- [x] AppTest and isolated test specifications committed; authenticated-format report tests written using **fake constants exclusively in test fixtures**.
- [x] Manual-only CI configured with free open-source UI dependencies and PM-12 repeat export comparison.
- [ ] Official hosted CI test/lint/type/PM-10 results for **exact PM-12 commit** verified with logs — **BLOCKED, NOT RUN**.
- [ ] Genuine archived PM-10/11/12 numerical artifacts and checksums inspected — **BLOCKED, NONE**.
- [ ] Actual web runtime, screen-reader/accessibility and download checks — **BLOCKED, NOT RUN**.
- [ ] Release-review gates and fresh author approval for any public/PR/deployment action — **NO PUBLIC ACTION APPROVED**.

GitHub connector can read archived hosted logs when runs exist, but cannot start a fresh manual workflow via a verified dispatch action in this conversation. Private Actions billing/quota is unverified, so no paid/minutes-consuming dispatch is assumed. Existing older PM-04 runs do not validate PM-12. **Review GO:** inspect source and planned tests. **Completion and public release NO-GO.**

## Version delta and subsequent dependencies

**PM-11 parent:** `c0ab9547afe233fbdb2a63be0c5896b165e839fe`. **PM-12 review branch:** `pm12/explorer-controls-smoke`. Package stays `0.1.0.dev0`; no tag, public release, CI attestation, deployed UI, funding claim, user count or research paper. Added private modules `src/psychneuro/explorer.py` and `tests/test_app.py`; changed `app.py`, manual CI and README. The exact final review head and source verification are separately recorded in the consolidated PM-12 Notion mission.

The next consolidated mission is **PM-13 — Integrated user-facing research workflow & honest results**, but it is **not dependency-ready while PM-10, PM-11 and PM-12 hosted acceptance are blocked**. No change to PM-13's planned status or scheduled date is justified.

## Official references
- [Streamlit AppTest and CI](https://docs.streamlit.io/develop/concepts/app-testing)
- [Streamlit uploader and widget API](https://docs.streamlit.io/develop/api-reference/widgets)
- [scikit-learn GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html)
- [scikit-learn common data leakage pitfalls](https://scikit-learn.org/stable/common_pitfalls.html)
