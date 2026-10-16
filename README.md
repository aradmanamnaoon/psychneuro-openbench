# PsychNeuro OpenBench

### Behavioral machine learning you can inspect, reproduce, and challenge.

**From a synthetic trial to an evidence-backed benchmark—without hiding the data contract, subject splits, or evaluation decisions.**

> **Private development • Pre-release • Synthetic-only • Nonclinical**  
> This repository stays **private until the project is complete, quality-reviewed, and its owner explicitly approves publication**. The current code is a research-software foundation, **not** a finished benchmark, hosted demo, clinical tool, or validated model of human behavior.

**Explore:** [What we're building](#the-problem-were-solving) · [What works today](#what-exists-today) · [Try the generator](#a-concrete-example) · [Reproducibility](#reproducibility-is-a-contract-not-a-seed) · [Roadmap](#roadmap--engineering-backlog) · [Evidence](#what-has-actually-been-tested) · [Release gates](docs/release-checklist.md)

---

## The problem we're solving

A behavioral ML result is only as credible as the decisions made **before** training:

- **Who was held out?** Repeated trials from the same participant must not silently appear in both training and evaluation data.
- **What information was available at prediction time?** A post-response latency or the response itself can leak the target when predicting trial correctness.
- **Where did the data come from?** A dataset needs an inspectable source, version, rights basis, schema, and content digest.
- **Can another researcher replay the analysis?** Seed, participant assignments, preprocessing, baselines, metrics, dependency versions, and known failure modes all matter.

**PsychNeuro OpenBench** is intended to make those choices *first-class research artifacts*, rather than details buried in notebook cells.

The intended users are psychology methods students, research assistants, computational neuroscience analysts, and ML researchers/reviewers who need to inspect and reproduce **nonclinical behavioral-trial** workflows. This is an engineering and methodology project; whether anyone needs it in practice remains a hypothesis to test.

### One motivating example

Suppose a fictional task has 24 participants and 20 trials per participant. Randomly splitting the 480 **rows** can put trials from the same participant in training and test sets. A model may exploit stable participant-specific patterns instead of generalizing to unseen participants.

Our **planned evaluation engine** will split by participant, check for overlap, hold the test set untouched, and compare a simple dummy baseline with a logistic baseline on the same splits. **That engine has not been implemented yet.** The existing generator gives us a controlled, synthetic fixture for building and testing it.

## From synthetic trials to a reproducible experiment

The long-term vertical slice is deliberately narrow: one synthetic binary-outcome task, strong validity gates, transparent classical baselines, and a portable run record.

\`\`\`mermaid
flowchart TD
    A["Configuration + fixed seed"] --> B["Synthetic trial generator"]
    B --> C["Structural validation"]
    C --> D["Canonical CSV + dataset card + SHA-256"]
    D -. "planned" .-> E["Participant-held-out splits"]
    E -. "planned" .-> F["Train-only preprocessing"]
    F -. "planned" .-> G["Dummy vs logistic baselines"]
    G -. "planned" .-> H["Metrics, warnings + replay manifest"]
    classDef built fill:#dcefe6,stroke:#38805b,color:#173c2c;
    classDef future fill:#eef1f6,stroke:#8291a7,color:#273344,stroke-dasharray: 5 4;
    class A,B,C,D built;
    class E,F,G,H future;
\`\`\`

**Solid steps = candidate implementation exists. Dashed steps = design only, not yet working.** An integrated UI and installation-free *executable* demo are future work; nothing is currently deployed.

## What exists today

| Component | Evidence-based status | Why it matters |
| --- | --- | --- |
| Typed, seeded two-choice trial generator | **Implemented**, with hosted PM-02 tests | Gives deterministic, entirely fictional input data without participant privacy risks |
| Config validation and bounded generation | **Implemented** | Rejects invalid seeds, unsafe identifiers, impossible sizes, and oversized trials |
| Trial consistency checks | **Implemented** | Detects duplicate keys, invalid values, inconsistent correctness and trial ordering |
| Canonical CSV + dataset card / source digest | **Implemented** | Makes synthetic provenance and exact exported bytes inspectable |
| Initial automated quality checks | **31 PM-02 tests passed** on a [real GitHub-hosted run](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313) | Verifies the existing generator foundation; not scientific validity |
| Additional PM-03 test scenarios and CPU matrix | **Authored on a private feature branch; not yet run** | Adds candidate regression coverage without claiming results |
| Participant-held-out benchmark and ML baselines | **Planned** | Prevent leakage and establish interpretable comparisons |
| Real-data adapters, hosted browser app, release | **Not implemented / not authorized** | Require separate scientific, rights, security, and release gates |

**Current software version in** [\`pyproject.toml\`](pyproject.toml): \`0.1.0.dev0\`. This is a development version, **not a published package**.

## A concrete example

The initial code generates an entirely invented left/right choice task. This example uses the **real committed PM-02 API**:

\`\`\`python
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

assert len(trials) == 24 * 20
assert card["n_trials"] == len(trials)
assert card["synthetic"] is True
assert card["rights_basis"] == "synthetic-original"

# Inspect data and provenance; no real participants are involved.
first_trial = trials[0]
source_digest = card["source_sha256"]
\`\`\`

The output objects expose fields such as:

| Field | Example meaning | Prediction-time role |
| --- | --- | --- |
| \`participant_id\`, \`session_id\`, \`trial_id\` | Invented identities and trial keys | **Grouping / provenance only** |
| \`trial_order\` | 1-based index within a synthetic session | Provenance only in the v0 contract |
| \`stimulus_condition\` | Left/right cue | Permitted *pre-response* feature |
| \`difficulty\` | Invented task difficulty in [0, 1] | Permitted *pre-response* feature |
| \`correct\` | Invented binary correctness | **Target**, never a predictor |
| \`response\` | Invented post-trial choice | **Forbidden predictor** for same-trial correctness |
| \`response_time_ms\` | Invented latency in milliseconds | **Forbidden post-response predictor** |
| \`generator_seed\` | Integer PRNG seed | Reproducibility metadata |

See the normative [data schema](docs/data-schema.md) and [scientific v0 contract](docs/spec-v0.md). The generator's parameters and response-time distribution are **arbitrary engineering choices**, not estimates derived from real psychology or neuroscience experiments.

### Browser-only review—no installation needed

If you are reviewing this private repository through GitHub, the following path requires **no local installation**:

1. Read the [scientific contract](docs/spec-v0.md) and [data schema](docs/data-schema.md).
2. Inspect the [generator](src/psychneuro/synthetic.py), the [PM-02 tests](tests/test_synthetic.py), and the [synthetic rights policy](docs/license-policy.md).
3. Open [GitHub Actions](https://github.com/aradmanamnaoon/psychneuro-openbench/actions) and inspect the commit, steps, and logs for an **actual** run rather than relying on a badge.
4. Review the [PM-03 branch](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm03-quality-foundation), its additional [tests](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/tests/test_synthetic_pm03.py), and the [engineering backlog](https://github.com/aradmanamnaoon/psychneuro-openbench/issues).

This is an **installation-free evidence-review workflow**, *not* a runnable browser demo. A real zero-install data-to-results experience is a later release requirement.

### Optional developer setup (not required for review)

Once a developer has authorized access and an appropriate Python 3.11+ environment, the editable development package uses:

\`\`\`bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check .
python -m mypy src
\`\`\`

The owner is **not** being asked to perform these steps. Hosted execution evidence is the acceptance route. The default-branch workflow remains manually triggered to avoid automatic private-repository runner consumption.

## Reproducibility is a contract, not a seed

An integer seed is necessary for a repeatable simulation—but it is not enough to justify a reproducible *benchmark*.

| Question | Present foundation | Required before benchmark claims |
| --- | --- | --- |
| **Is the simulation replayable?** | \`random.Random(seed)\` scoped to the generator; exact CSV export | Pin Python/dependencies and record generator revision |
| **Can an input be identified?** | Synthetic dataset card and SHA-256 of canonical CSV bytes | Immutable source/version and transformation chain |
| **Can data contamination be found?** | Composite trial-key and consistency checks | Group-overlap, forbidden-feature and preprocessing-leakage tests |
| **Can models be compared fairly?** | No trained benchmark models yet | Identical saved participant splits and dummy/logistic baselines |
| **Can another lab audit the result?** | Spec, source and individual engineering checks | Environment lock, fold manifest, metrics, warnings and replay artifact |

A later benchmark run should be able to answer: **“Which exact records, groups, transformations, versions and decisions produced this result?”**

See [docs/spec-v0.md](docs/spec-v0.md) for the proposed split and manifest acceptance gates. Deterministic synthetic output **does not** establish human generalization, scientific reproducibility across studies, or clinical utility.

## What has actually been tested

### PM-02 foundation: verified

The [GitHub Actions run on 16 October 2026](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313) completed successfully on **Python 3.11**:

- **31 pytest tests passed**.
- **Ruff:** all checks passed.
- **mypy:** no issues found in two source files.

That run tested the PM-02 generator foundation on its specific commit. It is **not** evidence that the added PM-03 tests pass, that Python 3.12 is verified, or that an ML benchmark works. Engineering acceptance is separate from empirical or scientific validation.

### PM-03 quality extensions: pending execution

The additional [PM-03 tests](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/tests/test_synthetic_pm03.py), [manual CPU matrix](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/.github/workflows/ci.yml) and [evidence ledger](https://github.com/aradmanamnaoon/psychneuro-openbench/blob/pm03-quality-foundation/docs/decisions/week1.md) are authored on a **separate private branch**. No PM-03 passing test count or hosted-job result is claimed.

GitHub-hosted runner usage on a private repository may affect plan allowances. Do not trigger paid capacity or recurring runs without authorization.

## Roadmap & engineering backlog

The goal is a research-software artifact with inspectable failures and honest limitations, not a collection of unverified demos.

| Stage | Deliverable | Gate |
| --- | --- | --- |
| **01 · Foundation** | Synthetic generator, schema, source digest, typed packaging | Real source + passing engineering tests; available for PM-02 |
| **02 · Data integrity** | Loaders, missingness, schema migration, provenance/rights checks | Invalid or restricted inputs fail closed |
| **03 · Leakage-safe evaluation** | Saved participant splits, train-only preprocessing, dummy and logistic baselines | No participant overlap; reproducible fold manifests |
| **04 · Research artifacts** | Metrics, uncertainty/undefined states, models and machine-readable run manifest | Rerun evidence on pinned data/environment |
| **05 · Browser workbench** | Zero-install demonstration of the full data-to-report workflow | Real hosted URL, usability/accessibility and security checks |
| **06 · Release** | License and rights audit, documented limitations, independent review, reproducible release | Owner approves public visibility only after gates pass |

Six actionable issues track the next engineering work:

| Issue | Acceptance focus |
| --- | --- |
| [#1 — Trial schema](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/1) | Required columns, unique keys, complete dataset cards |
| [#2 — Seeded simulation](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/2) | Deterministic replay, invalid inputs, RNG isolation |
| [#3 — Group leakage](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/3) | Disjoint participants, forbidden-feature checks |
| [#4 — Baselines](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/4) | Matched split manifests, transparent metrics |
| [#5 — Data rights](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/5) | Fail-closed licensing, provenance and privacy |
| [#6 — Evidence export](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6) | Stable run manifest, CPU CI and reviewer navigation |

Issues are **development work**, not evidence that the features are complete.

## Scientific, security and ethical boundaries

**This is not a diagnostic device, a clinical decision-support tool, or a validated behavioral model.**

- **Synthetic ≠ observed.** The generator fabricates all identities, choices, outcomes and latencies. No human participants, medical data or consented studies underlie its outputs.
- **Reproducible ≠ externally valid.** Exact replays show code repeatability, not generalization to people, laboratories or populations.
- **Correlation ≠ mechanism.** A future predictive score cannot establish a neural or psychological mechanism or an intervention effect.
- **No target leakage.** Response, response time, the target itself and identity fields must not enter predictors for same-trial pre-response correctness.
- **No unapproved real-data ingestion.** Future adapters need source rights, licensing/terms, ethics/consent, privacy and provenance checks. PHI and identifiable patient records are out of scope.
- **No misleading release claims.** A published page, passing unit tests, attractive screenshots or GitHub stars would not constitute scientific validation.

For exact boundaries, see the [scientific spec](docs/spec-v0.md) and the [rights decision record](docs/license-policy.md).

## Development and publication policy

This is intentionally a **private build until complete**, not an accidentally hidden public release.

1. Keep repository visibility **private** throughout architecture, implementation, testing and internal review.
2. Finish the end-to-end workflow and prove the acceptance gates with actual source, hosted logs, valid artifacts and documented limitations.
3. Audit dependencies, licenses, real-data rights, security, accessibility and public-facing claims.
4. Obtain the owner's **separate, explicit approval** before switching repository visibility to public, publishing packages/datasets, promoting the project, or soliciting external contributors.

**No automatic publishing, profile updates, outreach or “release because the date arrived.”**

See [Release checklist](docs/release-checklist.md). Being private during development is intentional and is **not** a product defect.

## License, citation and contributions

**Software license:** not yet selected. This code must not be described as open source or redistributable until the owner chooses and approves a license. The dataset-card field \`rights_basis: synthetic-original\` describes synthetic *data origin*, not a license to reuse the source code.

**Contributions:** issue tracking is internal while the repository is private. A public contribution guide, external review process and licensing terms will be considered after release readiness.

**Citation:** no DOI, archival publication or scientific paper has been issued for this project. Do not cite it as a validated benchmark or claim independent recognition. Future releases can provide a versioned citation and artifact record once those exist.

---

**The standard we're aiming for:** *A researcher should be able to disagree with our result—and still reconstruct exactly how it was produced.*
