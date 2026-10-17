# PM-01–PM-16 consolidated gap closure and honest acceptance ledger

**Date:** 2026-10-17. **Private source-only remediation.**
This reconciles real GitHub/Notion statuses across sixteen consolidated
missions instead of recreating previously committed engineering work.
No local Python/CLI/IDE, Work, Codex, Docker, paid runner, hosted browser,
public repository change or external data/person contact was used.

## What PsychNeuro OpenBench actually is

A private, nonclinical, rights-gated, originally synthetic behavioral
machine-learning benchmarking project intended for psychology methods
students, neuroscience software researchers and reproducibility auditors.
The current frozen predictor task is fictional binary trial correctness
from pre-response stimulus condition and difficulty, with grouped
participants, training-only model selection, two transparent baselines,
held-out outcomes, seed-replicated descriptive uncertainty and provenance.
No human participant observation, clinical result, real adopted product,
public benchmark success or actual hosted app has been demonstrated.

## Evidence matrix at start of remediation

| PM | Notion state checked 2026-10-17 | Verified existing work | Unfinished gate that MUST remain explicit |
| --- | --- | --- | --- |
| [01](https://app.notion.com/p/3fa977a963b2812f982bc4fb33fbca94) | **Needs Review** | Competitive and hypothesis dossier in Notion; frozen [v0 contract](spec-v0.md) committed; private repo exists | Human scientific contract review; five proposed hypotheses are NOT measured |
| [02](https://app.notion.com/p/3fa977a963b281218ee8fba8083a07b7) | **Verified Done** | Private repo and generator/source foundations, original [commit](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/0960b8f58dd2065ec4da19538177c8e0b657d9cb) | Preserve; old pass is not a PM-16 full pipeline pass |
| [03](https://app.notion.com/p/3fa977a963b2813583a9e497e2ef0519) | **Verified Done** | Real historical [hosted generator QA](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38864568384) | Preserve original exact-run evidence |
| [04](https://app.notion.com/p/3fa977a963b28110b77efdf6e6f1f78a) | **Verified Done** | Real historical [rights/schema QA](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677) | Preserve historical source/rights and synthetic fallback |
| [05](https://app.notion.com/p/3fa977a963b281079280f6cc9d51fee6) | **Blocked** | Validated CSV/Parquet/synthetic source adapters, rights manifests | No hosted source/current data-path test proof |
| [06](https://app.notion.com/p/3fa977a963b281708893fb1fc33d05ea) | **Blocked** | Synthetic data-quality test specifications, pilot exploration and card | No genuine synthetic pilot artifacts with current SHA |
| [07](https://app.notion.com/p/3fa977a963b281adbe67c0013d3b635f) | **Blocked** | Group-safe split algorithms and intentional negative fixture tests | No current hosted execution and audit of group partitions |
| [08](https://app.notion.com/p/3fa977a963b2815584e0c0691d47b685) | **Blocked** | Frozen dummy prior/logistic baselines, binary metric definitions, runner | No actual current-commit ML scores or CI logs |
| [09](https://app.notion.com/p/3fa977a963b281f8b05dccf23de8ecf7) | **Blocked** | Locked JSON configuration, integration and model cards | No current hosted integration, typing, lint and acceptance |
| [10](https://app.notion.com/p/3fa977a963b2815bb650e5e6dac5b40e) | **Blocked** | Seed-repeat pipeline, nominal 5-eligible-repeat CI, guarded slices | No current complete, actually generated 5-repeat report |
| [11](https://app.notion.com/p/3fa977a963b28141a56fe1ede9af967a) | **Blocked** | Report validation, charts, JSON/Markdown and source manifest | No current real artifact checksum/plot/browser verification |
| [12](https://app.notion.com/p/3fa977a963b2810bbc64c5f79652fa23) | **Blocked** | Fixed synthetic-only UI controls and AppTest specifications | No actual browser / current SHA smoke run |
| [13](https://app.notion.com/p/3fa977a963b28124bfb6d37ec767de07) | **Blocked** | Opt-in bounded original-synthetic model runner and interval plots | No real hosted model run, in-app download or CI proof |
| [14](https://app.notion.com/p/3fa977a963b281b0ae07f0283f17de72) | **Blocked** | Tutorial, static accessible data tables, privacy-safe errors, opt-in profiler | No keyboard/screen-reader/zoom browser test or actual memory/CPU measurement |
| [15](https://app.notion.com/p/3fa977a963b28149af2bd10610db99fe) | **Blocked** | Candidate free/private Streamlit host pins/config/runbook and preflight tests | No full dependency lock/vulnerability scan, approved hosted CI, deployment/URL, viewer/privacy QA |
| [16](https://app.notion.com/p/3fa977a963b281c3b1e2f709f6cde1be) | **Blocked** | Reproducibility guide, FAQ, use cases, private CONTRIBUTING/templates and real issue #7 | No verified hosted replay or owner-approved default-branch template activation |

## New private source changes in this reconciliation

1. **Report protocol authenticity boundary improved:** source
   [config.py](../src/psychneuro/config.py) now reconstructs the exact
   original frozen baseline JSON schema from bounded reported seeds,
   participant count, trials, split seed and five CV folds, and verifies the
   claimed SHA. This catches a report altered and self-rehashed with a forged
   baseline configuration, even when its own report SHA appears consistent.
   Allows the two equivalent permitted JSON numeric spellings of fixed C=1.
   [reporting.py](../src/psychneuro/reporting.py) enforces this check before
   viewing/exporting anything, with [negative tests](../tests/test_reporting.py).
   **Written, not run.** A self-consistent score is still not an
   authenticated CI run; report checksum is not a digital signature.
2. **JSON-native data lineage:** [pipeline.py](../src/psychneuro/pipeline.py)
   normalizes nested slice confusion counts to JSON-native lists at the
   pipeline output boundary; avoids tuple/list differences between in-memory
   rows and the identical JSON export/read-back.
   Existing test specification in [test_workflow.py](../tests/test_workflow.py)
   checks real pipeline JSON round trip. **Not run.**
3. **PM-16 unfinished beginner issue #7:** real
   [issue #7](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/7)
   is a narrow offline Markdown-link QA check. Private
   [test_doc_links.py](../tests/test_doc_links.py) now implements a
   stdlib-only checker for bounded root/PM13-16 docs, positive/negative
   fixtures, fenced/inline code exclusion, remote URLs ignored and
   repo-root traversal rejection. External links are **never fetched**.
   The new test code was source-inspected; checked Markdown candidates
   against exact GitHub repo-tree paths without executing Python, finding
   no *obvious* missing paths. Full pytest and CommonMark edge-case proof
   remain **NOT RUN**, so do not close #7 as Verified Done.
4. **Independently inspectable hosted run evidence:** new
   [attestation.py](../src/psychneuro/attestation.py) refuses missing
   GitHub Actions identity, unsafe/missing artifacts, ineligible synthetic
   cohorts, changed PM10/11/13 report bytes or absent dependencies freeze.
   The [manual-only workflow](../.github/workflows/ci.yml) will, if
   independently approved and run, save actual GitHub SHA/run ID, Python
   version, checksum table and resolved package list under
   `artifacts/verification/`, archived for 7 days.
   [test_attestation.py](../tests/test_attestation.py) specifies negative
   identity/incomplete/tampered/missing cases with TEST-ONLY mocked bytes.
   **No hosted job was dispatched; sidecar files and run links DO NOT EXIST.**

## Scientific fidelity and limitations

- No change to prespecified seed-selection policy, dummy/logistic models,
  held-out grouping, sampling unit, post-response exclusions or original
  synthetic rights. Changes only strengthen validation and artifact evidence.
- Source-derived manifest hashes protect accidental corruption; without a
  genuine provider run/artifact comparison they cannot prove anything was
  executed on GitHub.
- A fake fixture score, doctest string or linked historical Actions run is
  not a measured PM-05–16 benchmark score.
- Reproducibility across Python 3.11 vs 3.12 is unverified; exact runtime
  dependency versions must be recorded separately for each.
- The v0 spec originally said the repository was unprovisioned: this is
  **historical context now superseded** by actual private GitHub ownership
  and PM-02–04 source/CI proof, not a present-day blocker.

## Why all 16 cannot be marked complete without new permission/capability

The remaining work is **external execution or human scientific review**:
(1) explicitly authorized **private GitHub Actions quota/spending** and a
supported new workflow dispatch, followed by actually inspecting the complete
Python 3.11/3.12 log/artifacts at this exact new commit; (2) a real
owner-approved **private Streamlit Cloud OAuth/login/hosting** operation and
genuine browser/mobile/keyboard/screen-reader/privacy check; (3) owner
scientific/spec, third-party license/security, and publication/PR approvals.
These actions must not be impersonated by test specs or new text. The
connected GitHub tool can inspect existing runs/logs but exposes no verified
new-dispatch action. Deploying without current code/safety evidence and
explicit permission is NO-GO. Do not ask the user to code or run local tools.

**Current decision:** GO private code audit and source review; **NO-GO**
marking PM-05–16 Verified Done, calling the demo tested, publishing
metrics/figures, public release, external recruitment or deployment.
This ledger is an independent PM-01–16 reconciliation, not a new project
version or overwrite of historical evidence.
