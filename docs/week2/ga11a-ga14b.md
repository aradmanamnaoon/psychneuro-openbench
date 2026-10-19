# Week 2 GA-11A through GA-14B — verifiable career, replication and manuscript foundations

Internal evidence prepared 2026-10-18 for the flexible 2026-10-25 to 28 calendar queue. AI-assisted educational artifacts; NO outreach, real user feedback, validated learning, real human-study results, journal submission, profile update, funding, or adoption. Website sources checked 2026-10-18; unknown details stay unknown.

## GA-11A — Private portfolio proof index

| Claim | First-party evidence | Boundary |
| --- | --- | --- |
| Reproducible synthetic-only OpenBench source/test execution | [W01 passing CI #39109383260](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39109383260), code SHA 2479f0d322b3179c30b64673f8beac584a4ba162 | 318 tests in Python 3.11/3.12, Ruff and mypy; NOT an external validation of neuroscience. |
| New W02 software-controlled simulated experiments | [W02 passing CI #39111357989](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111357989), code SHA 36dbf9a8c37e8f5bf55576dd7f8456433d5b1c81 | 335 tests in 3.11/3.12, 10 private CI archives; conditional cluster bootstrap and frozen-prediction permutation tests, not real-population inference. |
| Review-ready case study, QA and source audit | [Private case study](../case-study.md), [PM19](../pm19-independent-qa-2026-10-18.md) and [PM20](../pm20-competitive-release-gate-2026-10-18.md) | Internally prepared and AI-assisted; no publisher, real sample or referee acceptance. |
| Recognized public release, researcher response, scholarship award, recruitment, accepted OSS contribution | NONE VERIFIED | No profile claim or recognition should be created. |

Exact source versions matter: W02 code SHA is not W01 SHA. This is a private link-only index; no public personal profile changed.

## GA-11B — Three official-source computational neuroscience research group fit cards (no contact)

| Lab/organization (official website) | Methods and accessible source | Fit and counterexample |
| --- | --- | --- |
| [International Brain Laboratory / IBL Core](https://www.internationalbrainlab.com/) | [IBL Brainwide Map and data](https://www.internationalbrainlab.com/data): multisite mouse behavioral decision task and Neuropixels recordings with public documentation; original IBL site says superseded in Jan 2026 by IBL Core. | Strong conceptual fit for metadata harmonization and group/site validation; no permission inferred to treat public mouse neural data as original OpenBench fictional human-style trials. Check current IBL Core page and explicit data licences before a future analysis. |
| [Kording Lab, University of Pennsylvania](https://kordinglab.com/) | Computational neuroscience, causality, ML and mechanistic explanation, official lab materials. | Strong methodology fit; **counterexample to funding claims:** [Join page](https://kordinglab.com/join/) currently says lab is not hiring; visiting positions need their own funding and at least six months. No invitation or funding guaranteed. |
| [Allen Institute](https://alleninstitute.org/open-science) | Official open-science programme offers neural atlases, cell type data, methods/models; [resources](https://alleninstitute.org/science-resources). | Data curation/provenance fit; distinct from benchmarking original synthetic correctness on fictional trials, and not proof any Allen source may be redistributed in OpenBench. |

This is a private comparison, NOT a collaboration, reply, email, lab admission or endorsement.

## GA-12A — Focused falsifiable nonclinical question and measurement table

**Question:** Under a fixed synthetic repeated-trial generator, does an invalid row-wise split which places the same fictional participants across training/evaluation inflate apparent held-out balanced accuracy relative to a genuinely participant-disjoint split?

- Population: fictional participants only; exact generator revision, n participants, trials/participant and independent seed list fixed in advance.
- Treatment/exposure: subject leakage induced only in an explicitly isolated adversarial stress harness; canonical production split must still fail closed.
- Outcome: balanced accuracy (0–1 unitless) primary; macro F1 (0–1) descriptive secondary; prevalence support and per-participant fold sizes disclosed.
- Independence unit: fictional participant; multiple trial rows are NOT extra independent subjects.
- Possible confounders: differing train size, class imbalance, per-participant signal, preprocessing, model tuning, seed changes, source hash and temporal predictor availability.
- Falsification: no consistently positive leakage-induced difference across predetermined paired synthetic seeds or wide intervals compatible with no effect; never suppress negative evidence.
- Predeclared analysis: paired seed comparison with matching split sizes, same model and fold-selection policy; no inferential claim about humans.
- **Not yet executed:** The current Week 2 production tests verify leakage guards, not a full paired *intentional leakage inflation* experiment. This difference is recorded rather than inventing results.

## GA-12B — Practice methods communication draft (not a submitted paper)

PsychNeuro OpenBench is a **synthetic-only, nonclinical, versioned software testbed**. Records arise from a seeded toy generator and contain a stable fictional participant identifier; all train/validation/test assignment operates on complete participant groups rather than rows. Predictors are available before the outcome, while response, correctness and response time are excluded from pre-response inputs. An interpretable logistic regression model and a dummy-prior baseline are compared by training-only cross-validation, and balanced accuracy/macro-F1 are used as descriptive metrics; undefined support is reported rather than silently imputed. Independent seed repetitions yield synthetic-cohort descriptive uncertainty, not human or participant bootstrap confidence intervals. A Week 2 helper additionally demonstrates conditional **fixed-prediction** group bootstrap with at least ten fictional groups, suppresses the five-person held-out test example, and provides a label-permutation diagnostic that holds predictions fixed. It is not full model-refit uncertainty, a formal significance test or proof of clinical utility. Code, configuration, environment-sensitive hashes and GitHub CI logs support reproducibility within the declared source settings; a checksum of an uploaded report is not an authenticated provenance certificate. Artificial generated record export licence is still under review, and external participant records remain disabled. AI assistance contributed to implementation and drafting; independent scientific findings are not claimed.

Sources: [W02 GitHub CI](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111357989), [Week 2 code](../../src/psychneuro/week2_controls.py), [W01 CI](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39109383260). This is a practice passage, not W05 manuscript drafting.

## GA-13A — Replicability gap table for one accessible primary study

Selected paper: [Hodgkin & Huxley 1952](https://doi.org/10.1113/jphysiol.1952.sp004764); [original article PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC1392413/).

| Modern reproduction requirement | Evidence and gap |
| --- | --- |
| Stable provenance | DOI, authors, journal, date, PMCID verified. Historical apparatus and figure panel details should be extracted from full primary pages before a replication plan. |
| Raw observed data | Original 1952 article accessible, but a modern ready-to-download raw dataset has NOT been located/verified in this exercise. This does not prove no raw record exists. |
| Original executable code | No runnable 1952 source/code distribution verified. A modern implementation would be a subsequent independent model, not automatically authors' original. |
| Units, parameters, solver and held-out comparison | Voltage, current, conductance, time/temperature and numerical solver conventions require exact tabulation; comparing graphs without units/version checks would be inadequate. |
| Allowed reproduction comparison | Preselect a rights-cleared modern solver implementation, compare predicted ionic current/action-potential traces with primary empirical curves, disclose digitization uncertainty and separate numerical vs biological validity. |
| Actual reproduced result | **NOT RUN**. No HH simulated result, fit metric or replication of published conclusions has been generated here. |
| Relationship to OpenBench | Both projects value method transparency but the axon membrane model does not validate the current fictional behavior classification project. |

The gap table satisfies the research-method reading task, not empirical replication.

## GA-13B — Two tailored, **UNSENT** expert-feedback request drafts

**Draft 1 — MNE-Python #13406 methods documentation reviewer** (prepared, not sent):
Subject: A small human-reviewed documentation check on independent axes and cluster permutation methods
Hello. I am preparing a private, synthetic-only methodology learning exercise and saw the open [MNE documentation consistency issue #13406](https://github.com/mne-tools/mne-python/issues/13406). Would it be useful for a contributor to prepare a personally verified table clarifying the first observation dimension and the independent units assumed by the tutorial and API, with one minimal runnable example? I understand the project [prohibits fully automated AI-generated submissions](https://github.com/mne-tools/mne-python/blob/main/CONTRIBUTING.md), so I would not submit generated text or code without personally reviewing, understanding, testing and accurately disclosing assistance. This is only a draft; no message has been sent.

**Draft 2 — MOABB #1307 loader contributor/maintainer** (prepared, not sent):
Subject: Metadata-only regression test idea for Wang2016 advertised participant list
Hello. While preparing a group-aware synthetic benchmarking exercise I noticed [MOABB issue #1307](https://github.com/NeuroTechX/moabb/issues/1307) reporting that Wang2016's declared 35 participants and an implementation returning 34 differ. Before proposing anything, which upstream source should control whether S35 belongs in the current supported release? Would a small metadata-only assertion help prevent unintentional truncation without fetching or modifying human participant data? I would review the current loader, project contribution rules and tests before any submission. No message has been sent.

Neither text implies affiliation, guaranteed expertise, maintainer interest or reply. Two review-ready drafts ONLY.

## GA-14A — Week 5 manuscript component-readiness audit rubric

- [ ] Narrow falsifiable nonclinical paper question and actual paper type identified (conceptual review/methods/preregistered simulation/replication, not fabricated human empirical study).
- [ ] At least five primary sources are actually read and independently checked, with correct DOI, access/edition date, experimental units, methods and limitations. This five-source minimum is an internal preparation threshold, not a journal rule.
- [ ] Search strings, databases, inclusion/exclusion criteria, sources and rights recorded before drafting evidence claims.
- [ ] Study design or synthesis plan specifies analysis unit, independent folds, seed and uncertainty interpretation; absent raw authorised data means omit empirical findings.
- [ ] Ethics/consent/secondary reuse/participant confidentiality and research permits verified if real participants are implicated.
- [ ] All tables/figures derive from actual cited measurements or explicitly synthetic results, never inferred screenshots or unsupported graphics.
- [ ] Methods have versioned source, exact build/setup, a linked passing actual run and limitations, plus independently reviewable code.
- [ ] AI contribution disclosed for literature assistance, programming, analysis, writing, revisions, diagrams and source checks; AI not listed as human author.
- [ ] Journal format/current policy/fees/eligibility and actual approval independently checked before submission.
- [ ] No public promotion, DOI, acceptance claim or affiliations without confirmed evidence.

Week 2 satisfies part of the methods and citation-preparation work only. No Week 5 manuscript has been authored by this exercise.

## GA-14B — Initial evidence scorecard (dated 2026-10-18; scheduled Week 2 is 22–28 Oct)

| Evidence category | Status | Source/next action |
| --- | --- | --- |
| GA evidence artifacts 08A–14B | **PREPARED** | Two private reports, primary source URLs and explicit fact/unknown labels, pending academic review. |
| Week 2 code tests | **HOSTED VERIFIED** on exact tested code | [run #39111357989](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111357989): 335 pytest PASSED each in Python 3.11/3.12, Ruff & mypy pass, 10 real archives. |
| Browser/screen-reader/live demo | **NOT RUN** | No authorized private deployment and no B01–B20 real observed accessibility/browser matrix. |
| Scientific/clinical efficacy, independent new empirical neuroscience discovery | **NOT ESTABLISHED** | All experiments are fictional-data software tests. |
| Human study compliance and rights to redistribute external data | **BLOCKED** | Six external dataset sources disabled; original synthetic generated-export licence not explicitly issued. |
| Real career impact (funded admission, job, citation, accepted PR, mentors) | **UNKNOWN / NONE VERIFIED** | No external outreach, reply, scholarship, university admission or paid arrangement observed. |
| Human Academy study/learning | **NOT VERIFIED** | This AI-created ledger does not mark lesson progress; Academy left unchanged. |
| Public communications/profile updates | **NONE** | No posting/public release performed. |

**Carry-forward into W03:** generated-data licence approval; real private browser accessibility/privacy run; independent mixed-seed replay/lockfile attestations; prospectively defined genuine null/shift experiments; full figure reading and source-rights check; private credential/programme verification; personal upstream policy-compliant review. If W03 is generated later, avoid creating duplicates of these source-backed deliverables.

**Decision:** prepared source-backed Week 2 career/academic evidence; actual external outcomes, education progression and research publication remain unverified. AI-assisted preparation is disclosed.

## CI proof reconciliation (2026-10-18)
The current tested Week 2 source is commit `dd79565e07923b35db7a7f09e0724a8c0594158e`, with [GitHub Actions #39112127659](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39112127659) **both Python 3.11/3.12 SUCCESS**, **336 tests each**, Ruff and strict mypy pass across 22 files, and 12 actual synthetic archives including a 60-fictional-participant, 12-subject held-out comparison and conditional null/bootstrap descriptive outputs. Earlier GA-11A proof index row for 335 tests is a dated earlier snapshot, **not** the latest candidate. No external domain effect, public release, scholarship, learning, or recognition follows from this result.
