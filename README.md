# PsychNeuro OpenBench

**Status: private, pre-release nonclinical research-software prototype; implementation and tests are not yet hosted-CI verified.**

PsychNeuro OpenBench aims to support reproducible behavioral trial-level machine-learning methods, with subject-held-out splits, provenance checks, transparent baselines, and audit-ready reports. Intended readers: psychology methods students, research assistants, computational neuroscience analysts, and ML reproducibility reviewers. The first engineering slice is synthetic only.

## Implemented candidate foundation (PM-02)
- A typed Python standard-library generator of invented left/right trials with `SyntheticConfig`, `TrialRecord`, `generate_trials`.
- Local seeded RNG, bounded record count, schema validation, canonical CSV, and a synthetic dataset card with source-byte SHA-256.
- Existing PM-02 [generator tests](tests/test_synthetic.py) plus [PM-03 supplemental checks](tests/test_synthetic_pm03.py) for edge cases and replay invariants. **Test files have been authored; a passing CI run is not yet evidenced.**
- [Scientific v0 contract](docs/spec-v0.md), [field schema](docs/data-schema.md), and [software/data rights policy](docs/license-policy.md).

**Not implemented:** group-respecting ML evaluation, real-data ingestion, hosted interactive experiment interface, benchmark accuracy metrics, external validation, released package or clinical assessment.

## Generated trial example (developer-facing)

```python
from psychneuro.synthetic import SyntheticConfig, dataset_card, generate_trials, to_csv_text

config = SyntheticConfig(seed=42, n_participants=24, trials_per_participant=20)
records = generate_trials(config)
csv_text = to_csv_text(records)
card = dataset_card(config, records)
assert card["n_trials"] == len(records)
```

This synthetic fixture has **no empirical human-behavior calibration**. `response`, `response_time_ms`, IDs and `correct` (the target) cannot be predictors of the same-trial pre-response correctness.

## Seed / reproducibility contract

`SyntheticConfig.seed` controls a local `random.Random` instance. A pinned Python environment, equal implementation/configuration, and the same seed should reproduce the same records, CSV and source digest. Cross-version or cross-platform bitwise identity is **not** guaranteed. Synthetic samples demonstrate software mechanics, not inferential or clinical validity.

## Installation-free reviewer workflow in a browser

No local development setup is required for **review**:
1. Review [v0 scope](docs/spec-v0.md), [schema](docs/data-schema.md) and [license policy](docs/license-policy.md).
2. Inspect the [seeded/schema tests](tests/test_synthetic.py) and [supplemental PM-03 regression tests](tests/test_synthetic_pm03.py).
3. Open the [manual CPU workflow](.github/workflows/ci.yml) and the [GitHub Actions page](https://github.com/aradmanamnaoon/psychneuro-openbench/actions). Only a real completed run/log tied to a specific SHA counts as evidence; none is claimed here.
4. Check the [evidence ledger](docs/decisions/week1.md) and [six development issues](https://github.com/aradmanamnaoon/psychneuro-openbench/issues).

This is **browser-only inspection**, not a browser-executable simulation or benchmark. A zero-install public demo is planned for a later milestone and is **not deployed**.

## Hosted test workflow, pending authorized run

The [CPU test workflow](.github/workflows/ci.yml) is `workflow_dispatch`-only and uses Python 3.11 and 3.12. It installs the editable package + development dependencies, then executes pytest, Ruff and strict mypy. This avoids silently consuming private-repository runner minutes before Action availability and cost authorization are verified. Manual local commands shown for future contributors (not requested of the human reviewer):

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check .
python -m mypy src
```

No passing results or CI log URLs exist in this README.

## Engineering backlog (actual private GitHub issues)

- [#1 Trial schema and dataset-card validation](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/1)
- [#2 Seeded generator reproducibility and edge cases](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/2)
- [#3 Participant leakage prevention](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/3)
- [#4 Dummy/logistic comparison](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/4)
- [#5 Provenance/rights fail-closed registry](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/5)
- [#6 Stable manifest and CI evidence](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6)

## Rights, privacy and scientific limits

All identities and outcomes are invented. No PHI, identifiable participants, EEG, fMRI, clinical diagnosis, intervention or medical-performance assertions. New real datasets require independent consent/ethics/privacy and per-dataset license verification. No software license has yet been chosen: `rights_basis=synthetic-original` refers to the synthetic data, **not** a code redistribution license. No release, outreach, website/profile update or external collaboration has been authorized.
