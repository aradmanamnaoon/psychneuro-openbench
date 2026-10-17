# PM-14 — Accessible, resilient research UI and honest performance review

**Evidence status (2026-10-17): PRIVATE SOURCE COMMITTED, HOSTED AND BROWSER QA NOT RUN.**
No pass/fail test log, rendered screenshot, measured CPU time, measured RSS,
browser contrast ratio, assistive-technology feedback, real benchmark accuracy
or deployed service is presented here. PM-13 remains BLOCKED on hosted source
acceptance. This document records an auditable SOURCE REVIEW and acceptance plan
only, not WCAG 2.2 AA conformance or a release authorization.

## Product boundaries

PsychNeuro OpenBench is nonclinical software for inspecting leakage-safe,
reproducible synthetic behavioral ML exercises. Intended reviewers include
psychology methods students, computational neuroscience analysts and ML
scientific-software maintainers. Only self-generated, entirely fictional trial
cohorts are enabled in the source registry. External or human participant
ingestion is disabled; no patient data, participant contacts or clinical claims.

## P1-057 — Beginner-facing, truthful tutorial

[`docs/tutorial.md`](tutorial.md) includes the motivation, 3 distinct
step-by-step source-mode journeys (preview, explicitly submitted seeded original
synthetic benchmark, independently checked PM-10 report), metric and nominal
uncertainty definitions, nonvisual/keyboard guidance, error recovery, rights
and performance caveats. **No images or screenshots are embedded** because
there is no genuine authorized private browser capture. This is NOT a tested
human-validated user tutorial; reviewer must still test actual wording/live UI.

## P1-058 — Static accessibility issue log (not a browser audit)

The comparison baseline is WCAG 2.2 A/AA as appropriate. W3C source:
https://www.w3.org/WAI/WCAG22/quickref/ . Browser/assistive-tech measurements
are PENDING on the exact committed PM-14 branch.

| ID | Observation/issue from SOURCE | Risk / WCAG | Source action | Real browser result |
| --- | --- | --- | --- | --- |
| A01 | Altair charts may not provide all point-level data to every screen reader; interactive `st.dataframe` can require keyboard navigation | High; 1.1.1/1.3.1/1.4.1 | `app.py` uses explicitly introduced **static `st.table` numeric alternatives** for toy preview, point chart, model summaries and nominal intervals, retains informative plot title/tooltips/captions, preserves score units | **NOT TESTED** with NVDA/VoiceOver |
| A02 | Error output previously included raw exception text (could reveal unsupported paths/data or confuse new users) | High; understandable errors, 3.3.1/3.3.3 | `src/psychneuro/ux.py` maps known errors to actionable, deterministic safe messages without reflecting arbitrary uploaded JSON/exception contents; `app.py` calls mapping | **NOT TESTED** as live announcement |
| A03 | Source navigation/control semantics were labeled, but first-run keyboard sequence undocumented | Medium; 2.1.1/2.4.3/2.4.7 | Added keyboard and source selection copy and first-user keyboard walkthrough. Native Streamlit widgets retained; no JS focus trap/custom keyboard handlers introduced | **NOT TESTED** for focus order/visibility |
| A04 | Charts distinguish models by color; must not depend on color alone | Medium; 1.4.1/1.4.11 | Original PM-13 charts already used shape for score series; numeric tables + model/metric tooltips/captions are retained | **NOT TESTED** for color vision or non-text contrast |
| A05 | Default Streamlit palette, focus outlines and disabled controls cannot be audited from Python alone | Medium; 1.4.3/1.4.11/2.4.7/2.4.11 | No unmeasured custom CSS, contrast claims or unsafe focus override. Full browser check required at 320/768/1024/1440px and 200% zoom | **BLOCKED** on private browser runtime |
| A06 | Live form submission/spinner/state changes need screen-reader status feedback | Medium; 4.1.3 | Native `st.spinner`, `st.info`, `st.error`, `st.success` are present, and all statuses include meaningful text instead of color-only indicators | **NOT TESTED** screen-reader announcement/focus |
| A07 | Static preview still includes fictional participant IDs even though no user data exists | Low; privacy/data minimization | Only invented IDs and pre-response fields are shown; no correctness, response, latency, contact identifiers or raw research upload | Source inspected; runtime still **NOT TESTED** |

