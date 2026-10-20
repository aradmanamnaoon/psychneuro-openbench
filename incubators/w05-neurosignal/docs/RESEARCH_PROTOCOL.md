# Working protocol / manuscript draft · W05 (not submitted)

## Proposed title
**Do file format and streaming chunk boundaries change EEG spectral estimates? A falsifiable, rights-aware reproducibility protocol for EDF, FIF and NWB pipelines**

**Type:** preregistration-ready *methodological evaluation protocol*, not a completed empirical study. No participant recordings have been studied; no findings or effect sizes are claimed. Creative software claims require prior-art review before submission. October 20, 2026.

## Narrow question and target estimand

Across explicitly licensed, nonclinical EEG recordings represented equivalently in EDF/FIF/NWB, how large are the absolute/relative deviations in (1) sample-aligned voltage signal and (2) per-channel Welch band-power estimators when readers and DSP streaming chunk sizes change? Primary estimand: paired absolute deviation of log10 alpha-band integrated power (8–12 Hz) between a single-read reference and each tested streaming chunk size, stratified by recording and input adapter. This contrasts an **engineering invariance property** with potentially informative format-specific parser deviations. Data from different modalities must not be treated as identical EEG merely because NWB can encode time series.

Null engineering hypothesis: for a fixed canonical recording/clock/rate, causal FIR transforms are equivalent within `epsilon = 1e-17 V` across chunk size when initial state is equal. Scientific equivalence margin for alpha power is **not predefined from a clinical effect threshold**; a defensible practical threshold must be calibrated in a pilot with licensed source data and openly justified before confirmatory analysis. Reject any claim of human/neural outcome superiority from synthetic-only data.

## Sourced introduction (draft)

Large-scale reuse of electrophysiological signals requires preserving not only sample arrays but also sampling clocks, channel types, events and legal data provenance. The EEG-BIDS proposal makes acquisition and event metadata an explicit part of a sharable EEG organization scheme [1], while the MNE-BIDS software provides an implementation path for BIDS organization in electrophysiology [2]. The NWB data standard offers a broader modular neurophysiology framework that can describe heterogeneous electrical and optical experiments [3]. Those two ecosystems should be interoperable where meanings align, but should not be conflated: an NWB extracellular ElectricalSeries need not represent conventional scalp EEG and its electrode ontology can be substantially different.

MNE-Python has established a widely adopted workflow for MEG/EEG analysis and commonly serves as an import/processing reference [4,5]. Still, reading file arrays is only one phase of scientific integrity. EDF physical units and heterogeneous sampling, FIF annotation origins, and NWB time-series conversion/offset semantics can alter downstream data interpretations when propagated incompletely. The PyNWB I/O documentation explicitly treats on-disk arrays as lazily indexed HDF5 datasets [6], making it possible to avoid eager whole-file loading but putting responsibility on adapters to retain file handles and respect data layout.

Spectral estimation provides a tractable computational invariant to audit because the scale of a PSD has an analytical unit and the expected peak position of a known sinusoid can be derived. Welch's periodogram-averaging procedure [7] and Thomson's multitaper work [8] motivate controlled contrasts of bias, variance and frequency resolution. Time/frequency inference is not automatically justified by observing a strong peak: cluster-based nonparametric EEG/MEG tests depend on exchangeability, familywise testing definitions, and experimental design [9]. Beyond signal processing, measurement and evaluation uncertainty must reflect genuine sampling units. Varoquaux shows that cross-validation error bars from small neuroimaging studies can be large [10]; Winkler and colleagues emphasize exchangeability-aware permutation inference [11]. EEGLAB provides a complementary, influential tool ecosystem for EEG preprocessing and time/frequency analysis [12].

This protocol therefore ties adapters, clock alignment, causal transforms and group-aware analysis to explicit, testable data-rights evidence. It tests software reproducibility first rather than implying any neural discovery. A positive *engineering* result would mean equality of outputs within justified machine-precision tolerance on identical signals, whereas a scientific population generalization requires separately sampled independent participants, documented exclusions and field-specific uncertainty methods.

## Design and pre-specified methods

