# PM-20 — Competitive utility review and release GO/NO-GO
**Decision: NO-GO as of 2026-10-18**, applied to PM-17 private development SHA `ba4bafcdf4ffa3e76b927139ac23e753d0546074`. Evidence: [PM-19 audit](pm19-independent-qa-2026-10-18.md). No version tag/release, repository visibility change, hosted deployment or public profile update was authorized **by the release gate**, regardless of broad user instruction to execute the audit.

## P1-083 — Existing real software and honest differentiation
| Established project | What it already does | Implication for PsychNeuro OpenBench |
| --- | --- | --- |
| [MOABB](https://github.com/NeuroTechX/moabb) | EEG dataset pipelines and benchmark evaluation | No blanket novelty claim for neuroscience ML benchmarking, subject-aware evaluation, baseline comparisons |
| [NeuroBench](https://github.com/NeuroBench/neurobench) | Neuroscience-inspired/neuromorphic algorithm and model benchmark frameworks | A benchmark harness alone is not new |
| [MNE-BIDS-Pipeline](https://mne.tools/mne-bids-pipeline/) | Reproducible BIDS-driven EEG/MEG preprocessing and analytics | Do not suggest OpenBench replaces modality-specific processing |
| [Nilearn](https://nilearn.github.io/stable/decoding/decoding_intro.html) | Established neuroimaging ML decoding and cross-validation | No claim to invent cross-validation/decoding in neuroimaging |
| [scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data) | Group-aware CV, splitters, classifiers, metrics and Pipelines | OpenBench reuses standard components; its candidate utility is integrated defaults/documented boundaries, not new algorithms |

**Potential project utility (hypothesis, not measured differentiation):** a simple rights-aware *synthetic-only* behavioral trial workflow joining fail-closed source metadata, locked subject-group split, feature-eligibility guardrails, transparent dummy/logistic baselines, uncertainty caveats and a reproducible export. A genuine comparative benefit requires a specific cross-project use case, benchmark and third-party feedback. No real users, independent comparison measurements or validated feature superiority are established. Avoid “first”, “unique”, clinical benefit, or published research outcome claims.

## P1-084 — Gate rubric (fail closed)
| Gate | Current evidence | Decision |
| --- | --- | --- |
| Real product functional end-to-end | Source files and unit tests on PM17 feature branch; no branch-specific hosted integration or browser observation | **FAIL / UNVERIFIED** |
| Exact-candidate CI, tests, static typing, packaging and artifacts | Only older PM02/PM04 hosted green logs; no PM17 run; no current uploads/artifact digest verification | **FAIL** |
| Rights/privacy and nonclinical scope | Code restricts to original synthetic; external human data disabled; external consent absent; synthetic dataset publication licensing not specified | **PARTIAL / RELEASE BLOCKED** |
| Split, inference, uncertainty and metric review | Static reviewed protections with real risks; no independent hosted regression/negative run at target SHA; t-based intervals only toy seed summaries | **FAIL** |
| Security, dependency and web vulnerability assessment | Source-level threat notes, no current verified supply-chain/license/dependency/security scan or hosted incident checks | **FAIL** |
| Hosted app browser, mobile, accessibility, crash and isolation | No live deployment, B01–B20 all NOT RUN | **FAIL** |
| Correct public README/release manifest/demo/citation | Repo is PRIVATE and default `main` behind PM17; no tag/release/demo | **FAIL** |
| Prerequisite PM-18 completion and user review | PM-18 Notion state remains Planned with no evidence URL | **FAIL** |
| Explicit separate public action authorization | User requested completing missions but quality gate is mandatory; no permission can substitute for failed science/security checks | **NOT APPLICABLE UNTIL GATES PASS** |

**Decision rule:** All mandatory gates must have exact SHA evidence before `GO`. No “release candidate passed” assertion from unrun source tests, early CI or attractive UI descriptions.

## P1-085 — Conditional versioned release
**Not performed**: No Git tag, GitHub release, public package, release-notes claim, visibility change, or website update. Current `pyproject.toml` version `0.1.0.dev0` is development metadata, **not a published version**. Required later: merge/review verified release candidate, record SHA, dependencies, input source manifest, tests and artifacts, freeze changelog/release notes, security/rights signoff, then request explicit approval for each public surface.

## P1-086 — Live links audit
- [Private repository](https://github.com/aradmanamnaoon/psychneuro-openbench): exists to connected authorized account, **not public**.
- [Development branch](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm17/upstream-oss-research-patch): source only, **not release**.
- [Default README](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/main/README.md): no legitimate deployed demo/release link to audit.
- Releases API: empty list; GitHub Pages flag `has_pages=false`; deployment list empty in accessible results. **Live app URL: none established.** No HTML/screenshot/mobile test fabricated. Re-check public URLs only *after* legitimate release/hosting.

**PM-20 status: BLOCKED.** PM-19 evidence documents failure; cannot perform version release. Next permissible activity: private remediation and actual hosted verification (no paid/cloud deployment without consent). Do not create public claims or future Week-2 planning records.

## Dependency update — 2026-10-18
PM-18's internal case study, consent-aware questionnaire, unsent outreach drafts and issue ledger now exist at [PM-18 case study](case-study.md) and [PM-18 evidence](pm18-backlog-evidence-log.md). This resolves **document absence**, but **not** its required upstream PM-17 verification, actual reviewers, final CI or live usability conditions: PM-18 status is **Blocked**. MOABB's [official cross-subject evaluation](https://moabb.neurotechx.com/docs/generated/moabb.evaluations.CrossSubjectEvaluation.html) further confirms that subject-aware benchmarking is pre-existing and must not be claimed as invention. No release gate status changes: **NO-GO**. No GitHub release exists at recheck.


## PM-20 dated release decision after real CI — 2026-10-18
**Change since initial audit:** exact candidate [run #39109383260](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39109383260) at `2479f0d322b3179c30b64673f8beac584a4ba162` verified Python 3.11/3.12 **318 pytest passed per matrix job**, Ruff and mypy passed, synthetic PM06–PM13 executed, within-environment original report/export byte checks passed and **10 real CI archives were uploaded**. This **closes the evidence absence for the source/CI subgate only**. Interpreter-dependent experiment manifest hashes are correct under versioned environment provenance; the scientific metric summaries matched. The [large internal PR #10](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/10) is **DRAFT/UNMERGED**. No release/tag has been published.

**Remaining gate FAIL / NO-GO:** generated-data licensing decision (#9), owner review/sign-off for large integration diff, real private-host/auth/performance/privacy/browser/mobile/screen-reader B01–B20 (#8; **0/20 run**), external/participant-source rights (all six sources remain disabled), independently attested user-uploaded provenance, real reviewer/user feedback. Historical older source-only claims that CI was unrun have been superseded *for this exact code SHA*, not for future code or live hosts. Competitive differentiation remains a narrowly stated **hypothesis**; no comparative effectiveness benchmarking on real data has been established. **NO-GO for integration merge, deployed demonstration, tag/public release or profile announcements.**
