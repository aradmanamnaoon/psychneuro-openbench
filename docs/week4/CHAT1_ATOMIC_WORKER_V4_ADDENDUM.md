# W04 Chat 1 — private atomic-worker continuation (2026-10-19)

**Scope:** additive backend implementation on the existing verified *private* W03-descended W04 branch. This does **not** merge, publish, deploy, contact people, enable real data, dispatch hosted runners, or finish the November 5–11 mission.

**Repository:** `aradmanamnaoon/psychneuro-openbench` PRIVATE. **New branch:** `review/w04-chat1-atomic-worker-20261019`, based exactly on `review/w04-chat1-independent-receipt-20261019` commit `a020f0487859121d748cfbee63464972a21c9df0`. That branch has existing P25 v2 policy+SQLite ledger, v2 queue, and independent P13/P25 v3 receipt. W03 integration ancestors and PRs #13/#14 remain unmodified. New source/test commits through `cd0f5d8c94a04bb2cfb8591ba17c15f615410def` (before this addendum); confirm the live branch HEAD when reviewing subsequent documentation commits.

## Actual changes and dependency graph

```
original invented synthetic W03 registry
     |
     v
P25 PolicyStore -> short HMAC permit -> v4 atomic immutable request + v2 queue
     |                                      |
     +-> v4 W03 load_dataset preflight --------+
              | source digest must equal APPROVED P25 source_sha256
              v
         W03 ExperimentRequest (strict) -> W03 execute/GroupKFold nested CV
              | outputs held in RAM only (custom RunStore-compatible sink)
              v
         P13 verify_record (v3 independent DAG verifier)
              |
              v
ONE SQLite BEGIN IMMEDIATE: verified P25 policy revision/source/retention,
                    v2 job state/subject/lease/fence, immutable P13 receipt,
                    durable v4 artifact + v2 job SUCCEEDED + audit event
              |
              v
private ACL read -> fresh P25 READ permit -> same-transaction integrity
             + revocation/policy-drift verification -> v3 report
```

- `src/psychneuro/w04/private_worker_v4.py`: strict `Request` (`w04-worker-request-4`), `InMemorySink`, actual W03 preflight source digest, `AtomicWorker` with transactional request enqueue, due discovery, claim/retry/lease-fenced promotion and authorization-checked receipt read. It connects the **actual** `psychneuro.w03.service.execute` by default rather than injecting a metric. Its only on-disk scientific output is immutable aggregate v4 artifacts, not a raw participant dataset. The optional injected runner/preflight exist for deliberate isolated test doubles.
- `tests/test_w04_atomic_worker_v4_contract.py`: explicitly labeled local **test-double** policy/queue/W03 fixture and nine isolated SQLite contract tests. It must not be counted as a real P1 model-run test. The monkeypatch fixture scopes all fake modules to its test lifetime rather than contaminating other suite modules.
- `tests/test_w04_worker_v4_real_w03_integration.py`: source-authored end-to-end test requiring **actual** repository files and dependencies, registry, source digest, P25/queue and real nested grouped CV on two synthetic seeds. It uses **no supplied model metrics**. **Not executed here** because the full repository is not available in this runtime and git clone failed DNS resolution.

## DB schema, transaction and migration

Existing `p25_v2_*`, `w04_v2_jobs` and `w04_v2_audit` tables are reused, without altering their schemas. With `PolicyStore.path == QueueStore.path == AtomicWorker.database` (enforced), v4 creates:

- `w04_v4_meta(key TEXT PRIMARY KEY, version TEXT NOT NULL)` — rejects unknown `worker=4` version; fails closed.
- `w04_v4_requests(id TEXT PRIMARY KEY REFERENCES w04_v2_jobs(id), tenant, subject, payload, sha)` — strict, bounded canonical experiment request plus digest, inserted **in the same SQLite transaction** as v2 queue admission.
- `w04_v4_artifacts(id TEXT PRIMARY KEY REFERENCES w04_v2_jobs(id), tenant, subject, payload, sha)` — immutable P13/P25 v3 receipt. Exact-identity duplicates cannot overwrite changed bytes. Result insertion, `state=succeeded`, persisted-stage digest/fence and operator audit are **one SQLite transaction**.

