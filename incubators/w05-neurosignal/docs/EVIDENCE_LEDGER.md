# W05 implementation and evidence ledger — 2026-10-20 (pre-week work)

**Private GitHub review:** [draft PR #26](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/26), original head `1092a541c0a63e5522c6f9d815d5ccff46faa8d2`; GitHub Actions first run [#39388959792](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39388959792): **Python 3.11 and 3.12 pytest steps passed, overall both jobs FAILED Ruff (15 style/import findings)**. Patch corrects the logged 15 issues in isolated source/tests; exact patched commit has NOT yet been rechecked on host as of this text. Preserve failed run in evidence history. No merge/release.

**Status language:** DONE = narrowly completed and locally observed, PARTIAL = useful implemented component but missing epic-level gates, BLOCKED = no validated execution; no full W05 release GO. Scheduled W05 remains 2026-11-12–18; original Notion Done must remain unchecked. All data are explicitly synthetic, including generated FIF; source record rights declarations are caller-provided and are **not independent legal evidence**.

## Observed environment and commands

From folder `incubators/w05-neurosignal/` or extracted W05 ZIP root:

```shell
python --version                              # Python 3.13.5 observed
PYTHONPATH=src python -m pytest -q tests       # 37 passed in 2.47s, exit 0
npx --no-install tsc --noEmit -p sdk/tsconfig.json  # exit 0, TypeScript 5.8.3
PYTHONPATH=src python -m neurosignal.cli demo --seed 42 --samples 4096 --chunk-size 333
PYTHONPATH=src python tests/bench.py
PYTHONPATH=src python tests/browser_smoke.py  # failed: Chromium ERR_BLOCKED_BY_ADMINISTRATOR
python -m ruff check src tests                # BLOCKED: No module named ruff
```

Local dependency observations: NumPy 2.3.5, SciPy 1.17.0, MNE 1.11.0, pytest 9.0.2, FastAPI 0.128.2; PyNWB and Ruff absent. The dependency ranges in pyproject.toml are NOT a complete reproducible lockfile; CI hosted Python 3.11/3.12 installations and pytest steps were observed on original W05 head, but full CI failed Ruff. Installation of Ruff failed in the network-isolated sandbox: DNS failure. The pytest log, portable JSON integration report, observed bench log, failed Chromium trace, and repository tree SHA manifest are in this evidence pack. The source and this snapshot are private and unreviewed.

### Synthetic trace with seed 42

- Signal 4 channels × 4096 samples at 256 Hz; known injected 10-Hz signal; chunk =333.
- Pipeline dominant spectral frequency **10.0 Hz** (a tautological injected-component recovery, not empirical brain data).
- Direct O(NK) convolution vs stateful streaming FIR max absolute error **2.0328790734103208e-20 V**.
- Bootstrapped fictional-score group mean 0.595, percentile 95%-style interval [0.57428125,0.6175], 8 fictional independent groups, 500 seed-controlled resamples. **Not uncertainty/calibration for human EEG or model prediction.**
- Exact SHA-256 and 18-decimal-normalized spectrum SHA-256 are both exported; normalization only makes a tolerance-level identity string, never cryptographic proof of bitwise identity. SHA provenance hashes do not authenticate a data supplier.
- Independent Python direct convolution oracle; MNE synthetic generated FIF lazy smoke tested including nonzero `first_samp`=10,000 and aligned relative event at local sample 100. No EDF/NWB empirical fixture run.

### Observed performance (no SLA)

Five synthetic repetitions per setting (Python 3.13.5 / Linux; single local process, tracemalloc excludes native array buffers; includes Python pipeline+evaluation+serialization):

| Samples | Chunk size | Median elapsed | Largest tracemalloc peak |
|---:|---:|---:|---:|
| 1,024 | 64 | ~114.7 ms | ~0.72 MB |
| 4,096 | 256 | ~436.7 ms | ~2.74 MB |
| 8,192 | 512 | ~860.3 ms | ~5.45 MB |

This is not distributed throughput, representative EDF/NWB decode speed, true RSS, memory safety, or production latency.

## E1–E14 epic evidence and release gaps

| Epic | State | Present implementation and verified evidence / missing blocker |
|---|---|---|
| E1 EDF/FIF/NWB | PARTIAL | Typed rights+SHA, channel units, event metadata, lazy MNE FIF smoke (including first_samp offset). EDF native mixed-rate and PyNWB real adapter runs NOT tested; no third-party human data authorized. |
| E2 preprocessing | PARTIAL | Configured average-reference, amplitude QC and lowpass FIR graph, provenance SHA and seeds. No bad electrode interpolation, ICA or EEG-montage suitability review. |
| E3 spectrum/time-frequency | PARTIAL | Protocol-like Welch/STFT plugin API typed output; synthetic peak/Parseval tests. No statistical time-frequency inference, corrected cluster comparison or real EEG QC validity. |
| E4 benchmark DSL | PARTIAL | Versioned schema for groups, slices, nominal CI, leakage preflight. No nested CV or calibration analysis with real independent subjects. |
| E5 P26 runtime | PARTIAL | Causal streaming FIR, checkpoint state, order validation, independent numerical oracle, sync helper, CLI, local API. No arbitrary job checkpoint resume or production streaming protocol. |
| E6 numerical falsification | PARTIAL | 37 local tests cover 4+ seeds, invariance and null/negative cases, exact direct-convolution oracle, known tone spectral verification. EDF/NWB and real field-specific ablation not yet performed. |
| E7 database/lineage/rights | PARTIAL | Immutable strict contracts, rights declaration+content digest+approved root, SQLite schema, transition history. No signed rights authority, migrations, revocation or retention enforcement. |
| E8 durable concurrency | PARTIAL | SQLite WAL `BEGIN IMMEDIATE`, leases, fencing, cancel/reconcile/retry, idem request conflict; locally tested. No multi-process crash chaos, auto-poller, backpressure or checkpoint store. |
| E9 API/SDK/UI | PARTIAL | Versioned OpenAPI, bearer+tenant local demo, TS SDK and keyboard-intended static browser; HTTP tests PASS, TypeScript typecheck PASS. Headless Chromium real page navigation BLOCKED_BY_ADMINISTRATOR; no AT/manual review. |
| E10 performance | PARTIAL | Local seeded tracemalloc and monotonic latency measurements for 3 sizes ×5; no load/stress, RSS, external deployment regression gate. |
| E11 security/privacy | PARTIAL | Rights root traversal, unauthorized tenant, bearer token, malformed schemas, idempotency conflicts, stale workers and no data import by URL. No independent pentest/TOCTOU, auth provider or formal property-based random adversary. |
| E12 hosted release | PARTIAL | First exact-head private CI run observed: Python 3.11/3.12 installed and pytest PASS, Ruff FAIL (15 findings). Corrections prepared; no new-head hosted pass yet, lock, rollback, or deployment. |
| E13 three-system E2E | PARTIAL | Actual `run_synthetic()` integrates P2→P26→P2 spectrum→P14 and returns JSON SHA/provenance with negative leak tests; no actual distributed cross-repo E2E. |
| E14 reviewer pack | PARTIAL | ADR, reproducible script, protocol, skeptical memo, scientific/career outputs, benchmark/CI spec, evidence JSON. Independent human reviews and production release runbook remain open. |

## GA1–GA8 status

| GA | State | Specific artifact and limitation |
|---|---|---|
| GA1 | DONE, source-check scope | `RESEARCH_PROTOCOL.md` contains 11 stable DOI publications + one PyNWB method-doc reference, limitations, claim links; no full systematic literature review. |
| GA2 | PARTIAL | Narrowed manuscript question, intro, methods/protocol outline, null controls, claim matrix, disclosure; no data-backed manuscript results or target journal approval. |
| GA3 | PARTIAL | Real MNE annotation-origin upstream issues identified, proposed test, own adapter test implemented. No upstream reproduction on main head or submitted external patch. |
| GA4 | PARTIAL | Five official sources for Aalto, UCL, and Max Planck candidate programs; no verified exact funded lab position, immigration/degree credential determination. |
| GA5 | PARTIAL | Technical one-page proposal and UNSENT, currently generic outreach draft; no recipient-specific publication alignment yet. |
| GA6 | PARTIAL | Synthetic code-linked case study, reproducibility instructions, CV proposed line, educational 90s script; no approved public portfolio publication. |
| GA7 | PARTIAL | Welch/Parseval, FIR latency, grouped-permutation written replication exercise; independent learner evaluation remains to be done. |
| GA8 | DONE, draft scope | Skeptical reviewer objections, replication memo, public/private/unverified ledger, ethics and permission rules. No actual independent peer review. |

## Evidence level

- **Public independent:** DOI source pages, university program pages and MNE contributor/issues information. No code public release claimed.
- **Private locally observed:** files packaged in this release candidate; `local_pytest.log`, `evidence_synthetic.json`, `bench_observed.json`, `browser_log.txt` and isolated source tree. SHA manifest generated at pack time.
- **Unverified:** successful all-gates exact-SHA CI, fully locked transitive installs Python 3.11/3.12, dataset rights sign-off, EDF/NWB runs, real browser assistive use, independent review, qualified manuscript findings, jobs/funding availability and production recovery.

## Immediate independent review sequence (ordered)

1. Run hosted Python 3.11/3.12 unit/scientific tests, lint/typecheck, TS SDK and real local browser smoke at exact PR head; do not infer run from a workflow file alone.
2. Pin and install tested transitive requirements, produce SBOM, check numerical variance across SciPy/MNE versions, eliminate optional untrusted dependency drift.
3. Add a fully synthetic EDF+ roundtrip and a PyNWB ecephys fixture with scientifically truthful metadata; compare sample clocks/voltage conversion to a separate library, audit rights.
4. Migrate SQLite schema via explicit versioned migrations, persist DSP state checkpoints, recover interrupted bounded worker process, rate-limit API and provide independent tenant credentials.
5. Human screen-reader and neurophysiologist test; security/privacy/rights review; only afterward permissioned real research data and preregistration; no public/clinical claims.

**NO-GO:** This locally verified, deliberately incomplete vertical slice is not three finished flagship products, an empirical neuroscience manuscript, a hosted deployment, or a production-ready service.
