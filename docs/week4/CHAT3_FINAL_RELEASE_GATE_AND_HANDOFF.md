# LATEST VERIFIED DELTA — W04 Chat3 exact-source QA, 2026-10-19

**Release remains NO-GO.** The authoritative latest observed QA note is [CHAT3_EXECUTED_QA_EXACT_SOURCE_20261019.md](./CHAT3_EXECUTED_QA_EXACT_SOURCE_20261019.md); it supersedes stale statements in this original handoff about untested atomic regressions and missing local full-tree quality checks.

- Private DRAFT [PR #22](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/22), **not merged**.
- The reviewed Python/git blob snapshot at `b3c5563f19e988173302f462df2b871fd1d97447` matched **83/83 tracked files** in the independent local source tree; additional commits changed private CI YAML and documentary evidence, not those Python sources.
- **400 pytest PASSED, 247 WARNINGS**; strict mypy **47/47 files PASSED**; Ruff `check .` **0 findings** after committed lint changes. The same 400 tests passed after fixes. This is local Python 3.13.13 evidence, **not** current GitHub Actions 3.11/3.12 certification.
- Actual fictional source: 36 groups ×12 records, group partitions **21 train+7 validation+8 test**, generator seeds 73–75; logistic/dummy/held-out BA all 0.500, chosen C 0.1. Full portable values and hashes in `benchmarks/w04_chat3_3seed_observed.json`.
- Current manual CI TypeScript job updated to lockfile-based `npm ci`, but no hosted dispatch or independently witnessed mobile/browser/axe audit. Rights signatures/worker recovery/CI remain hard blockers.
- W04 Status **In Progress**, Done **unchecked**; exactly one Career Thursday card scheduled **2026-11-05**. Academy not modified.
- GA1–GA8: private research/career artifacts present; **PARTIAL** pending independent validation and/or authorized external work. No paper submitted or contact initiated.

---

# W04 Chat 3 — independent final release gate and handoff

**Prepared:** 2026-10-19. **Scheduled W04:** Thursday 2026-11-05 through 2026-11-11.  
**DECISION: NO-GO** for merge, public/private production deployment, publication, use of human/third-party data or claims of neuroscientific validity.

This is an internal AI-assisted adversarial audit, **not an unaffiliated human scientific, legal, security or accessibility certification**. Existing historical W03 and W04 drafts remain unmerged and private.

## Canonical ancestry and evidence precision

- Private repository: https://github.com/aradmanamnaoon/psychneuro-openbench
- Canonical integrated Chat1+Chat2 parent: private draft PR #18, https://github.com/aradmanamnaoon/psychneuro-openbench/pull/18 ; integration head at initial reconstruction `563f3fe6f15af74c8feb16d493d2c00454cac308`, parent continued to receive concurrent commits; current PR is therefore not merge-certified; see live compare.
- Superseded divergent draft PR #20: https://github.com/aradmanamnaoon/psychneuro-openbench/pull/20 (preserved unmerged).\n- Current independent private draft PR #21: https://github.com/aradmanamnaoon/psychneuro-openbench/pull/21 ; branch `review/w04-chat3-on-latest-chat2-20261019` (use live HEAD SHA; documentation and lockfile commits occurred after tested reconstruction).
- Chat1 and Chat2 handoff files **verified present in integrated PR #18 ancestry**: `docs/week4/CHAT1_BACKEND_HANDOFF.md` and `docs/week4/CHAT2_PRODUCT_VALIDATION_HANDOFF.md`. Historical notes that they did not exist were limited to different earlier branches.
- Earlier W03 PR #13, W04 PR #14, Chat1 PR #16 and integrated product PR #18 remain unmerged; no unsupported composite merge or public deployment.
- Historic W03 Actions run https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934 reports 349 PASS in each of Python 3.11/3.12 for **historical commit 4eeb17845dac7641b75d9a8164f125db6c213659 only**. Do not treat it as current-head W04 evidence.

## Changed source and genuinely executed tests

| Source/claim | New implementation | Observed test scope | Confidence/status |
|---|---|---|---|
| W03 + P13 immutable run/store and W04 owner claim share a transaction | `src/psychneuro/w03/store.py` exposes `put_in_connection`; `src/psychneuro/w04/product.py` adds `TenantRunACL.put_owned` and `OwnerBoundRunStore`; v1/v2 callers in `src/psychneuro/w04/api.py` use owner-bound store | Reconstructed GitHub source at **887481665dba0f65278b4d10f99f1062f537ddde**; selected `pytest` W03+product+interop+atomic cases: **19 passed, 109.34s** | Targeted local PASS, later source HEAD not identical, no hosted CI |
| Failed owner claim cannot strand run or provenance sidecar | `tests/test_w04_atomic_ownership.py` five adversarial cases: SQLite injected trigger rollback, replay, foreign tenant, orphaned historical record, invalid manifest, separate DB refusal | Included in 19 pass; separately rerun atomic+rights subset **15 passed, 23.32s** | Same tests partly repeated; do not add counts as unique |
| Rights, fenced metadata queue and internal API | Chat1 `policy_v2.py`, `queue_v2.py`, `api_hardened.py` carried forward unchanged | Separate selected test run: **40 passed, 59.69s**; reported one warning | Worker actual model-fitting resume/lease/revocation **NOT** validated |
| Signed root/authenticated reimport | V1/v2 artifact-import routes now explicitly return 403 pending independently held root and authentic data grant | Existing v1/v2 API tests revised and included in 19 pass | **Intentional feature disablement**, not signed provenance |
| Static typing | P25 DecisionReason `Literal` fix in `rights.py`; source type check | Python3.13.13: mypy --python-version 3.11 on `w03/store.py`, `w04/{product,api,rights}.py`: **Success, no issues, 4 source files** | **Not** full-tree mypy, not Python3.11 runtime |
| Lint | Framework `Depends` defaults intentionally exempt B008 in two files; source imports remain under review | Whole reconstructed project Ruff still had **24 findings** before latest source edits (7 I001, 5 B008, others); current source full `ruff check .` not passed | **BLOCKED** full-project lint |
| TypeScript browser scientific summary | `apps/web/src/{science,client}.ts`; new `apps/web/package-lock.json` pins TypeScript 5.9.3; private manual CI now uses `npm ci` | Node20.20.2, local `npm test`: **4/4 passed**; `npm run typecheck`: exit 0. Lock SHA256 **c8666d9aa6c49060d9d5bdf82ae78f280d49d6da868093dff38a6ac44fb8e0de** on sandbox bytes | No actual browser axe/keyboard/screen-reader or hosted node validation |
| Current-head CI and release engineering | `.github/workflows/w04-private-manual.yml` is `workflow_dispatch` only | **No current GitHub Actions run dispatched in this audit** | **BLOCKED**; no statement of free-runner eligibility or independent audit |

**Test-count rule:** 19 + 40 = 59 nonoverlapping targeted suites by test-file selection; the subsequent 15 are partly repeats. A successful reconstructed-source run is not proof of successful final HEAD.

### Genuine W03 synthetic multi-seed benchmark reproduction

Executed `psychneuro.w03.service.execute` with actual `data/registry.json`, `RunStore`, grouped CV and four-node P13 sidecar, Python3.13.13. Predeclared generator seeds **73, 74, 75**, split seed **42**, 36 entirely fictitious groups × 12 observations (432 rows per run). All returned logistic outer BA **0.5**, grouped dummy outer BA **0.5**, held-out BA **0.5**, selected C **0.1**. No metric improvement and no human/neuroscience evidence.

| Seed | Source SHA256 | Split SHA256 | Run ID SHA256 | P13 root SHA256 |
|---|---|---|---|---|
| 73 | `bc6f7b672193d4c4b4af13d1df25964454d3216d6e5c4b3c9c9c6099363412b8` | `9d1dce92823468eb1019629b7c9c8f86c391d6f151fb5ed9b418d3b5377ad6c8` | `b4a0f38b4c3302c56a1e75151813dc0bada8c1f95b45269eee9fe0914ba16844` | `2579eb8213827b0fd434f3339f11b7651ca545562852d6a8742bd97fd11b38d2` |
| 74 | `ebb2d8b22cf5d06e500e16f6c329656f707b164a6b66dcffb30a79a2e31f16b3` | `497db65b7592540297a991c2373d981e594b814aeff198a6a0b69914061e7a57` | `b7fcae5c239a25439470c273cb49dd3fd9b232d2bf85ca01d8c47053386564e9` | `0341ebd097fa187b1b93a06bc0edffb29a5f3c2a861c2580a06a4b280f54482d` |
| 75 | `fa223ea141d75b04696d74a8978761833b9439ed27379b48af65e1167d0ff89d` | `3735f0faa1b1d43116417cd141a6ec2e49ca0f5d6b61a95955f9cdcd745b5221` | `0b4c87c60d7acf59c6804037015089f45fd9730d88c8eaf7ecd617f024cdf824` | `b947ca6b43f45cd66b4816aee424b8120c5fb50e93b84872c07c29f4c4d10d78` |

Remote synthetic output JSON byte SHA256: `ec71940095fd4bd87c8708eb1abff2dc011ee5ea2f4a2b9f579c6c809a56ad90`. The seed-73 **source/split/run** hashes agree with archived W03 output. The newly observed P13 root is different from archived `8d7c322a...`; the W03 model node includes `GITHUB_SHA` or `unattested`, hence runs in different environments are **not byte-identical provenance roots**. This mismatch is disclosed, not hidden or described as independently replicated exact historic provenance. No confidence intervals/p-values because 3 chosen seeds and correlated CV folds do not justify them.

### Data registry and trust

Original W03 synthetic generator is internal-only with dataset license metadata `not-separately-specified`: **do not assert a standalone public CSV license**. Six OpenNeuro human/third-party candidate sources remain unapproved and unused; no institutional consent, subject IRB or legal grant claimed. P25 `verified_by` string is not a legally independent grant. SHA hashes detect accidental or naive tampering but not coherent replacement of a receipt and claimed root. The HMAC-protected policy permit is an internal decision token, **not** a P13 report signature; trusted root custody and signer rotation remain missing.

## E1–E14 reviewer disposition

| Engineering epic | Status | Required verification still missing |
|---|---|---|
| E1 P1 multi-dataset API + browser | PARTIAL | Multiple real licensed datasets and live a11y browser |
| E2 P13 explorer + import/export | PARTIAL | Imports intentionally disabled; independently authenticated root |
| E3 cancellation/resume/role audit | PARTIAL | Actual compute worker kill/restart + revocation timing |
| E4 Docker/CI/export | PARTIAL | Reproducible hosted exact commit, private Docker smoke, Python transitive lock |
| E5 P25 rights engine | PARTIAL | Legal rights attestation, owner custody and lifecycle compliance |
| E6 independent scientific baseline | PARTIAL | Three-seed synthetic repeat done; ablation, external generator and held-site falsifications missing |
| E7 schema/persistence/migration | PARTIAL | Atomic ACL repaired locally; schema migrations, backup restore/rollback unverified |
| E8 distributed/restart-safe jobs | PARTIAL | Queue fencing exists; no trained model executor |
| E9 browser/API/typed client | PARTIAL | TypeScript tests pass; no keyboard/axe/screen-reader or API browser E2E |
| E10 performance/scale | BLOCKED | CPU/RSS/p95 and realistic load absent |
| E11 adversarial QA | PARTIAL | New negative owner tests pass; no hostile parallel DoS/fuzz/privilege penetration |
| E12 release/recovery hosted CI | BLOCKED | Full lint/strict type CI, SBOM/security scan, exact-head job log absent |
| E13 P1×P13×P25 interoperability | BLOCKED | Real P25 v2 authorization to fitted worker and trusted root absent |
| E14 reviewer evidence | PARTIAL | This doc/GA set and local output; human independent review absent |

## GA1–GA8 completed **documents**, not completed outcomes

| GA | Review status | File |
|---|---|---|
| GA1 methodological bibliography (13 sources, correct primary/review/standard labels) | PARTIAL | `ga/GA1_LITERATURE_EVIDENCE.md` |
| GA2 falsifiable pre-results research protocol/methods, disclosure and rights | PARTIAL | `ga/GA2_PROTOCOL_METHODS.md` |
| GA3 real skrub upstream issue/policy check, private reproducer, no public PR | PARTIAL | `ga/GA3_UPSTREAM_REVIEW.md` |
| GA4 official international labs, programs, funding/eligibility gaps | PARTIAL | `ga/GA4_ACADEMIC_PATHWAYS.md` |
| GA5 six-to-eight-week proposal and tailored UNSENT messages | PARTIAL | `ga/GA5_COLLABORATION_PROPOSAL_AND_UNSENT_DRAFTS.md` |
| GA6 runbook, case study, CV bullets, prospective feedback, optional original videos | PARTIAL | `ga/GA6_CASE_STUDY_RUNBOOK_AND_PUBLIC_DRAFTS.md` |
| GA7 skeptical referee, replication and 9 falsification objections | PARTIAL | `ga/GA7_INDEPENDENT_SKEPTICAL_REFEREE_REPORT.md` |
| GA8 evidence/claim ledger, 30-day backlog and approval decisions | PARTIAL | `ga/GA8_CLAIM_LEDGER_AND_BACKLOG.md` |

Official references verified: https://imprs-coni.mpg.de/application-dates (IMPRS CoNI **02 Nov 2026 23:59 CET** application deadline, recommendation letters **10 Nov 2026**), https://imprs-coni.mpg.de/application-faqs (MSc completion conditional rule) and https://www.aalto.fi/en/doctoral-education/funding-your-doctoral-studies (not automatic funding). User-specific admissions/salary/visa eligibility unknown. Published methodological anchors are in GA1; example: Cawley & Talbot (2010) https://www.jmlr.org/papers/v11/cawley10a.html; Varoquaux (2018) https://doi.org/10.1016/j.neuroimage.2017.06.061; Kapoor & Narayanan (2023) https://doi.org/10.1016/j.patter.2023.100804; W3C PROV-O https://www.w3.org/TR/prov-o/. No systematic review or peer acceptance claimed.

## Prioritized next 30 days and human decisions

**P0:** reconcile PR #18 base HEAD changes against independent branch, run exact-HEAD Python3.11/3.12 test+Ruff+mypy and npm ci, resolve all lint/type failures; enforce v2 policy at fit/checkpoint/commit; establish real trusted rights and root anchoring. **P1:** add fenced model worker/restart equivalence, multi-process queue stress, schema backup/restore, signed receipt contract and faithful UI browser a11y checks. **P2:** precommit ablation and multi-seed held-site synthetic protocols, proper participant-level uncertainty, p95 CPU/RSS benchmark and unaffiliated scientific/security review.

**Explicit approval-only:** PR merge, public repository, deployment, real human/third-party data, manuscript/preprint submission, public upstream PR, academic outreach, recommendation requests, payment or claims of adoption/recognition. No such action taken. Existing single Career calendar date **2026-11-05** and **Done unchecked**, status In Progress, Academy read-only 40h/week, total learner focused work <=10h/day, R reminder and three optional original videos untouched.

**Final internal rubric:** do **not** score >=90/100 or check Done with hard gates missing. **NO-GO.**