**Migration:** back up closed SQLite DB and its *separately held* audit anchor, then initialize P25 v2, QueueStore v2, AtomicWorker v4 using the same path. No destructive v2 migrations. **Rollback:** stop the worker and v4 entrypoints; preserve v4 tables/data and never silently revert policy revocation. Older code may ignore new tables but MUST NOT read v4 receipts without policy checks. Verify `PRAGMA integrity_check` and restore a reviewed backup after a corrupt schema; the code does not implement automated schema upgrades, purge, backup encryption, retention enforcement or anchor/key custody.

## Threats and exact limits

- **Rights:** fail-closed tenant, purpose, action, retention and revocation checks before W03 data preflight, before model fitting and at same-database artifact commit. Only the original synthetic W03 registry is permitted. Human/clinical and public redistribution sources stay disabled. Apache-2.0 **code** license is not a dataset license. An operator-supplied `attestation_ref` does not prove legal authorization or human consent.
- **Concurrent transitions:** `BEGIN IMMEDIATE` and `fence` exclude concurrent cancellation, revocation, duplicate worker completion or stale lease from **publishing an artifact**. Claim/lease expires after up to 300 seconds, and no heartbeat is provided by the synchronous worker. Long fitting can be recomputed on retry; it is **not checkpointed mid-fit**. Cancel does not terminate CPU fitting immediately; it prevents durable publication. An expired/stale worker may continue consuming CPU but cannot commit results.
- **Persistence:** no partial durable artifact if snapshot / receipt / policy / fence fails. Queue source remains immutable after submission and checksum checked before fit. Test doubles demonstrate rollback/denial; actual v2/real W03 replay is pending and may uncover interface or environmental issues.
- **Authenticity:** hash-digested P13 graphs and receipts plus P25's short HMAC *permit* are NOT independently signed report receipts. An attacker owning keys/DB and trusted-root file can falsify history. Signing/key rotation, authenticated attestor, independent permanent anchor and full ACL/penetration test remain **BLOCKED**.
- **Authorization:** worker constructor and `due()` are trusted operator-only internal Python interfaces. There is **no privileged unauthenticated HTTP route**. Caller authentication and secret management are external prerequisites. Read is reauthorized even after success. No raw human dataset ingestion path.
- **Scientific:** true model fitting must be witnessed from actual W03 `execute`; fake W03 test paths are strictly marked. Fold-level standard errors are not independent participant-level uncertainty. Do not select hyperparameters or report favorable results using the sealed holdout.

## Reproducible commands and observed evidence

Observed in the isolated local patch (Python 3.13.5, Linux x86_64; pytest 9.0.2, Pydantic 2.13.5, numpy 2.3.5, scikit-learn 1.8.0, FastAPI 0.128.2, httpx 0.28.1):

```bash
PYTHONPATH=/mnt/data/w04_chat1_patch/src python -m pytest -q \
  /mnt/data/w04_chat1_patch/tests/test_w04_receipt_v3.py \
  /mnt/data/w04_chat1_patch/tests/test_w04_receipt_guard_v3.py \
  /mnt/data/w04_chat1_patch/tests/test_w04_atomic_worker_v4_contract.py
# 36 passed in 0.35 seconds (includes 9 v4 mocked-integration tests)
python -m compileall -q /mnt/data/w04_chat1_patch/src /mnt/data/w04_chat1_patch/tests
# exit 0
python -m pip check
# exit 1: unrelated installed moviepy 2.2.1 requires pillow<12 but pillow=12.3.0
```

