# W04 Chat 3 — final reconciled release gate and handoff

**Dated 2026-10-19. W04 scheduled: Thursday 2026-11-05 through Wednesday 2026-11-11.** **RELEASE DECISION: NO-GO** for integration merge, hosted/public release, human data, manuscript/preprint submission, claimed neuroscience findings or institutional rights approval. This is an AI-assisted technical assessment; an independent third-party human review has not taken place.

## Observed work completed in this Chat 3 pass

1. Read private repository and existing Notion W04 page, verified W03 and original W04 PR metadata. [PR13](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/13) head `8e511988e1feecce434eb7a5c109df5ebaf4ef90` and [PR14](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/14) head `a9c84cba4bb0fcec44197ddffe782ab75d9e7ae3` are **unmerged**.
2. Discovered additional private branches [Chat1](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/review/w04-chat1-durable-backend-20261019) head `8fbfb1ed27d4ac22ea46fa859951e0cd4f5b647f` and [Chat2](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/review/w04-chat2-product-20261019) head `2d436aaac460cff5bc7d29fd4f2026b7b56be4a2`. Named `CHAT1_BACKEND_HANDOFF.md` and `CHAT2_PRODUCT_VALIDATION_HANDOFF.md` remain **MISSING**; Chat2's real [CHAT2_ARCHITECTURE_AND_RUNBOOK.md](CHAT2_ARCHITECTURE_AND_RUNBOOK.md) is an **equivalent architecture handoff only**, not evidence of completed validation. No associated PR-triggered hosted runs or commit status entries returned for either head or original Chat3 head.
3. Created a **separate, private, review-only** branch [`review/w04-chat3-reconciled-security-20261019`](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/review/w04-chat3-reconciled-security-20261019) **from the actual Chat2 SHA**. Did not merge/rebase Chat1, W03 PR13, W04 PR14 or touch `main`. This branch contains Chat2's W03-backed P1/P13/P25 product, UI/TS SDK/test source and transferred eight GA documents plus independent audit.
4. **Concrete defensive code change:** disabled Chat2's non-atomic `POST /w04/v2/artifacts/import` with a fail-closed `403 W04_IMPORT_DISABLED` before any mutation in `src/psychneuro/w04/product.py`; updated `tests/test_w04_product_v2.py` to require no ACL record for an otherwise-valid import. Previously `acl.claim` could commit before `runs.put` failed. This is a safety mitigation, **NOT** a fixed/import-capable atomic protocol.
5. Ran standalone independent NumPy/sklearn grouping and BA oracle: Python 3.13.5, NumPy 2.3.5; 16 fictional groups ×6=96 rows; row-wise `KFold(4,shuffle=True,random_state=73)` overlapping training/test groups [13,13,13,12], `GroupKFold(4)` [0,0,0,0]; independent confusion counts TP=3,FN=0,TN=5,FP=2 yielded analytical BA `6/7 = 0.8571428571428572` exactly matching scikit-learn. JSON log SHA-256 `caecf81d8724072439ac07e6735bd5f2fbc228d118189750e4eb7871d23e493b`. Also locally simulated the original non-atomic SQLite ordering and observed one orphaned ownership claim after storage failure. **Neither check runs the exact checked-out GitHub project.**
6. Reconciled and rewrote [independent audit](INDEPENDENT_SCIENCE_SECURITY_AUDIT.md) to distinguish Chat1/Chat2 genuine source from current unverified evidence. Reviewed exact [skrub #2340](https://github.com/skrub-data/skrub/issues/2340): open issue authored by `aradmanamnaoon`, 0 maintainer comments; the official `CONTRIBUTING.rst` requests maintainer approval before an upstream enhancement PR.

## Tests, artifacts, hashes and material omissions

| Evidence | Observed numeric result | Limitation |
|---|---|---|
| Prior W03 manual Actions [run 39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934) | **Historical** 349 pytest PASS on each Python 3.11 and 3.12, reported on source SHA `4eeb17845dac7641b75d9a8164f125db6c213659` | Not current W03 PR head or any W04 head. Earlier report, not a new test run |
| W03 fictional registry | Seed 73, split 42, 36×12 =432 synthetic rows; 21 train/8 test/7 reserved; outer logistic=0.5, dummy=0.5, heldout=0.5 | **Historical reported** scores; NO independent regenerated W03 source hash here |
| Historical fixture hashes | source `bc6f7b672193d4c4b4af13d1df25964454d3216d6e5c4b3c9c9c6099363412b8`, split `9d1dce92823468eb1019629b7c9c8f86c391d6f151fb5ed9b418d3b5377ad6c8`, run `b4a0f38b4c3302c56a1e75151813dc0bada8c1f95b45269eee9fe0914ba16844`, root `8d7c322a7d1d17f0fb41f87c9e6f78b4d409ed1650f604e3bf70821b157981ed` | Copied from historic report; do not assert rehashed or legally licensed export |
| Original Chat3 PR14-oriented local prototype | **17 pytest PASS** reported by earlier internal reviewer on recreated files, Python3.13.5 | NOT byte-identical to any current merged/Chat2 head. Do not combine with new patch test counts |
| New Chat3 standalone oracle | analytic BA 0.857142857, KFold group contamination 4/4 vs GroupKFold 0/4 | verified locally here, independent demonstration **only**, not actual W03 model |
| New Chat3 import regression | source patched + regression test written; **0 exact-head test executions** | expected 403 cannot be labeled pass without real pytest/CI |
| Current-head GitHub Actions | **0 PR-triggered runs returned** for Chat1, Chat2, original Chat3 | does not prove no manual workflows exist; no exact-head hosted PASS |
| Source/fixture rights | synthetic only; W03 standalone CSV license separately `not-separately-specified` | No authenticated rights grant, no human data, no public dataset distribution approval |

**NOT RUN:** complete repository pytest on reconciled head, Ruff/mypy, Hypothesis, actual W03 seed/hash rebuild, Python 3.11/3.12 matrix, Chat1+Chat2 merged contract, worker retry/cancel/resume equivalence, externally pinned/signed provenance, data steward attestation, revocation worker race, load/RSS/latency, Docker/private-host smoke, migration rollback, real browser keyboard/axe/screen-reader checks, source policy legal review, real upstream skrub integration/docs build. No performance, inferential p value, confidence interval, brain decoding result or external user feedback claimed.

## Status: E1–E14 (zero DONE)

| Epic | State | Key evidence / unmet gate |
|---|---|---|
| E1 multi-dataset benchmark and browser | PARTIAL | Chat2 v2 W03-backed UI source; no second lawful dataset or live browser |
| E2 provenance explorer/import/export | PARTIAL | unsigned 4-node DAG, JSON verification, **unsafe import disabled** |
| E3 async jobs/permissions | PARTIAL | Chat1 SQLite lease/fencing and Chat2 metadata API divergent; no worker |
| E4 Docker/hosted product CI | PARTIAL | Docker/manual workflow source, no actual run/lock/audit |
| E5 independently useful P25 | PARTIAL | typed policy store/HMAC in Chat1; attestor and client integration unverified |
| E6 statistical baseline/falsification | PARTIAL | local 96-row group oracle; old W03 results not re-run |
| E7 durable schema/rights lifecycle | PARTIAL | P25 SQLite and W03 store; rollback/retention unauthorized |
| E8 restart-safe distributed execution | PARTIAL | Chat1 fenced queue code; no resumed computation proof |
| E9 browser/API/typed client | PARTIAL | Chat2 TS+HTML+REST source; a11y and E2E untested |
| E10 genuine scale/performance | BLOCKED | no representative CPU/RSS/p95/load measurements |
| E11 threats/adversarial QA | PARTIAL | source/test negative controls; current-head security and auth gates open |
| E12 exact hosted QA/recovery | BLOCKED | no tested current SHA or DB rollback |
| E13 P1×P13×P25 E2E | PARTIAL | Chat2 registry-backed test written, NOT independently executed; Chat1 not integrated |
| E14 reproducibility/reviewer bundle | PARTIAL | GA1–GA8 and audit; no independent external sign-off |

## GA1–GA8 deliverables

| GA | State | Private file; limitations |
|---|---|---|
| GA1 8–15 sources | PARTIAL | [GA1_LITERATURE_EVIDENCE.md](ga/GA1_LITERATURE_EVIDENCE.md) — 13 source-typed records, targeted not systematic |
| GA2 publication methods | PARTIAL | [GA2_PROTOCOL_METHODS.md](ga/GA2_PROTOCOL_METHODS.md) — protocol, hypotheses, rights/ethics and AI disclosure; NO findings |
| GA3 upstream contribution | PARTIAL | [GA3_UPSTREAM_REVIEW.md](ga/GA3_UPSTREAM_REVIEW.md) — real issue #2340 and private reproducer; **not maintainer-endorsed**, no PR |
| GA4 official pathways | PARTIAL | [GA4_ACADEMIC_PATHWAYS.md](ga/GA4_ACADEMIC_PATHWAYS.md) — five degrees/pathways + official research-lab and funding addendum; credential and eligibility unknown |
| GA5 collaboration draft | PARTIAL | [GA5_COLLABORATION_PROPOSAL_AND_UNSENT_DRAFTS.md](ga/GA5_COLLABORATION_PROPOSAL_AND_UNSENT_DRAFTS.md) — 6–8 week division, 3 UNSENT notes, no offers |
| GA6 public proof | PARTIAL | [GA6_CASE_STUDY_RUNBOOK_AND_PUBLIC_DRAFTS.md](ga/GA6_CASE_STUDY_RUNBOOK_AND_PUBLIC_DRAFTS.md) — case study, conditional commands, no adoption, optional original scripts |
| GA7 skeptical referee | PARTIAL | [GA7_INDEPENDENT_SKEPTICAL_REFEREE_REPORT.md](ga/GA7_INDEPENDENT_SKEPTICAL_REFEREE_REPORT.md) — objections, numeric/ethics plan; no human peer review |
| GA8 evidentiary decisions | PARTIAL | [GA8_CLAIM_LEDGER_AND_BACKLOG.md](ga/GA8_CLAIM_LEDGER_AND_BACKLOG.md) — fact/inference/approval boundaries and prioritized backlog |

## File manifest and change control

- **New or integrated in this Chat3 branch:** `docs/week4/INDEPENDENT_SCIENCE_SECURITY_AUDIT.md`, this final gate, `docs/week4/ga/GA{1..8}_*.md` (original private reviewed documents reused by their Git blob SHAs, then edited where appropriate).
- **Modified source now:** `src/psychneuro/w04/product.py` — import disabled pending atomic rights/ACL/store; `tests/test_w04_product_v2.py` — 403 and zero-ACL regression assertion.
- **Existing Chat2 source inherited:** `src/psychneuro/w04/{api,interop,product,rights,ledger,jobs,ui,server}.py`, `apps/web/src/client.ts`, `docs/week4/CHAT2_ARCHITECTURE_AND_RUNBOOK.md`, Docker/manual workflow/tests.
- **Chat1 source not integrated:** `w04/{policy_v2,queue_v2,api_hardened}.py`. The missing exact Chat1 handoff is still BLOCKED.
- The private branch is **not** an open PR, main merge, authorized deploy, or approval to spend CI resources. GitHub content writes create sequential commit SHAs; use live [branch HEAD](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/review/w04-chat3-reconciled-security-20261019) for exact tree and `git rev-parse HEAD`.

## Priority and owner review decisions

**P0:** verify a real Chat1 handoff and Chat2 actual validation traces; choose a reviewed integration base (do not assume DAG merge); make W03 outcome the only permitted source of W04 score; implement atomic tenant claims + immutable store writes and prove rollback with fault injection; bind policy revocation to every worker stage and every export/import; attest source grant and hash against a separately held root. **P1:** run clean pinned GitHub code and full pytest/type/lint/CV replay, host CI exact commit subject to no-cost policy, source-only Docker smoke, lease/fence/cancel and migration/rollback, screen-reader/keyboard checks. **P2:** multi-seed/ablation and held-site/time synthetic shift, performance and signed provenance, independent human security/science review, verified academic prerequisites. No statistical effect claims before robust sampling/estimand plan.

**Rubric:** W04 demands at least **90/100 AND all safety/science/rights/security/independent evidence gates**. Given essential tests not run, a qualifying score cannot be established. **Status In Progress, Done FALSE**. Keep sole W04 Thursday Career calendar date 2026-11-05, suggested Career growth 24 h across week only within <=10 h/day combined learner capacity, Academy READ ONLY 40 h/week, R course reminder and up to 3 optional videos separate. Future course attendance/work not marked completed.

**Separate explicit human approvals required:** review/merge, public repo, external/public deployment, real/human/clinical data, legal/IRB data-clearance, paid compute, any journal/preprint submission, external contact/email, recommendation letters, upstream public PR, career posting. No such action performed. **Final: NO-GO.**

**Additional independent tests preserved in review branch:** `tests/test_w04_independent_oracles.py` (locally **7 passed / 1.43 s** against standalone byte-source preparation, not full GitHub checkout; Python3.13.5; three CV seed tests + four confusion-score tests). Original local test source SHA-256 `79877d59f7200c742c40d7109bdfab9eeb5513754e0b7e440b03923a2a4024a9`. The GitHub commit adding it is `5594bae2e3c185b7c5af77650edd054be6bc11fc`. NO assertion that the current GitHub HEAD passed a complete suite.
