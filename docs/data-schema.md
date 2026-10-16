# PM-02: synthetic behavioral data schema (draft)

**Status:** implemented as candidate code; requires human review against the PM-01
[spec-v0](spec-v0.md). The dataset is invented, **not** real participant data and
not a validated behavioral or clinical simulator. Schema version \`0.0.1-draft\`.

## Contract

| Field | Type, constraints | Role and units |
| --- | --- | --- |
| dataset_id | 1-64 safe ASCII token chars | Synthetic dataset label |
| participant_id | Opaque \`sub-NNNN\` | Group ID; no actual person |
| session_id | Opaque \`ses-NN\` | Session within invented participant |
| trial_id | Opaque \`tr-NNNN\` | Unique with dataset, participant, session |
| trial_order | positive integer, contiguous from 1 per session | Order/count |
| stimulus_condition | \`congruent\` or \`incongruent\` | Pre-response feature |
| difficulty | finite 0.0 to 1.0 | Invented pre-response feature, dimensionless |
| stimulus_side | \`left\` or \`right\` | Invented pre-response cue; not model feature in PM-01 default |
| response | \`left\` or \`right\` | Post-response, forbidden model feature |
| correct | integer 0 or 1 | Synthetic binary target, forbidden predictor |
| reaction_time_ms | finite float > 120 | **Milliseconds**; post-response, forbidden predictor |
| seed | integer 0 to 2^32-1 | Dataset-generation provenance only |

Compound primary key: (\`dataset_id\`, \`participant_id\`, \`session_id\`, \`trial_id\`).
\`trial_order\` is unique within participant/session; an example output contains no
missing values. Real user identifiers, response free text, timestamps, diagnoses,
and clinical labels are prohibited by this generator. Zero real data rights required.

## Generator and serialization

- API: \`generate_reaction_times(seed=..., n_participants=24, n_sessions=2,
  trials_per_session=10, dataset_id="synthetic-rt-v0")\`.
- Example size: 24 × 2 × 10 = 480 *invented* trial records.
- A local \`random.Random(seed)\` instance isolates global RNG state. The
  same seed/arguments/runtime/source produces equal ordered rows.
- Conditions differ by at most one within each participant/session; trial
  correctness and response side are consistent.
- Invented correctness probability = 0.94 - 0.09 if incongruent - 0.08*difficulty.
  Parameters are arbitrary; **no effect-size or accuracy claim about humans**.
- Invented RT = 120 + exp(log(320) + participant_offset + condition_shift
  + 0.20*difficulty + Gaussian noise), reported in milliseconds.
- \`to_csv_bytes(rows)\` emits UTF-8 CSV with LF line endings, fixed field order,
  and current-Python-version float formatting. Reproduction across different
  Python versions is NOT promised by the standard library random module.
- \`make_dataset_card(rows)\` emits the preliminary fields named in PM-01:
  schema/version, source generator/revision, rights basis, SHA-256 of CSV bytes,
  synthetic flag, seed, field definitions, counts, target and feature timing.
- At most 100,000 rows are generated per call, in-memory. Not a large dataset
  loader or production ingestion pipeline. The dataset card is still a draft;
  no external dataset is imported or redistributed.

## Leakage and experimental restrictions

Only \`stimulus_condition\` and \`difficulty\` are the v0 default pre-response
predictors. Do **not** train against \`response\`, \`reaction_time_ms\`,
\`correct\`, IDs, or post-trial signals. Participant-level split safety, schema
validation, missingness, immutable run manifests and model benchmarking belong
to later missions and must fail closed when missing. Do not interpret generated
accuracy, latencies or condition shifts as observed neuroscience findings.

## Rights, versions, and test gates

Original synthetic records contain no personal data, clinical claims, or
third-party datasets. Source code license undecided pending owner approval.
Tests cover deterministic rows/CSV, uniqueness, balance, unit domains,
target/response agreement, safe IDs, global RNG isolation, boundary parameters,
card checksums and empty/mixed-source errors. Tests must run in hosted CI before
claiming implementation quality. Preserve Python/runtime/source revision in
any full reproducibility manifest; \`generator_revision\` alone is not a Git SHA.

Official reference: https://docs.python.org/3/library/random.html#notes-on-reproducibility