The local full-repo real model tests (new test file), Ruff, strict mypy, 3.11/3.12 matrix, Docker, browser E2E, representative performance, and exact-head GitHub CI are **NOT RUN**. Historical W03 [run 39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934) tested W03 SHA `4eeb17845dac7641b75d9a8164f125db6c213659`, NOT this v4 source. No fabricated W04 fitted scores, clinical subjects, human datasets, datasets exports or scientific significance.

SHA-256 exact local source bytes:

| File | SHA256 |
|---|---|
| `private_worker_v4.py` | `919434d07ae7e5841274fd03560d13114a1c5ff75bfd34fcfeebdc90f4b05863` |
| `test_w04_atomic_worker_v4_contract.py` | `1ca46884c66b0580d9da520c91e86452dd5de4c40d3c28a2c060ea7fd54499f1` |
| `test_w04_worker_v4_real_w03_integration.py` | `3c0266787eee94125fd50c2a1a58723561dc5e445eb72d6917b87a52b88f1c40` |

The previously committed receipt and guard v3 remain unchanged. File blobs were independently fetched back from GitHub and compared byte-for-byte to the transferred local code.

## Chat 2 and independent reviewer priorities

1. Run full *real* checked-out repository tests, especially `tests/test_w04_worker_v4_real_w03_integration.py`; debug any true W03 API/strict typing mismatches on a fresh additive branch and record SHA of every fix. Run Ruff, strict mypy, Python 3.11/3.12 and actual fixture checksum/replay from tested SHA; no older-run shortcuts.
2. Provide *real* worker process/service lifecycle and carefully authenticated internal enqueue/read endpoints; never expose trusted worker IDs or `policy.install` as privileged browser routes. This operator-only class is not a deployable public service.
3. Demonstrate 2-process claim/lease expiry, revocation during real fitting, cancel then authorized resume, and durable reproducibility after crash. Show all failure logs and use stage-bound retraining; do not promise mid-fit resume.
4. Review source/hash truth: current preflight repeats generation before the actual W03 call; check actual registry source identity. Require independently checked steward attestation and externally controlled rights-to-source mapping before accepting any human dataset.
5. Add migration/rollback and external audit-root/key-management artifacts, a real signing policy only after key custodianship approval, and a browser/accessibility/role walkthrough. No human/clinical or public exports.
6. Coordinate with concurrent Chat 2/Chat 3 branches through separate PR review; **do not merge or rewrite unreviewed histories**. No hosted private CI spend without no-cost confirmation or authorization.

## Requirement matrix / release

| E | Status | What was actually gained / remaining gate |
|---|---|---|
| E2 P13 export/import | PARTIAL | Versioned v3 portable receipt + v4 atomic aggregate artifact storage and live reauthorization; full real P13 import/graph UI untested |
| E3 jobs and permission | PARTIAL | v4 real-worker adapter + v2 fenced cancel/retry hooks with isolated tests; real mid-fit and resume equivalence untested |
| E5 P25 rights | PARTIAL | Inherited v2 strict HMAC permit and DB ledger integrated before preflight/fit/publish/read; no legal attestation or audited key service |
| E6 scientific oracle/negative | PARTIAL | Historical W03 and 36 isolated tests, no new verified W03 model-run metrics |
| E7 durable schema | PARTIAL | Transactional v4 immutable requests/artifacts, version check, SHA/revocation; actual migration and recover proof outstanding |
| E8 concurrent durable queue | PARTIAL | End-to-end atomic queue/artifact code, local 15-thread duplicate-key test, fenced cancellation and recovery using doubles; actual v2 concurrent E2E not run |
| E11 adversarial security | PARTIAL | Tenant, replay, hash/source corruption, cancel, revocation, stale lease tests; no real IAM, signer or independent review |
| E13 P1/P13/P25 actual flow | PARTIAL | Actual W03 import path and 2-seed full-repo test **authored**, not run; no fitted result claimed |

**Decision: NO-GO.** Preserve the original single W04 Career card dated 2026-11-05, Status In Progress, `Done=false`; Academy read-only, existing reminders and bounded learner hours unchanged.