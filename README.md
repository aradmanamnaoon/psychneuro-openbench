# PsychNeuro OpenBench

**Status: private, pre-release research-software prototype. This repository has not demonstrated scientific validity or benchmark performance.**

PsychNeuro OpenBench aims to make nonclinical behavioral trial-level ML benchmarking reproducible, with subject-held-out splits, lawful data provenance, transparent baselines, and audit-ready reports. The first engineering slice is deliberately synthetic only.

## What is actually implemented

- A typed, bounded Python standard-library generator of entirely invented two-choice trials (response, correctness, reaction time in milliseconds).
- A strict structural validator for its output, a canonical CSV exporter, and a synthetic dataset card with source-byte SHA-256.
- Verified GitHub-hosted tests for deterministic generation, schema validation, invalid inputs/edge cases, and serialization: **31 passed**. Ruff lint and strict mypy source checks also passed; [successful CI run](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313) used the exact source/test blob content now on `main`.
- A proposed benchmark reproducibility specification in [docs/spec-v0.md](docs/spec-v0.md).

A subject-group-aware ML benchmarking engine, real dataset adapters, a hosted interface, and a verified reproducibility release are **not implemented**.

## Intended developer verification (not instructions to the project owner)

Python >=3.11, in a suitable authorized test environment:

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check .
python -m mypy src
```

The default-branch workflow remains **manual-only** (`workflow_dispatch`) to avoid recurring private-repository runner usage. A separate branch, `ci/pm02-verification`, was used for limited hosted checks. This is **engineering validation of the synthetic fixture**, not a scientific benchmark or clinical verification.

## Source example

```python
from psychneuro.synthetic import SyntheticConfig, generate_trials, to_csv_text, dataset_card

config = SyntheticConfig(seed=42, n_participants=24, trials_per_participant=20)
records = generate_trials(config)
csv_text = to_csv_text(records)
card = dataset_card(config, records)
assert card["n_trials"] == len(records)
```

All participant IDs and responses are invented. The generator is an engineering test fixture, **not a model of empirical human behavior**. `response`, `response_time_ms`, `correct` (the target), and identifiers must not be supplied as ML predictors of pre-response correctness.

## Project documents

- [Scientific vertical-slice contract](docs/spec-v0.md)
- [Trial data schema](docs/data-schema.md)
- [License and data rights](docs/license-policy.md)

## Legal and privacy status

No externally obtained participant data or PHI. The source code has **no open-source license grant** until the owner chooses one. No redistribution, clinical use, diagnosis, treatment advice, or medical benefit claims are authorized by this prototype.
