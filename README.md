<div align="center">

# PsychNeuro OpenBench

### Reproducible behavioral machine learning, from data validation to defensible evaluation.

**Know your data. Protect the holdout. Trace every result.**

[Get started](#quickstart) · [Research design](#research-design) · [Roadmap](#development-roadmap) · [Contributing](#contributing)

</div>

---

## Why this project exists

A machine learning score is only as trustworthy as the experiment that produced it.

In behavioral research, multiple rows often come from the same participant. If those rows cross training and test boundaries, a model can appear to generalize while mostly recognizing participants it has already encountered. Similarly, a predictor measured *after* a response may quietly leak information that would not be available at prediction time.

**PsychNeuro OpenBench** explores how to make those choices explicit and reproducible. The project builds tools for validating trial-level datasets, documenting provenance, protecting participant-level evaluation boundaries, comparing transparent baselines, and preserving the evidence needed to reproduce results.

The initial foundation is **nonclinical and synthetic-data-only**. It is useful for exploring methodological safeguards and engineering practices; it is not a validated neuroscience prediction system or a clinical product.

## What you can explore

| Area | Available on \`main\` | Further development |
| --- | --- | --- |
| Synthetic trial generation | Deterministic, configurable fictional participant/trial records | Richer simulation and controlled signal fixtures |
| Trial data contracts | Structural checks for IDs, types, outcomes and predictor timing | Extended ingestion and schema interoperability |
| Source provenance | Dataset cards, rights metadata, stable CSV export and SHA-256 hashes | End-to-end run and artifact traceability |
| Rights-aware registry | Only the original synthetic source is enabled by default | Individually reviewed third-party data sources |
| Data loading | Synthetic CSV replay and validation modules | Broader validated input formats |
| Participant-held-out evaluation | Scientific specification and reviewable design | Independent grouped-CV and baseline implementations on development branches |
| Research workbench | Python package and tests | More complete services, reporting and interface integration |

**Branch distinction:** This table describes the default branch. Additional evaluation, provenance and web/service components are under review in separate branches and pull requests. A development branch is not automatically part of the released or default-branch API.

## The research principles

### 1. Treat participants—not rows—as independent observations

When the scientific objective is generalization to unseen participants, every split should be constructed around participant identity. The same person must not appear in both training and held-out test sets.

### 2. Use only features available at prediction time

A model predicting trial correctness before a response must not be trained on reaction time, the response itself, identifiers or outcome-derived summaries. Predictor availability is part of the dataset contract.

### 3. Always compare against a meaningful baseline

Accuracy without class prevalence, a dummy classifier, fold composition and suitable metrics is difficult to interpret. Honest baselines make otherwise impressive-looking results easier to assess.

### 4. Preserve a reproducible chain of evidence

A dataset card should identify the generator or permitted source, schema revision, seed, row/group counts, rights basis and exact source digest. Later experiment records should connect splits, preprocessing, models and scores without claiming integrity checks prove independent authenticity.

### 5. Distinguish software tests from scientific validation

Synthetic cases can demonstrate that validators, splits and storage contracts behave as intended. They cannot establish that a trained model predicts real human behavior, generalizes between laboratories or has clinical utility.

For the normative methodology and acceptance criteria, see the [v0 research specification](docs/spec-v0.md) and [data schema](docs/data-schema.md).

## Quickstart

### Requirements

- Python **3.11 or newer**
- Git
- No GPU, paid API, cloud account or human participant data

Clone the repository and install the development dependencies:

~~~bash
git clone https://github.com/aradmanamnaoon/psychneuro-openbench.git
cd psychneuro-openbench
python -m pip install -e ".[dev]"
~~~

Generate a deterministic synthetic trial dataset:

~~~python
from psychneuro.synthetic import (
    SyntheticConfig,
    dataset_card,
    generate_trials,
    to_csv_text,
)

config = SyntheticConfig(
    seed=42,
    n_participants=24,
    trials_per_participant=20,
)
trials = generate_trials(config)
csv_text = to_csv_text(trials)
card = dataset_card(config, trials)

print("Trials:", len(trials))
print("Fictional participants:", card["n_participants"])
print("Synthetic dataset:", card["synthetic"])
print("SHA-256:", card["source_sha256"])
~~~

The configuration requests **24 fictional participants × 20 trials = 480 rows**, subject to successful validation. Every participant is invented; the data does not represent empirical human behavior.

Run the repository checks:

~~~bash
python -m pytest -q
python -m ruff check .
python -m mypy src
~~~

Use the output from your own checkout as the test evidence for its exact commit. Earlier [verified checks](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677) demonstrate specific synthetic-foundation tests, not completion of the full research platform.

### What the generated dataset contains

The synthetic task produces trial records with participant, session and trial identifiers, pre-response task conditions, binary correctness, response details and reaction-time values. Fields not available until after the response are retained for inspection but excluded from the prespecified predictor set.

The accompanying **dataset card** captures origin, versioning, sample counts, feature metadata, usage limitations and a checksum. See [dataset-card and schema documentation](docs/data-schema.md).

## Research design

~~~mermaid
flowchart TD
    A["Synthetic trial data"] --> B["Schema and rights checks"]
    B --> C["Participant-aware data partition"]
    C --> D["Training-only preprocessing"]
    D --> E["Transparent baseline comparison"]
    E --> F["Evaluation and uncertainty review"]
    F --> G["Reproducible research record"]
~~~

*This diagram presents the intended end-to-end methodology. Not all stages are available as integrated, default-branch commands.*

**Evaluation design matters as much as implementation.** Group-respecting splitting, fixed test identities, train-fold-only preprocessing and matched evaluation of classifiers are central requirements. When there are too few groups or undefined metrics, the pipeline should explain why the experiment is ineligible rather than inventing a score.

For researchers, the [methodological specification](docs/spec-v0.md) describes the data contract, model baselines, metrics and leakage rules in detail.

## Data sources and responsible use

The default registry accepts the project's **original synthetic generator**. External neuroscience and behavioral dataset entries are recorded for research and suitability assessment, but remain disabled unless independently approved for the intended processing and redistribution.

A permissive-looking dataset license does not automatically resolve consent, ethical clearance, privacy, modality compatibility or downstream artifact rights. The [dataset candidate audit](docs/dataset-candidate-audit.md) and [licensing policy](docs/license-policy.md) describe these distinctions.

**No clinical or patient-level prediction is claimed.** The project must not be used to diagnose, treat or make decisions about individuals.

## Repository structure

~~~text
src/psychneuro/       Synthetic generation, schema and registry utilities
tests/                Data, validation and regression checks
data/registry.json    Versioned source availability and rights metadata
docs/data-schema.md   Field-level trial and dataset-card contract
docs/spec-v0.md       Scientific objective and evaluation protocol
docs/license-policy.md Data and software licensing distinctions
docs/release-gates.md Release-readiness checklist
pyproject.toml        Python package and development configuration
~~~

Further work is developed and reviewed through topic branches and pull requests. The default branch is deliberately kept distinct from experimental integrations.

## Development roadmap

- [x] Reproducible synthetic trial records and machine-readable dataset cards
- [x] Deterministic serialized dataset checksums and schema validation
- [x] Rights-aware source registry with synthetic-only default policy
- [x] Negative tests for malformed records and prohibited predictors
- [ ] Finish integrating participant-group splitting and leakage-safe baselines into the supported default workflow
- [ ] Validate complete experiment-to-report reproducibility across supported environments
- [ ] Establish an approved import path for additional data formats and sources
- [ ] Independently verify UI, security, accessibility and deployment behavior
- [ ] Prepare a reviewed, versioned research-software release

Progress is tracked through [issues](https://github.com/aradmanamnaoon/psychneuro-openbench/issues) and [pull requests](https://github.com/aradmanamnaoon/psychneuro-openbench/pulls). The [release criteria](docs/release-gates.md) explain which checks are required before describing the integrated workbench as ready for broader use.

## Verification and reproducibility

The repository includes pytest checks, Ruff linting and strict mypy configuration. Test logs, pinned implementations and research methods are more informative than a success badge without a known commit.

For scientific results, distinguish:

| Verification | What it can support | What it cannot support |
| --- | --- | --- |
| Synthetic generator tests | Determinism and contract behavior for tested fixtures | Realistic human behavior |
| Leakage negative tests | Rejection of known contaminated splits or predictor sets | Universal absence of leakage |
| Grouped-CV checks | Independence under the tested grouping contract | Cross-population generalization |
| Provenance checksums | Byte-level identity and recorded dependency relationships | Independent truth or cryptographic authorship |
| Benchmark scores | Results under a specific validated protocol | Clinical, causal or real-world usefulness |

Every reported model result should include dataset and split identity, experiment configuration, exact code/version context, warnings and the appropriate baseline.

## Contributing

Focused improvements are especially welcome in **data validation**, **leakage-resistant evaluation**, **reproducibility**, **statistical reporting**, **security** and **reviewer documentation**.

A good change should have a clear use case, a small reviewable diff, regression coverage and an explicit explanation of its maintenance cost. Prefer strengthening an existing module over adding a new abstraction or dependency without demonstrated benefit. For data or methodology changes, include negative and boundary cases—not only a successful example.

When reporting issues, provide a minimal reproducible example using invented data. Do not upload real participant records, credentials or confidential research documents.

## License and acknowledgments

The repository's original code is distributed under the [Apache License 2.0](LICENSE), subject to the specific notices in [NOTICE](NOTICE). The software license does **not** grant rights to third-party datasets or independently exported research material.

The project draws on established principles from statistical learning, reproducible research and leakage-aware neuroimaging evaluation. Attribution for methods should refer to the relevant scholarly literature, not to the project as independent scientific validation.

**Maintained by [aradmanamnaoon](https://github.com/aradmanamnaoon).**

---

*PsychNeuro OpenBench aims to make behavioral ML experiments easier to inspect, reproduce and challenge—because trustworthy research needs more than a single score.*