**Accessible browser acceptance gate:** With owner-approved private host and
authorized accessibility testing, navigate every widget using only keyboard,
observe visible focus, check expected reading order, test assistive-technology
announcement of errors/spinners, verify labels for download/input/buttons,
compare chart points with tables, measure AA normal text contrast >=4.5:1
(large text >=3:1) and nontext UI contrast where applicable >=3:1, test text
reflow and 200% zoom, both light/dark themes if exposed, and narrow mobile
widths without horizontal clipping of critical operations. Record screenshots
ONLY if genuine, with date, URL, browser/AT versions and exact branch SHA.
**No WCAG compliance certification or browser pass is claimed.**

## P1-059 — Invalid/missing/restricted data QA matrix

| ID | Input or condition | Expected source behavior and human-readable guidance | Test specification | Hosted/browser result |
| --- | --- | --- | --- | --- |
| E01 | Cold start, no report | Fictional preview only, no charts of scores/downloads | Existing `tests/test_app.py` plus `tests/test_pm14.py` cold test | NOT RUN |
| E02 | Report mode, no file selected | Explicit “No report uploaded”; no charts/exports | `test_report_review_mode_without_file_has_friendly_empty_state` | NOT RUN |
| E03 | Empty or >2MB JSON file | Reject, explain size and original synthetic report requirement | `test_malformed_oversize_or_raw_trial_upload_never_yields_report` | NOT RUN |
| E04 | Malformed UTF-8/JSON, duplicate keys, NaN | Reject with safe re-export instructions; no data echo | same parser test and `test_report_errors_recover_without_exposing_input` | NOT RUN |
| E05 | CSV header or raw trial/clinical/person records presented to PM-10 report loader | Refuse (not a PM-10 report); no fallthrough to real participant loader | parser test with fake CSV; original source-rights validator | NOT RUN |
| E06 | Report with rights basis other than original synthetic or unexpected fields | Reject; user told real/private sources unsupported; no export of injected metadata | `test_disabled_external_dataset_cannot_enter_scenario_runner`; inherited PM-13 adversarial export test | NOT RUN |
| E07 | Wrong PM-10 protocol/seed/score hash, unsupported metric | Fail closed, use fresh locked synthetic report, no invented scores | inherited `tests/test_reporting.py`; friendly error mapping tests | NOT RUN |
| E08 | Missing/untrusted rights registry in live in-app mode | Stop before models run; explain checked-in registry recovery | `test_missing_registry_halts_before_any_model_and_is_friendly` | NOT RUN |
| E09 | Disallowed scenario seed, bool/integer spoof or excessive trial volume | Reject without training or retaining a new partial result | inherited `tests/test_workflow.py`; scenario mapping test | NOT RUN |
| E10 | Rehashed uploaded metadata contains patient-like contact or unsafe reason string | Reject despite recomputed self-hash; never echo personal-looking text | `test_report_recovery_never_echoes_attacker_supplied_text` + PM-13 `test_unexpected_export_fields_and_sensitive_text_are_rejected` | NOT RUN |
| E11 | Fewer than 5 eligible fictional cohort repeats | No fabricated 95% interval; N/A text and no interval plot | inherited `tests/test_workflow.py` | NOT RUN |
| E12 | Browser control changes after submitting a prior run, then a failed new submission | Never attribute old score to new control state; failure clears old session result | Inherited PM-13 source guard; separate browser test required | NOT RUN |
| E13 | Random exception string includes filesystem path/username/token | Do not reflect exception input into the UI; general recovery guidance only | `test_report_recovery_never_echoes_attacker_supplied_text` + `test_scenario_error_messages_have_textual_why_and_recovery` | NOT RUN |

