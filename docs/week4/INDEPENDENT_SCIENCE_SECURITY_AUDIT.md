# Independent W04 science/security audit (AI-assisted internal; 2026-10-19)
**DECISION: NO-GO for merge, public release, human-data use, scientific claims and publication.** This is *not* an external independent auditor's attestation. Scheduled W04 is **2026-11-05–11**; this is preparatory work on 2026-10-19, not completed future human study hours.

## Source identification and branch DAG
- **Repo:** private [aradmanamnaoon/psychneuro-openbench](https://github.com/aradmanamnaoon/psychneuro-openbench).
- **W03:** private [draft PR #13](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/13) unmerged; head at first inspection `8e511988e1feecce434eb7a5c109df5ebaf4ef90`; original historic exact source SHA `4eeb17845dac7641b75d9a8164f125db6c213659`. Historical [CI #39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934) reported 349 PASS in each Python 3.11.17 and 3.12.15. Source tested then; no blanket CI proof for current PR.
- **W04 original:** private [draft PR #14](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/14), base `main`, head `a9c84cba4bb0fcec44197ddffe782ab75d9e7ae3` when inspected; four changed files: `rights_v1.py`, `interop_v1.py`, `test_w04_interop.py`, `docs/week4/release-gate.md`. First check returned **no associated PR workflow runs** for this SHA. Do not interpret absent result as evidence that no other CI exists elsewhere.
- **Chat3 review branch:** `review/w04-independent-audit-20261019` forked from W04 PR #14 SHA; separate new private branch **not integrated into PR #14**. Patches: contract-field/type/size validation and an optional externally pinned digest; new negative tests; this audit plus eight GA files and final gate. Neither W03's branch nor original W04 PR merged.
- Required Chat1 `docs/week4/CHAT1_BACKEND_HANDOFF.md` and Chat2 `docs/week4/CHAT2_PRODUCT_VALIDATION_HANDOFF.md` were 404 on `main` and the first-inspected W04 head. There is **no evidence** of their asserted PR/branch/test claims. Other equivalently named artifacts were not discovered in the inspected four W04 PR-changed files; treat as **BLOCKED**. Concurrent future writes in other chats are not assumed.
- **Contract DAG observed rather than imagined:** W03: `SyntheticConfig` + `load_dataset(registry)` → `create_group_split` → `validate_group_split` → `nested_grouped_benchmark` → `RunResult` → `make_chain` of 4 nodes → `RunStore` immutable aggregate + provenance sidecar; internal `FastAPI` POST/GET. W04 *separate* prototype: caller-constructed P25 `DatasetGrant` → `evaluate` → `validate_split` (group names, not W03 raw row indices) → caller-provided `accuracy` → SHA256 event hash. **No actual W03 measured result to W04 event mapping.**
- **Contract versions:** W03 `w03-engine-1` (`src/psychneuro/w03/contracts.py`); W04 `p25.v1` (`src/psychneuro/rights_v1.py`) and `interop.v1` (`src/psychneuro/interop_v1.py`). Versions are *not* a guaranteed stable/public compatibility specification.

## Traceable claim → source → test → CI evidence → status
| Claim | Source paths | Tests / negative oracles | Hosted CI/log | Status |
|---|---|---|---|---|
| Group isolation against duplicate/partial/crossover participants | `src/psychneuro/w03/nested.py` (`validate_isolation`), `src/psychneuro/split.py` | `tests/test_w03_integrated.py` | W03 run 39228198934, earlier exact SHA | HISTORIC-VERIFIED ONLY |
| Nested train-only preprocessing and C selection | `w03/nested.py` `_model/_select` | W03 test and CV source inspected | same earlier W03 run | PARTIAL independent review; current clean-room run NOT DONE |
| W03 P13 four-node chain and SQLite corruption detection | `w03/vault.py`, `w03/store.py` | `tests/test_w03_integrated.py` | earlier W03 run | PARTIAL; unsigned, mutable root |
| W04 denied rights, revoked local grant, prohibited action | `rights_v1.py`, `interop_v1.py` | `tests/test_w04_interop.py` | no W04 hosted run at inspected head | LOCAL-TARGETED, no authentic attestation |
| W04 altered event schema / unknown fields / duplicate groups | patched `interop_v1.py` | added independent negative pytest cases | new review head hosted CI NOT VERIFIED | LOCAL-TARGETED, no hosted proof |
| Independently pinned digest detects coherent rehash | patched `verify_artifact(expected_sha256=...)` | test rehash then pin rejects | no hosted W04 proof | LOCAL-TARGETED, not a digital signature |
| Independent model score and effect | W03 source plus report; no new experiment | handwritten BA oracle; no new real fit | prior reported BA logistic=.5,dummy=.5,test=.5 | SCIENTIFIC EFFECT NOT ESTABLISHED |
| Real source rights, current revocation/tenant ACL | W04 caller-supplied booleans; no credential service | no authoritative rights attestation | none | BLOCKED |
| UI, multi-service E2E, worker resume, migration/rollback, private deployment, load | none on inspected W04 patch | none observed | none | BLOCKED |

## Actual local execution details
Executed sandbox **Python 3.13.5**, `PYTHONPATH=src python -m pytest tests/test_w04_interop.py -q` on a **locally reconstructed patch prototype** at `/mnt/data/w04_audit`, **17 passed in 0.06 s** after fixing an initial broken roundtrip representation (two failed tests before fix). Verification includes 9 parameterized rehashed off-contract vectors, event unknown fields/overlap/duplicates, bool/NaN/infinite/invalid seeds, oversized payload, external digest pin mismatch, present/absent rights and a hand-calculated balanced-accuracy check. Because local files were recreated from reviewed source and the GitHub review branch has separate source formatting/test composition, **the 17-pass count is not an exact-current-commit CI or full-repository test claim**. Ruff and mypy are not installed in sandbox; those checks were NOT RUN for this review branch. A Python 3.11/3.12 live matrix, actual W03 registry replay, migration recovery, property-testing Hypothesis, browser keyboard audits, load measurements and private hosted smoke were NOT RUN. Targeted execution log sandbox SHA256: `89e1b0af37b0d94ce229fc7d791696421fed9f216ea64fa59a7364500c439d87`; sandbox reconstructed source SHA256 `40a32dcc2a5a1b50c080dd598694f0cb0564f4366c208500eded44dbe0efd101` (not GitHub blob hash).

**Independent BA oracle:** TP=3,FN=1,TN=5,FP=1 → BA=[3/4+5/6]/2=19/24≈0.791667. Dummy all-negative with both truth classes present → BA=.5. These are hand-chosen counts, NOT a fitted scientific run. W03 archived original reported 36 fictional participant IDs×12 trials=432, 21 train/8 test/7 reserved, generator seed 73, split seed 42; outer and dummy BA=.5, heldout=.5. Historical source hash `bc6f7b672193d4c4b4af13d1df25964454d3216d6e5c4b3c9c9c6099363412b8`, split `9d1dce92823468eb1019629b7c9c8f86c391d6f151fb5ed9b418d3b5377ad6c8`, run `b4a0f38b4c3302c56a1e75151813dc0bada8c1f95b45269eee9fe0914ba16844`, provenance root `8d7c322a7d1d17f0fb41f87c9e6f78b4d409ed1650f604e3bf70821b157981ed`. **Copied from historic report, not freshly recreated/rehash-checked by Chat 3.**

## Data seed/licence/hash and rights registry
| Item | Seed/source hash | Rights status |
|---|---|---|
| W03 fictional generator only | seed 73, W03 archived SHA above | `not-separately-specified`; private internal synthetic only; standalone CSV public redistribution **not authorized** |
| W03 partition | seed 42, W03 archived split SHA above | participant disjointness checked in reported W03 run; current clean rebuild not verified |
| W04 mocked “fictional” grant | `"a"*64` is a placeholder, not actual source content | `license_id="CC0-1.0"` **in test object only**; DO NOT interpret as a granted CC0 data license |
| Real OpenNeuro candidates | no human inputs downloaded/used in W04 | disabled/no authorization, consent and compliance review not verified |

## Threat model and residual risk
- **Actors/assets:** malicious dataset submitter; compromised worker or operator; concurrent or replayed clients; unauthorized tenant; stolen internal header token; privacy-sensitive study source; dataset rights; benchmark validity and provenance chain.
- **Trust boundaries:** untrusted dataset→rights attestor; source→group partition; train data→model; test cohort→model choice; API caller→tenant run store; persisted event→trusted independent digest; export→external audience.
- **Positive controls presently visible:** W03 manifest fixed pre-response predictors, bounded participant counts; group-isolated sklearn Pipeline; internal token check; immutable same-run SQLite payload and sidecar; W04 local-rights denial and strengthened type/size/schema validation.
- **Unmitigated:** rights attestation is user-supplied `verified`; revocation neither stored nor checked at replay/export; forged linked digests pass without external anchor; W04 `accuracy` is an arbitrary scalar; no trained weight digest; tenant ACL; key rotation; rate limit; queued-job concurrency/leases/cancellation; reproducible transitive lock; DB rollback; raw dataset commitment; live accessibility; rate/latency and resource DoS. HTTPS/private host not independently inspected. A `GITHUB_SHA` environment value written to W03 chain is not cryptographic proof of running code.

## E1–E14 disposition (no epic marked DONE)
| Epic | Status | Evidence / blocking gate |
|---|---|---|
| E1 multi-dataset API/browser & split view | BLOCKED | no W04 integrated UI |
| E2 provenance explorer/export/import | PARTIAL | W03 digest DAG, W04 event hash, no explorer/authenticated import |
| E3 cancellation/resume/roles/audit | BLOCKED | no job worker/ACL tests |
| E4 Docker/cloud/CI/locked export | BLOCKED | only earlier W03 manual CI |
| E5 P25 rights contract | PARTIAL | `rights_v1.py` local booleans, no true license attestor |
| E6 independent baseline/falsification | PARTIAL | BA oracle and local negative tests, W03 historical 0.5; no fresh registered replay |
| E7 typed persistence/schema rights lifecycle | PARTIAL | W03 immutable SQLite only, no migration/revocation |
| E8 distributed fault-tolerant execution | BLOCKED | no lease/job/queue/recovery |
| E9 accessible browser/API/SDK | BLOCKED | W03 API source; no W04 UI/SDK/accessibility |
| E10 performance/scale | BLOCKED | no measured capacity tests |
| E11 adversarial threat QA | PARTIAL | malformed/tamper tests; forged hash/tenant/revocation unsolved |
| E12 exact-head hosted validation/recovery | PARTIAL | older W03 CI only, no exact W04 current-head run |
| E13 integrated P1+P13+P25 | PARTIAL | isolated mock event only; **not true cross-system execution** |
| E14 reviewer artifacts/runbook | PARTIAL | private GA/docs and local log; no production walkthrough |

## Referee recommendation and experiment
**MAJOR REVISION**: (1) no behavioral/neuroscience construct validated; (2) participant-only split ignores site/time dependence; (3) score reflects synthetic task and possible inspection bias; (4) three related folds give invalid naive confidence intervals; (5) signed provenance absent; (6) P25 bool grant can be forged; (7) model-score input arbitrary; (8) robustness across realistic imbalance and independent trials absent. See [GA7 peer-review objections and falsification matrix](ga/GA7_INDEPENDENT_SKEPTICAL_REFEREE_REPORT.md). Require precommitted synthetic multi-seed factorial tests, two independent metric implementations, sealed external/held-site validation if ever lawfully available, rights/tenant negatives and exact private CI before reconsidering.

## References and audit limits
Full targeted 13-source primary-methods/standards bibliography [GA1](ga/GA1_LITERATURE_EVIDENCE.md); key direct publisher records include [Cawley & Talbot](https://www.jmlr.org/papers/v11/cawley10a.html), [Varma & Simon](https://doi.org/10.1186/1471-2105-7-91), [Varoquaux et al.](https://doi.org/10.1016/j.neuroimage.2016.10.038), [Roberts et al.](https://doi.org/10.1111/ecog.02881), [Kapoor & Narayanan](https://doi.org/10.1016/j.patter.2023.100804), [W3C PROV-O](https://www.w3.org/TR/prov-o/). This assistant is not an unaffiliated third-party auditor and does not certify scientific generalization, regulatory compliance, institutional rights or public release readiness.
