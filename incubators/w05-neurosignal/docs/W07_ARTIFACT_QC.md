# W07 · Artifact QC, event-locked ERP and trace exploration

**Stage:** pre-week review candidate; W07 scheduled 2026-11-26. No human EEG, medical claims, publishing or external contribution. This extends W05/W06 P2 NeuroSignal Atlas + P14 EvalOps + P26 DSP.

## Dependency DAG and contracts

`synthetic recording (P2, rights: CC0 synthetic) → physical volts + integer sample events → P26 ordered sample clocks → W07 artifact epoch decisions → P2 aligned ERP / minmax trace → authenticated local FastAPI and same-origin keyboard button → browser SVG`.

The artifact acceptance operator is **all channels pass** peak absolute voltage <=120 µV and peak-to-peak <=180 µV; both thresholds are nonclinical placeholders, not EEG diagnostic cutoffs. The epoch `[sample - pre_samples, sample + post_samples)` is sample-locked; no interpolation of fractional events, baseline correction or re-reference is applied. Out-of-range events are counted and omitted; all-rejected/none-in-range raises a failure rather than fabricating a result. SEM of one retained epoch is NaN in Python; JSON API must not claim finite error bars (current API may need refusal or masking for single-epoch data). Error bars across events are not participant-level confidence bands, because repeated events are dependent within recording.

The extrema-based decimator preserves each bin's minimum and maximum but the alternating min/max sequence may distort temporal order. Treat this as an exploratory envelope, not a reconstructed waveform.

`POST /v1/artifacts/synthetic`: strict request version inherited from W05 `JobRequest`, bearer token and configured single local tenant. Samples max 8192, first channel max 256 bins → at most 512 plotted points; no file upload, and no direct identifiers. Browser provides keyboard-operable button and aria-live status, but real assistive-technology/browser E2E tests are **NOT** claimed.

## Scientific oracle/negative controls

Synthetic 12-µV event peak at sample event+3 verifies integer alignment at 100 Hz and physical volts; independent direct array indexing is the reference. Inject 121 µV absolute and ±95 µV peak-to-peak artifacts; require rejection on explicitly specified threshold crossings. Test events near both boundaries, all-invalid epoch, NaN failure, exact zero SEM for identical retained waveforms, 4-V synthetic sample spike preservation under display decimation. CI needs exact commit logs. No real-world sensitivity/specificity has been estimated.

## Research manuscript progression

Working title: **"How do artifact thresholds and event alignment rules alter the reproducibility of event-related EEG summaries? A falsifiable, synthetic-first validation protocol."** Introduction: artifact thresholds and event timing can change which trials enter an average and hence the estimate. Threshold-based rejection trades contamination risk against selection bias; missingness can be stimulus- or recording-dependent. A sample-indexed ERP estimator is easy to falsify on synthetic known-latency events, but synthetic pass results cannot establish robustness on scalp EEG. Methods: generate seeded four-channel simulated volts, define event indices a priori, flag epochs with channel-maximum absolute / peak-to-peak thresholds, report accepted/rejected/boundary exclusions and compute uncorrected mean and SEM; compare to a direct independent NumPy epoch average and adversarial artifact injection. Do not fill Results section without executed CI and observed metrics. Scope excludes human inference.

Methodological reference leads (verification of complete bibliography and version-specific applicability remains pending):
- Luck, *An Introduction to the Event-Related Potential Technique*, second ed. (2014), MIT Press, https://mitpress.mit.edu/9780262525855/an-introduction-to-the-event-related-potential-technique/
- Delorme & Makeig (2004), EEGLAB, https://doi.org/10.1016/j.jneumeth.2003.10.009
- Gramfort et al. (2013), MNE, https://doi.org/10.3389/fnins.2013.00267
- Pernet et al. (2019), EEG-BIDS, https://doi.org/10.1038/s41597-019-0104-8
- Bigdely-Shamlo et al. (2015), PREP, https://doi.org/10.3389/fninf.2015.00016
- Jas et al. (2017), autoreject, https://doi.org/10.1016/j.neuroimage.2017.06.030
- Winkler et al. (2014), permutation inference, https://doi.org/10.1016/j.neuroimage.2014.01.060
- Maris & Oostenveld (2007), cluster permutation, https://doi.org/10.1016/j.jneumeth.2007.03.024
- Varoquaux (2018), CV instability, https://doi.org/10.1016/j.neuroimage.2017.06.061

## GA1–GA8 scoped dossier

GA1 bibliography leads above, **not a systematic completed search**; GA2 falsifiable manuscript methods and explicit exclusion policy above; GA3 potential upstream contribution: prepare test demonstrating absolute-threshold rejection at event epochs where source channel units are volts (MNE-Python event/epoch rejection docs), no submission or claim of maintainer interest; GA4 inspect eligibility for official PhD/research routes Aalto https://www.aalto.fi/en/study-at-aalto/doctoral-programmes , UCL Gatsby https://www.ucl.ac.uk/life-sciences/gatsby/study-and-work/gatsby-unit-phd-programme , and Max Planck https://www.mpg.de/doctoral_students — specific funding/positions are not verified; GA5 **unsent** methods-group invitation draft: "I am developing a synthetic-first protocol for event-alignment and artifact threshold QA; could you challenge the assumptions around dependent trials and threshold-induced selection? I can share a small reproducible negative-control notebook and the error ledger." No named person selected or contacted. GA6 case study/CV draft: "Built a synthetic EEG artifact/ERP QC workflow with event alignment, explicit rejection gates and authenticated trace visualization, plus hosted tests [link only once verified]." Educational video hook: *An EEG average can look cleaner because you removed contaminated trials—or because your threshold silently selected a different population.* GA7 reproduce with independent manual epoch slices, compare sample-indexed onset peak and threshold boundary; GA8 skeptical memo: no verified human data rights, amplitude criteria context-sensitive, trial SEM ignores participant clustering, no direct browser accessibility proof, no realistic load or release readiness.

## Gate assessment

E1 artifact module partial (tested if CI); E2 browser partial; E3 grouped per-recording fairness **not done**; E4 Parquet/JSON open manifest/provenance export **not done**; E5 W05 DSP reused; E6 synthetic oracle partial; E7–E8 W05 lineage/job reused but not integrated for W07; E9 API tests partial and real browser blocked; E10 benchmark unperformed; E11 local single-tenant guard/API negative tests partial; E12 Python hosted CI partial and locks/deploy/rollback pending; E13 three-system full W07 workflow incomplete; E14 this review memo partial.

**Release boundary:** GO only for review/merging isolated synthetic nonclinical code with successful CI. No clinical/real EEG/production readiness. W07 Done must remain unchecked. Human total focused work <=10 hours/day across Academy and Career; continue existing R course when scheduled; optional three educational videos/week drafts only.
