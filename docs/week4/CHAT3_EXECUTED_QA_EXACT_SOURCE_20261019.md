# W04 Chat 3 — executed exact-source QA delta (2026-10-19)

**Release decision: NO-GO.** This is an **internal AI-assisted private audit**, not independent third-party validation, hosted CI, human neuroscience evidence, public release approval, or manuscript acceptance. The private repo must remain private; the pull request remains draft and unmerged.

## Exact checked source and proof provenance

- Private GitHub PR: https://github.com/aradmanamnaoon/psychneuro-openbench/pull/22
- Branch: `review/w04-chat3-final-rebase-20261019`; authoritative live HEAD may advance.
- Reviewed/tested Git tree fingerprint: commit **`b3c5563f19e988173302f462df2b871fd1d97447`**.
- A second, **independent Git blob identity comparison** checked all **83/83** selected `src/**/*.py`, `tests/**/*.py`, `app.py`, `pyproject.toml`, and `data/registry.json` files. For each file the tool computed SHA-1 of `b'blob ' + str(len(raw)).encode() + bytes([0]) + raw`; all 83 matched GitHub's returned tree blob hashes. No file mismatches or missing paths.
- Subsequent branch changes were confined to the private manual CI YAML and this documentation; **the 83 audited Python files were unchanged** when the manual CI YAML was updated.
- Local platform **Python 3.13.13**, NumPy **2.3.5**, scikit-learn **1.6.1**, Pydantic **2.13.3**, FastAPI **0.148.0**, SQLite **3.46.1**, pytest **8.3.5**, mypy **1.20.2**. No claim of identical Python 3.11/3.12 runtimes.

## Observed execution (original synthetic source only)

```bash
# In the private reconstructed source tree, not GitHub-hosted Actions
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src \
python -m pytest -q -p no:cacheprovider --maxfail=1
# 400 passed, 247 warnings in 12.32s (exit 0)

# After resolving writable sandbox permissions and Ruff-safe autofixes
python -m ruff check .
# All checks passed! (exit 0)

PYTHONPATH=src python -m mypy --python-version 3.11 --no-incremental src
# Success: no issues found in 47 source files

# Exact same local Python source after lint auto-fixes
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src \
python -m pytest -q -p no:cacheprovider --maxfail=1
# 400 passed, 247 warnings in 14.26s (exit 0)
```

The 400 tests include five **atomic P13 run/provenance+P25 ACL** tests and a dotted tenant/subject **owner-collision regression**. SQLite failure injection verified transaction rollback and cross-tenant ownership protection. W04 v1/v2 artifact import intentionally remains disabled (403) until separately anchored trust and rights can be demonstrated.

Warnings: one Starlette/TestClient dependency deprecation plus scikit-learn/scipy L-BFGS-B deprecations; warnings have **not** been fixed. Local tests do not constitute hosted browser/manual screen reader, HTTP deployment, secure threat-model certification, worker kill/restart, DB migration rollback, or population inference.

The workflow `.github/workflows/w04-private-manual.yml` now uses `npm ci --prefix apps/web` and versioned lockfile instead of an ad-hoc `npm install --no-save`, plus `npm run typecheck --prefix apps/web` and `npm test --prefix apps/web`. This updated workflow **has not run on hosted GitHub Actions**; neither TypeScript nor Chromium automated browser tests were re-executed during this later audit. Screenshots supplied by earlier Chat2 are not independently verified as a11y or production evidence.

## Actual original W03 synthetic three-seed run

Executed actual `psychneuro.w03.service.execute()` against `data/registry.json` with P13 `RunStore`, generator seeds 73,74,75; split seed 42; **36 fictional participants ×12 observations = 432 per seed**. Split partitions **21 train, 7 validation, 8 sealed test**; W03 nested fitting consumes train and test indices but not the intermediate seven validation groups. No human/third-party data. `RunResult` reports `n_train_groups+n_test_groups=29`, which is **not** the dataset's total participant count and must not be presented as 29 original groups.

| Seed | Logistic outer BA | Grouped dummy outer BA | Held-out BA | Chosen C |
|---|---:|---:|---:|---:|
| 73 | 0.500 | 0.500 | 0.500 | 0.1 |
| 74 | 0.500 | 0.500 | 0.500 | 0.1 |
| 75 | 0.500 | 0.500 | 0.500 | 0.1 |

Observed registry/split/run SHA-256 hashes and four-node P13 roots, with **no empirical performance gain**, are in `benchmarks/w04_chat3_3seed_observed.json`. Manifest file byte SHA-256 at creation: `67e5a8eb29c87e869517709454c21dfcd8b267c189face8ed59052fea5cbbcdd`. Roots contain environment-dependent metadata; hash integrity is **not** cryptographic authenticity, third-party sign-off or proof of data rights. Three seeds are a small, dependence-contaminated synthetic illustration; **do not compute naive fold confidence intervals, p-values, calibration or population generalization claims**.

## W04 E1–E14, strict reviewer statuses

