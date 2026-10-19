# CHAT1_BACKEND_HANDOFF — W04 private scientific/backend foundation

**Date:** 2026-10-19 (early work for the 2026-11-05–11 W04 mission)  
**Repository:** `aradmanamnaoon/psychneuro-openbench` — verified **PRIVATE**; do not change visibility.  
**Implementation branch:** `review/w04-chat1-independent-receipt-20261019`  
**Exact code/test commit:** `68ad1e3275629192c95734cc3c403b0174f06360` (four added Python files). This document is a subsequent documentation commit; local test claims attach to those exact **file blobs**, not a new CI run.  
**Base:** `review/w04-chat1-durable-backend-20261019`, verified source commit `c45e36633efd84e9359249f50e30c13434602b5d`; that in turn descends from W03 integrated `8e511988e1feecce434eb7a5c109df5ebaf4ef90`.  
**W03 exact historic CI:** [Actions run 39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934) tested **only** `4eeb17845dac7641b75d9a8164f125db6c213659`. No W04 exact-head hosted CI observed.

## Decision record and dependency DAG

Do not overwrite PR #13 (W03, draft) or #14 (isolated W04 rights, draft); other private W04 branches diverge. Preserve history and create only an additive private review branch. Dependency order:

`synthetic registry -> P25 policy installation/independent steward attestation -> fresh action- and tenant-scoped permit -> W03 P1 grouped/split-isolated scientific run -> W03 immutable RunStore -> P13 source/split/model/benchmark four-node graph -> independent W04 receipt verification -> P25 read/export-permit guard -> private viewer/API (Chat 2)`.

No real human datasets are enabled; the repository's Apache-2.0 **code** licence is not a dataset licence. An attestation string is not itself independent proof. Public redistribution is DENIED.

## Actual package changes

| File | Role | Git blob SHA / bytes |
| --- | --- | --- |
| `src/psychneuro/w04/receipt_v3.py` | Independent four-node W03 P13 verifier, source/split/model/result relationship checks, bounded aggregate-only `w04-p13-p25-receipt-3` | `fb1dbbaad921d794f4081ce15890585f55dd7e8c` / 8184 |
| `src/psychneuro/w04/receipt_guard_v3.py` | Fail-closed permissioned export/import facade; live P25 permit validation before and after graph traversal, no browser routes | `c2099cc8ee4378556b004e35283886e52d5a0665` / 2740 |
| `tests/test_w04_receipt_v3.py` | Five fixture seeds, 14 graph/metric mutations, root/tenant/replay adversarial checks, independent arithmetic oracle | `68dd05b6d7ec563dc0445e8e4d5654a5da1eec81` / 6250 |
| `tests/test_w04_receipt_guard_v3.py` | Test-only P25 validator double for scope, revocation timing, policy revision and identity checks | `680dd651f7d65ca59b654c4fb9e4060f9f1c1f41` / 4218 |

All four remote blob SHAs were fetched back and matched locally tested exact Git object hashes. Existing W03/W02 source, database schema and CI workflows were **not modified** by this branch.

## Versioned cross-system contract

`P13P25Receipt` fields: `schema_version=w04-p13-p25-receipt-3`, `tenant`, `dataset=w03-original-synthetic`, `purpose=internal-method-validation`, `export_scope=aggregate-internal-only`, `policy_revision`, `policy_sha256`, `run_id`, `provenance_root`, `record`, `receipt_sha256`. P13 expects precisely `source -> split -> model -> benchmark` with four SHA-256 node hashes and canonical UTF-8 JSON, matching W03's existing format. Receipt/record upper bound is 250,000 UTF-8 bytes.

`export_authorized(record, policy, permit, tenant, subject)` requires fresh `p25-permit-2` action `export_aggregate`. `import_authorized(receipt, policy, permit, tenant, subject, trusted_root)` requires `read_aggregate`, matching policy revision and live rechecks. Permit MAC remains P25's responsibility; **never accept arbitrary PermitLike objects from an untrusted caller**. Actor authentication and authorization remain server-side. A receipt never grants rights on its own.

**Critical trust limit:** SHA-256 is not a signature. A coordinated adversary could rewrite graph and receipt and all hashes; only an *independently secured* expected root detects that change. Authentication/attestation/key storage, key rotation, replay nonce/time gates and trustworthy receipt signatures remain BLOCKED. `trusted_root` is caller-supplied: do not take it from the same untrusted archive.

## Locally executed tests — scoped evidence

Commands run in a clean patch directory with precisely the four listed files:

```bash
PYTHONPATH=/mnt/data/w04_chat1_patch/src python -m pytest -q /mnt/data/w04_chat1_patch/tests
# 27 passed in 0.08s
python -m compileall -q /mnt/data/w04_chat1_patch/src /mnt/data/w04_chat1_patch/tests
# exit 0
python -m pip check
# FAIL: moviepy 2.2.1 requires pillow<12.0, but environment pillow=12.3.0
```

An initial pytest invocation encountered a **test harness dynamic-import/Pydantic forward-reference error** (8 failed, 15 passed); adjusted the test harness, reran the exact four files, and got **27 passed**. Tests do **not** invoke real W03 nested CV or a P25 SQLite policy store, and cannot establish whole-repository correctness. Python 3.13.5; pytest 9.0.2; Pydantic 2.13.5; NumPy 2.3.5; scikit-learn 1.8.0; FastAPI 0.128.2; httpx 0.28.1; Linux x86_64. Ruff and mypy not installed; lint/type **NOT RUN**, full-repo tests **NOT RUN**. GitHub clone blocked by sandbox DNS; the actual repository and branch were inspected through the authorized GitHub connector.

Synthetic/test-only seeds: `1,42,73,101,2026`. Independent mathematical oracle: `TPR=3/4`, `TNR=2/4`, balanced accuracy `(0.75+0.5)/2=0.625`. Always-negative null baseline `0.5` on equal class support. **These values are hand-constructed test cases, not output from a fitted model.** The fixed W03 predictor allowlist remains `difficulty, stimulus_condition`, grouped outer/inner 3/2, dummy same-fold baseline and sealed holdout; this addition does not change model code.

One-process local-only `verify_receipt` performance smoke: 500 repetitions on a synthetic fixture, observed median **0.073045 ms**, p95 **0.096596 ms**; does not measure API, SQLite concurrency, model fit, network, RSS or production traffic.

Observed SHA-256 of local files, respectively:

```
receipt_v3.py            9e4ddc032381ee6b91c0753cd935abd91f22b96bb7514a8076170754ac6dde4e
receipt_guard_v3.py      2ccdb41d385e7397d08e3bdb500a9e016649bdee0643ac90ab8148dd2c207f69
test_w04_receipt_v3.py   d6462a0a6204e9bddd1b3fe02f2b38f3c8b61e2ae12ea376d721bf804d05793f
test_w04_receipt_guard_v3.py 169d450da646a2fad0bbfc81979ef74199068dc14b386b19a8289abe5f6b9fc3
```

## Scientific oracles, threats, acceptance and budget

Threats: compromised database operator replacing hashes, stale P25 policy grants, cross-tenant reads, accidental public dataset export, malformed/cyclic/orphan P13 edges, grouped-participant leakage, post-response target leakage, duplicate worker delivery, expired leases and stale fenced completion. The isolated tests establish receipt-graph and permission-*interface* denials, not independent external-security proof. The existing `policy_v2.py` and `queue_v2.py` on the inherited base implement SQLite revisions, event chains, HMAC permits, atomic enqueue, claim/lease/fencing, bounded retries, cancel/resume and stage checkpoints; those were **not retested** by this patch against the private full repository.

Validation still needed: exact-head Python 3.11/3.12 pytest, Ruff, strict mypy, W03 registry -> real fitted metrics -> P13 RunStore -> P25 permission -> v3 receipt, two-user session ACL, SQLite corruption/rollback/migration and concurrent job recovery, immutable externally held trust root, null/ablation/multi-seed robustness and true browser E2E. Fold scores are dependent, so a naive fold-level confidence interval is not subject-level uncertainty; model selection biases naive reported maxima. Test set is for final locked evaluation once, never hyperparameter tuning.

Compute budget: use existing free local/sandbox permitted CPU for bounded synthetic fixtures and short tests; **no hosted private GitHub Actions dispatch** or paid compute without separate approval. Large multi-seed runs remain backlog; stay within the learner's existing ≤10 combined focused human hours/day and independent Academy 40h/week.

## Chat 2 priority instructions

