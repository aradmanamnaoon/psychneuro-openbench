# CHAT3 — FINAL INDEPENDENT REVIEW, RELEASE GATE AND HANDOFF
**Prepared:** 2026-10-19, before scheduled W04 2026-11-05–11.
**RELEASE / MERGE / PUBLICATION DECISION: NO-GO.** Independent in this report means *separate adversarial checks performed by an AI assistant*, **not** an attestation from an external human auditor. No Code/rights/security independent release certification; Done remains unchecked.

## Verified repository pointers and branch relationship
- Private repository: https://github.com/aradmanamnaoon/psychneuro-openbench . Unmerged W03 draft PR #13 https://github.com/aradmanamnaoon/psychneuro-openbench/pull/13 (initial inspected head `8e511988e1feecce434eb7a5c109df5ebaf4ef90`). Its historical CI run https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934 ran on **`4eeb17845dac7641b75d9a8164f125db6c213659`**, NOT this new review head.
- Unmerged original W04 draft PR #14 https://github.com/aradmanamnaoon/psychneuro-openbench/pull/14, first inspected W04 head **`a9c84cba4bb0fcec44197ddffe782ab75d9e7ae3`**, base `main`; no pull-request workflow run was returned for that exact SHA in the first check.
- Chat 3 private branch **`review/w04-independent-audit-20261019`** created *from original W04 PR #14 SHA*, **not** a merge of W03. New changes exist only on this private branch. Follow the branch HEAD instead of relying on this pre-finalized doc for the eventual final commit SHA; GitHub's contents API updates create additional commits as documents are written.
- The anticipated `docs/week4/CHAT1_BACKEND_HANDOFF.md` and `docs/week4/CHAT2_PRODUCT_VALIDATION_HANDOFF.md` returned 404 at default and original W04 head. Neither was among four inspected W04 PR14 changed paths. This does not rule out other concurrently edited branches; their work is **unverified/BLOCKED** here. No fictional PR#15 or new product deployment asserted.
- Existing W04 Notion card: https://app.notion.com/p/3fd977a963b281d29c67df3f38231508 ; only Career calendar https://app.notion.com/p/63dd550782f940f399910a2991cb26cf . W04 begins Thursday **2026-11-05**. The Academy is READ ONLY. No calendar cards created.

## Exact code, run and scientific observations
1. Inspected W03 P1: `src/psychneuro/w03/{contracts,nested,service,store,vault,api}.py`; and `src/psychneuro/metrics.py`, `tests/test_w03_integrated.py`. W03 source shows GroupKFold outer3/inner2 with fresh Pipeline scaler/encoder in fit, C grid {0.1,1}, dummy prior same-fold, one heldout and SQLite provenance sidecar. This is a SOURCE INSPECTION plus historical W03 hosted evidence, not an independent current-head full-suite PASS.
2. Inspected W04 actual original P25 `src/psychneuro/rights_v1.py` and `interop_v1.py` and tests; its `accuracy` is **supplied by caller**. The rights evaluator trusts a caller-constructed `verified=True` and claimed `license_id`. No live rights issuer, tenant ACL, distributed queue, revocation projection, signed provenance, browser UI or true W03→W04 measured-result integration exists in the inspected W04 patch.
3. Chat 3 safely changed `src/psychneuro/interop_v1.py` to fail closed for unknown/malformed/out-of-version event fields, invalid group IDs, NaN/bool accuracy, improper seeds, oversize payload and unexpected bundle keys; added `expected_sha256` option requiring caller-supplied independently trusted pin for detecting coherent rehash. Added tests `tests/test_w04_interop.py` illustrating rehashed off-contract denial and coherent attacker rehash vs pinned root. These changes **do not** authenticate the pin or grant; they simply expose a boundary for future integration.
4. **Actually executed locally** (separate reconstructed prototype, NOT checkout of final GitHub SHA) Python 3.13.5 `PYTHONPATH=src python -m pytest tests/test_w04_interop.py -q`: **17 passed in 0.06 seconds**. SHA-256 of local log `89e1b0af37b0d94ce229fc7d791696421fed9f216ea64fa59a7364500c439d87`, local reconstructed source SHA `40a32dcc2a5a1b50c080dd598694f0cb0564f4366c208500eded44dbe0efd101`; local tests are related but **not byte-identical** to final private branch. Initial local prototype failed two test cases before a tuple/list roundtrip correction, then passed 17.
5. **Actually executed separate GA3 synthetic oracle** (Python3.13.5, NumPy2.3.5, scikit-learn1.8.0): 16 fictional groups ×6 rows; row-wise `KFold(4,shuffle=True,random_state=73)` contaminated **4/4 folds** while `GroupKFold(4)` contaminated **0/4**. An educational artificial split comparison, not an upstream skrub integration. Code in [GA3](ga/GA3_UPSTREAM_REVIEW.md).
6. W03 **historic** CI report: 349 pytest PASS Python3.11.17 and 349 PASS Python3.12.15; generator seed73, split42, 36 fictional groups×12=432 rows, train21/test8/reserved7; outer logistic balanced accuracy **0.5**, dummy **0.5**, heldout **0.5**, C=0.1. Original source SHA `bc6f7b672193d4c4b4af13d1df25964454d3216d6e5c4b3c9c9c6099363412b8`, split SHA `9d1dce92823468eb1019629b7c9c8f86c391d6f151fb5ed9b418d3b5377ad6c8`, run `b4a0f38b4c3302c56a1e75151813dc0bada8c1f95b45269eee9fe0914ba16844`, P13 root `8d7c322a7d1d17f0fb41f87c9e6f78b4d409ed1650f604e3bf70821b157981ed`. Those SHA/score values were copied from W03 archived source report and **NOT freshly independently rebuilt in Chat3**.
7. Analytical BA oracle: if TP=3,FN=1,TN=5,FP=1 then BA = `(3/4+5/6)/2=19/24=0.791666…`; majority-class constant prediction gives BA 0.5 when both truth classes are present. No human findings or population sampling claim.

