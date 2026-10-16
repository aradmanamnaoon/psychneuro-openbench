# v0 synthetic behavioral trial schema

**Status:** canonical **v0 synthetic-generation** schema for private engineering (implementation and seeded tests verified on pinned blobs); **not** scientific validation, an external dataset-ingestion contract, or a final public release. The schema/API selection and its competing branch are resolved in [ADR-0001](decisions/pm02-reconciliation.md). This schema describes only the generator output; no real people, clinical conditions, identifiers, or sensitive health data are accepted.

## One record per synthetic trial

UTF-8 CSV, LF newlines; composite unique key `(dataset_id, participant_id, session_id, trial_id)`. The generator emits deterministic, contiguous `trial_order` within each subject/session (1-based). IDs are generated from an allowed ASCII-token configuration. **Do not** treat this validator as a complete parser or security boundary for externally supplied datasets; it checks that record IDs are nonempty, but it does not restrict all arbitrary IDs to an ASCII allowlist.

| Column | Python type | Meaning / units | Model use |
| --- | --- | --- | --- |
| `dataset_id` | nonempty identifier string | logical synthetic dataset | provenance only |
| `participant_id` | nonempty identifier string | **invented** participant/group ID | split grouping only |
| `session_id` | nonempty identifier string | synthetic session ID | provenance only |
| `trial_id` | nonempty identifier string | trial identifier, unique within group | provenance only |
| `trial_order` | positive integer | index within session, starts at 1 | provenance only |
| `stimulus_condition` | `left` or `right` | pre-response cue | permitted predictor |
| `difficulty` | finite float 0..1 | unitless synthetic difficulty | permitted predictor |
| `correct` | integer 0 or 1 | synthetic binary target | **target only** |
| `response` | `left` or `right` | choice observed after response | **never a predictor** |
| `response_time_ms` | positive finite float | synthetic post-response latency, **milliseconds** | **never a predictor** |
| `generator_seed` | nonnegative integer | local RNG seed within 64-bit range | provenance only |

The response and response time are deliberately generated but explicitly excluded from pre-response prediction; using them to predict correctness would be severe target leakage. No demographic, diagnosis or neurophysiological claims are encoded.

## Generation semantics

- `SyntheticConfig(seed=42, n_participants=24, trials_per_participant=20)` emits 480 **invented** trials.
- `random.Random(seed)` local PRNG: repeatable on the pinned Python environment; not guaranteed bit-identical across every Python release.
- Response correctness uses arbitrary toy probabilities, **not fitted human-performance parameters**.
- Synthetic latency follows a deliberately invented function and is clamped positive by construction; it is not psychometric evidence.
- Bounded output: maximum 100,000 trials; reject invalid identifiers, seeds, sizes and empty sessions.
- Session identities are scoped to participant; uniqueness enforced on composite key and contiguous trial order. The default emits **one session per participant** (the label `session-01` repeats across participants). Consequently, `dataset_card.n_sessions` is the count of unique **(participant_id, session_id)** pairs, default **24**, not the number of globally distinct session labels or the number of sessions per participant.
- A `dataset_card` declares `schema_version`, `synthetic`, `rights_basis`, `generator_seed`, `source_sha256`, field definitions and feature time availability.
- Source hash is computed over the canonical UTF-8 CSV bytes; any transformation must produce a new hash and provenance entry.

## Research and rights gates

No real dataset ingestion, participant uploads, PHI or clinical outcomes; `rights_basis=synthetic-original` refers to the generated records, **not** any license for this source code. Real-data adapters need independent dataset permission/privacy/ethics review in a later mission. The v0 performance benchmark and its group-aware train/test splitting are **not implemented** by the generator.

[Main science contract](spec-v0.md). Reference: [Python random generator notes](https://docs.python.org/3/library/random.html#notes-on-reproducibility).

## Frozen PM-02 engineering decision and actual test evidence

Use the `main` API and schema above for all PM-03+ examples until a separately versioned and tested migration is approved. Do **not** combine the alternate `congruent/incongruent` trial schema or `reaction_time_ms` field with the canonical `left/right` / `response_time_ms` contract. See [ADR-0001](decisions/pm02-reconciliation.md).

[Hosted CI run #38864568384](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38864568384) confirmed 46 passing tests on both Python 3.11 and Python 3.12, plus Ruff and strict mypy, for matching main-line generator and test blobs. This evidence covers synthetic code only; it does not validate a scientific model, a group-held-out benchmark, an external CSV reader, or rights to use third-party data.


## PM-04 dataset registry and strict loader boundary

The [v0 registry](../data/registry.json) now lists **one enabled internal generator** plus six *disabled public metadata candidates*. The `source_kind`, `source_url`, `source_version`, `source_ref`, `license`, `rights_basis`, `consent_boundary`, `modality`, `review_state` and explicit ingest/download flags are checked by [`registry.py`](../src/psychneuro/registry.py). External data cannot be enabled merely by editing a URL or switching a flag. The synthetic output is generated internally from `SyntheticConfig`; the loader does not parse user CSVs or fetch URLs.

`load_registered_synthetic(config, registry_path)` returns generated trial records, dataset card, validated summary, and source registry metadata. The card's per-export SHA-256 is checked against the serialized dataset, and post-response fields remain excluded by `validate_predictor_columns`. `validate_trials` now rejects boolean values mistakenly passed as numeric difficulty/latency. A missing `synthetic` attestation returns a validation error, rather than an uncaught `KeyError`.

The registry is not a cryptographic signature, consent verification engine or firewall for malicious code. The six external entries represent reviewed *source metadata*, NOT reviewed actual event columns. Source records must not be downloaded, transformed, or modeled using this code. The existing v0 schema's synthetic column names are **not assumed** to match any real research dataset.

[Six-source rights audit](dataset-candidate-audit.md). **Hosted CI for PM-04 source:** [successful run #38874446677](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677) validated the eight exact source/test/registry blobs subsequently fast-forwarded to private `main`: 80 pytest tests, Ruff and strict mypy. Earlier passing PM-04 runs tested an older source state.

### PM-04 follow-up provenance safeguards (private branch)

The registry now rejects a synthetic source URL that does not identify the project's own generator. For disabled real-data candidates, the recorded URL must be an exact OpenNeuro HTTPS snapshot URL consistent with the dataset ID and snapshot version; unrelated domains or query parameters fail validation. These checks constrain the **metadata**, but cannot certify the published license, consent, BIDS events or downloaded raw-file integrity. Exact event variables and actual content hashes remain **not reviewed** for all six human datasets. The synthetic validator requires concrete Python `float` values (not booleans or integers) for difficulty and latency as specified by the v0 typed schema. Regression cases for both type mismatches and metadata tampering **passed hosted verification** in [run #38874446677](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677). The modified CI workflow was temporary; the private default branch still uses manual dispatch.
