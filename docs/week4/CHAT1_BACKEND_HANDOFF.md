# W04 Chat 1 — PRIVATE backend/scientific foundation handoff

**Prepared 2026-10-19; W04 calendar date remains 2026-11-05.** No merge, release, deployment, external invitations, real-person data or paid CI. The sole W04 Career Notion card must remain **Planned / Done unchecked** until all release gates pass. The separate Academy is read-only.

## Verified source and decision record

- Private repo: https://github.com/aradmanamnaoon/psychneuro-openbench ; GitHub connector confirmed `visibility=private` and branch push access.
- New additive review branch: `review/w04-chat1-durable-backend-20261019`, created from integrated W04 `7c0ffd2b6779b22dbdebfc443f9827e9ba502536`; **the final branch HEAD is the GitHub PR head**, not a SHA embedded in this mutable document.
- Original W03 head `8e511988e1feecce434eb7a5c109df5ebaf4ef90` is the direct ancestor of W04 `7c0ffd…`, according to an actual compare (ahead 3, behind 0). PR #13 (W03) and #14 (isolated W04 reference) remain draft/unmerged and unmodified. Source history and default branch remain untouched.
- Historical W03 CI PASS: https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934 on **exact** `4eeb17845dac7641b75d9a8164f125db6c213659` (349 tests on Python 3.11 and 3.12); this evidence **does not apply to this Chat 1 commit**.
- Prior W04 integrated patch at `7c0ffd…` has `src/psychneuro/w04/{rights,ledger,jobs,interop,api}.py`, source-only private browser UI and W03 `src/psychneuro/w03/{contracts,nested,service,store,vault}.py`. The prior W04 report explicitly states isolated tests used W03 shadows. Keep existing public-facing API disabled; **do not mistake SHA-256 for a signature**.
- Architectural decision: retain the W03 science and prior W04 modules unchanged; add namespaced v2 policy/queue, a **separate explicitly opt-in private API**, negative proof and a regression suite. Not a destructive replacement of existing rights/jobs or an assertion that the application is integrated with a worker.

## Dependency DAG / versioned interfaces

`server-side synthetic-source attestation (UNVERIFIED unless independently reviewed)` → `P25 v2 operator-installed policy + rights revision` → `HMAC-authenticated, short-lived per-action permit` → `W04 v2 tenant-scoped job admission` → `durable SQLite enqueue` → `atomic lease + fencing + stage checkpoint` → **[BLOCKED real worker binding]** → `W03 registry → grouped 3×2 nested CV / DummyClassifier → sealed holdout` → `W03 RunStore durable P13 SHA DAG` → `W04 preexisting envelope import/export/verify` → **[BLOCKED P25-anchored receipt + trusted external root]**.

New files (all additive):

| File | Contract / ownership |
| --- | --- |
| `src/psychneuro/w04/policy_v2.py` | Strict Pydantic `PolicyRecord` (`p25-policy-2`), `Permit` (`p25-permit-2`), `PolicyStore`: synthetic-only tenant and purpose/action-scoped policy, explicit attestation *reference*, SHA-256 event chain, revocation precedence, retention, HMAC-scoped permit TTL ≤60 s, revision validation. Caller, not this store, authenticates the operator and checks actual rights. |
| `src/psychneuro/w04/queue_v2.py` | Typed `Job` / `QueueStore`: tenant/owner ACL, idempotency, atomic lease/claim, worker fence, retry budget + delay, cancel/resume and stable checkpoint stage IDs. No model-fit checkpointing or automatic worker execution. |
| `src/psychneuro/w04/api_hardened.py` | Optional internal-only versioned FastAPI endpoints with server-mapped credentials. No unauthenticated privileged worker operation. No default global ASGI application. |
| `tests/test_w04_hardened_backend.py` | Corrupt/rehashed policy, revocation, forgery, schema version, scope/tenant denial, concurrent queue insertion, stale fence, crash lease expiry, retry budget, stage regression, cancellation/resume and migration failure tests. |
| `tests/test_w04_api_hardened.py` | Internal FastAPI `TestClient` role/tenant-admission, rights and cancellation tests. **Local run used a minimal W03 `ExperimentRequest` contract mirror**, not an entire live W03 stack. |
| `tests/test_w04_numeric_oracles.py` | Independent hand-count balanced-accuracy oracle, five fixed permutations/seeds `0,42,73,123,2026`, null majority control, undefined fold and invalid-input sentinels. Local `psychneuro.metrics` is byte-identical to W03 existing Git blob `6861330f071e9a3b71500e51f3dbb7f448868ed8`. These are metric unit tests, **NOT new trained-model benchmark results**. |

