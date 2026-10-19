# W04 independent release review packet — reviewer-only, not a signed approval

**Status:** PRIVATE / DRAFT / **NO-GO**. This is a checklist for people who are genuinely independent of the implementation. AI-generated audits, tests, checksum matches or fabricated signoffs cannot substitute for the listed reviewers. Do not publish this packet or elevate W04 status without the required evidence.

## 1. Exact immutable review subject

- Repository: `aradmanamnaoon/psychneuro-openbench` (private)
- Pull request: [#22](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/22)
- Review the live PR head SHA and the exact workflow run/job logs. Do **not** sign an earlier SHA when source or dependencies changed.
- Systems: P1 grouped synthetic evaluation, P13 provenance receipts/DAG, P25 policy and rights + W04 fenced model worker.
- Input policy: internally generated fictitious participants only; no external human or third-party data.
- Required non-public evidence: consent/license instrument where applicable, independent attestation authority, privacy/legal advice, provenance signing keys and trust roots, reproduced test logs, installed dependency inventory and SBOM, trial backup/restore and data-deletion controls.

## 2. Independent reviewer matrix

| Independent specialty | Mandatory hands-on review | Fail-closed evidence | Signoff status |
| --- | --- | --- | --- |
| Numerical/statistical methods | Rerun W03 grouped holdout, sealed-test isolation, nested CV, dummy baseline, seeds, nonparametric participant-level uncertainty; check no metric leakage or false neuroscience conclusions | Run ID, exact input SHA, split, source code SHA, installed library versions, program output and signed comments | **UNASSIGNED / UNSIGNED** |
| Data rights, ethics and privacy | Evaluate real grant authority, dataset licence scope, subject rights/consent, purpose limitation, retention, revocation, exports, provenance root custody and deletion | Signed permissions attached *independently* of the application DB; no self-asserted `verified_by` | **UNASSIGNED / UNSIGNED** |
| AppSec and dependency supply chain | Threat model, P25 tenant and subject boundaries, release-secret isolation, deserialization, SSRF, path traversal, audit-root corruption, authority escalation, dep SBOM/CVE, backups and rollback | Versioned pentest notes, reproductions, risk register with owners and remediations | **UNASSIGNED / UNSIGNED** |
| SRE/restore | Run exact-head CI, SIGKILL and concurrent fitted workers, power failure/dirty SQLite, interrupted backup + restore, corrupt schema migrations, retry exhaustion, queues under contention | Job run URL/job logs and isolated restore artifacts, measured RTO/RPO on specified infrastructure | **UNASSIGNED / UNSIGNED** |
| Accessibility | Keyboard-only, actual screen-reader workflow, focus management, validation/error recovery, mobile zoom, contrast, axe, WCAG 2.2 mapping | Human observed device/browser/assistive-tech versions and issues | **UNASSIGNED / UNSIGNED** |

## 3. Reviewer acceptance decision — all required

- [ ] Exact current PR head has hosted Python3.11 and 3.12 full pytest, Ruff, strict mypy with accessible logs.
- [ ] Exact-head TypeScript install is from committed lockfile, typecheck and all tests pass.
- [ ] Physical SIGKILL and separately relaunched worker reruns with exactly one trusted durable receipt.
- [ ] Independently witnessed multi-process/fault/lease and cancellation/revocation tests at fitted-worker boundaries.
- [ ] Verified backup/restore, at-least-one downgrade/rollback rehearsal, corruption detection and documented retention purge.
- [ ] CVE and dependency SBOM review, risk acceptance with versions and dates.
- [ ] Off-DB, independently controlled provenance trust root and authentication/signature verification; replacement of hash *and* root cannot pass.
- [ ] Real P25 rights authority verified, with source license, consent/ethics if applicable, export/purpose/retention and explicit revocation.
- [ ] Human scientific referee signs off on leakage, uncertainty, suitable baseline and prohibition on population/neuroscience claims from synthetic fixtures.
- [ ] Human security reviewer and human accessibility reviewer sign off.
- [ ] Actual nonclinical performance p95, throughput, CPU and RSS measured under specified synthetic representative load with reproducible tooling.
- [ ] Owner explicitly approves the exact merge, deployment or externally visible publication separately.

## 4. Recording reviewer evidence

Each external reviewer must provide: name/institution/relationship/conflict of interest, exact Git commit SHA, scope and environment, date and timezone, individual reproduction commands and quantitative observations, issue IDs and severity, independent evidence link, affirmative/negative decision and cryptographically verifiable or otherwise independently authenticated signoff. Keep non-public details out of a public CV/post. Never prefill a reviewer's signature, institution, findings, grading or acceptance.

**FAIL CLOSED:** if any checkbox is unverified, unavailable, rejected or merely claimed by the project author/model, the system stays NO-GO. A green CI icon is necessary but not sufficient; do not auto-release or mark Notion Done based on a boolean alone.