**Test facts:** All new and inherited tests above are committed source
specifications. No pytest execution, result screenshot or failing test log is
available in this chat. Test names do NOT prove the features passed.

## P1-060 — Resource measurement / caching decision

**Measured hosted CPU/wall/memory numbers: NONE; UNMEASURED.**
No local Python, Docker, laptop benchmark or free/paid external runner was
used. No speculative results or workload latency were assigned.

New bounded `src/psychneuro/profiling.py` measures ONE actual authorized
small synthetic cohort (seed 73, 24 fictional participants x 20 trials,
one group-separated repeat = 480 artificial rows) via the existing PM-13
rights-checked `run_scenario`. Captures exact-host wall clock seconds
(`time.perf_counter`), process CPU seconds (`time.process_time`), Python
peak tracked allocation bytes (`tracemalloc`), Linux process-wide
`ru_maxrss` before/after in KiB, Python version, report status/sha and
literal caveats, without hostnames, raw participant data or user paths in the
saved JSON. Native NumPy/BLAS memory is not fully measured by tracemalloc;
`ru_maxrss` is a process-wide high-water mark and cannot identify isolated
run memory. One run is insufficient to make statistically reliable performance
claims.

Hosted CI remains manual-only. **Optional input
`profile_small_synthetic` defaults to `false`**; the profiling step runs
only when explicitly enabled on a future authorized dispatch and Python 3.11.
That opt-in may consume additional PRIVATE Actions minutes, so before ANY
manual dispatch verify account permission and billing/quota with the owner.
No external host, additional paid service or app deployment was installed.
The GitHub connector can read existing runs/logs but provides no verified
fresh dispatch action in this conversation. A profiling JSON artifact is
archived for seven days ONLY if that optional hosted step actually executes.

**Caching decision: DEFERRED, NOT IMPLEMENTED** until measured time/CPU/memory
and correctness effects justify it. Incorrect cache reuse across experiment
seed, dataset rights registry or model-selection config would risk scientific
validity and show stale metrics. Future caching requires content-addressed
keys covering canonical config SHA, generator/split seed schedule, repo code
SHA and rights registry revision; independent tests must prove cache
invalidation and no cross-user leakage. Existing per-session report storage
is NOT treated as a benchmark cache.

### Performance evidence ledger (not measured)

| Evidence item | Value | Status |
| --- | --- | --- |
| Trial count to be measured | 480 fictional rows, one repeat | PREDECLARED |
| Hosted `perf_counter` time | — | UNMEASURED |
| Hosted `process_time` CPU | — | UNMEASURED |
| Python traced peak bytes | — | UNMEASURED |
| Linux process-wide max RSS KiB before/after | — | UNMEASURED |
| Exact hosted commit SHA and run URL | — | NO PM-14 RUN |
| Caching comparison or independent repeats | — | NOT RUN; no optimization justified |

## Review gate and provenance

- [x] PM-13 private source preserved on PM-14-only branch.
- [x] Tutorial, source accessibility fixes, safe error classification and test
      matrix committed via authorized GitHub connection.
- [x] Bounded optional resource instrumentation added; opt-in defaults off.
- [ ] pytest + lint + strict type checks passing at exact commit.
- [ ] Actual private browser acceptance across keyboard/contrast/screen-reader.
- [ ] Genuine small hosted CPU/memory log and source/output SHA verification.
- [ ] Owner-approved GitHub Actions usage, accessible deployment, PR, publication
      or release (if eventually needed).

**Source-review GO, scientific/release NO-GO.** Proceed to dependency-ready
missions only after PM-13/PM-14 hosted verification and review gates are met.
The private repo package version remains `0.1.0.dev0`; no release, PR, hosted
app, screenshot, public claim or scientific publication was created.

References:
- [Official W3C WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [Streamlit AppTest docs](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)
- [scikit-learn data leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html)
- [PM-13 private implementation evidence](pm13-live-workflow.md)