| Epic | Status | Evidence / hard gate still missing |
|---|---|---|
| E1 | PARTIAL | Synthetic private API/browser implementation; no multiple independently licensed real datasets |
| E2 | PARTIAL | W03/P13 DAG and receipt verification exist; signed externally held root and safe re-import missing |
| E3 | PARTIAL | P25 queue/ACL controls tested, but no production compute-worker crash/resume equivalence |
| E4 | PARTIAL | Private Docker/runbook/manual CI; no exact-head hosted Python 3.11/3.12 execution or rollback |
| E5 | PARTIAL | Synthetic-only registry and revocation; no legally trusted consent/licence external grant |
| E6 | PARTIAL | 3 independently run synthetic seed results, dummy baseline; no external scientific validity |
| E7 | PARTIAL | P13/P25 atomic run-owner tests pass; historical-record migration and backup/recovery remain unproven |
| E8 | BLOCKED | Durable real compute worker, cancellation/restart replay and sealed-holdout checkpoint semantics not validated |
| E9 | PARTIAL | Chat2 Chromium desktop/mobile screenshots & automated script source; no independently witnessed axe/manual reader |
| E10 | PARTIAL | Chat2 in-process HTTP timings exist; production/load/worker p95 and measured RSS missing |
| E11 | PARTIAL | 400 full local tests pass and injected owner failures; external adversarial security QA missing |
| E12 | BLOCKED | No exact-HEAD hosted QA, independent disaster recovery, comprehensive dependency/CVE proof |
| E13 | PARTIAL | W03/P13 + v2 user-facing selected tests; actual P25 v2 → recoverable worker → P1 → P13 full execution not independently witnessed |
| E14 | PARTIAL | All evidence docs, citations and GA files recorded, but hard gates not complete |

**0/14 engineering epics DONE**. The private scientific demo and docs do not satisfy >=90/100 plus all hard release criteria.

## GA1–GA8 research/career output dispositions

| GA | Status | Internal output and outstanding non-document requirement |
|---|---|---|
| GA1 | PARTIAL | `docs/week4/ga/GA1_LITERATURE_EVIDENCE.md`: 13 genuine methodological/policy sources, classified by design; targeted narrative, not systematic review |
| GA2 | PARTIAL | `GA2_PROTOCOL_METHODS.md`: protocol, leakage and rights design, manuscript methods; no actual clinical/participant findings |
| GA3 | PARTIAL | `GA3_UPSTREAM_REVIEW.md`: actual skrub proposal, local approach; no independently maintainers-endorsed issue, patch accepted or public upstream contribution |
| GA4 | PARTIAL | `GA4_ACADEMIC_PATHWAYS.md`: official five-pathway research/admissions evaluation; qualifications, fees and eligibility personal evidence unverified |
| GA5 | PARTIAL | `GA5_COLLABORATION_PROPOSAL_AND_UNSENT_DRAFTS.md`: proposal and unsent messages; no outreach |
| GA6 | PARTIAL | `GA6_CASE_STUDY_RUNBOOK_AND_PUBLIC_DRAFTS.md`: case study/CV/script drafts; no public posting or adoption |
| GA7 | PARTIAL | `GA7_INDEPENDENT_SKEPTICAL_REFEREE_REPORT.md`: falsification objections and next experiment; no independent human referee |
| GA8 | PARTIAL | `GA8_CLAIM_LEDGER_AND_BACKLOG.md`: public/private claim ledger and ranked backlog; release gates remain open |

## Referee objections and next experimental design

(1) Fictional predictor/response constructs have no validated neural target; (2) subject-only grouping fails to rule out site/session/time leakage; (3) 7 held-out validation groups are not used in the current W03 nested fit; (4) CV fold correlations invalidate naive uncertainty calculations; (5) choosing experiments after test-set inspection can contaminate the sealed holdout; (6) SHA-256 receipts can be coherently forged absent independent signing/root custody; (7) synthetic data rights do not grant licences for external datasets; (8) tenant and role tests do not validate worker revocation under delayed jobs; (9) absent independent scientific, accessibility, privacy and security reviews preclude deployment claims.

**Next falsification experiment:** Preregister a rights-cleared multi-site external dataset and participant/site/time hierarchical splits; freeze exact predictors/target time, nested train-only tuning, dummy/ablation and multi-seed reproducibility runs; do not touch prospective sealed evaluation until independent review and true data authority confirmed. Report clustered resampling only when its sampling assumptions hold. No human subjects are authorized in this stage.

## Reviewer decisions

- **NOW:** Keep private PR #22 as DRAFT, run exact-commit hosted manual CI only once free-runner/billing permissions have been independently confirmed, and evidence the browser accessibility test and worker revocation fault injection.
- **Before release:** Sign/externally anchor rights and provenance, verify real tenant-grade IAM and worker lease fencing, migration/rollback, CVE/SBOM and load measurement, source rights and independent human peer/security review.
- **Approvals separate:** No publicization, PR merge, deployment, journal/preprint submission, outreach, spending or human/clinical data use has occurred. Done stays unchecked on the single W04 2026-11-05 Career card; independent Academy remains untouched.
