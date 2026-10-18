# PM-37 — four genuine primary-neuroscience figure evidence cards (source audit)

Prepared 2026-10-18. **All four figures below were checked against the figure captions and surrounding methods/results in the original publisher article**, not generated for OpenBench and not reproduced as image files. Source: International Brain Laboratory et al. (2025), *A brain-wide map of neural activity during complex behaviour*, Nature 645, 177–191, [DOI 10.1038/s41586-025-09235-0](https://doi.org/10.1038/s41586-025-09235-0), [full primary publisher article](https://www.nature.com/articles/s41586-025-09235-0). Publisher marks article CC BY 4.0 subject to figure-specific third-party credit exceptions. Images have **not** been copied.

## Figure 1 — IBL task, behavioural trial units and reaction-time censoring

Primary source: [Nature 2025, Fig. 1](https://www.nature.com/articles/s41586-025-09235-0#Fig1).
- **Question:** How is correct choice/reaction time related to stimulus contrast and block prior? Participants are **139 mice**, not 459 independent people; some panels summarize **459 sessions**, Fig. 1d uses **454 sessions**, and each mouse contributes repeated trials.
- **Panels/axes:** Fig. 1c reaction-time histogram, stimulus-to-first-wheel-movement duration **milliseconds/seconds**, restricted to 80 ms–2 s in analysis; 22.8% first movements occurred before 80 ms and are explicitly outside the plotted range. Fig. 1d performance versus visual stimulus contrast; upper y correct-choice proportion, lower y first wheel-movement time, one dot per mouse per contrast. Fig. 1g reversal curve by trial distance from prior block switch; Fig. 1h right-choice probability by signed contrast.
- **Uncertainty:** Fig. 1d reports 0%-contrast performance 58.7% ±0.4% **mean±SEM across mice**, not across trials; other panels mean±SEM where caption says so. Contrast with 81.4%±0.4% (mean±SD) across trials in main text; never confuse SD with SEM or trial count with n animals.
- **Threats/limitations:** Truncated reaction times exclude a meaningful early-event fraction; task structure and repeated measures create within-mouse dependence; no causal statement about cognition from a plotted correlation alone. Connection to OpenBench: explicit source/censoring and group-identity reporting, **not equivalent data**.

## Figure 2 — brain regions, electrode sampling and measurement selection

Primary: [Nature Fig. 2](https://www.nature.com/articles/s41586-025-09235-0#Fig2).
- **Question:** Where and how many well-isolated neurons were recorded relative to total observed units? Fig. 2a anatomical Neuropixels insertions and 3D brain map; Fig. 2b region on categorical horizontal grouping, horizontal **number of recorded units** as full bar length, **number well-isolated** in filled bar, 10% reference line. Fig. 2c anatomical flatmap region abbreviations, not a scale-free causal network.
- **Sample/source:** 699 probe insertions across 139 mice in 12 laboratories; 621,733 detected units, but only 75,708 well-isolated neurons by explicit quality-control criteria. Analysis further filters coverage by sessions and neurons per region.
- **Uncertainty/limitations:** Variable probe placement, recording and spike-sorting yield; occupancy of larger regions correlates with sampling opportunity. Bars are counts, **not confidence limits or activation strength**. Missing/white regions not proof of zero neural activity, and isolated-unit filtering may bias representation. No known human dataset included.
- **Not justified:** Treating all 621,733 units as independent high-quality neurons or all insertions as independent animal samples.

## Figure 3 — four distinct analyses and temporal windows

Primary: [Nature Fig. 3](https://www.nature.com/articles/s41586-025-09235-0#Fig3).
- **Question:** What different claims can neural decoding, conditional single-neuron statistics, trajectory distances and encoding analyses support? Panels 3b–e are analysis **schematics**, not directly comparable plotted effect sizes.
- **Variables/methods:** (b) spike-count predictors and regularized logistic/linear decoding of task variables; (c) conditioned Mann–Whitney-style single-cell comparison to control correlated stimulus/choice/block factors; (d) trial-averaged high-dimensional neural trajectories, projected in three principal visualized dimensions; distance between condition trajectories defines separation; (e) time-aligned kernel linear encoding. Grey time windows define timing relative to stimuli, movements or outcomes.
- **Axes/uncertainty:** schematic time and spike response; projected 3D axes are visualization dimensions, not independently validated biological axes. Authors employ permutation/null reference tests and multiple-region Benjamini–Hochberg **FDR 0.01** in later quantified figures. Fig. 3 itself cannot establish an error bar.
- **Limitations:** Decoding may carry information from correlated choice/block variables, whereas conditional univariate tests have different power. Comparing the significance of these four methods by appearance alone would be inappropriate.

## Figure 4 — visual stimulus coding and corrected inference

Primary: [Nature Fig. 4](https://www.nature.com/articles/s41586-025-09235-0#Fig4).
- **Question:** Where does neural activity predict or represent stimulus side between **0 and 100 ms after stimulus onset**, and with what conditions? Fig. 4a flatmap colour represents **null-corrected median balanced accuracy (0–1 unitless)**, NOT raw firing rate. Fig. 4b significant-cell fractions per region; Fig. 4c trajectory separation has **spikes/second** per specified dimension on **log10** scale. Fig. 4d separation latency (time relative to stimulus). Fig. 4e improvement in model R² (unitless).
- **Sample/plot units:** Authors' canonical analysis includes 201 regions and 62,857 well-isolated neurons with region/session eligibility restrictions. Fig. 4i shows decoded stimulus-side probabilities with **95% confidence intervals over 474 trials** for an example of **40 VISp neurons**. Those trials are repeated within sessions, not 474 independent mice.
- **Uncertainty and multiple comparison:** Regions marked grey fail FDR 0.01 after correction; white regions not analysed. Fig. 4h shaded PETH curves reflect ±1 SEM (as stated by publisher); Fig. 4i is its own interval definition, which cannot be transposed into CI for a human population. Shuffle controls appear in Fig. 4c, j and k.
- **Confounding:** Authors explicitly caution that unconstrained decoding of stimulus can also reflect correlated animal choice/block state. Single-cell conditional analysis tries to control this but has different statistical power and assumptions; no new cause established by correlations alone.
- **OpenBench lesson:** annotate variable timing and independent animal/session/neuron/trial unit before choosing a predictive split. Do not mistake full-brain decode maps as published OpenBench results.

## Evidence classification and limits

These four are **actual, primary-paper publisher-caption-grounded figure audits**, not assistant-created replacement figures, not downloaded images, not independently regenerated underlying mouse analysis. All axis/uncertainty interpretations are from the published captions and accompanying text checked 2026-10-18. Reproduction of graphs from raw neural data **NOT RUN**; no public dataset downloaded, no participant/mouse recording ingested into OpenBench, no human studies and no claimed consent/rights inference.

**Review checklist:** check figure page anchor resolves; confirm exact sampled unit and time interval, panel-defined outcome unit, correction and SD/SEM/CI definitions; preserve conflicts between panels rather than invent universal n; check third-party material-specific rights before redistributing a source image. Four figure cards satisfy the Week 2 source-audit deliverable; visual/data-reproduction work is separate and remains NOT RUN.