**Population/materials:** Step 0: fully synthetic 10/20 Hz sinusoids with independently seeded noise, 200/256/512-Hz rates, 2/4/16 channels, event timing and ±100 ppm clock perturbations. Step 1 (requires approval): rights-reviewed openly licensed healthy-volunteer resting or task EEG with public data-use terms, non-identifying subject keys and preserved metadata; no participant-level clinical inference. Do not include unknown-license datasets. Acquire authorization and hash bytes before processing. Neither actual EDF/NWB public datasets nor mixed-rate equivalence have yet been tested.

**Adaption/transform:** Instantiate lazy MNE EDF/FIF and PyNWB ElectricalSeries readers with strict volts schema. Reject unsupported electrode types and irregular timestamps. Define one pinned canonical path using physical unit volts, sample timestamps in ns or rational sample ticks and explicit channel/electrode mapping. Apply average reference on specified channels then causal windowed lowpass FIR with carried filter state; omit auto-ICA/autorejection. Compare chunk sizes {1, 7, 64, 256, 333, 999, whole}. Record every input/source/license checksum, source version, seed, channel-mask, transform digest and QC flags.

**Primary outcomes:** (a) max absolute and RMS deviation V vs independent direct FIR convolution (shift/lag oracle), (b) peak-frequency location Hz, (c) PSD integrated power V², (d) alpha log band power deviation and PSD relative error, (e) event sample/clock drift, (f) percent rejects/unsupported rights/errors and worst-case memory/latency. Choose tolerance criteria separately for absolute V, floating point PSD, and event alignment. Do not use bitwise serialized hashes as proof of numeric equivalence.

**Design/separation:** Unit is source recording and subject; windows from the same subject or recording never cross predictive train/test partitions. For paired software-format differences, analyze within original recording; aggregating overlapping epochs as independent observations is pseudoreplication. Construct conditional subgroup slices by sample rate, device, format, event density and session. Freeze choices before running real data. Start with at least 3 independent groups per slice (diagnostic minimum only); full sample size target needs simulation with realistic within-participant variance.

**Statistics/uncertainty:** Preliminary bootstrap resamples group means, 500–2,000 draws for diagnostics; report nominal 95% percentile CIs and observed coverage on simulated data. Confirmatory study to use hierarchical/paired resampling and conditional equivalence assessment with preregistered margins, plus cluster/permutation correction for time-frequency *hypotheses*. Null controls: permute group labels independently by legitimate exchangeability blocks; shuffle EEG samples to destroy temporal structure; disconnect channels intentionally; inject clock/sample-rate mismatch, out-of-bounds events, voltage-unit mismatch and unauthorized files. Multiple-seed ablation separates alpha-channel reference choice and FIR response effects; no post-hoc selective exclusions.

**Replication artifacts:** Pinned environment manifest and lock, commands, source hashes, test logs, reader/clock masks, complete benchmark CSV, CI URL, unprocessed failure logs, synthetic-only case study, software license and third-party data rights ledger, independent senior-methodologist review. No identities or data exports by default.

## Claim–evidence matrix (draft)

| Claim | Primary basis | Status |
| --- | --- | --- |
| EEG interoperability requires metadata organization | [1], [2] | Source-checked conceptual basis; comparative experiment untested |
| NWB can encode diverse neurophysiology, lazy HDF5 | [3], [6] | Source-checked; PyNWB adapter not installed-tested |
| Welch gives modified-periodogram average PSD | [7] | Source-checked and synthetic SciPy smoke tested |
| Causal FIR chunk invariance when state carried | Direct FIR equation and test oracle | Synthetic locally tested; no real EDF/NWB claim |
| Group split leakage invalidates group generalization | [10], [11] | Leakage sentinels tested; no real cohort studied |
| Significance in EEG time-frequency requires correction | [9], [11] | Protocol proposal only |

## Disclosure and ethics

- This draft and synthetic software were prepared with AI assistance and must undergo human verification of code, source meanings, and prose before submission. No author identities, institutional access, collaborations or funding are invented.
- Software tests use deterministic simulated signals and fictional group labels; no IRB/ethics approval, informed consent or human subject data is involved in the existing prototype.
- Real EEG analyses require case-specific study ethics/data consent, license checks, restrictions on subject-identifiable data, and only permitted analysis/dissemination. Public access is not equivalent to redistributability.
- No results, empirical superiority, p-values, journal acceptance prospects, or participant-level conclusions are provided.

