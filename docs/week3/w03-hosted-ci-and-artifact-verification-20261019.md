# W03 P1 + P13 — exact-code private integrated verification report (2026-10-19)

**Binding mission:** [single existing W03 Career Lab mega-mission](https://app.notion.com/p/3fd977a963b2812fa746e654bf134b0f), scheduled 2026-10-29–2026-11-04. **Private draft review:** [PR #13](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/13), **unmerged**. **Exact tested implementation SHA:** [`4eeb17845dac7641b75d9a8164f125db6c213659`](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/4eeb17845dac7641b75d9a8164f125db6c213659). **Actual hosted run:** [Actions #39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934), **conclusion SUCCESS**, BOTH Python jobs green (separate logs inspected).
**No participant data, public dataset distribution, public host, external upstream PR/issue message, outbound outreach, merge, Academy update or paper submission.**

## Real hosted checks (not inferred from configuration)
| Check | GitHub quality (Python 3.11.17), job 117979562276 | GitHub quality (Python 3.12.15), job 117979562573 |
|---|---|---|
| `python -m pip install --disable-pip-version-check -e '.[dev,benchmark,w03,ui,parquet]'` | PASS | PASS |
| `python -m pip check` | PASS | PASS |
| `python -m pytest -q` | **349 passed**, **1 StarletteDeprecationWarning**, 4.87s | **349 passed**, **1 StarletteDeprecationWarning**, 6.82s |
| `python -m ruff check .` | **All checks passed** | **All checks passed** |
| `python -m mypy --python-version <matrix.version> src` | **Success: no issues in 29 source files** | **Success: no issues in 29 source files** |
| Original registered synthetic P1→P13 `ExperimentRequest → execute → RunStore → verify_serialized` **twice** | PASS; same return both invocations | PASS; same return both invocations |
| Archived artifact `w03-original-synthetic-provenance-<python>` | PASS | PASS |
| Workflow result | **success** | **success** |

**History of actual CI corrections:** [run 39227438165](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39227438165) had 349 pytest green but five Ruff failures (selection expression, import order and exception classes). [run 39227663432](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39227663432) had pytest and Ruff green but mypy typing failures. [run 39227935263](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39227935263) passed all gates on Python 3.11 while 3.12's mypy Python-3.11 target could not parse the NumPy 3.12-only `type` statement. Final run fixed the per-interpreter target; all true failed attempts remain acknowledged, including cancelled intermediate pushes.

## Observed original synthetic dataset and benchmark

CI used a registry-approved, wholly original fictional two-choice generator with **36 synthetic participant IDs ×12 fictional trials = 432 rows**, generator RNG seed **73**, participant split seed **42**, 3 outer and 2 inner grouped CV folds, logistic `C` in `{0.1, 1.0}` with deterministic 0.1 tie policy. Only `difficulty` and `stimulus_condition` are allowed pre-response features; `correct`, response, reaction time and participant ID are excluded from predictors. Preprocessing refits inside each training fold. The **21 train** and **8 held-out** participant groups are disjoint; the remaining 7 groups in the original P1 assignment form a separately reserved validation cohort, not used for model choice here.

| Independently archived aggregate result | Python 3.11 | Python 3.12 |
|---|---|---|
| Nested outer logistic mean balanced accuracy | 0.5 | 0.5 |
| Same-fold dummy-prior outer mean balanced accuracy | 0.5 | 0.5 |
| Frozen final selected regularization `C` | 0.1 | 0.1 |
| One-time sealed test balanced accuracy | 0.5 | 0.5 |
| Repeated original request on same run store | Equal `RunResult` | Equal `RunResult` |
| Deterministic source SHA-256 | `bc6f7b672193d4c4b4af13d1df25964454d3216d6e5c4b3c9c9c6099363412b8` | same |
| Deterministic split SHA-256 | `9d1dce92823468eb1019629b7c9c8f86c391d6f151fb5ed9b418d3b5377ad6c8` | same |
| Run ID | `b4a0f38b4c3302c56a1e75151813dc0bada8c1f95b45269eee9fe0914ba16844` | same |
| P13 provenance root SHA-256 | `8d7c322a7d1d17f0fb41f87c9e6f78b4d409ed1650f604e3bf70821b157981ed` | same |

**What a 0.5 means:** original completely invented task and two prespecified toy models, no detected improvement on this run. It is NOT evidence of psychological/neuroscience validity, accurate human prediction, clinically useful classification, a causal effect, scientifically calibrated confidence interval or model-significance p-value. Outer CV fold means are not 3 independent subject cohorts and must not be promoted to a population CI.

## Downloaded archive integrity, exact independent recheck
GitHub REST artifact metadata under [run #39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934/artifacts) and separately downloaded ZIP bytes were rehashed in an isolated stdlib Python environment; **ZipFile.testzip() yielded no CRC fault**, each ZIP had one `synthetic-p1-p13-proof.json`, parsed as JSON and cross-compared:
- Python 3.11 [artifact ID 12176370444](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934/artifacts/12176370444): ZIP SHA256 `2a377943721c7e43ab7a0bce483e7839471bdfedeb0f4ed80023714e852ae3f6`, JSON member SHA256 `97ac944694e09a91afe2ec96bb994819874eb712aab7deafdb2798de8e41b68c`.
- Python 3.12 [artifact ID 12176140538](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934/artifacts/12176140538): ZIP SHA256 `c9d77182a8ba83cd80f36250dead3f3f19f08450a2533af90afc547025fbc222`, JSON member SHA256 `1407828a32e3b17331da234362057ef3a24d3d8f04a77ed30c920204d581b2dd`.
- Both aggregate JSON reports have **all fields identical apart from `python_version`**. Recorded SHA paths, run ID, root and metrics match. JSON archive bytes cannot be identical because Python version is preserved, which is a useful provenance distinction.
- Artifacts expire **2026-10-26 ~09:12 UTC** unless separately archived. The local review handoff embeds exact hashes, and both private ZIPs were downloaded as audit evidence. Source code and data license policy remain separately constrained.

## Four engineering packages — current disposition
1. **P1 typed experiment manifests/group isolation — IMPLEMENTED; targeted/hosted tests VERIFIED.** [contracts.py](../../src/psychneuro/w03/contracts.py), [nested.py](../../src/psychneuro/w03/nested.py), [service.py](../../src/psychneuro/w03/service.py). Pydantic strict bounded schema, no unknown predictor fields; reject duplicated rows, crossover subjects, partial-subject omissions, out-of-bounds source and one-class folds; group-aware nested train-only selection, sealed test.
2. **P1 deterministic benchmark — IMPLEMENTED; actual full-repo integration VERIFIED for invented data.** Logistic and dummy-prior, CV seed/config, selected `C=0.1`, reported 0.5 scores. No statistically defensible human inference and no evidence for model superiority.
3. **P1 FastAPI & SQLite — IMPLEMENTED; internal TestClient contract / real registered end-to-end VERIFIED.** [api.py](../../src/psychneuro/w03/api.py), [store.py](../../src/psychneuro/w03/store.py). POST/GET/provenance, internal bearer-like token header, strict 403/404/422/409, idempotent immutable aggregate writes, four-node sidecar rows and fail-closed tampering. No production deployment, multi-user role enforcement, rate limiting, offline signed receipts or real browser.
4. **P13 SHA-256 DAG / indexed custody — IMPLEMENTED; integrity tests VERIFIED, trusted signer BLOCKED.** [vault.py](../../src/psychneuro/w03/vault.py) + [store.py](../../src/psychneuro/w03/store.py). Source→split→model specification→result graph. This is **content-integrity linkage, not a signature of trained weights or independently authenticated ownership.**

## Independent research/career strand (W03 is protocol/appraisal only)
[GA dated source/ethics/upstream memo](./w03-ga-source-and-upstream-audit-20261019.md): researched genuine methods sources:
- Cawley GC & Talbot NLC (2010), *On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation*, JMLR 11:2079–2107, [publisher](https://www.jmlr.org/papers/v11/cawley10a.html); no DOI invented. Explains selection bias.
- Varoquaux G et al. (2017), *Assessing and tuning brain decoders: Cross-validation, caveats, and guidelines*, NeuroImage 145:166–179, [DOI:10.1016/j.neuroimage.2016.10.038](https://doi.org/10.1016/j.neuroimage.2016.10.038). Reviews cross-validation and tuning caveats in brain decoders.
- Varoquaux G (2018), *Cross-validation failure: Small sample sizes lead to large error bars*, NeuroImage 180:68–77, [DOI:10.1016/j.neuroimage.2017.06.061](https://doi.org/10.1016/j.neuroimage.2017.06.061). Fold variation is not a reliable small-sample population uncertainty measure.
[skrub-data/skrub issue #2340](https://github.com/skrub-data/skrub/issues/2340) is OPEN (0 comments on 2026-10-19); [private reproducible leakage-negative test](../../tests/test_w03_upstream_reproducer.py) verified rowwise failure vs GroupKFold, but skrub gallery API/docs build/acceptance remains **NOT RUN**. No external collaboration, peer review, recognized citation, scholarship, credential, manuscript, preprint or submission claim. W05 is earliest actual manuscript section drafting.
Independent Academy (40h/week, Sunday recovery), saved R lesson progress and 3 original videos/week are **human learning/optional reminders, not artificially marked as completed**; combined human focus <=10h/day.

## Safety and release NO-GO / retained stretch backlog
- Synthetic generator metadata `license=not-separately-specified`, separate standalone generated-export public redistribution **NOT APPROVED** [issue #9](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/9); **six real OpenNeuro human datasets disabled for download/ingest**. Apache-2.0 repository code license is not a new public CSV grant.
- No signed/proof-of-person authorization for P13 (SHA alone is not secure against coherent malicious DB rewriting), external audit or immutable WORM store. File permissions, service tokens, rotation, rate limiting, stored-code attestations, sidecar migrations and multi-user auth require a production threat model. Report includes a `code_sha` field but no external cryptographic signature.
- No deployed private FastAPI/browser walkthrough, live load/latency, keyboard/screen-reader/mobile checks [issue #8](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/8); no PostgreSQL migration, task queue, production job retries, lockfile of complete transitive Python environments (venv logs are archived in Actions logs), independent scientific dataset or adequate inferential uncertainty.
- W03 **one Career calendar card remains In Progress / Done unchecked**, as the acceptance threshold >=85/100 AND all safety/rights integrity gates is **not established**. Even flawless synthetic CI is not public-release eligibility. 2026-10-29 scheduled human Academy activity has not occurred. No other calendar edits.

**Next narrow step:** finish independent production threat-model and rights review, then one separately authorized private deployment with actual accessibility/auth/load tests and attached logs. Keep PR #13 PRIVATE DRAFT/unmerged; merge/release only after explicit approvals, owner-reviewed diff and policy gates. Do not submit an upstream patch or external correspondence without approval.

## Post-verification workflow safety (2026-10-19)
After all green tests and both artifact reads, the W03 review-only workflow's temporary `push` trigger was **reverted to manual-only `workflow_dispatch`** on private commit [`c760a1c`](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/c760a1c4e72e8db355fe1f643fbddff05ad5f027). This prevents later private review-branch pushes from automatically consuming runner minutes or being mistaken for new independent verification. **The tested implementation source files remain byte-identical to the successful exact-code SHA `4eeb17845dac7641b75d9a8164f125db6c213659`; only documentation and the workflow event selector were edited afterward.** The final GitHub branch/PR HEAD is later; do not claim hosted CI executed at that post-verification head. Any additional hosted runs now require an explicit manual dispatch and review of applicable minutes/costs. No paid compute or billing status is asserted as checked.