**NOT RUN or NOT VERIFIED:** exact-current-GitHub-head pytest, Ruff, mypy, Hypothesis property suite, clean-room W03 data rebuild and independent rehash, complete Python3.11/3.12 installed dependency matrix, OpenNeuro data rights, API↔browser E2E, cross-W03/W04 measurement wiring, signing, auth/tenant permissions, kill/resume/lease race, migration/rollback, stress CPU/heap/latency, Docker/private host and screen-reader tests, full skrub DataOps/gallery, W04 exact-SHA hosted CI. Past CI success does NOT certify this branch. User did not approve paid runners/deployment; none dispatched deliberately.

## E1–E14 (DONE / PARTIAL / BLOCKED, all hard gates must pass)
| Epic | Status | Evidence / hard blocker |
|---|---|---|
| E1 benchmark API and browser visualization | **BLOCKED** | No W04 browser or multi-dataset measured run |
| E2 provenance explorer/import/export | **PARTIAL** | W03 4-node unsigned DAG, W04 event hash; no explorer or validated re-import |
| E3 cancellation/checkpoints/role audit | **BLOCKED** | No persisted worker and ACL |
| E4 Docker/CI/locked artifact packaging | **BLOCKED** | No current hosted W04 CI, no reproducible lock |
| E5 rights contracts engine P25 | **PARTIAL** | W04 typed mock grant/action/revocation; authority cannot be trusted |
| E6 benchmark and falsification | **PARTIAL** | Hand BA oracle + separate local negatives; W03 historic benchmark only |
| E7 persistence/rights lifecycle/migrations | **PARTIAL** | W03 SQLite index; no W04 durable rights/revocation/migrations |
| E8 concurrency/restart/backpressure | **BLOCKED** | No durable queue or worker tests |
| E9 accessible browser/API/SDK | **BLOCKED** | W03 internal API source only |
| E10 performance/scale | **BLOCKED** | No measured capacity/resourcing |
| E11 threat/property/adversarial QA | **PARTIAL** | Narrow negative tests; no coherent signed attestation and tenant tests |
| E12 hosted CI/rollback/release engineering | **PARTIAL** | Historical W03 run only, no exact W04 head run |
| E13 P1×P13×P25 interoperability | **PARTIAL** | Reference hand-fed W04 metric, not true source-linked pipeline |
| E14 documentation/reviewer evidence | **PARTIAL** | This audit and 8 GA files, no audit certification/live test |