1. Compare the diverged Chat 2 product branch with this implementation. **Do not force-push**, merge or overwrite either branch. Cherry-pick/reimplement v3 receipt and tests only after reviewing downstream interfaces and safeguarding unchanged W03 code.
2. Wire the server-side P25 policy store and fresh `export_aggregate` / `read_aggregate` permits into v3 functions; never expose `issue_receipt` directly as an unauthenticated route, do not leak MAC/secrets to the browser.
3. Execute **actual W03 registry-backed** `execute` on original synthetic with rights authorization before data processing; verify `source_sha256` against independently approved policy dataset source hash, then verify/publish the real `RunStore.get(run_id)` output. Revalidate policy at write/read boundaries and document revocation races. Do not fill metrics manually.
4. Build job-worker stage-aware execution with latest fenced claim and cancellation before any durable artifact write. A `fit_completed` boundary is not an arbitrary mid-fit checkpoint. If a cancelled worker can create a report before the queue completion CAS, isolate/quarantine the report until authorized promotion.
5. Versioned internal API/OpenAPI and browser integration must preserve tenant isolation and accessible keyboard workflows. Run hosted CI only with owner authorization; never assert it ran without exact SHA logs.
6. Add targeted test of v3 against a true W03 `RunStore` record; the synthetic hand-built graphs here prove the *format verifier*, not the scientific calculation. Confirm archival export import before externally trusting its digest.

## Release decision / E-status

| Requirement | Status | Precisely established |
| --- | --- | --- |
| E2 — P13 graph import/export and validation | PARTIAL | Real independent verifier and authenticated-adapter source; pure contract tests pass; graph explorer/actual W03 import untested |
| E3 — jobs/cancel/resume permissions | PARTIAL | Existing inherited v2 queue, new permit guard; worker fitting/replay and concurrency not rerun |
| E5 — P25 rights/CLI/API | PARTIAL | Existing v2 typed/HMAC/SQLite modules inherited; new strict receipt scopes; independent attestation absent |
| E6 — scientific proof/negative controls | PARTIAL | Arithmetic oracle, five seed graph cases, negative corruption tests; no new model evaluation |
| E7 — DB/provenance/rights lineage | PARTIAL | Existing inherited SQLite migrations and checksums; no v3 schema migration needed; whole-app rollback not tested |
| E8 — durable concurrent jobs | PARTIAL | Inherited fenced queue source, no actual combined worker execution or restored crash test this turn |
| E11 — privacy/security adversarial QA | PARTIAL | Denials for tenant, scope, revocation, stale policy, bad SHA, graph replay; no independent pen test or trust anchor |
| E13 — three-system integration | PARTIAL | Exact v3 schema + protected adapter for W03/P13/P25; real fitted E2E NOT RUN |

**NO-GO / do not merge or publish.** Neither a signed receipt nor independent security review, verified public dataset permission or W04 exact-head hosted CI has been established. This is a **tested private incremental backend slice**, not a full W04 release or complete Chat 2 product.

## Migration and rollback

No new schema tables or migrations introduced by this v3 patch. The inherited `p25_v2_meta` and `w04_v2_meta` require migration review and transaction-safe backup before future schema upgrades. Rollback v3 code by removing its additive imports; do not delete W03 SQLite records or silently downgrade policy revisions. Maintain event anchors outside the SQLite path. Do not redact failure evidence.

**Notion scope:** Update only original W04 Thursday Career page, date `2026-11-05`; leave `Done=__NO__` and do not touch Academy or add calendar days.

---

## 2026-10-19 Chat 1 continuation: atomic W03 worker v4 (additive; new evidence)

**Latest focused source+tests commits:** `97195f42244861f74397fd025646e5e0eb0fc3b4`, `173fa2e7f1ef7f6605958dc4264380aabefc9ccf`, `cd0f5d8c94a04bb2cfb8591ba17c15f615410def`. The documentation addendum commit is `ae408d9f9155ff41616e2ea4ca0e8665f5b0cd4d`; refer to the live branch HEAD for current tree. See the full [W04 v4 worker architecture, migration, security, real-run test and evidence](CHAT1_ATOMIC_WORKER_V4_ADDENDUM.md).

**Implemented:** `src/psychneuro/w04/private_worker_v4.py` and two new test files. P25 scoped authorization BEFORE original W03 dataset preflight, pre-fit registered source SHA check, actual W03 nested-CV service adapter, in-memory-only fitting reports, single-SQLite-transaction job completion/immutable aggregate receipt/rights revision/fence and read-time P25 reauthorization. Original W03 and prior W04 modules were not modified. Restart retries recompute after fit interruption; mid-fit checkpoint/resume is NOT implemented.

**Observed scoped tests only:** 38 passed (0.32s, Python 3.13.5); eleven new v4 tests use explicit W03/P25/queue doubles; `compileall` exit 0. `pip check` exit 1 due unrelated MoviePy/Pillow conflict. `tests/test_w04_worker_v4_real_w03_integration.py` is WRITTEN but **NOT RUN** against actual original source: full repository checkout unavailable in this container. Full repo pytest, Ruff, mypy, hosted CI, Docker/browser and independent attestation/signature all **NOT RUN/BLOCKED**. No fitted W04 numeric outcomes are claimed.

