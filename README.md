<div align="center">

# 🧠 PsychNeuro OpenBench

### From behavioral trials to defensible research evidence.

**A synthetic-first, reproducibility-oriented research workbench for psychology and computational neuroscience.**

*Know the source. Keep participants apart. Trace every result.*

[Explore the workflow](#a-workbench-that-explains-its-decisions) · [Quick start](#run-a-local-synthetic-experiment) · [Offline evidence review](#generate-a-private-review-page) · [Architecture](#architecture) · [Scientific limitations](#scientific-boundaries)

</div>

> [!IMPORTANT]
> **PRIVATE ENGINEERING PREVIEW — NOT A RELEASE.** This repository and its W04 integration remain private, unmerged and unsuitable for public hosting, human datasets, clinical decisions or publication claims. No user adoption, independent external review, or end-to-end production validation is asserted. Review the [release gates](docs/release-gates.md) and [W04 independent reviewer packet](docs/week4/W04_INDEPENDENT_REVIEWER_PACKET.md). Changing repository visibility requires separate explicit authorization.

## Why this exists

Imagine two researchers forecasting whether a person will answer a behavioral task correctly. Both get an impressive score. One accidentally trains on trials from people also present in their test data; the other holds out entire people. One includes reaction time measured **after** the response.

Those numbers do not answer the same question.

**PsychNeuro OpenBench makes the decisions surrounding a number inspectable.** The project couples synthetic data provenance, participant-level separation, interpretable baselines, immutable aggregate records, policy gates, and skeptical scientific reporting. It is designed for researchers who prefer an explicit refusal over a misleading metric.

It is also a practical platform for experimenting with scientific software architecture: typed Python contracts, FastAPI endpoints, SQLite transaction boundaries, a separate fenced worker, browser interfaces and adversarial regression tests.

## A workbench that explains its decisions

| Capability | What it does | Current evidence boundary |
| :--- | :--- | :--- |
| **Synthetic behavioral trial lab** | Generates deterministic fictional two-choice trials with schema and source digests | Implemented and previously exercised by CI |
| **Source-rights gate** | Rejects unapproved external sources and post-response predictor fields | Source + negative tests; independent legal review pending |
| **Group-safe ML baselines** | Compares a grouped dummy policy with logistic regression using nested group-aware selection and a sealed test partition | W03 source and prior synthetic tests; no human validity |
| **Reproducibility graph** | Content-addressed source → split → model → benchmark chain with immutable SQLite records | Implemented; a hash is not a signature |
| **Private W04 research API** | Authenticated synthetic runs, aggregate inspection and restricted routes | Integration on private branch; not publicly hosted |
| **Rights-aware durable jobs** | SQLite leases, idempotency, cancellation fencing, retry accounting, separate operator worker | Code and negative tests; exact current-head hosted gate pending |
| **Independent receipt verification** | Validates P13/P25 receipt identity and optional externally pinned Ed25519 root anchors | Keys and independent trust channel are an operator obligation |
| **Offline evidence reviewer** | Verifies a local synthetic W03 aggregate; exports accessible, stand-alone HTML, Markdown or JSON | Added on this feature branch; exact-head CI pending |
| **Reproducibility documentation** | Protocols, example limitations, tests, architecture, decision records and review gates | Extensive docs; some historical pages predate W04 |

**Do not mistake implemented source or older-commit CI for a verified release candidate.** A run may have internally consistent hashes without being real, independent, authorized or reproducible on another machine.

## Who can use the approach?

- **Psychology and cognitive-science students:** see why row-shuffled evaluation and leakage can produce persuasive but invalid performance.
- **Computational neuroscience researchers:** prototype scientific pipelines with explicit participants, labels, source rights and feature timing.
- **ML engineers:** study deterministic data generation, group-aware nested CV, transaction-safe output, lineage and safe async coordination.
- **Scientific reviewers and maintainers:** inspect every reported checksum and score alongside the exact assumptions and remaining limits.

The current dataset is **entirely fictional**. There are no claims of validity for human emotion, mental health, behavioral phenotypes, EEG, fMRI or clinical prediction.

## Architecture

~~~mermaid
flowchart LR
    A["Original synthetic generator"] --> B["Schema + feature timing"]
    B --> C["Participant-disjoint split"]
    C --> D["Nested group-aware CV"]
    D --> E["Dummy + logistic models"]
    E --> F["Sealed test evaluation"]
    F --> G["Immutable W03 run + P13 provenance"]
    P["P25 operator-reviewed rights"] --> W["Private W04 API and job queue"]
    W --> D
    G --> R["P13/P25 aggregate receipt"]
    R --> V["Independent root verifier"]
    G --> Q["Offline HTML/Markdown reviewer"]
~~~

A compact mental model:

**P1 = scientific data and evaluation · P13 = integrity and provenance · P25 = access and rights · W04 = private application and worker integration.**

The SQL boundary matters: a W04 worker must not commit aggregate results after its lease expires, its job is cancelled or its P25 permission is revoked. A cancel cannot interrupt a CPU-bound scikit-learn fit already executing; it can fence the result from publication. The project is deliberately conservative about this distinction.

## Run a local synthetic experiment

The code is currently maintained on **private review branches**, rather than fully integrated into `main`. These commands target a checked-out branch containing W03/W04. Use an isolated, operator-approved development environment; no cloud provider or paid model is required.

**Requirements:** Python 3.11 or 3.12; a local environment with permission to install open-source packages; no real participant data.

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[benchmark,w03,dev]'
python -m pytest -q
python -m ruff check .
python -m mypy src
~~~

On Windows activate with `.venv\Scripts\activate`. Installation and exact-head tests on this new branch **have not yet been independently verified**. Hosted CI must prove compatibility before release.

### 1. Generate a fictional dataset

~~~python
from psychneuro.synthetic import SyntheticConfig, dataset_card, generate_trials

config = SyntheticConfig(seed=73, n_participants=36, trials_per_participant=12)
trials = generate_trials(config)
card = dataset_card(config, trials)

print("Synthetic rows:", len(trials))
print("Source fingerprint:", card["source_sha256"])
~~~

The contract specifies 36 fictional participants and 12 trials each. The records are simulated, not observations collected from people.

### 2. Execute a grouped W03 benchmark

This example is **only a local scientific development smoke test**, not a production P25-authorized API or proof of model performance.

~~~python
import json
from pathlib import Path

from psychneuro.w03.contracts import ExperimentRequest
from psychneuro.w03.service import execute
from psychneuro.w03.store import RunStore

storage = RunStore(Path("private-synthetic-experiments.sqlite"))
result = execute(
    ExperimentRequest(generator_seed=73, split_seed=42),
    Path("data/registry.json"),
    storage,
)

record = storage.get(result.run_id)
assert record is not None
Path("private-w03-aggregate.json").write_text(
    json.dumps(record, sort_keys=True), encoding="utf-8"
)

print("Run ID:", result.run_id)
print("Sealed test balanced accuracy:", result.test_balanced_accuracy)
~~~

The executable path performs actual grouped model fitting on **invented** data. No illustrative score is hard-coded as a claimed outcome. For protected W04 workflows, use the P25-authorized product path rather than directly exporting storage contents.

### 3. Inspect the result independently

~~~bash
python -m psychneuro.w04.reviewer \
  --record private-w03-aggregate.json \
  --format html \
  --output private-research-review.html
~~~

Open the generated HTML file locally. It includes a readable metric table, source/split/run fingerprints and limitations. The page contains **no JavaScript, remote fonts, trackers, third-party assets or network requests**.

For a second separately authorized aggregate:

~~~bash
python -m psychneuro.w04.reviewer \
  --record private-w03-aggregate.json \
  --compare second-authorized-aggregate.json \
  --format markdown \
  --output internal-comparison.md
~~~

Comparisons check whether source and split digests match. If not, the report explicitly refuses to frame the metrics as a controlled head-to-head comparison. Even matching hashes do **not** provide paired predictions or a significance test. Output files are created privately and never overwritten silently.

**Important:** the reviewer accepts an optional `--expected-root` checksum provided through a separate trusted channel, but does not prove provenance authenticity. Signed-root verification remains the job of [`anchor_v1.py`](src/psychneuro/w04/anchor_v1.py), with independently managed public keys and sequence floors. A check against a checksum copied from the same untrusted JSON document is not an independent trust signal.

## Private application and durable jobs

For an explicitly approved local review, the strict FastAPI entrypoint is:

~~~text
psychneuro.w04.server_strict:app_factory
~~~

It expects separate 32+-character operator-provisioned `W04_PRIVATE_TOKEN` and `W04_P25_PERMIT_KEY`, a private SQLite path (`W04_DB_PATH`), and `W04_REGISTRY_PATH`. The P25 source policy must be installed before privileged use. A static token is **not production identity management**. The server must not be exposed to the public Internet.

The separate operator-only queue runner is:

~~~bash
python -m psychneuro.w04.worker_cli_v5 --help
~~~

A full usage and negative-testing guide lives in [W04 review](docs/W04_REVIEW.md) and the [reviewer packet](docs/week4/W04_INDEPENDENT_REVIEWER_PACKET.md). These are not permissions to launch a host, install policies on behalf of others, or process real human records.

## Project map

~~~text
psychneuro-openbench/
├── src/psychneuro/
│   ├── synthetic.py, schema.py, registry.py     # Fictional data and fail-closed sourcing
│   ├── split.py, baselines.py, experiments.py    # Evaluation integrity and baselines
│   ├── reporting.py, workflow.py                 # Research report tooling
│   ├── w03/                                      # Strict grouped engine / record vault
│   └── w04/                                      # P25 policy, leases, receipts, APIs, reviewer
├── apps/web/                                     # TypeScript client/scientific view checks
├── tests/                                        # Python negative, science and integrity tests
├── benchmarks/                                   # Auditable scripts and explicitly marked evidence
├── docs/                                         # Methods, decisions, release gates, W04 audit
├── data/registry.json                           # Synthetic enabled; third-party data disabled
├── app.py                                        # Private Streamlit exploration pathway
├── pyproject.toml                                # Python package, development extras
└── .github/workflows/                            # Private review/manual quality workflows
~~~

There are multiple historical private branches and draft PRs. **Do not merge divergent W04 branches without first reconciling their exact commits, test evidence and release conditions.** The primary integrated but unmerged feature line is [W04 unified draft PR #24](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/24).

## Scientific boundaries that do not go away

1. **Independence:** trials from one fictional participant must not appear on both sides of a held-out-person evaluation. Do not confuse trial-level and subject-level generalization.
2. **Timing:** response and reaction-time outcomes are not legitimate pre-response predictors.
3. **Baselines:** compare under the same source, grouping and evaluation conditions; the dummy policy matters.
4. **Uncertainty:** group-aware CV is not proof of calibration, causal inference or real-population external validity.
5. **Integrity vs authenticity:** SHA-256 alone only detects changes relative to known expected values. It is not a digital signature.
6. **Rights:** open-source software licensing does not establish consent, clinical approval, or rights to use third-party human data.
7. **Safety:** no medical diagnosis, treatment guidance, mental-health classification or patient-facing decisions.

Read the [data schema](docs/data-schema.md), [grouped evaluation protocol](docs/evaluation-protocol.md), [research contract](docs/spec-v0.md), and [independent science/security audit](docs/week4/INDEPENDENT_SCIENCE_SECURITY_AUDIT.md).

## Engineering verification and release gate

The repository contains **historical hosted test evidence**, including a W04 Chat3 ancestor run that reported 491 Python tests per version and a successful TypeScript job. That result belongs to its **specific ancestor commit**, not this branch or the current unified W04 integration. W04 also has reported prior failures and subsequently committed corrections. Never infer success without a matching run SHA.

- [ ] Exact-head Python 3.11/3.12 pytest, Ruff and strict mypy.
- [ ] Exact-head Node/TypeScript tests and build.
- [ ] Real bounded operator-worker crash/recovery/backup and concurrency checks.
- [ ] Independent root trust and retention of signature/sequence floors.
- [ ] Rights/dependency/security assessment beyond toy fixtures.
- [ ] Private browser accessibility, keyboard, mobile, security and failure-case audit.
- [ ] Independent human scientific/security review and publication approval.

Until then: **private development, no deployment, no data rights escalation, no clinical claim, no external public release.** See [release gates](docs/release-gates.md) and [W04 reviewer handoff](docs/week4/W04_INDEPENDENT_REVIEWER_PACKET.md).

## Contributing and reproducibility

Contributions should preserve scientific meaning, fail closed when evidence is missing, use seeded synthetic fixtures for automated tests and include negative cases. A proposed feature should explain its independence unit, leakage risks, privacy model, exact execution evidence and compatibility with the frozen research contract.

Start with [CONTRIBUTING.md](CONTRIBUTING.md), [the tutorial](docs/tutorial.md), [reproducibility protocol](docs/reproducibility.md) and the [offline reviewer guide](docs/offline-reviewer.md). Please do not post real participant records, secrets or private operational logs in issues.

### License and research use

Code and original documentation: [Apache License 2.0](LICENSE). That license does not automatically grant rights over separately sourced datasets or generated exports; consult the [license policy](docs/license-policy.md) and the open [data-rights decision issue #9](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/9).

---

<div align="center">

**Better benchmarks should tell you not only what scored well — but what that score is allowed to mean.**

*PsychNeuro OpenBench · Private synthetic research engineering, not a clinical product.*

</div>