Existing W03 `ExperimentRequest` still requires `(generator_seed=73, split_seed=42, n_participants=36, trials_per_participant=12)` by default and frozen allowlist `('difficulty','stimulus_condition')`; `nested_grouped_benchmark` GroupKFold outer=3 inner=2 and DummyClassifier are source-verified and unchanged. Existing W03 vault `source→split→model→benchmark` is verified on-read by `RunStore`, but hashing authenticates no signer; model weights and personally sourced rights are unverified.

## SQL and state machine

`p25_v2_meta(k,v)`, `p25_v2_policy(tenant,dataset,revision,payload,sha)`, `p25_v2_events(seq,parent,payload,sha)`; `w04_v2_meta`, `w04_v2_jobs`, `w04_v2_audit`. v2 initializers use SQLite transaction/`BEGIN IMMEDIATE`, preserve legacy tables, and reject unknown version rows. Policy canonical JSON + SHA covers revision; chain records policy SHA, and snapshot-to-event linkage catches policy edits even when the attacker recomputes the row checksum. An attacker who changes *all* database contents and the chain can still forge the root: **external, independently maintained root required**; none has been established. HMAC authenticates a *short-lived internal permit* only and requires a genuinely secret out-of-band key; it does **not sign provenance DAG reports**.

Job contract is `queued → running → succeeded|failed|cancel_requested`; expired lease can be reclaimed with monotonically increasing `fence`. Success requires a previously validated persisted checkpoint and matching artifact hash. Cancel invalidates the current worker; cancelled work can resume as `queued` only after fresh policy permit. Retries are bounded with backoff. Checkpoints are **validated boundary metadata, not persisted model state or a mid-fit resume**. Multi-process durable workers, actual compute scheduling and backpressure have not been tested.

Do not trust a caller-supplied `tenant`, `subject`, dataset attestation, verified-by string or purported data licence. The v2 API maps long random internal tokens server-side and refuses foreign subjects; it creates jobs but **does not start model execution**. Keep it internal/private and disable any privileged worker endpoints in a browser.

## Local execution evidence — scoped, not hosted CI

Executed in an isolated mounted sandbox with generated synthetic metadata only:

```sh
cd /mnt/data/w04_chat1
PYTHONPATH=src python -m pytest -q tests/test_w04_hardened_backend.py tests/test_w04_api_hardened.py tests/test_w04_numeric_oracles.py
# 29 passed in 0.86s (last observed), Python 3.13.5, pytest 9.0.2
python -m compileall -q src tests
# exit 0
python -m pip check
# FAILED: unrelated environment: moviepy 2.2.1 requires pillow<12, installed pillow 12.3
python -m ruff --version
# NOT INSTALLED, NOT RUN
python -m mypy --version
# NOT INSTALLED, NOT RUN
```

Other inspected installed versions: SQLite 3.46.1; Pydantic 2.13.5; FastAPI 0.128.2; scikit-learn 1.8.0. A local isolated single-process synthetic smoke once measured 100 policy admissions and 100 SQLite enqueues, with ledger verification around **3.7 ms**; this result is exploratory, on a prior policy revision, NOT a cross-version benchmark. A previous W04 patch reports 13 tests against fake W03 stand-ins; do not merge that number with 29. No exact-code W04 hosted CI log, full-repo pytest, Ruff, mypy, actual W03 model fitting, end-to-end report export or Docker launch has been observed; mark those **NOT RUN**.

SHA-256 of final source and fixture files should be calculated from the exact PR HEAD checked out by Chat 2. Local bytes may differ by one trailing newline from GitHub Contents API normalization. Branch commit SHA and source Git blob hashes are retrievable from GitHub; avoid claiming that an earlier local suite passed a later commit's complete environment.

## Threat model, correctness and red lines

- Legitimate users are server-mapped internal roles; attackers may submit malformed inputs, tenant/subject guesses, forged/replayed permits, huge JSON, cross-tenant job IDs, interrupted jobs and stale worker results. Model/data provenance claims may be altered. File/SQLite administrative adversaries can rewrite hash chains or copy an older DB if there is no external trusted root.
- This system protects a **fictional synthetic generator only**. A textual `attestation_ref` is not independent permission or proof of data ownership. No human/clinical sources are enabled; Apache-2.0 source license is not a dataset license. Consent fields for human studies are not implemented; real people require separate legal/ethical evaluation and affirmative evidence.
- Performed adversarial sentinels cover malformed SHA, wrong purpose/action, unknown dataset, cancelled/revoked permit, cross-tenant ownership, stale worker completion, rollback on invalid transition, schema mismatch and recomputed forged snapshot SHA. Missing independent penetration tests, corrupt-DB whole history substitution and resource-exhaustion assessment remain.
- Fold scores are correlated by group structure; do not compute a conventional independent-fold confidence interval. Hyperparameter selection can bias in-sample comparisons; use prespecified holdout, selection logs and replicated synthetic seeds, then design participant-level uncertainty only when scientifically justified. Artificial unit-test oracle scores are not research results.

