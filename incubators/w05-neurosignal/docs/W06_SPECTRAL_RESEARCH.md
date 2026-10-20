# W06 spectral analytics: research protocol, architecture and career evidence

**Status:** draft, synthetic-only, unsubmitted. This is incremental W06 work on the W05 P2/P14/P26 system, not three new mature applications. W06 scheduled 2026-11-19–25.

## Architecture and quantitative contract

`licensed/synthetic volts and rate (P2) → W06 StreamingWelch/DPSS (P2/P26) → P14 paired_stratified_ci → typed NumPy outputs`.

`StreamingWelch(fs, channels, nperseg, overlap)` accepts ordered `channels × samples` blocks, stores at most a partial window plus incoming chunk, and produces one-sided V²/Hz density averaged over **complete** windows. There is no disk cache, cross-worker recovery of its PSD accumulator, adaptive taper weighting, or raw-data streaming HTTP interface. Time complexity is O(number of windows × N log N), tail space O(channels × N), with an intermediate input-buffer allocation O(channels × (incoming chunk + N)). **The client must cap input block sizes**; this isn't an end-to-end memory bound on arbitrary caller-supplied blocks. A safe default for the existing local API remains synthetic-only.

Multitaper uses SciPy's periodic DPSS windows with uniform averaging, no taper-eigenvalue/adaptive weighting or confidence interval. Effective resolution is governed by time-bandwidth product NW; it is not interchangeable with Welch. Re-reference, montage, artifact rejection, PSD calibration and clinical EEG conclusions are out of scope.

The P14 group-key paired bootstrap resamples independent groups within fixed strata; groups with multiple epochs must be aggregated *before* calling this function. It does not deliver coverage calibration, selection-adjusted uncertainty or neural significance tests. Reject missing groups/stratum mismatches.

**CI acceptance:** compare streaming outputs against independently invoked `scipy.signal.welch` for chunk sizes 1/13/77/256/511; compare frequency/physical power for a seeded or analytical sinusoid; assert positive and zero paired contrasts and illegal cross-stratum pairs. Actual runs must be read from hosted logs. Python 3.11/3.12 and Ruff. Require no unverified claims regarding real clinical EEG.

## Manuscript methods/search strategy (GA1–GA2)

Working question: *When do segmentation and spectral estimator choices materially change EEG band-power reproducibility, conditional on consistent physical units, montage, and independent recording groups?*

Search strategy for a future systematic review: PubMed, IEEE Xplore and Crossref, query combinations of ("EEG" OR "electroencephalography") AND ("Welch" OR "multitaper" OR "wavelet") AND ("spectral power" OR "reproducibility" OR "validation"), publication years 1967–2026. Record search date, search string, deduplication, inclusion criteria (EEG signal estimation, primary methods or validation), exclusion (unclear units/unsupported claims) and risk of bias. **Search has not been systematically performed**; this is a prepared protocol, not a completed evidence synthesis.

Initial methodological source anchors and cautions:
1. Welch (1967), modified periodogram averaging: https://doi.org/10.1109/TAU.1967.1161901 — window, overlap and scaling determine estimates.
2. Thomson (1982), spectrum estimation and harmonic analysis: https://doi.org/10.1109/PROC.1982.12433 — multitaper concentration and weighting assumptions.
3. Percival & Walden (1993), *Spectral Analysis for Physical Applications* (book, not primary experiment): https://doi.org/10.1017/CBO9780511622762 — units and stochastic assumptions.
4. Torrence & Compo (1998), practical wavelet analysis: https://doi.org/10.1175/1520-0477(1998)079%3C0061:APGTWA%3E2.0.CO;2 — edges, significance and red-noise assumptions.
5. Maris & Oostenveld (2007), cluster-based nonparametric M/EEG inference: https://doi.org/10.1016/j.jneumeth.2007.03.024 — permutation exchangeability.
6. Gramfort et al. (2013), MNE-Python methods: https://doi.org/10.3389/fnins.2013.00267.
7. Gramfort et al. (2014), MNE MEG/EEG processing: https://doi.org/10.1016/j.neuroimage.2013.10.027.
8. Pernet et al. (2019), EEG-BIDS: https://doi.org/10.1038/s41597-019-0104-8.
9. Appelhoff et al. (2019), MNE-BIDS: https://doi.org/10.21105/joss.01896.
10. Rübel et al. (2022), NWB ecosystem: https://doi.org/10.7554/eLife.78362.
11. Varoquaux (2018), validation error in small neuroimaging samples: https://doi.org/10.1016/j.neuroimage.2017.06.061.
12. Winkler et al. (2014), permutation inference for GLM: https://doi.org/10.1016/j.neuroimage.2014.01.060.

