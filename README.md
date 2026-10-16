<div align="center">

# PsychNeuro OpenBench

### From behavioral trials to research results you can actually audit.

**A reproducibility-first workbench for behavioral psychology and computational neuroscience ML.**

*Understand the data. Protect the holdout. Explain every score.*

[Why this exists](#why-this-exists) · [See what works today](#what-works-today) · [Try the synthetic example](#try-the-synthetic-example) · [Research safeguards](#research-safeguards) · [Roadmap](#development-roadmap)

</div>

> [!IMPORTANT]
> **Private development preview — not a public release.** The current code is a synthetic-data engineering foundation, not a complete ML benchmark or a scientifically validated behavioral simulator. This repository stays **private until the project is complete, all release gates pass, and the owner explicitly approves publication**.

## Why this exists

Imagine two labs reporting different machine-learning scores on behavioral reaction-time experiments. Were they predicting the same outcome? Did both hold out **entire participants**, or did the same participant's trials appear in training and test data? Were their preprocessing steps fitted only on training data? Could another researcher reproduce the exact split, input, and baseline?

A score alone cannot answer those questions.

**PsychNeuro OpenBench is being built to make the answers inspectable.** The goal is one coherent path from lawful behavioral-trial data to subject-safe evaluation, transparent baselines, and portable provenance. It is intended to help:

| Who | The question they need answered |
| --- | --- |
| Psychology students | *How do I know that my evaluation is methodologically sound?* |
| Research assistants | *Which trials, conditions, participants, and source rights went into this analysis?* |
| Computational neuroscience researchers | *Do these model comparisons really generalize to unseen participants?* |
| ML reproducibility reviewers | *Can I trace and rerun the result instead of trusting a screenshot?* |

This is **post-collection research software**, not a stimulus presentation tool, EEG/fMRI processor, diagnostic system, or substitute for scientific validation.

## From data to evidence

The planned research workflow has a narrow, testable first milestone. Solid arrows represent code already present; dashed arrows are **planned, not delivered**.

\`\`\`mermaid
flowchart LR
    A["Invented choice-task trials<br/>AVAILABLE"] --> B["Structural validation<br/>AVAILABLE"]
    B --> C["Canonical CSV + dataset card<br/>AVAILABLE"]
    C -. "NEXT" .-> D["Participant-group holdouts<br/>PLANNED"]
    D -.-> E["Transparent ML baselines<br/>PLANNED"]
    E -.-> F["Auditable run manifest<br/>PLANNED"]
\`\`\`

The eventual value is not the complexity of the model. It is the ability to answer **what was evaluated, under which assumptions, with which held-out participants, and using which source revision**.

## What works today

<details open>
<summary><strong>Implemented foundation — inspectable source, narrow verified checks</strong></summary>

| Capability | What is implemented |
| --- | --- |
| Seeded toy trial generator | Repeatable, wholly fictional two-choice trials using a local \`random.Random(seed)\` instance |
| Typed records | Synthetic participant, session, trial, stimulus condition, difficulty, response, correctness, and response time |
| Controlled fixture size | Default **24 fictional participants × 20 trials = 480 rows**; limit of 100,000 rows per call |
| Structural validation | Rejects empty trials, duplicate trial keys, invalid trial ordering, wrong value domains, and response/correctness inconsistencies |
| CSV serialization | Stable column order and LF-terminated CSV text intended for a pinned Python environment |
| Provenance card | Declares synthetic origin, rights basis, seed, schema, feature timing, counts, and SHA-256 of serialized CSV bytes |
| Verification evidence | A hosted job reported **31 tests passed**, Ruff checks passed, and strict mypy checks passed for the synthetic-foundation source |

</details>

<details>
<summary><strong>Not implemented yet — do not mistake plans for product features</strong></summary>

- Import/validation of independently licensed external behavioral datasets.
- Persisted participant-group train/validation/test splits and leakage-failure gates.
- Executed \`DummyClassifier\` / \`LogisticRegression\` comparisons on identical folds.
- End-to-end benchmark metrics, participant-level uncertainty, canonical run manifests, or reproducible result reports.
- A browser workbench, hosted application, distributed package, public release, or clinical use case.

</details>

### Verification evidence, not a performance claim

A [GitHub-hosted verification run](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313) completed successfully for the synthetic-data code: **31 pytest assertions passed; Ruff and strict mypy also passed**. The verification was performed on a dedicated CI branch using the source/test content recorded for the current main-line foundation. Documentation-only edits after that run are not a new CI run.

This proves a limited set of **software properties**, not biological realism, valid cognitive modeling, generalization to people, model accuracy, research reproducibility across arbitrary machines, or readiness for public release.

## Try the synthetic example

> Developer example for an authorized Python 3.11+ environment. This is **not** an instruction for the project owner to install or run anything locally; development and review are handled separately.

From a checked-out repository:

\`\`\`bash
python -m pip install -e .
\`\`\`

Then generate fictional trials and save a CSV plus its provenance card:

\`\`\`python
import json
from pathlib import Path

from psychneuro.synthetic import (
    SyntheticConfig,
    dataset_card,
    generate_trials,
    to_csv_text,
    validate_trials,
)

config = SyntheticConfig(
    seed=42,
    n_participants=24,
    trials_per_participant=20,
)
records = generate_trials(config)
validate_trials(records)
card = dataset_card(config, records)

output = Path("example-output")
output.mkdir(exist_ok=True)
(output / "trials.csv").write_bytes(to_csv_text(records).encode("utf-8"))
(output / "dataset-card.json").write_text(
    json.dumps(card, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

assert len(records) == 480
print(f"Generated {len(records)} fictional trials")
print(f"CSV SHA-256: {card['source_sha256']}")
\`\`\`

The printed hash depends on the actual serialized bytes and runtime; no hard-coded hash or benchmark score is claimed here.

<details>
<summary><strong>What is in the generated dataset?</strong></summary>

The CSV contains these fields:

\`\`\`text
dataset_id,participant_id,session_id,trial_id,trial_order,
stimulus_condition,difficulty,correct,response,response_time_ms,generator_seed
\`\`\`

- **Before response:** \`stimulus_condition\` (left/right cue) and \`difficulty\` (invented unitless value) are the proposed candidate predictors.
- **Outcome:** \`correct\` is an artificial binary label, **not** a predictor.
- **After response:** \`response\` and \`response_time_ms\` are synthetic observations; they must **not** be used to predict pre-response correctness.
- **Grouping and provenance:** participant/session/trial IDs and \`generator_seed\` are not ML features. Response time is measured in **milliseconds**.

Default data are generated for **one synthetic session per participant**. All participant identifiers are invented, and all model parameters are illustrative rather than fitted to human observations.

The accompanying card reports the generator revision, seed, the \`synthetic-original\` rights basis, source checksum, column meanings, target, and feature availability.

See the full [data contract](docs/data-schema.md) for constraints and validation boundaries.

</details>

## The design principles

| Principle | Why it matters | State |
| --- | --- | --- |
| **Hold out people, not just rows** | Repeated trials from a participant cannot be treated as independent cross-group generalization | Design specified; enforcement planned |
| **Keep predictions temporally honest** | Post-response fields and the target must not leak into predictors | Feature availability documented; full pipeline enforcement planned |
| **Use baselines before sophisticated models** | A model should be compared against the simplest defensible alternative on the same folds | Planned |
| **Make dataset rights explicit** | Software licenses do not imply permission to use or redistribute research data | Synthetic rights card implemented; external-source adapters gated |
| **Make provenance replayable** | Inputs, transformations, versions, split membership, and metrics must be traceable | Source hash/card implemented; full run manifest planned |
| **Fail clearly** | Invalid trials, insufficient groups, undefined metrics, and contaminated splits should surface as failures | Initial structural checks implemented; broader gates planned |

The [scientific v0 contract](docs/spec-v0.md) is the authoritative design target, not evidence that every feature described there exists.

## Project structure

\`\`\`text
psychneuro-openbench/
├── src/psychneuro/
│   ├── synthetic.py          # generator, validator, CSV, dataset card
│   ├── __init__.py           # package exports
│   └── py.typed              # type information marker
├── tests/
│   └── test_synthetic.py     # regression and boundary checks
├── docs/
│   ├── spec-v0.md            # research and reproducibility requirements
│   ├── data-schema.md        # field definitions and permitted uses
│   └── license-policy.md     # current rights constraints
├── .github/workflows/
│   └── ci.yml                # manual-only default-branch CI
├── pyproject.toml
└── README.md
\`\`\`

The current package has **no third-party runtime dependencies**. Optional development dependencies support testing, linting, and type-checking.

### Reproducibility: a meaningful promise needs boundaries

The same generator configuration and seed reproduce the same records **on a pinned implementation, Python runtime, and source revision**. The card's SHA-256 detects changes to the serialized CSV. Python's random sampling internals and floating-point serialization are not universally guaranteed to produce byte-identical outputs across versions and platforms.

Full benchmark reproducibility will require saved split memberships, code/dependency revisions, preprocessing configurations, input hashes, and declared numerical tolerances. Those artifacts remain on the roadmap.

[Python's official reproducibility notes](https://docs.python.org/3/library/random.html#notes-on-reproducibility)

## Development roadmap

This roadmap lists **acceptance milestones**, not promised release dates.

| Milestone | Evidence needed | Current position |
| --- | --- | --- |
| **01 — Scientific contract** | Concrete research questions, normative schema, data-rights and evaluation gates | Draft on \`main\`, under review |
| **02 — Trustworthy synthetic foundation** | Typed package, schema, seeded generator, validation, source evidence, hosted checks | Implemented; limited hosted checks verified |
| **03 — Group-safe evaluation** | Fail-closed grouped splits, leakage fixtures, dummy and logistic baselines on identical folds | Not yet verified |
| **04 — Reproducible research output** | Frozen configs, actual benchmark reports, uncertainty handling, manifests, independent rerun evidence | Not yet verified |
| **05 — Usable research workbench** | End-to-end workflows, usable documentation, appropriate browser experience and usability checks | Not yet verified |
| **06 — Release readiness** | Security/rights/dependency review, reproducible CI, license approval, independent review, explicit owner sign-off | **Not authorized** |

Progress is accepted by reproducible evidence, not task count or calendar dates.

## Research safeguards

- **No real participants or protected data in v0.** All current records and identifiers are invented. No patient information, study recruitment, demographic profiling, or health records.
- **No clinical interpretation.** Accuracy, reaction times, and condition effects from this generator are *fabricated software fixtures*, not estimates of psychological processes, diagnoses, treatments, or human performance.
- **No implicit rights grant.** The source code does not yet have an approved open-source license. The synthetic data's origin is distinct from the code's eventual distribution license; see [rights policy](docs/license-policy.md).
- **No benchmark leaderboard yet.** The passing tests are engineering checks, not comparative ML benchmarks.
- **No publicity before readiness.** The repository remains private during development. Making it public requires completed release gates and the owner's fresh, explicit authorization.

## Project status and participation

PsychNeuro OpenBench is an active research-engineering project, **not currently accepting public uploads, external behavioral datasets, clinical requests, or participation claims**. Contribution guidelines, issue templates, licensing, public demos, and a citable release will be established only when the relevant engineering and governance gates are satisfied.

Useful starting documents for reviewers with authorized access:

- [Scientific specification and acceptance gates](docs/spec-v0.md)
- [Trial schema and leakage-relevant field definitions](docs/data-schema.md)
- [Data/source licensing policy](docs/license-policy.md)
- [Hosted verification run for current synthetic foundation](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313)

---

<div align="center">

**Good research software should make it easier to question a result—not harder.**

*PsychNeuro OpenBench · Private development · Nonclinical synthetic foundation*

</div>