## GA1–GA8 completion states
All GA documents are **delivered as private drafts/evidence**, but no entire GA epic is marked DONE because source verification, real deployment, admissions outcomes, reviewer approval and outreach are distinct.
| GA | Status | Committed artifact |
|---|---|---|
| GA1 literature 8–15 genuine methods/standards | **PARTIAL** | [13-source bibliography](ga/GA1_LITERATURE_EVIDENCE.md): primary simulations/reviews/standards clearly distinguished; not systematic review |
| GA2 publication protocol and methods | **PARTIAL** | [Hypotheses, claim-evidence matrix, plan, disclosure](ga/GA2_PROTOCOL_METHODS.md), no experimental paper/results |
| GA3 upstream contribution | **PARTIAL** | [skrub open issue #2340 and reproducer](ga/GA3_UPSTREAM_REVIEW.md); maintainers approval absent, no upstream PR |
| GA4 labs/pathways/fees | **PARTIAL** | [5 official degree/pathway options](ga/GA4_ACADEMIC_PATHWAYS.md); individual eligibility, funding and live fees/deadlines require recheck |
| GA5 collaboration and unsent notes | **PARTIAL** | [6–8-week proposal and three personalized UNSENT messages](ga/GA5_COLLABORATION_PROPOSAL_AND_UNSENT_DRAFTS.md) |
| GA6 portfolio/public technical education | **PARTIAL** | [Case study, commands, factual CV bullets, prospective feedback rubric, scripts](ga/GA6_CASE_STUDY_RUNBOOK_AND_PUBLIC_DRAFTS.md); none published |
| GA7 critical referee/replication | **PARTIAL** | [9 objections, failure-design and sampling caveats](ga/GA7_INDEPENDENT_SKEPTICAL_REFEREE_REPORT.md); independent human peer review absent |
| GA8 credibility, decisions and backlog | **PARTIAL** | [Evidence ledger, 30-day ranked P0/P1/P2 backlog](ga/GA8_CLAIM_LEDGER_AND_BACKLOG.md); real external impact absent |

## Inventory, rights and scholarly evidence
Files newly created: this handoff; `docs/week4/INDEPENDENT_SCIENCE_SECURITY_AUDIT.md`; eight GA Markdown documents in `docs/week4/ga/`. Files edited: `src/psychneuro/interop_v1.py`; `tests/test_w04_interop.py`. Original W04 rights file **not** replaced. GA4 scholarship statement was corrected to treat user's credentials and eligibility as **unverified**.

**Dataset/public rights:** W03 internally generated data registry says `not-separately-specified`; W04 `CC0-1.0` is **only a mocked test-string**, not proof of licensed export. No real human or clinical input used. Six candidate human OpenNeuro entries remain unapproved for use, according to historic W03 source memo.
**Key bibliography:** Cawley & Talbot 2010 https://www.jmlr.org/papers/v11/cawley10a.html ; Varma & Simon 2006 https://doi.org/10.1186/1471-2105-7-91 ; Varoquaux et al. 2017 https://doi.org/10.1016/j.neuroimage.2016.10.038 ; Varoquaux 2018 https://doi.org/10.1016/j.neuroimage.2017.06.061 ; Kapoor & Narayanan 2023 https://doi.org/10.1016/j.patter.2023.100804 ; W3C PROV-O https://www.w3.org/TR/prov-o/ ; FAIR https://doi.org/10.1038/sdata.2016.18 ; full 13 entries in GA1.
**External third-party audit:** NONE. No university admission, acceptance, scholarship, paper, external maintainer praise or software adoption verified.

## Release rubric and next work
W04 requires **>=90/100 AND EVERY scientific, rights, security, independent evidence release gate**. This branch is incomplete; a valid numeric score cannot be responsibly awarded for unrun gates and should not be used to make Done true. Keep Notion **In Progress / Done unchecked**, original single 2026-11-05 Thursday card and existing 24 suggested Career hours; total human focused work <=10h/day, Academy unchanged 40 h/week; R-course reminder and three optional original videos remain separate. No claims that study occurred before scheduled week.

**P0:** reconcile missing Chat1/2 deliverables and merge-base conflicts in private review, run exact W03/W04 code on a single clean fixture with current-source CI; derive W04 metric from trusted W03 RunResult (never caller input); establish rights attestation by data owner and immutable source hashes; prove revoked cached use fails and independently pinned signatures defend coherent tampering.
**P1:** tenant ACL/role probes, idempotent worker race/cancel/resume, schema migrations and rollback, accessible browser integration/keyboard review, small no-cost authorized private smoke with real logs.
**P2:** instrument CPU/heap/latency, lock transitive deps, run multi-seed + held-site synthetic falsification, then human independent scientific/security referee. Re-evaluate funding/entry status only against official university records with verified credentials.

**Approvals that remain separate and required:** user approval to merge PRs, publicize repository, deploy even publicly, ingest human datasets, submit manuscript/preprint, contact any academic, open upstream public PR, spend money or claim public recognition. No such actions taken.

**Final determination: NO-GO** for code merge, scientific public proof, private production use, human-data processing, journal submission and public release; retain an unmerged private audit branch and use the status tables for next cycle.