## Rollout/migration/rollback

1. Review branch diff against `review/w04-p25-private-integration-20261019`; ensure the repo stays PRIVATE and existing legacy v1 modules/test contracts are unchanged.
2. For a disposable private database, both v2 stores initialize their own namespace and version rows within a SQLite write transaction; neither migrates/drops historical W03 runs. Back up the SQLite DB **out of process** before a production-oriented migration; fail closed on unsupported version or corrupt snapshot. No production rollback procedure executed.
3. For rollback, stop writers/workers, discard only a newly created disposable test DB or restore the externally verified pre-migration backup. Do not casually drop version tables or overwrite an active run store; first test recovery and provenance indexes on a copy.
4. Never deploy using a hardcoded test HMAC secret, public CORS, synthetic role headers, fake dataset grants or exposed default app. Prefer operator-held rotated secrets and trusted TLS/private network boundary.

## Chat 2 priority execution (in order)

1. **Integrate real W03 P1 and P13:** gate authorizer before calling `w03.service.execute`, bind policy source hash to actual registry-generated source bytes before W03 `RunStore.put`, verify after persisted DAG/root; implement atomic/versioned P25 run/report linkage and immutable supported envelope import/export. Do not accept user-supplied numerical metrics. Use only original synthetic fixture.
2. **Make job engine execute:** add worker that checks a fresh permit *at claim time*, rechecks before commit/result publication, persists stage checkpoint artifact hashes, validates fence on every mutation and recovers crashed `running` jobs. Compare interrupted vs uninterrupted exact P1 synthetic result/roots and test cancellation mid-stage (never promise mid-estimator resume).
3. Test cross-process claims (not merely threads), idempotency under duplicate delivery, cross-tenant read/search, stale permit during fit, retry-exhaustion on expired lease, DB migration/rollback and tampering against both mutable state and audit chain. Introduce bounded ingestion, queue depth, quotas and timing budget.
4. Review/extend P13 import verification: require right run + report relationships and independently held roots; do not add fake signature. Have operator establish signing key custody/rotation/threat boundary first if signing is needed.
5. Run entire existing repo pytest and strict Ruff/mypy with actually installed dependencies, plus isolated W03+W04 integrated model test. Use manual **free/permitted** CI only after verifying runner spending policy; record exact PR commit SHA + log URLs. No claims for earlier SHA.
6. Chat 3 is independent skeptical reviewer: fuzz race/state/rights, verify science/lineage, test UI keyboard/browser/access controls and recommend GO/NO-GO. Do not merge/publish/call it passed before explicit independent approval.

## Requirement disposition at Chat 1 handoff

| Epic | State | Evidence / blocker |
| --- | --- | --- |
| E2 provenance graph import/export | **PARTIAL** | Existing W03 DAG and old W04 envelope source verified; v2 P25 receipt / root signing / real import roundtrip NOT RUN. |
| E3 cancellation/checkpoint/permissions/trace | **PARTIAL** | Durable v2 queue, fencing/cancellation/role API tests pass isolated; no real P1 worker. |
| E5 P25 rights policy | **PARTIAL** | Typed purpose/action/tenant synthetic-only policy, revocation, HMAC permit, tests; attestation must be independently verified. |
| E6 numerical/scientific falsification | **PARTIAL** | Hand-count oracle + five-seed label permutations / majority null and W03 static code inspected; not repeated model training or ablation. |
| E7 rights lifecycle/migrations | **PARTIAL** | Transactional namespaced SQLite v2, policy SHA, audit chain/corruption tests; backup/rollback real exercise and consent lifecycle absent. |
| E8 restart-safe execution | **PARTIAL** | Fencing/idempotency/retry/lease tests pass isolated; no worker process/mid-fit restart or multi-process soak. |
| E11 adversarial security | **PARTIAL** | Cross-tenant, forgery, tamper, stale-fence/permit sentinels; no independent audit/key custody/root anchor. |
| E13 actual P1/P13/P25 interoperability | **BLOCKED** | API admits jobs but cannot dispatch W03 scientific execution; integrated real registry→P1→P13→P25 verification NOT RUN. |

**Release decision: NO-GO.** Maintain Planned + Done unchecked on the single W04 Career calendar card (Nov 5, 2026). Respect 10 combined focused hours/day alongside separate Academy 40 h/week and the existing R reminder. No software-completion dependency on optional videos.