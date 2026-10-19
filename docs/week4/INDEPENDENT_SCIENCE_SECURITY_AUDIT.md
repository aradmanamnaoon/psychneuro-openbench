# W04 latest independent execution evidence — 2026-10-19

See [executed exact-source QA delta](./CHAT3_EXECUTED_QA_EXACT_SOURCE_20261019.md) and [private draft PR #22](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/22). Independent local test source **83/83 Git blobs matched** the review commit `b3c5563f19e988173302f462df2b871fd1d97447`. Subsequent committed pure Python lint changes were already included when the **400 pytest / 247 warnings**, **47-file mypy strict**, and **zero-finding full Ruff** tests passed. Previous sections saying Chat3 tests were NOT RUN or handoffs absent are historical branch-limited observations and are **superseded by these recent direct executions**.

Actual W03 fictitious three-seed benchmark: **36 participants per run**, split **21 train+7 validation+8 test**; model/dummy/sealed test balanced accuracy **0.500** each; no neuro/clinical significance. The GitHub manual CI workflow was improved but is **not hosted-run-certified**. Authenticated report import remains intentionally disabled pending external root trust and source rights. Keep **NO-GO**, **Done false**, and public/clinical/academic release approval separate.

---

# W04 — Canonical Chat1×Chat2 scientific/security review update (19 October 2026)

**Release: NO-GO.** This *current addendum* supersedes historical claims below wherever the reviewed integration differs. AI-performed internal adversarial review, **not** independent human security or neuroscience attestation.

## Current exact source ancestry

- BASE: private W04 [Chat2 on Chat1 draft PR #18](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/18), HEAD at inspection `563f3fe6f15af74c8feb16d493d2c00454cac308`, forked directly from Chat1 final commit `e0a32b00843ae1346dc3382908de436b497c7cb0`.
- Current review branch: `review/w04-chat3-on-latest-chat2-20261019` (GitHub branch HEAD is authoritative). Base and review branch remain **PRIVATE**, unmerged.
- Actual mandatory [Chat1 handoff](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/review/w04-chat2-on-chat1-final-20261019/docs/week4/CHAT1_BACKEND_HANDOFF.md) and [Chat2 handoff](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/review/w04-chat2-on-chat1-final-20261019/docs/week4/CHAT2_PRODUCT_VALIDATION_HANDOFF.md) **EXIST** in this canonical ancestry. Earlier branch-only searches incorrectly marked them missing.
- W03 historic run [39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934) was on a different source SHA and does **not** attest these review changes.

## Independent source defect, repair, test and CI state

| Claim / issue | Changed source | Adversarial regression | Actual execution evidence | Status |
|---|---|---|---|---|
| Persisting W03 P13 result and W04 tenant owner must be one transaction | `src/psychneuro/w03/store.py` (`put_in_connection`), `src/psychneuro/w04/product.py` (`TenantRunACL.put_owned`, `OwnerBoundRunStore`), `src/psychneuro/w04/api.py` | `tests/test_w04_atomic_ownership.py`: success, idempotency, cross-tenant denial, injected ACL insert failure, orphaned legacy run, corrupt provenance, split database | New GitHub integration suite **NOT EXECUTED**. Separate standalone SQLite **3/3 passed** local (Python3.13.5, 0.10s), confirming SQLite rollback *mechanics only*, not GitHub integration | PARTIAL |
| Imported hashes are not independently authenticated and tenant ownership could be forged | `product.py`, `api.py` | Existing v1/v2 API tests amended for maintainers receiving HTTP 403 while import disabled | New exact-head API tests **NOT RUN** | PARTIAL; importing intentionally DISABLED pending signed independently held root & rights |
| Group isolation with repeated observations | `src/psychneuro/w03/nested.py` (historical unmodified) | `tests/test_w04_independent_oracles.py` from prior Chat3 | Separate offline 7/7 passed; hypothetical group overlap 13,13,13,12 rowwise vs 0,0,0,0 grouped; not actual W03 numeric replay | PARTIAL |
| P25 V2 grant, job queue, cancellation and restart under revocation | `src/psychneuro/w04/{policy_v2,queue_v2,api_hardened}.py` unchanged from Chat1 | `tests/test_w04_hardened_backend.py` and API tests as previously recorded in Chat1 handoff | Historical Chat1 isolated tests **29 passed** on a local W03 contract mirror, **NOT** unified repo or current HEAD | PARTIAL |
| Hosted CI/typed SDK/browser security | `.github/workflows/w04-private-manual.yml`, `apps/web/` | Existing suite/manual workflow | No new dispatch/runner bill, live browser, scanner, package lock or exact SHA log | BLOCKED |

**Important:** The SQL implementation uses one `BEGIN IMMEDIATE` transaction shared by the immutable run, four provenance index rows, and owner claim, with strict refusal to automatically claim older unowned records. This addresses only that atomic boundary. It does **not** repair missing W04 v2 permission checks around actual W03 fitting, durable compute workers, external identity, forged/rehashed root trust or time-of-check/time-of-use revocation. No human/clinical dataset was accessed or authorized.

## Reviewer assessment

Unresolved substantive objections: (1) fictional predictor constructs do not establish neural/behavioral meaning; (2) participant-disjoint CV still omits site/time/source clustering; (3) model selection/trial dependence precludes naive fold CIs; (4) holdout reused during iterative engineering would bias any empirical claim; (5) source rights are internal synthetic only, no public CSV redistribution license; (6) P13 SHA DAG without independent signature can be coherently rewritten; (7) P25 v2 and legacy v1 remain separate authorization paths in the product; (8) no model-worker crash/lease replay; (9) incomplete independent deployment/accessibility and adversarial performance validation.

## E1–E14 disposition at this stage

| E | Status | Reason |
|---|---|---|
| E1 | PARTIAL | P1 API/browser source, no witnessed real browser verification |
| E2 | PARTIAL | Source DAG/verification; external signatures and import remain blocked |
| E3 | PARTIAL | V2 job coordination source; no actual compute worker restart |
| E4 | PARTIAL | Manual Docker/CI files, no exact commit run or verified lock/SBOM |
| E5 | PARTIAL | P25 v1 and v2 internal synthetic rights contracts, no independent attestor |
| E6 | PARTIAL | Synthetic oracles and W03 historic scores, no new fitting replicates |
| E7 | PARTIAL | Atomic run/owner repair and v2 policy, no backup/rollback stress |
| E8 | PARTIAL | Durable fenced queue metadata, not fitted job resumability |
| E9 | PARTIAL | Browser/TS source, no keyboard/axe/device check |
| E10 | BLOCKED | No current measured end-to-end p95/RSS/throughput |
| E11 | PARTIAL | Added fault-injection regression source; no exact-head test |
| E12 | BLOCKED | No hosted QA or tested migration/recovery |
| E13 | BLOCKED | Actual P25 v2-permitted worker→P1 fit→P13 chain not demonstrated |
| E14 | PARTIAL | This file and GA docs, missing current exact-head CI/host record |

**Exact W04 internal release rubric >=90/100 AND ALL gates: NOT MET / score not awarded.**

---

## Archived earlier Chat3 review (branch-scoped, not the final canonical source)

# W04 Independent Scientific and Security Audit — reconciled review

**Review date:** 2026-10-19 (W04 scheduled 2026-11-05–11). **Decision: NO-GO.** This is an independent *AI-assisted second-pass code review*, not a third-party human assurance report. No production approval, release, clinical claim, thesis result, merge, deploy or external outreach.

## Exact checked source and dependencies

| Evidence | Immutable identifier / scope | Audit disposition |
|---|---|---|
| Private repo | [psychneuro-openbench](https://github.com/aradmanamnaoon/psychneuro-openbench), private, writable, default `main` | VERIFIED connector metadata |
| Historic W03 | [PR #13](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/13), head `8e511988e1feecce434eb7a5c109df5ebaf4ef90`, unmerged | source separate; historical [Actions #39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934) tested `4eeb17845dac7641b75d9a8164f125db6c213659`, not current W04 |
| Original W04 | [PR #14](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/14), head `a9c84cba4bb0fcec44197ddffe782ab75d9e7ae3`, unmerged | separate four-file P25 mock slice |
| Chat 1 actual | [private Chat1 branch](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/review/w04-chat1-durable-backend-20261019) commit `8fbfb1ed27d4ac22ea46fa859951e0cd4f5b647f` | inspected `w04/policy_v2.py`, `queue_v2.py`, `api_hardened.py`, tests; no exact named handoff file, no hosted run returned |
| Chat 2 actual | [private Chat2 branch](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/review/w04-chat2-product-20261019) commit `2d436aaac460cff5bc7d29fd4f2026b7b56be4a2` | `CHAT2_ARCHITECTURE_AND_RUNBOOK.md` exists as **equivalent** design handoff; `CHAT2_PRODUCT_VALIDATION_HANDOFF.md` does not; browser/TS/product/test code exists, no hosted run returned |
| Original prior Chat3 | [private review branch](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/review/w04-independent-audit-20261019) commit `9b35a993b3a5b832d844c6f8b937a9ef4409b051` | original PR14-oriented independent mock-contract validation; not a merged Chat1/2 test |
| Current reconciled Chat3 | [private security review branch](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/review/w04-chat3-reconciled-security-20261019), based on actual Chat2 head `2d436aaa...` | **new fail-closed import patch**, regression test source, 8 transferred GA drafts and this revised audit; no PR or merge |

**Critical dependency DAG:** `W03 original synthetic registry → W03 SourceRights/P25 synthetic-only policy → W03 GroupKFold nested CV → immutable RunStore → unsigned P13 4-node SHA-256 DAG → Chat2 v2 run ACL → browser/TS consumer`. Chat1 **separate** branch adds P25 `p25-event-2` ledger, HMAC-scoped permit, `w04-job-2` SQLite CAS/fencing/lease; not present on Chat2 base. Chat2 `w04-envelope-1` is hash-integrity-only, no source-owner signature. `w03-engine-1`, `p25-rights-1`, `p25-event-2`, `w04-envelope-1` are NOT a jointly reviewed versioned compatibility guarantee.

## Source-to-test-to-hosted-CI claim ledger

| Claim | Code and test | Independent observation | Exact-head CI |
|---|---|---|---|
| Participant disjoint grouped splits, train-only selection, dummy | `src/psychneuro/w03/nested.py`, `tests/test_w03_integrated.py` | Source and historic reported run inspected; clean W03 replay NOT RUN | historic #39228198934, different SHA |
| Local P25 policy with explicit revocation | Chat1 `w04/policy_v2.py`, `tests/test_w04_hardened_backend.py` | Source inspected; operator-provided rights not legally attested; HMAC key not external root | NONE returned for Chat1 head |
| Fenced queue and cancellation coordination | Chat1 `w04/queue_v2.py`, `tests/test_w04_hardened_backend.py` | SQLite transactional CAS/fence code exists; no real worker/computation checkpoint/restart equivalence | NONE |
| W03-backed run and artifact browser API | Chat2 `w04/product.py`, `w04/api.py`, `tests/test_w04_product_v2.py` | Real registry-backed test **written**; not executed on exact Chat2 SHA in this audit; no keyboard/screenreader audit | NONE |
| **Non-atomic artifact import** | Chat2 original `product.py` imported: `acl.claim → runs.put` | SQLite failure-model reproducer leaves **1 ownership row** after simulated storage exception. Independent model of observed sequence, not checked-out code | NONE |
| Import refusal regression | new Chat3 `w04/product.py`; `tests/test_w04_product_v2.py` | Import endpoint intentionally **403 W04_IMPORT_DISABLED** before any ACL write; new test asserts empty ACL after valid import attempt; **test code unrun** | NONE |
| Independent BA and grouping oracle | local synthetic script `w04_chat3_independent_oracle.json` | Python 3.13.5/NumPy 2.3.5/scikit-learn; confusion TP3 FN0 TN5 FP2 gives BA 6/7=0.857142857; row-KFold has overlapping groups [13,13,13,12], GroupKFold [0,0,0,0] | independent local-only, NOT W03/W04 regression |
| Hash event perturbation | original independent review `tests/test_w04_interop.py`, `interop_v1.py` | Prior local reconstructed prototype **17 passed** (not exact GitHub byte-identical) | NONE |

**Historic reported W03 fixture:** 36 fictional groups × 12 trials=432 rows; synthetic generator seed 73, split seed 42; 21 train, 8 test, 7 reserved; 3 outer/2 inner grouped folds, logistic `C=0.1`; dummy/logistic outer BA each 0.5 and heldout 0.5. These are historical W03 reported numbers, **not** new independent replication. Historical hashes reported: source `bc6f7b672193d4c4b4af13d1df25964454d3216d6e5c4b3c9c9c6099363412b8`; split `9d1dce92823468eb1019629b7c9c8f86c391d6f151fb5ed9b418d3b5377ad6c8`; result `b4a0f38b4c3302c56a1e75151813dc0bada8c1f95b45269eee9fe0914ba16844`; provenance root `8d7c322a7d1d17f0fb41f87c9e6f78b4d409ed1650f604e3bf70821b157981ed`. **The current GitHub heads were NOT rebuilt/rehashed from that dataset.**

## Rights and data provenance registry

| Item | Source and integrity | Rights conclusion |
|---|---|---|
| W03 fictional generated behavior | local generation, seed73, historic SHA as above | permitted as internal synthetic fixture by code conventions; separately licensed export NOT established |
| W03 train/test/validation partition | split seed42, historic split hash | group isolation source present; no claim of participant independence beyond fixture |
| Chat1 `W03_INTERNAL` | `rights.py`, server controlled | internal synthetic aggregate handling only; permission issuer/retention/legal authorization not externally reviewed |
| Chat2 dataset rights and `interop` | `p25-rights-1`, unsigned SHA-256 envelope | local integrity, not identity, consent, authenticated holder or lawful external redistribution |
| Original W04 `CC0-1.0` toy grant | test constant, not a signed source grant | no CC0 rights inferred |
| Human/OpenNeuro inputs | no W04 real dataset downloaded | excluded until specific consent, copyright/license, institutional and privacy review |

**Threat model:** principals (operator, API user, worker, tenant, source steward, malicious importer); assets (synthetic row data, run scores, participant splits, run ownership, policy revision, receipts); boundaries (source→permission, train→test, API→ACL, worker lease→storage, archived hash→trusted signer). Remaining P0 risks include: `runs.put` not transactionally co-committed with ownership (import disabled as mitigation, not a full fix); deterministic run collisions across tenants; mutable unsigned roots and coherent rehash forgery; no deployed auth/session, rate limiting or token rotation; revocation/permit check and worker stage not proven atomic; cancellation fencing only coordinates, cannot stop fitting without a worker; SQLite rights ledger not proof of consent; no real data rights adjudication, DB migration/rollback, cross-process load or clean private host.

## E1–E14 verified status

| Epic | Status | What exists / missing hard gate |
|---|---|---|
| E1 benchmark-to-browser | PARTIAL | Chat2 W03-backed v2 API/UI source; no actual browser or second dataset |
| E2 P13 graph/export/import | PARTIAL | source graph and verification; import deliberately disabled, unsigned |
| E3 job cancellation/resume/auth | PARTIAL | Chat1 coordination and Chat2 legacy job metadata on **different branches**; real worker absent |
| E4 Docker/cloud/CI/lock | PARTIAL | Docker/manual workflow source; Docker/CI/security scan not executed at reviewed head |
| E5 P25 rights engine | PARTIAL | typed v1/v2 policy code; independent rights authority unverified |
| E6 independent baselines/ablation | PARTIAL | independent arithmetic/grouping oracle; no fresh W03 multi-seed ablation |
| E7 schemas/persistence/revocation | PARTIAL | SQLite source and version tables; migration/retention/rollback not proven |
| E8 restart-safe distributed execution | PARTIAL | Chat1 transactional coordination/leases but **no actual worker/restart equivalence** |
| E9 accessible product/API/TS SDK | PARTIAL | browser/TS source; keyboard/axe/accessibility/SDK E2E not run |
| E10 latency/memory/scale | BLOCKED | no representative benchmark measured |
| E11 adversarial property/security | PARTIAL | artifact/tenant/negative tests in source; current-head full tests and threat remediation open |
| E12 exact-hosted CI/recovery | BLOCKED | no exact Chat1/Chat2/reconciled-head hosted CI and rollback |
| E13 three-system E2E | PARTIAL | Chat2 registry-backed integration **test source**, not independently executed; Chat1 not combined |
| E14 reviewer evidence | PARTIAL | 8 GA artifacts, independent oracle, threat memo; release/a11y gates open |

## Skeptical scientific peer review — MAJOR REVISION (software methods only)

1. **Construct mismatch:** fictional two-condition classifier has no established cognitive/neural construct validity; never infer diagnostic utility.
2. **Hierarchical dependence:** leaving subjects out does not address shared scanner/site/experimenter/time/session; prespecify a held-site or temporal stress test.
3. **Endogenous features/target timing:** prove no post-response field or outcome-derived metadata enters `X`; add a deliberate injected-future-feature negative test.
4. **Model selection leakage:** nested grouped CV is an intended defense, but verify preprocessors are fitted inside each inner fold, and do not use sealed holdout for tuning.
5. **Null and chance baselines:** a random balanced classifier's expected BA and dummy 0.5 are not evidence of biological signal; require predeclared ablation and no selection on seeds.
6. **Uncertainty:** overlapping CV train folds and shared subjects violate independent-fold assumptions; no naive p-value, fold-SE CI, calibration or population generalization.
7. **Rights vs hashes:** self-consistent rehash, stale permission and forged ledger roots break authenticity and legitimacy; require externally pinned signed evidence and revoke-before-worker-commit negative.
8. **Sampling under shift:** site/session effects and class imbalance can reverse apparent performance; report per-group label prevalence and distribution shift.

**Next experiment design:** (a) prespecify three or more independent fictional generator/partition seed pairs before looking at outcomes; (b) one model/dummy and fixed inner C-grid under same outer groups; (c) ablate one prespecified pre-response predictor; (d) inject identical-group and post-outcome leakage failures to demonstrate rejection; (e) independent sklearn-vs-hand balanced-accuracy confusion oracle for each run; (f) check run-hash corruption/complete coherent forgery with and without separately held trusted root; (g) simulate revocation between authorization and completion with a real worker; (h) record all results without hypothesis testing or significance unless participant-level estimands and independent sampling justify it.

**Key external method references:** [Cawley/Talbot 2010](https://www.jmlr.org/papers/v11/cawley10a.html), [Varma/Simon 2006](https://doi.org/10.1186/1471-2105-7-91), [Varoquaux et al. 2017](https://doi.org/10.1016/j.neuroimage.2016.10.038), [Roberts et al. 2017](https://doi.org/10.1111/ecog.02881), [Kapoor/Narayanan 2023](https://doi.org/10.1016/j.patter.2023.100804), [W3C PROV-O](https://www.w3.org/TR/prov-o/); [full typed bibliography, 13 sources](ga/GA1_LITERATURE_EVIDENCE.md).

**Scope:** no real psychology/neuroscience finding, independent human software audit, consent/legal attestation, clinical validation, third-party adoption, CI pass on current head, or publication.

**New isolated regression suite:** `tests/test_w04_independent_oracles.py` added to this review branch from a locally executed standalone file; `python -m pytest -q /mnt/data/test_w04_independent_oracles.py` gave **7 passed in 1.43 s**, Python 3.13.5 (three predeclared synthetic CV seeds 17/73/101 plus four confusion-matrix oracle vectors). Local tested file SHA-256 `79877d59f7200c742c40d7109bdfab9eeb5513754e0b7e440b03923a2a4024a9`. This is **not** an execution of the source checkout of this exact GitHub commit or proof of the W03/W04 end-to-end service. No current-head CI job was run. The synthetic run JSON SHA is `caecf81d8724072439ac07e6735bd5f2fbc228d118189750e4eb7871d23e493b`.
