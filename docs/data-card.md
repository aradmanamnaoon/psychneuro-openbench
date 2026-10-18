# PsychNeuro OpenBench — synthetic pilot dataset card

**State:** internal v0 software fixture; NOT an empirical, clinical, human-subject, or peer-reviewed dataset. This card covers the only dataset currently admitted by the private repository.

## Source, identity and rights

| Field | Verified contract |
| --- | --- |
| Dataset ID | `psychneuro-synthetic-v0` |
| Title | Entirely synthetic two-choice response task |
| Source | [Original deterministic generator](../src/psychneuro/synthetic.py), `psychneuro.synthetic.generate_trials` |
| Schema / generator revision | `0.1.0` / `0.1.0` |
| Rights approval | [Registry](../data/registry.json): only the synthetic entry is enabled |
| Source kind and rights basis | `synthetic`, `synthetic-original` |
| Source version | Exact repository commit at execution time, plus generator revision |
| Default PM-06 pilot | Seed 73, 12 fictional participants, 20 trials per participant, one session each |
| Source digest | Per-run SHA-256 of canonical UTF-8 CSV bytes, never a fixed invented hash |
| Raw-byte digest | `null` for direct generator; SHA-256 of actual local CSV/Parquet file otherwise |
| Transforms | `[]` (none) |

Original generated records have **no separately granted public dataset license**
(`license=not-separately-specified`). The repository's Apache-2.0
[LICENSE](../LICENSE) grants rights for source code and documentation as described in
[software licensing policy](license-policy.md), and does not clear external data.
No real people participated, so consent is not applicable to these invented
trials; no human-subject research ethics approval is asserted.

## Intended audiences and permitted use

This fixture supports research-software developers, computational psychology /
neuroscience engineers, instructors and benchmark auditors testing
reproducibility, loader correctness, schema validation, leakage controls, and
participant-group-aware evaluation infrastructure. It is NOT for research
inference about cognition, human neural processes, behavioral effects,
treatment, diagnosis, or clinically useful training.

## Schema and feature timing

The exact serialized CSV/Parquet column order is as follows.

| Column | Type and use |
| --- | --- |
| `dataset_id` | Nonempty ASCII dataset identifier; exclude as predictor |
| `participant_id` | Invented subject identifier; grouping/splitting only |
| `session_id` | Invented session ID; grouping/splitting only |
| `trial_id` | Trial ID; composite uniqueness key, not a predictor |
| `trial_order` | Positive contiguous trial index within session; exclude in v0 |
| `stimulus_condition` | Pre-response left/right cue; permitted predictor |
| `difficulty` | Finite float [0,1]; pre-response artificial scalar, permitted predictor |
| `correct` | Binary integer 0/1; target only, never a predictor |
| `response` | Post-response left/right selection; prohibited predictor (leakage) |
| `response_time_ms` | Finite positive invented latency; prohibited predictor (leakage) |
| `generator_seed` | 64-bit unsigned integer; provenance only |

Composite uniqueness: (`dataset_id`, `participant_id`, `session_id`,
`trial_id`) and per-session trial order. The loader enforces synthetic-only
reaction time bounds **100–3000 ms**, purely engineering plausibility limits,
not biological cutoffs.

## Quality controls, provenance and limitations

[PM-05 ingestion](../src/psychneuro/loaders.py) enforces strict UTF-8, CSV
column counts/order, Parquet schema types, row bounds, non-symlink local files,
registry approval, required card and source identity, finite/ranged values,
empty identifiers, collision counts, response/correctness consistency, and exact
deterministic replay for local exports. It fails closed, with no implicit fallback.
The returned `ProvenanceManifest` documents source URL, version, rights,
consent boundary, seed, generator revision, input format, SHA-256 identities,
transformations and actual trial count. Metadata is not a scientific validity
claim.

- Invented participant ability, accuracy and latency distributions are arbitrary
  simulation mechanics, not validated human behavior.
- Participant trials are dependent; never leak one participant between
  training and test splits.
- Given the stimulus, response encodes the target; it and response latency
  must not be used as pre-response predictors.
- No generalization, fairness, real-world privacy, clinical, or effect claims.
- External [OpenNeuro candidates](dataset-candidate-audit.md) are **disabled
  metadata-only**; no source rows are downloaded, admitted or redistributed.
  Public licenses are not sufficient proof of consent, task schema, ethics,
  participant privacy or acceptable secondary use.
- Input parsing is not a security sandbox for adversarial Parquet files.

## Exploration, reproducibility, citations

The [pilot protocol](pilot-exploration-protocol.md) and
[exploration implementation](../src/psychneuro/explore.py) generate descriptive
artifacts **only when executed on an authorized host**; no numbers or graphics
are claimed in the absence of a matching run link and artifacts. Log exact Git
SHA, generator parameters, Python/dependency versions, source manifest, CI
results and transformations. Internal citation: *PsychNeuro OpenBench authors,
synthetic pilot v0, generator revision 0.1.0, exact code commit + manifest.*
Repository is private; no public or peer-review status is claimed.
