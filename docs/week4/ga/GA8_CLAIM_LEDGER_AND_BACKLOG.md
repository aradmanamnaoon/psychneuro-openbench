# GA8 — verifiable claim, approvals and next-month ranked ledger (2026-10-19)
No public launch, new journal submission, scholarship application, professor email, software adoption study or recommendation was performed in Chat 3. All drafts require review before use.

| Claimed achievement | Code or first-party evidence | Permissible status |
|---|---|---|
| W03 grouped nested benchmark/API/vault implementation | [Private W03 PR 13](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/13) | CODED, earlier exact-SHA CI report; unmerged |
| W03 test and score statements | [Actions #39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934) on `4eeb1784...`; W03 archived QA report | HISTORICAL EVIDENCE only; 349 pytest/Python-version according to archived report; two BA =0.5 are synthetic |
| W04 original rights/split/digest slice | [Private W04 PR 14](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/14), initial head `a9c84cba...` | CODED, not independently hosted-tested |
| W04 independent schema/size/seed/pinned-hash hardening | `review/w04-independent-audit-20261019` new commits, `tests/test_w04_interop.py` | CODED; targeted sandbox prototype passed 17 tests; exact GitHub head hosted CI pending |
| Verified public dataset redistribution permission | none; W03 license `not-separately-specified` | BLOCKED |
| True P1+P13+P25 integrated scientific execution | separate W03 and W04 unmerged branches | BLOCKED |
| Signed immutable provenance, user/tenant access, revoked export | no trusted service/ledger/revocation store | BLOCKED |
| Public accessible UI / durable worker / Docker+private host evidence | no live URL/CI/logs | BLOCKED |
| Scholarly literature appraisal/protocol | GA1, GA2 author-drafted, linked primary sources | PRIVATE DRAFTS, not publications |
| Upstream skrub contribution | [issue #2340](https://github.com/skrub-data/skrub/issues/2340), previously user-opened, no maintainer review | OPEN PROPOSAL; no accepted upstream PR |
| Academic applications, research collaboration or award | no recorded relevant current application/offer | NO VERIFIED ACTIVITY |
| Prospective professional proof / video assets | GA5/GA6 user-approval-only drafts | NOT PUBLISHED |

## 30-day engineering/research backlog — rank by risk
P0 (next 7 days): confirm other two Chat 1/2 handoffs if later written; compare exact SHA and integrate source without unsafe overwrites; verify all Python tests at merged review-base; correct independent patch if regression discovered.
P0: resolve dataset generator/export rights and who controls explicit source/consent license grants. Reject `verified=True` from untrusted requesters. No human data pending authorization.
P0: pin a source/digest in a separately authenticated registry and deny coerced rehashes/reimports; design revocation semantics with no cached authorization bypass.
P1 (days 8–14): create operator-scoped token/tenant model and test unauthorized read/write/secondary tenant; cap resources and request lifetime.
P1: validate W03 source and W04 interop with same seed/input; run positive, denied license, revoked rights, tamper, corrupt sidecar and duplicate idempotent requests.
P1 (days 15–21): durable job queue, cancellation, resumability and lease-expiry tests; migrations/rollback with isolated SQLite fixture; artifact schema version compatibility.
P1: private accessible browser workflow, keyboard/focus screen-reader manual test and documented API positive/negative user journeys.
P2 (days 22–30): pinned lock, Python version matrix, exact commit hosted Actions, memory/latency benchmarks with measured caps, recovery drills.
P2: independent held-site/simulated-confounding robustness study, effect-vs-dummy model checks, paper protocol peer review, upstream current API/doc build after maintainer/user approvals.

## Reviewer decisions
- **Required before private merge:** owner approves exact comparison, all branch-matrix CI and rights/authorization tests pass.
- **Required before public hosting/repo publication:** explicit separate owner authorization, rights/license review, security privacy and accessibility pass.
- **Required before human data:** ethical/consent/data-processing source sign-off per dataset.
- **Required before external skrub PR:** scope accepted by maintainers plus explicit owner approval.
- **Required before manuscript/preprint/outreach:** separately granted owner approval and relevant human-authored review.
- **Academy:** untouched; 40 h/week, <=10 total focused h/day, R-course reminder and optional three original videos separate; no claim lessons completed.

**Current recommendation:** NO-GO for merge, release, public scientific assertion or manuscript submission. Approval-ready drafts exist; scientific/rights/security gates remain blocked.

## Updated claim ledger — 2026-10-19 Chat3 continuation (supersedes older rows above where they conflict)

- **True integrated P1/P13/P25 synthetic worker is CODED and LOCALLY TESTED in a previous exact-source worker slice**: genuine W03 grouped model fitting with P25 policy, fenced SQLite jobs and P13 receipt; 66 prior worker tests passed on a historical exact-source subset. Earlier row calling all three systems `BLOCKED` reflects an older split-branch snapshot and is superseded. Full exact-current-head hosted integration remains **UNVERIFIED**, not GO.
- **Real offline OS SIGKILL after fitted model / before publication:** new `tests/test_w04_sigkill_process_restart_v6.py`, committed, test **NOT YET EXECUTED**. It does not claim checkpointed training.
- **SQLite online backup/restore and restored payload tamper regression:** `tests/test_w04_sqlite_backup_restore_v6.py`, committed, test **NOT YET EXECUTED**.
- **Single-host concurrent independent worker claim fencing:** `tests/test_w04_concurrent_worker_race_v6.py`, committed, test **NOT YET EXECUTED**.
- **Typed browser science + client safety tests:** reconciled latest Chat2 source and test files exactly by Git object SHA; historical Chat2 isolated 9 tests passed, but the new integrated branch has not passed hosted CI.
- **Private PR branch divergence:** latest Chat2 base integrated via two-parent review-branch merge after checking all five changed files; GitHub says the private draft PR is now mergeable and behind by 0. This is not an approval to merge.
- **CI:** private Python3.11/3.12 and TypeScript Actions jobs were queued as of latest check, no observed current-head success. Do not add separate historical test counts or count unrun tests as passed.
- **Release decision:** NO-GO until externally authenticated provenance, independent data-rights authority, exact-HEAD hosted/OS-kill/recovery and full security/clinical/a11y reviews. No human data, release, deployment, academic submission, outreach or payments.
- **Authoritative current addendum:** [CHAT3_CONTINUED_IMPLEMENTATION_AND_BLOCKERS_20261019.md](../CHAT3_CONTINUED_IMPLEMENTATION_AND_BLOCKERS_20261019.md).