Documentation checked as API grounding (not evidence of neuroscience):
- SciPy DPSS: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.dpss.html
- PyWavelets CWT: https://pywavelets.readthedocs.io/en/latest/ref/cwt.html

**Scientific objections:** The 10/16-Hz test peaks are designed fixtures, not discoveries. Strong overlap creates dependent windows. Bandpass/montage choice can dominate method contrasts. Multitaper and Welch may have different bias/variance/resolution; don't assert equality. Bootstrap CIs over a handful of fictional groups are validation plumbing, not calibrated uncertainty in human EEG. Spectral comparisons need fixed frequency-bin integration and actual reference-aware electrode mapping. Wavelet coefficient norms have convention-dependent factors; no wavelet module is implemented here.

## GA3–GA8 continuing research/career deliverables

- **GA3 upstream contribution, prepared but NOT submitted:** MNE-Python annotation origin nonzero `first_samp` regression from W05; test upstream-supported version, inspect contributor instructions and ask maintainer before proposing patch. https://github.com/mne-tools/mne-python and https://mne.tools/stable/development/index.html
- **GA4 shortlist (no open place guaranteed):** Aalto Doctoral Programme in Science https://www.aalto.fi/en/study-options/aalto-doctoral-programme-in-science-0 ; UCL Gatsby Unit PhD https://www.ucl.ac.uk/life-sciences/gatsby/study-and-work/gatsby-unit-phd-programme ; UCL ICN PhD https://www.ucl.ac.uk/brain-sciences/icn/study/postgraduate-research-phd ; Max Planck doctoral opportunities https://www.mpg.de/doctoral_students . Funding/eligibility and exact EEG group open calls need independent dated checks.
- **GA5 unsent collaboration proposal:** ask an EEG methods researcher to independently reproduce Welch chunk-invariance while comparing DPSS spectra on a rights-cleared paired-format signal; define montage/unit and study-independent resampling before analysis. Draft request: "I am evaluating EEG spectral reproducibility through independent Welch, DPSS, and streaming implementations. Would you be willing to critique our unit/montage and group-inference assumptions? I can share synthetic tests and the negative-case ledger. No endorsement or contribution is presumed." No individual identity verified; do not send.
- **GA6 reusable evidence/CV draft:** "Developed and tested a synthetic EEG spectral analysis prototype with chunked Welch density, DPSS multitaper estimation and leakage-aware paired bootstrap evaluation." Only use after linked CI.
- **GA7 teaching script, 60 seconds:** "An EEG peak at ten hertz can look perfectly convincing. Yet if you switch the window or misread volts as microvolts, you may be answering a different question. Welch averages overlapping windows; multitaper uses specially concentrated DPSS windows. Neither method fixes a bad electrode reference or leaky participant split. Our synthetic benchmark compares independent implementations before touching human data. The useful result is knowing where a pipeline breaks, not a prettier graph."
- **GA8 skeptical review:** no real paired EEG data; rights unverified; estimator CIs not calibrated; UI, performance and output persistence incomplete; independent methodological replication absent. External release NO-GO.

**Evidence tiers:** public = methodological/official links only; private = branch, exact SHA and CI when confirmed; unverified = real datasets, funding eligibility, research results, upstream acceptance, product security, usability, licensing, deployments. One Career card only; Academy untouched. Remind learner to continue the existing R course; optional three videos/week require approval. No new reminders.
