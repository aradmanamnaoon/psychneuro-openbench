# PsychNeuro OpenBench

**Status: unreleased research-software prototype; main branch currently contains a proposed scientific contract, not a working benchmark.** This README is staged on `pm03-quality-foundation` for review. Do not cite, benchmark, or reuse as an evaluated research tool yet.

PsychNeuro OpenBench aims to help psychology-methods students, behavioral research assistants, computational neuroscience analysts, and ML reproducibility reviewers reproduce **nonclinical, synthetic-only** behavioral-trial classification workflows. The v0 focus is leakage-safe evaluation, provenance, auditable baselines, and transparent failures—not model accuracy or diagnosis.

## Scope and scientific contract

Read [docs/spec-v0.md](docs/spec-v0.md) before implementation. The proposed v0 vertical slice is:

1. Generate an explicitly synthetic binary trial-correctness dataset with participant/session/trial identifiers, pre-response task features and a documented seed.
2. Validate trial keys, values, synthetic rights/provenance, and immutable dataset-card metadata.
3. Hold out entire **participants**, not random trial rows. Fit preprocessing on training folds only.
4. Compare a configured DummyClassifier with LogisticRegression using identical group assignments.
5. Export group-level evaluation evidence, explicit undefined-metric states and a stable replay manifest.

**No real participant data, diagnosis, treatment claims, medical images, EEG, fMRI, live studies or public release are in v0.** All simulated effect sizes are illustrative, not calibrated to human research.

## Reproducibility and seeds

In the proposed generator, the seed controls a private pseudorandom number generator. Reproducing exact rows requires the **same seed, generation settings, generator implementation and pinned environment**. Different seeds usually differ on a sufficiently large random sample but no individual output is guaranteed to change. A seed is not evidence of scientific validity. Generator and dataset-card format remain subject to PM-02 integration.

The v0 predictive target is binary `correct`. Only pre-response stimulus/task settings are candidate predictors. In particular, response latency (even if the generator produces it for QC) and participant identifiers must **never** be predictors of the same-trial correctness outcome.

## Zero-install browser review

No local tools are needed to **review** source and evidence:
1. Open the [v0 contract](docs/spec-v0.md) and verify nonclinical scope and required columns.
2. Inspect [the staged synthetic tests](tests/test_synthetic.py) and their provisional generator API assumptions.
3. Review the [CPU workflow](.github/workflows/cpu-tests.yml), then visit the repository's [Actions tab](https://github.com/aradmanamnaoon/psychneuro-openbench/actions) for a **real** run, commit SHA, logs and outcome.
4. Inspect the [decision/evidence ledger](docs/decisions/week1.md) and the linked [engineering issues](https://github.com/aradmanamnaoon/psychneuro-openbench/issues).

**Important:** This is a browser-only *review path*, not a browser-hosted runnable app. There is currently **no verified live demo**, benchmark metric, passing generator test, released dataset, or CI run to link. Do not mistake workflow YAML or issue creation for execution. A future installation-free end-to-end demo would require separate implementation, hosting and verification.

## Tests and contributor setup (once PM-02 package is merged)

The proposed CPU check installs the editable package with pytest and runs `python -m pytest -q`. These commands are for the future GitHub-hosted runner, not instructions for the human reviewer. The tests currently define a provisional `psychneuro.synthetic.generate_trials` adapter and must be reconciled with PM-02's actual API before treating outcomes as valid.

**CI cost gate:** This feature branch uses nonautomatic workflow triggers; private-repository runner quota/billing must be checked and authorized before triggering a paid run.

## Scientific limitations and data rights

- Synthetic data are not actual observations, cannot validate neurocognitive mechanisms, and do not demonstrate out-of-sample generalization to humans.
- Subject-held-out results only address synthetic subjects under the stated data-generation process; external validation remains absent.
- Real datasets require per-source license, consent/ethics and privacy approval. Package/source-code licensing is separate from data rights; **no package license has been approved here**.
- Never ingest PHI, identifiable patient records or clinical labels for diagnosis.
- Undefined metrics, insufficient groups, class imbalance and provenance errors must be surfaced explicitly, not replaced by attractive numbers.

## Development backlog (real private issues)

- [#1 Schema and card invariants](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/1)
- [#2 Seeded generator testing](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/2)
- [#3 Participant-level leakage prevention](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/3)
- [#4 Dummy and logistic baselines](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/4)
- [#5 Provenance and permitted sources](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/5)
- [#6 Replay manifest and CI evidence](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6)

PM-01 is completing the scientific contract, PM-02 owns the typed package and seeded generator, and PM-03 owns testing, hosted checks, docs and the backlog. Do not merge or advertise the project until actual evidence and human approval.
