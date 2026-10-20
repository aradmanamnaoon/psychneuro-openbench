# W05 · Architecture, contracts and acceptance · 2026-10-20

**Decision:** isolate P2 + P14 + P26 under a private W05 incubator subtree; do not make P1 OpenBench's earlier W03/W04 source an EEG dependency. All externally consumed JSON reports carry version `1.0`. Reject schema version changes or unknown keys. Source authenticity = rights evidence + exact SHA-256 file checksum; **not** cryptographic proof of the provider's authority. No automatic dataset retrieval.

## Dependency DAG

```text
P2 adapters -> Recording/Chunk v1 + Rights --(volts, event samples, group IDs)--> P2 Graph
                         |                                    |
                         |                                    v
                         +----------------------------> P26 CausalFIR state/checkpoint
                                                              |
                                                              v
                                              P2 SpectralPlugin (V²/Hz, Welch)
                                                              |
                                synthetic segment tests ------+--> P14 preflight -> group CI
                                                              |
                                                hashes, JSON evidence + private API
```

- `contracts.py`: immutable strict Pydantic objects; channel names, sample clock, event spans, source-license/rights and exact byte digests.
- `fixtures.py`: CC0 synthetic-only labeled sinusoid with per-channel local RNG; no human/clinical recordings.
- `adapters.py`: `MNEReader` lazy EDF/FIF and optional `NWBReader` lazy ElectricalSeries. Reader lifetime encapsulates HDF5 handles. NWB requires one named acquisition ElectricalSeries with homogeneous sampling and voltage unit; irregular timestamps are denied, not interpolated.
- `pipeline.py`: typed causal preprocessing graph, no implicit data rejection; each transform traces config/input/output digests and QC flags.
- `dsp.py`: P26 causal FIR state boundary, exact start-index continuity and explicit checkpoint version/shape; timestamp precision tolerance set by caller.
- `evaluation.py`: Welch PSD (V²/Hz) and STFT; interpretation conditioned on stationary signal assumptions. No inferential conclusions.
- `evalops.py`: P14 group-level temporal/leakage guard and percentile group bootstrap; independent subject/recording IDs supplied by caller, not inferred from channel metadata.
- `storage.py`: local SQLite WAL, transactional idempotency, leases, fences, cancel and replayable transition audit. This is **not** a distributed consensus layer. Schema currently initial create-only; migrations and full recovery remain backlog.
- `service.py`, `cli.py`, `static`, `sdk/`: authenticated 1.0 API, local experimental UI and typed TS client, no external account management.

## Independent oracle and math

For channel c and sample n, causal FIR `y[c,n] = Σ[k=0..L-1] h[k] x[c,n-k]` with zero history outside input. Streamed SciPy `lfilter` with carried `zi` must agree with separate shift-and-add oracle to `atol=1e-17 V` on 1024/4096-sample synthetic signals. In practice choose tolerances from `eps * signal_scale * taps` rather than clinical-domain thresholds. Chunk sizes 1,7,64,256,333,999 test state invariance. A full-channel average reference is instantaneous per sample and commutes with chunking if channel set is stable; no implicit channel exclusion. Spectral source `scipy.signal.welch` uses Hann windows and one-sided density. Rectangular single-window FFT is a **physics/Parseval sanity oracle**, not identical to windowed Welch.

PSD integration approximately equals signal variance in V² for a sufficiently sampled stationary process; FFT peak location should identify an injected 10 Hz component at resolution 1 Hz when `nperseg=256` and `fs=256`. Spectrogram STFT is a descriptive time-frequency representation, not a multiple-comparison corrected inference. Synthetic noise is seeded, explicitly fictional.

## Evaluation contract

- Train and test need ≥2 distinct independent group IDs; overlapping group IDs or temporally overlapping windows across splits are blocked.
- Distinct window IDs, bounded 0–1 scores, frozen split roles; subject mean first, then bootstrap complete groups with replacement.
- Report `n_groups`, confidence level, seed and repetitions. The percentile CI is an uncertainty demonstration, not validated frequentist coverage with small/heterogeneous groups.
- Production experiments require nested cross-validation, holdout lock, outcome/predictor timing guards, and uncertainty-calibration/familywise-error assessment before claims.

## Security/rights/privacy threat matrix

| Threat | Current control | Missing release gate |
| --- | --- | --- |
| Unauthorized external human files | Explicit Rights + exact checksum + approved root; no downloader | Independent authorization/consent registry and DUA legal review |
| Path traversal / symlink | `resolve(strict=True)` plus root membership | Cross-platform race-resistant file descriptors, symlink TOCTOU review |
| Unauthorized tenant job read | `tenant` predicate on every job status/mutation | Production OIDC, authorization roles, external security assessment |
| Lease race / stale finish | SQLite `BEGIN IMMEDIATE`, revision/fencing, retry budget | Multi-host locking, crash fault injection, DB durability operational SLO |
| Negative/out-of-order samples | Strict sample clocks, finite values, bounds, known contract version | Streaming channel/dropout policy, end-to-end event clock drift correction |
| License laundering | Deny real data unless caller says verified and checksum matches | Third-party authoritative rights evidence; claims are not independently verified |
| Heavy CPU requests | Bounded API sample counts | Rate limiting, quotas, auth session rotation, multi-tenant resource scheduling |
| Clinical misuse | Nonclinical disclaimer; fictional scores | Full governance, ethics and validation if ever in scope (currently out of scope) |

## Acceptance and budget

**Provisional milestone**: (A) synthetic end-to-end with independent FIR oracle (relative 1e-17 V absolute); (B) group leakage negative test; (C) rights and checksum negative test; (D) trusted hosted CI same source SHA; (E) independent scientific, licensing, UI/screen-reader and privacy reviews. Passing local (A–C) never satisfies (D–E).

**Human learner time budget**: W05 24 suggested Career hours, distributed ~8h software core/tests, 5h scientific QA, 5h literature/manuscript, 3h upstream/career, 3h independent review and revision. Academy separately 40h/week. The combined 64h/week does **not** imply equal days; cap each focused day at 10h and spread across week/remaining days. No additional career calendar tasks. R course reminder stays; optional three original videos can replace (not add beyond) discretionary work. No paid compute.

## Explicit ambitious backlog

1. Rights-reviewed/licensed real public EDF and NWB integration fixtures; native mixed-rate EDF metadata preservation; strict EDF+ annotation calibration.
2. Resampling with transparent anti-alias guarantees, zero-phase offline vs causal-online equivalence documentation, traceable channel-select policies, EOG/ECG artifacts and localized neural activity metadata.
3. Hierarchical resampling, permutation/cluster tests with exchangeability groups, multiple comparison control, calibrated prediction evaluation with end-to-end group held-out train pipelines.
4. Arrow/Zarr/Parquet backing store, retention revocation/deletion, source-of-truth license signing and immutability audits.
5. Task payload schema migration, DB migrations, claim heartbeat, independent durable DSP checkpoint store, multi-worker fenced concurrency, fairness/backpressure, rate limiting.
6. External OIDC, third-party security and accessible user interviews, native EEG viewer, screen-reader and assistive technology manual tests.
7. Lockfile/SBOM, branch exact-head hosted CI, container clean deploy/restore/rollback RTO-RPO measurements, load testing across trusted host.
8. Field-specific scientific preregistration, licensed public EEG replication, multicenter confirmation and independent reviewer sign-off before study claims.

**Rollback:** Delete isolated W05 review branch or revert W05 subtree commit only. Do not alter W04 ancestor branch nor its pending PRs. Data migrations are not attempted. Deployment remains disabled.