**Security/release:** permit HMAC authenticates only the narrow v2 permit, not a signed receipt or legal rights. The v4 worker is trusted internal Python code without public privileged endpoints; external authentication, attestation, key rotation, model-run production proof and third-party audit remain release blockers. All E2/E3/E5–E8/E11/E13 remain **PARTIAL**, W04 **NO-GO**. Keep the sole original W04 Notion card dated 2026-11-05, Done false, Academy untouched.


---

## 2026-10-19 · Chat 1 v5 adversarial scientific verifier and operator CLI

**Exact tested source/test tree head (before this handoff-only edit):** `588177909003274d1797270338e00b8e9a7cae18`. The source and tests are unchanged by this documentation-only update. **Private draft PR:** [#19](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/19). Full v5 [scoped scientific and security audit](CHAT1_V5_SCIENCE_CONTRACT_AUDIT.md) and [machine-readable observed evidence](CHAT1_V5_SCOPED_OBSERVED_EVIDENCE.json).

**New tested code and tests:** `receipt_v3.py` independently cross-checks W03's deterministic run ID against its request/source/split and compares the reported grouped outer/dummy means, final C, sealed-test metric, time-safe predictors, group/seed counts, method and actual P13 graph benchmark metadata; eight coordinated rehash attacks now fail. `tests/test_w04_synthetic_numerical_oracles_v5.py` compares mathematical balanced accuracy to real scikit-learn and GroupKFold versus row-wise KFold on five fixed, entirely fictional seeds. `worker_cli_v5.py` is an operator-only bounded one-shot worker (existing SQLite, synthetic registry, `W04_PERMIT_KEY_HEX` via environment, mode 0600 SQLite on POSIX, no privileged browser route). CLI tests use explicit doubles. No new real dataset rights are granted, no independent signer, no public endpoints.

**Observed local command:** `PYTHONPATH=src python -m pytest -q tests/test_w04_receipt_v3.py tests/test_w04_receipt_guard_v3.py tests/test_w04_atomic_worker_v4_contract.py tests/test_w04_synthetic_numerical_oracles_v5.py tests/test_w04_worker_cli_v5.py` → **61 passed in 1.10s**, Python 3.13.5. `compileall` exit 0. Initial new numerical fixture run was **5 failed / 53 passed** because labels were expanded to 576 against 96 samples; fixed and rerun. Global `pip check` **FAIL** (MoviePy/Pillow incompatibility), unrelated to this package. Ruff/mypy **NOT INSTALLED / NOT RUN**. Exact-head full W03 project pytest, true registry→fitted CV→P13→P25 SQLite result, Actions CI, Docker, browser/keyboard, production auth, and independent human reviewer **NOT RUN**.

**Byte identity:** all locally tested Python files now have exact local Git blob hashes matching the committed private GitHub blobs. An initial library-to-GitHub transfer silently omitted final newlines; this was detected and corrected before finalizing the source evidence. See JSON file SHA-256 values and commit tree.

**Reviewer/Chat2 next action:** execute the already committed `tests/test_w04_worker_v4_real_w03_integration.py` against a real private checkout, then full pytest/Ruff/mypy 3.11/3.12 and refresh precise SHA logs; the integrated test is **unexecuted**. Validate P25 operator attestation, externally anchored P13 graph and key custody, permissions and cancellation with real SQLite store, and failure-injection migration/rollback. Do not treat a coherent graph or mock receipt as observed scientific model evaluation. The signed/attested data-rights release gate remains blocked. W04 date 2026-11-05 and Done unchecked; Academy untouched. **E2/E3/E5/E6/E7/E8/E11/E13 PARTIAL; release NO-GO.**


---

## 2026-10-19 · Exact-code replay evidence supplement

Latest tested W04 source/test commit: `db3b63b72d12853bd5b9956369cdb32a8e9bb3fd`, [full scoped QA report](CHAT1_QA_REPLAY_20261019.md), [machine-readable evidence](CHAT1_QA_REPLAY_RESULTS.json). **92 targeted tests passed**, including actual fitted W03 P1→P13→P25 two synthetic seeds; Ruff pass, mypy strict 30-source pass, compileall pass, pip check pass in isolated Python 3.13.13 environment. Both genuine fitted synthetic benchmarks scored 0.50, equal to dummy 0.50: **no predictive improvement**. Earlier 61/38 test results are historical baseline only. The current SHA's entire repository test suite and hosted 3.11/3.12 CI, independent attestation, external trust root, real worker crash/restart and browser/Docker proof remain BLOCKED; no merge/release. Existing Notion date and Done unchanged.
