# W05 GA3–GA8 · Career, reproducibility and academic deliverables (all unsent)

## GA3 · Maintainer-valued upstream path (UNSUBMITTED)

**Target upstream:** mne-tools/mne-python, read-only technical inspection. An actual open issue, **[mne-python #13890](https://github.com/mne-tools/mne-python/issues/13890)**, discusses annotation timestamps versus `raw.first_samp`; another open report **[#11731](https://github.com/mne-tools/mne-python/issues/11731)** concerns annotation shifts after cropped FIF round-trip. No claim that a newly implemented fix resolves either issue: both require upstream code-level reproductions and maintainer triage. This is a provenance-aware upstream preparation rather than an unauthorized external PR.

**Concrete patch proposal for maintainer review:** Extend `mne/io/tests` with a synthetic `RawArray` first_samp=10_000, two annotations at 2 and 4 s (unambiguous `orig_time`), extract signals using annotation-span converter instead of direct `get_data(tmin=annotation.onset)`, assert correct indices both before and after FIF round-trip. Confirm the minimal regression actually fails under an upstream supported version; otherwise do not submit a spurious issue. Local adapter in `adapters.py` uses `time_as_index(onset-first_time)`; the synthetic `test_mne_adapter.py` tests ordinary first_samp=0 only. **Update, 2026-10-20:** local synthetic `first_samp=10_000` roundtrip regression now passes; a maintainer/head-specific upstream reproduction remains untested. Contribution status: proposal drafted; no fork branch, issue comment or PR submitted.

Source for contributor guidance: https://mne.tools/stable/development/index.html ; license/reference code: https://github.com/mne-tools/mne-python . Review contributor documentation and tests on the exact upstream head before any authorized public action.

## GA4 · Lab/funding intelligence (official-source shortlisting, NOT openings)

1. **Aalto University School of Science doctoral research** (Finland): AI, software and neuroscience named in Science doctoral programme; an official current listing indicates an application period extending to **December 1, 2026**, subject to current confirmation. Admission requires a supervisor and documented prior degree/language eligibility; full-time SCI applicants need ≥6 months funding secured; salaried job applications are separate, not guaranteed by doctoral admission. Official: https://www.aalto.fi/en/study-options/aalto-doctoral-programme-in-science-0 and https://www.aalto.fi/en/doctoral-education/funding-your-doctoral-studies . Engineering fit: MNE-based EEG metadata + reproducible Python. **Individual position/funding: not verified.**
2. **UCL Gatsby Computational Neuroscience Unit** (UK): strong mathematical/ML preparation and relevant first degree are listed prerequisites, UCL language requirements apply. Official page states fully funded studentships for home/international candidates and a 2026/27 stipend; separate competition, dates and individual lab EEG fit must be checked. https://www.ucl.ac.uk/life-sciences/gatsby/study-and-work/gatsby-unit-phd-programme . **No admission likelihood asserted.**
3. **UCL Gatsby/Sainsbury Wellcome Centre joint PhD** (UK): computational/systems neuroscience, explicit funding for international candidates including 2026/27 stipend. Individual fit with EEG signal preprocessing is not guaranteed: SWC primarily systems neuroscience. https://www.ucl.ac.uk/life-sciences/gatsby/study-and-work/gcnu-swc-joint-phd-programme . **No live vacancy or supervision confirmed.**
4. **UCL Institute of Cognitive Neuroscience PhD** (UK): cognitive neuroscience + methodological research potential; funding may have international/fee-status restrictions, and **an offer does not guarantee funding**. https://www.ucl.ac.uk/brain-sciences/icn/study/postgraduate-research-phd . Need precise funded call and supervisor; do not assume compatibility or fee waiver.
5. **Max Planck Society doctoral research groups** (Germany): society-wide funding contracts, social insurance and structured training described on official page; these are not a single EEG-lab vacancy. Prefer selecting an *actual* signal-analysis institute + PI and verified open position before contacting. https://www.mpg.de/doctoral_students . **Institute-specific 2026 EEG call not verified.**

**Eligibility verification checklist:** credential level and degree equivalence, English score, recent researcher publications/fit, living/visa/residence rules, salary tax/social insurance, citizenship-specific funding limits, employer-sponsored vs fellowship, exact deadline/availability, 2027 intake, supervisor and explicit advertised topic. Do not interpret nationality-generic funding eligibility as immigration authorization.

## GA5 · One-page method-specific collaboration proposal (DRAFT)

**Working title:** *How much does EEG input format and streaming state change spectral features?*

**Problem:** Existing toolkits make heterogeneous electrophysiological formats processable, but downstream PSD comparisons can conflate physical-unit metadata, first-sample offsets and chunk-dependent state. The goal is an openly reviewable engineering benchmark **before** any human EEG inference.

**Proposed milestone:** A rights-reviewed, public-license EEG corpus with at least two independently re-exported file formats per source recording; a publication-ready, falsifiable comparison of normalized physical units, time/event alignment and Welch alpha/beta power under whole-file and streaming preprocessing. Start with synthetic gold-standard oracles in code and independent MNE calibration.

**Roles:** software proposer maintains typed readers/DSP, provenance and automated tests; collaborating neurophysiologist defines montage reference and artifact policy, EEG-specific annotations and interpretation; statistical methodologist reviews sample independence, equivalence thresholds and uncertainty design; data steward checks consent/licensing. No implicit commitment from any external party.

**Outputs:** pinned code and safe public fixture, full null/negative cases, group-aware analysis pre-registration, machine-readable reproducibility records. Deliverable gate is third-party reproducibility, not a performance leaderboard. Risk of NWB/EEG ontology mismatch, dataset restrictions and equivalent formatting not preserving ADC quantization. Proposed six-week pilot is optional—not scheduled or promised.

**UNSENT targeted message to a potential MNE methods collaborator (generic until recipient verified):**

> I'm building a synthetic-first, rights-gated reproducibility benchmark for EEG imports and causal streaming DSP. A current narrow question is whether EDF/FIF/NWB adapter timing and voltage-unit transformations measurably change otherwise identical Welch band-power estimates. I have a self-contained `P2→P26→P14` Python test slice, including a direct-FIR numerical oracle, group leakage checks and an intentionally strict limitations ledger. Would a 15-minute methodological review of the annotation-origin and montage assumptions be useful to your EEG interoperability work? I would value a specific failing test or critique, not endorsement or a recommendation.

**Individualization before sending:** inspect an actual group paper, recent research topic, institutional policy/contact route, accessibility of the repo/evidence and topic alignment. No send, connection request, recommendation request or publication is authorized now.

## GA6 · Case study, CV line and storytelling asset (private, approval-only)

**Case study / problem:** Raw EEG metadata errors can be amplified by numerically stable signal processing; a perfect power spectrum computed from wrong time bases is misleading. Our synthetic fixture injects a known 10 Hz component in volts, creates 256-Hz samples and fictional events. A group-aware evaluation rejects overlapping windows and split-participant leakage.

**Method:** numpy seeded synthetic oracle, physically explicit volts schema, MNE lazy FIF smoke, scipy.signal Welch, causal FIR with stateful incremental chunks, direct reference convolution, group bootstrap CI and SHA-256 recording identity; FastAPI local auth; SQLite transactional queue; Playwright loopback UI attempt. **Observed evidence must be taken from actual test logs.**

**Proposed CV sentence, after real branch evidence:** "Developed a synthetic-first neurophysiology processing prototype integrating typed lazy FIF ingestion, chunk-invariant causal FIR, spectral QC and group-leakage evaluation; wrote reproducibility/security tests and documented inference limits." Do not add numeric claims until linked to actual recorded tests/CI. Do not claim lab collaboration, publication or clinical use.

**Original ~90-second educational script, draft:**

> Imagine you have one minute of EEG. You open the file, process it, and see a beautiful peak around ten hertz. Great? Maybe. But what if the first event is shifted? Or the signal unit is microvolts and your code treats it like volts? The shape can look perfectly fine while the numbers are wrong. Here's the interesting part: even if you fix the units, your filter might change its answer depending on how many samples you read at once. So instead of trusting a nice graph, I built a synthetic signal where I know the frequencies, and I compare a chunk-by-chunk filter with an independent mathematical calculation. Then I test the uncomfortable cases too: corrupted checksums and participant leakage. This doesn't prove anything about a real brain. It proves whether the pipeline deserves the next test. In neuroscience, a nice-looking chart is not evidence that your measurements are reproducible.

Prospective feedback plan: ask one methods expert to reproduce source checksums and one EEG practitioner to critique event origin/montage; both **only after explicit contact approval**. Three videos/week are optional; no upload scheduled.

## GA7 · Skills mastery / replication exercise

**Exercise:** Derive the one-sided PSD normalization from the real FFT of `A sin(2πft)` with sample rate `fs`, then verify `∫PSDdf ≈ A²/2` for an exact-bin synthetic tone. Compare rectangular periodogram against Hann-window Welch; demonstrate that they have different leakage/smoothing. Implement FIR group delay `τ = (taps−1)/(2fs)` for the symmetric causal linear-phase filter; separate time-domain delay from event-trigger alignment. The independent oracle tests numerical identity, not whether zero-phase filtering was scientifically warranted.

**Replication prompts:** 1) How would an EDF mixed-rate channel violate a uniform sample grid? 2) Why must a `first_samp` offset be applied before sample indexing? 3) What is the exchangeability unit under repeated participant epochs? 4) Why is bootstrap-over-windows invalid when one person contributes 1,000 overlapping windows? 5) What failure would disprove the claim of chunk invariance? Answers are checkable against `docs/ARCHITECTURE_ADR.md`, the spectral equations, [Varoquaux 2018](https://doi.org/10.1016/j.neuroimage.2017.06.061), and [Maris & Oostenveld 2007](https://doi.org/10.1016/j.jneumeth.2007.03.024).

## GA8 · Skeptical review and evidence levels

**Reviewer #2 assessment:** No human empirical claim, no paired real-file conversion comparisons, no legal right to share an upstream dataset, no direct NWB adapter test, no portable lock/SBOM, no external threat-model audit and no statistical evidence of estimator calibration. The implementation may be a publishable *methodology* in the future but a synthetic demo alone is not an original EEG research result. A proper external evaluator should require arbitrary fixture tests, licensing provenance, sampling-frequency adversarial cases and a controlled free deployment/rollback demonstration before GO.

**Evidence levels**: `public`: primary literature, official program policies, upstream publicly visible issues, no public user code; `private`: local synthetic code/test/evidence and possibly private GitHub PR; `not-yet-verified`: human datasets, reader coverage across EDF/NWB, scientific inference, exact-head hosted CI, upstream review/acceptance, job/opening eligibility, browser assistive-technology sign-off.

## R course and time

Continue the preexisting R course reminder (do not create another task). Week 05 Career suggested 24h plus Academy separately 40h, distribute learner effort across 7 days to avoid >10h/day. Publication, outreach, submissions, employment applications and external PRs require explicit human review of the exact artifact.
