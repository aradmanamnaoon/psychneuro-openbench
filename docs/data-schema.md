# v0 synthetic behavioral trial schema

**Status:** private, unverified engineering contract. This file describes the only admissible v0 records; no real people, clinical conditions, identifiers, or sensitive health data are accepted.

## One record per synthetic trial

UTF-8 CSV, LF newlines; composite unique key `(dataset_id, participant_id, session_id, trial_id)`. The generator emits deterministic, contiguous `trial_order` within each subject/session (1-based).

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
- Session identities are scoped to participant; uniqueness enforced on composite key and contiguous trial order.
- A `dataset_card` declares `schema_version`, `synthetic`, `rights_basis`, `generator_seed`, `source_sha256`, field definitions and feature time availability.
- Source hash is computed over the canonical UTF-8 CSV bytes; any transformation must produce a new hash and provenance entry.

## Research and rights gates

No real dataset ingestion, participant uploads, PHI or clinical outcomes; `rights_basis=synthetic-original` refers to the generated records, **not** any license for this source code. Real-data adapters need independent dataset permission/privacy/ethics review in a later mission. The v0 performance benchmark and its group-aware train/test splitting are **not implemented** by the generator.

[Main science contract](spec-v0.md). Reference: [Python random generator notes](https://docs.python.org/3/library/random.html#notes-on-reproducibility).
