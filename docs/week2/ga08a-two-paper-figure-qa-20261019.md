# GA-08A: original-figure QA supplement — 2026-10-19

**Status (updated 2026-10-19 after reviewer approval):** **Verified Done — GA-08A research artifact only.** Original-source figures independently rechecked; learner mastery, original experimental replication and personal article reading **NOT VERIFIED**. Existing Week 2 dossier: [GA-08A–GA-10B](ga08a-ga10b.md). No new mission, human data, recruitment or external correspondence. This is a **private-branch** literature-reading supplement, not an original study or published finding.

## Why this supplement exists
The GA-08A Notion mission (2026-10-22 flexible queue) and its 2026-10-18 research report identified two published original studies but explicitly left **exact figure panels and preparation counts** for direct inspection. These details are now checked against scans of the original publications, not against textbooks or secondary summaries.

## Source and figure reading matrix

| Category | Hodgkin and Huxley (1952) | Neher and Sakmann (1976) |
| --- | --- | --- |
| Peer-reviewed citation | Hodgkin AL, Huxley AF. *A quantitative description of membrane current and its application to conduction and excitation in nerve.* *J Physiol* 117(4):500–544; DOI [10.1113/jphysiol.1952.sp004764](https://doi.org/10.1113/jphysiol.1952.sp004764). Journal date **28 Aug 1952**. | Neher E, Sakmann B. *Single-channel currents recorded from membrane of denervated frog muscle fibres.* *Nature* 260:799–802; DOI [10.1038/260799a0](https://doi.org/10.1038/260799a0). Nature issue **29 Apr 1976** (online record lists 1 Apr 1976). |
| Primary original document read on **2026-10-19** | [University-hosted original PDF, printed pp. 500–544](https://isn.ucsd.edu/courses/beng207/reading/Hodgkin_Huxley_1952_jp.pdf); [publisher identity](https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.1952.sp004764). | [University-hosted original four-page Nature PDF](https://cenl.ucsd.edu/psych506A/papers/neher-sakmann%2Bsingle-channel-currents-membrane-denervated-frog-muscle%2BNature%2B1976.pdf); [publisher identity](https://www.nature.com/articles/260799a0). |
| Question | Do voltage/time-dependent sodium and potassium conductances quantitatively account for excitation, refractoriness and propagation in a giant nerve fibre? | Can lower-noise recordings from a small membrane patch resolve elementary ACh-receptor channel-current events? |
| Sample and eligibility | Squid (*Loligo*) giant axon electrophysiology from the published study series. **Fig. 3: axon 17**, temperature **6–7 °C**, sea water/choline sea water; **Fig. 2: axon 18**, **21 °C**. **UNKNOWN**: total distinct squid preparations across the study series. The **12 traces A–L are voltage conditions on an identified axon, not 12 independent animals**. | Chronically denervated hypersensitive **Rana pipiens** cutaneus pectoris muscle, extrasynaptic membrane. **Fig. 3a**: traces from **three different experiments**; **Fig. 3b**: **eight experiments pooled**; **Fig. 3c**: **eight histograms averaged**. Conductance mean **22.4 ± 0.3 pmho** (mean ± SE; **27 determinations**). These counts have different denominators; number of *individual frogs* and within-frog dependence **UNKNOWN**. |
| Design / recorded quantities | Model-fitting/mechanistic account using macroscopic voltage-clamp-derived ion currents and time-dependent conductance. Independent variable: membrane voltage/time; response: potassium/sodium conductance, model action-potential behavior. Observed circles vs fitted curves. | Small glass pipette electrode (Fig. 1: 3–5 µm opening) with two-microelectrode clamp, agonists ACh/SubCh/carbachol, local conductance sensitivity. Responses: discrete membrane current, current-step amplitude, event frequency, inferred open time. Figure 2: **~10 µm² patch, −120 mV, 8 °C, 200 Hz**, direct single-patch trace. |
| **Main figure** | **Fig. 3 printed p. 508**, **Eq. (11)** and **Table 1 p. 509**: circles are experimental points for axon 17; smooth curves are voltage-dependent fitted conductances. Upper 10 curves share ordinate; lower 2 are shown at 4× larger scale. Authors explicitly note experimental initial-delay mismatch. | **Fig. 3a–c printed p. 801**: a=SubCh/ACh/carbachol traces; b=event frequency vs sensitivity (8 experiments; stated **r=0.91**, t-test significance “better than 0.1%”); c=amplitude histogram from digitized **4-s** records, using by-eye baseline fitting, eight averaged histograms. Figure 2 printed p. 800 is the direct large current trace. |
| Further reported uncertainty | Fitted parameters presented in Table 1, but formal biological-replicate confidence interval and fit covariance for Fig. 3 **UNKNOWN**. Authors on p. 506 warn physical interpretation of model equations may be incorrect; p. 509 notes early mismatch and parameter pragmatism. | Mean open duration at −120 mV, 8 °C: SubCh **45 ± 3 ms (n=11)**; ACh **26 ± 5 ms (n=4)**; carbachol **11 ± 2 ms (n=3)**. SubCh at −80 mV **28 ± 3 ms (n=14)**. Counts refer to author's determinations, **not verified number of independent frogs**. Authors consider uneven current amplitude due to channel placement or measurement artifacts. |
| Inference and counterexample | Macro conductance dynamics can approximate a squid axon but do **not** directly observe molecular gating or uniquely identify microscopic channel states. | Small-patch traces are consistent with discrete agonist-gated channel openings, but artifacts/noise or incomplete current capture could affect measured amplitudes, and muscle-receptor traces do **not** independently validate propagating action potentials or human neuron physiology. |
| Ethics, rights and reproducibility | Historical invertebrate experiments; retrospective ethics approval and raw machine-readable recordings **UNKNOWN**. **No scanned figures or raw PDF copied into this repo.** | Historical vertebrate experiments; retrospective animal-care approval and complete raw traces/frog-level allocation **UNKNOWN**. The Nature PDF bears publisher copyright: **no figure redistribution without valid reuse permission**. |

**Unit-of-analysis QA:** Neither a plotted voltage trace nor an individual current opening automatically constitutes an independent biological replicate. The studies have different species, preparations, endpoints, and estimands; **do not pool or claim independent replication**.

## Independent numerical check of the published correlation

For **eight experiments** and **reported rounded r=0.91**, ordinary Pearson-to-Student test:
`df=n−2=6; t=r·sqrt((n−2)/(1−r²))≈5.3762`. Two-sided `p≈0.0017017`; one-sided `p≈0.0008508` (standard Student-t tail). The article reports “better than 0.1%” (p<0.001). This **agrees with a one-sided test on rounded input**, not a standard two-sided test on those rounded inputs. Test sidedness, unrounded correlation, and exact original test details: **UNKNOWN**. Do not call this a new biological result or proven author error.

Dependency-free reproducibility snippet:
```python
import math
r, n = 0.91, 8
df = n - 2
t = r * math.sqrt(df / (1 - r*r))
def pdf(x):
    c = math.gamma((df+1)/2) / (math.sqrt(df*math.pi) * math.gamma(df/2))
    return c * (1 + x*x/df)**(-(df+1)/2)
k = 10000
h = t/k
area = h/3 * (pdf(0) + pdf(t)
    + 4*sum(pdf(i*h) for i in range(1,k,2))
    + 2*sum(pdf(i*h) for i in range(2,k,2)))
p2 = 1-2*area
assert 5.37 < t < 5.39
assert 0.0016 < p2 < 0.0018
print(f"t={t:.5f}, df={df}, two-sided p={p2:.7f}, one-sided p={p2/2:.7f}")
```

## Independent acceptance / human review gates

- [x] Verified **two original peer-reviewed publications** by DOI/publisher identity; OpenStax [section 5.2](https://openstax.org/books/biology-2e/pages/5-2-passive-transport) is **background, not a primary article**.
- [x] Verified **exact HH Fig. 3** (printed p. 508) and **Neher/Sakmann Fig. 3a–c** (p. 801) against primary scanned pages.
- [x] Figure denominators/temperature recorded and contrast in scale made explicit.
- [x] Independent rounded-statistic arithmetic performed, with numerical test and test-direction limitation.
- [x] **Artifact review authorization received from user on 2026-10-19.** Independent paper/figure/caption and inference QA performed by assistant; this does **not** establish that the user personally read the original figures.
- [ ] Access to original preparation-level full sample list, raw recordings, model fit uncertainty and original correlation-sidedness: **UNKNOWN**.
- [x] Verified the artifact makes **no claim** of learner mastery, research publication, formal education, experimental replication or endorsed interpretation.

**No external contacts, dataset downloads, direct human/animal experimentation, manuscript submission, new PR, merges, public release, or modification of the read-only Neuroscience Academy.** This is evidence for a private draft in the Career Lab, not academic endorsement.

## Final independent evidence acceptance — 2026-10-19 (supersedes former Needs Review artifact label)

**Verdict: GA-08A research-reading deliverable VERIFIED DONE; human neuroscience mastery NOT ASSESSED.** The user explicitly approved finishing the existing mission. Reviewer approval authorizes updating the artifact and its Notion evidence status; it is not evidence that they personally inspected or independently replicated these historical experiments. No other Career/Academy task status changes.

**Second-pass evidence read:**
1. [Hodgkin & Huxley 1952 original PDF](https://isn.ucsd.edu/courses/beng207/reading/Hodgkin_Huxley_1952_jp.pdf#page=9), PDF p. 9/printed p. 508 Fig. 3 directly labels **axon 17**, **6–7 °C**, observed circles vs Eq. (11) curves A–L; [PDF p. 10/printed p. 509](https://isn.ucsd.edu/courses/beng207/reading/Hodgkin_Huxley_1952_jp.pdf#page=10) describes the **initial-delay model mismatch**, and Table 1's chosen parameters. Hence neither twelve voltage conditions nor individual time observations should be counted as twelve independent axons.
2. [Neher & Sakmann 1976 original Nature scan](https://cenl.ucsd.edu/psych506A/papers/neher-sakmann%2Bsingle-channel-currents-membrane-denervated-frog-muscle%2BNature%2B1976.pdf#page=3), PDF p. 3/printed p. 801 directly labels **Fig. 3a** three different experiments (three agonists), **Fig. 3b** eight pooled experiments, **Fig. 3c** eight averaged histograms; the text lists **27 conductance determinations**, not 27 frogs. [PDF p. 2/printed p. 800](https://cenl.ucsd.edu/psych506A/papers/neher-sakmann%2Bsingle-channel-currents-membrane-denervated-frog-muscle%2BNature%2B1976.pdf#page=2) describes the frog muscle preparation and patch electrode.
3. **Independent computational QA actually executed on 2026-10-19:** re-ran the dependency-free Simpson-integral check in this file's source matrix, and cross-checked with SciPy's Student-t survival function available in the assistant's isolated runtime (no user installations). For published rounded `r=0.91, n=8`: `t=5.3762453`, `df=6`, `two-sided p=0.001701696`, `one-sided p=0.000850848`; both methods agreed within displayed precision. Paper reports significance better than 0.1%; exact historical sidedness/unrounded r **UNKNOWN**. This is a consistency review, not original data reanalysis or proof the authors erred.

**Unknowns retained transparently:** full independent squid-axon and frog-animal counts, underlying raw recordings/fit covariance, original t-test convention and present-day animal ethics documentation. They are **not prerequisites to an honest annotated primary-literature matrix** when labeled as unavailable; no values imputed. No original copyrighted figure/pdf or real experimental data copied or redistributed. Original read-only Neuroscience Academy remains untouched. No third-party outreach, human/animal experiment, paper submission, merge or public posting.

**Acceptance criteria passed:** two real peer-reviewed primary journal studies with verified DOIs; source dates and direct links; questions, preparation/sample *as reported*, experimental design and main panels; limits and counterexamples; distinction of pooled vs independent units; executable and observed numerical QA; explicit rights/ethics guardrails; explicit learner-mastery boundary. **No further user action is required for this source-reading deliverable.**
