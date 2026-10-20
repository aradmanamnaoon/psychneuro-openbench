# W08 validation & release engineering — reviewer evidence and research package

Status: **synthetic-only candidate; no real EEG, no external production deployment**. Week 8 is scheduled 2026-12-03–09, implementation prepared ahead of time on a review branch.

## Architecture / DAG / quantitative gates

P2 synthetic provenance/units → P26 causal FIR streaming with independent direct-convolution oracle → P2 streaming Welch with independent SciPy Welch estimator → canonical SHA256 evidence → P14 tenant-scoped SQLite registry / regression comparator → authenticated local API. P2/P14/P26 share a local typed Python package; **there are not yet separately deployed independently released services**.

`validate_synthetic(seed=42, samples=4096, chunk_size=127)` generates deterministic 256-Hz 10-Hz sine in V and 0.02 µV Gaussian noise. It compares chunk-independent Welch spectra (relative L2 <=1e-10) and streaming FIR versus direct shift/add (<1e-16 V), a zero-signal null spectrum and FFT peak exactly 10 Hz. These are engineering tolerances, **not statistical confidence intervals or clinical sensitivity**. Negative tests force refusal at stricter-than-observed thresholds; source SHA256 proves only bytes of seeded generated array.

`EvidenceRegistry`: strict schema 1.0 synthetic-only canonical JSON, content hashing, idempotency, configured-tenant isolation, unit/cohort comparison before metric regression. Observed pairwise delta is NOT longitudinal causal evidence, and comparison assumes lower numeric metric is better. API `POST /v1/evalops/compare` only reads previously registered records; no public registry write/upload API.

`infra/Dockerfile.w08` and `infra/compose.w08.yml`: 2-service loopback-only API plus one-shot smoke probe with nonroot API user, capability drop, filesystem read-only, state volume, pids/CPU/RAM caps and health probe. Image is built from unpinned dependency ranges (not reproducible lockfile). Docker has **not been executed solely by creating Compose files**; actual build/start/rollback/HTTPS cloud preview must be observed before claiming deployability. No public endpoint or remote cloud resources are provisioned.

## Science protocol and manuscript draft — GA1–GA2

Provisional methods title: **Numerical invariance is necessary but insufficient: seeded signal and evaluation provenance checks for reproducible neurophysiology pipelines**.

Introduction draft: EEG spectral and event-related estimates are sensitive to units, segment boundaries, preprocessing, artifact rejection, and the unit of independence. A numerically correct streaming implementation can still produce misleading human inference if recordings are leaked across training and testing, repeated events are counted as independent people, or acquisition metadata lose physical units. This protocol tests the *software* guarantees before attempts at real EEG scientific inference. It cannot establish generalization to unseen participants or devices.

Methods draft: pre-register source waveform parameters, timing, channel order, signal units, independent reference formula and comparison tolerances. Execute seeded synthetic variants with different chunk sizes and an unfiltered zero-signal null. Record exact software versions, SHA256 of source samples, quantization/FFT window rules and immutable regression comparator configurations. Compare paired versions only if dataset/cohort/units match. Negative controls must force failure for changed cohort, mismatched metric units, nonfinite values and untrusted tenant. No results on real EEG may be included absent authorized acquisitions and independent methodological review.

Methodological source leads (stable DOI links; not a completed systematic search):
1. Welch 1967, https://doi.org/10.1109/TAU.1967.1161901 — periodogram averaging.
2. Thomson 1982, https://doi.org/10.1109/PROC.1982.12433 — multitaper harmonics.
3. Delorme & Makeig 2004, https://doi.org/10.1016/j.jneumeth.2003.10.009 — EEG pipeline.
4. Gramfort et al. 2013, https://doi.org/10.3389/fnins.2013.00267 — MNE-Python.
5. Maris & Oostenveld 2007, https://doi.org/10.1016/j.jneumeth.2007.03.024 — EEG permutation tests.
6. Pernet et al. 2019, https://doi.org/10.1038/s41597-019-0104-8 — EEG-BIDS.
7. Winkler et al. 2014, https://doi.org/10.1016/j.neuroimage.2014.01.060 — permutation GLM.
8. Varoquaux 2018, https://doi.org/10.1016/j.neuroimage.2017.06.061 — small-sample validation.
9. Jas et al. 2017, https://doi.org/10.1016/j.neuroimage.2017.06.030 — artifact autoreject.
10. Rübel et al. 2022, https://doi.org/10.7554/eLife.78362 — NWB ecosystem.

**Not systematic-search verified**: journal publication details and inclusion/exclusion decisions, field-specific evidence synthesis, independent peer review; citations must be checked before a submission.

## GA3–GA8 preparatory outputs

GA3 upstream test-backed idea: propose MNE-Python regression covering sample offsets and chunk-independent EDF metadata, test upstream release before any external PR. Not submitted. GA4 official graduate/research opportunity starting points: Aalto doctoral https://www.aalto.fi/en/study-at-aalto/doctoral-programmes ; Gatsby Unit PhD https://www.ucl.ac.uk/life-sciences/gatsby/study-and-work/gatsby-unit-phd-programme ; Max Planck doctoral https://www.mpg.de/doctoral_students ; UCL Institute of Cognitive Neuroscience postgraduate https://www.ucl.ac.uk/brain-sciences/icn/study/postgraduate-research-phd . Open vacancies, eligibility, visas and funding are **not checked**. GA5 unsent methods-review proposal: share a fixed seed/FFT/units/negative-control specification with a signal-processing lab and ask for blind independent recomputation. Unsent generic note: “Would you be willing to independently inspect our streaming-vs-batch PSD tolerances and participant-level inference boundary? I can share synthetic-only evidence and open failure criteria.” GA6 portfolio/case-study line: “Built content-addressed synthetic EEG evaluation and independent SciPy/FIR oracle tests in a review-gated Python CI pipeline” (only cite passing CI when verified); video script: “Ten hertz looks easy. A plot can be right while the science is wrong: did you preserve volts, event indices and subject independence? This pipeline independently checks numerical results, then refuses mismatched benchmark cohorts.” GA7 replicate FFT and direct convolution from scratch, permute chunk size and seed, log controlled failure. GA8 skeptical review: tiny synthetic 10-Hz signal is not human EEG; comparator metric direction hardcoded; sample budgets and raw allocator bounds partial; no independent study, real browser E2E, tested Compose or cloud preview; lockfile/security scans/rollbacks absent.

## Release gates and backlog

E1/4 comparator and methods PARTIAL; E2 Compose config PARTIAL, deployed/cloud BLOCKED; E3 registry PARTIAL; E5 DSP reused PARTIAL; E6 independent numerical oracle PARTIAL; E7 schema/rights PARTIAL; E8 persistent registry PARTIAL; E9 API tests incomplete; E10 no hosted benchmark; E11 unit-level boundary only; E12 hosted Python CI pending, locks/rollback BLOCKED; E13 in-process P2+P14+P26 path PARTIAL; E14 evidence document PARTIAL.

No real human recordings or clinical endorsement, no external contacts, no spending. W08 Notion date and Done checkbox must stay unchanged. Learner time max 10 hours/day combined with Academy; continue existing R course; educational videos optional and unsent.