## Peer-review skepticism and replication memo

**Critical concern A:** Average reference depends on channel set and bad-channel exclusion; a change to the channel montage alters physical outputs before any format differences. Freeze montage and record missing/bad channels. **B:** MNE EDF may resample mixed rates and EDF+ annotations may be read eagerly; lazy acquisition does not mean bit-exact original sensor-rate retention. Record raw native rates or exclude these files; field-specific ontology required. **C:** NWB extracellular series metadata do not necessarily encode EEG scalp montage; prohibit mislabeling. **D:** Frequency peak at 10 Hz is nearly guaranteed by design; a useful null must vary and falsify the pipeline. **E:** Percentile bootstrap on eight fictional groups says nothing about human-data interval coverage. **F:** Sample-level permutations destroy temporal dependence and are not appropriate inferential nulls for EEG without careful design. **G:** Format conversion can be lossy (quantization/compression/rereferencing), so measured differences may be confounded with conversions. **H:** Duplicate real recordings across formats must be linked by source lineage and tested against genuine independent file re-exports; avoid cross-split duplicates.

**Independent replication request:** A reviewer should re-run clean-room Python 3.11/3.12 on pinned source, use a new seed not selected by authors, inspect numerical oracle correctness at n=1 and n=999, audit MNE `first_samp` annotation alignment, verify signed source rights and checksums, and manually review accessible keyboard/screen reader operation. Prefer reporting failures and countersamples; do not cherry-pick published fixtures.

## References: 12 checked works/documents

[1] Pernet CR et al. (2019). EEG-BIDS. *Scientific Data* 6:103. https://doi.org/10.1038/s41597-019-0104-8

[2] Appelhoff S et al. (2019). MNE-BIDS. *JOSS* 4(44):1896. https://doi.org/10.21105/joss.01896

[3] Rübel O et al. (2022). The Neurodata Without Borders ecosystem for neurophysiological data science. *eLife* 11:e78362. https://doi.org/10.7554/eLife.78362

[4] Gramfort A et al. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience* 7:267. https://doi.org/10.3389/fnins.2013.00267

[5] Gramfort A et al. (2014). MNE software for processing MEG and EEG data. *NeuroImage* 86:446-460. https://doi.org/10.1016/j.neuroimage.2013.10.027

[6] PyNWB, File Basics (documentation, not a primary research study). https://pynwb.readthedocs.io/en/latest/tutorials/general/plot_file.html

[7] Welch PD (1967). Use of FFT for estimation of power spectra. *IEEE Transactions on Audio and Electroacoustics* 15:70-73. https://doi.org/10.1109/TAU.1967.1161901

[8] Thomson DJ (1982). Spectrum estimation and harmonic analysis. *Proceedings of the IEEE* 70:1055-1096. https://doi.org/10.1109/PROC.1982.12433

[9] Maris E, Oostenveld R (2007). Nonparametric statistical testing of EEG- and MEG-data. *Journal of Neuroscience Methods* 164:177-190. https://doi.org/10.1016/j.jneumeth.2007.03.024

[10] Varoquaux G (2018). Cross-validation failure: Small sample sizes lead to large error bars. *NeuroImage* 180:68-77. https://doi.org/10.1016/j.neuroimage.2017.06.061

[11] Winkler AM et al. (2014). Permutation inference for the general linear model. *NeuroImage* 92:381-397. https://doi.org/10.1016/j.neuroimage.2014.01.060

[12] Delorme A, Makeig S (2004). EEGLAB: an open source toolbox for single-trial EEG dynamics. *Journal of Neuroscience Methods* 134:9-21. https://doi.org/10.1016/j.jneumeth.2003.10.009

Note: 11 primary research/software-method publications among the 12 sources (PyNWB documentation is supporting engineering context, not a primary study). These works establish rationale, not prospective study novelty nor verified claim of an unexamined result.
