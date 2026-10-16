# PM-05 — synthetic-only local loader, quality gate and provenance

**Status:** private implementation, pending hosted CI on the exact PM-05 commit. This
is a software-only fixture loader, not permission to process human participant data.

## Scope and trust boundary

The frozen v0 contract uses `dataset_id`, `participant_id`, `session_id`,
`trial_id`, `trial_order`, `stimulus_condition`, `difficulty`, `correct`,
`response`, `response_time_ms` and `generator_seed`, in that exact order.
Only the internal synthetic registry entry is enabled. Six public human-data
candidates remain **disabled, metadata-only**. A publicly displayed license is
not adequate secondary-use, consent, anonymization or schema evidence.

`load_dataset(SyntheticConfig(...), Path("data/registry.json"))` explicitly
generates the **synthetic fallback**. No source file or raw participant records
are accessed. This path returns a `LoadedDataset` with:

- `records`: original invented trials
- `card` and `schema`: source identity, rights attestation and canonical CSV SHA-256
- `quality`: number of invented subjects, sessions and rows; missing, duplicate,
  invalid-ID, response-time and range diagnostic counts (zero on success)
- `registry_entry`: pre-existing PM-04 rights-gated source metadata
- `provenance`: machine-readable `ProvenanceManifest`

Explicit local export round trip:

```python
from pathlib import Path
from psychneuro.synthetic import SyntheticConfig, to_csv_text
from psychneuro.loaders import load_dataset, manifest_json

registry = Path("data/registry.json")
generated = load_dataset(SyntheticConfig(seed=31), registry)
path = Path("synthetic-trials.csv")
path.write_text(to_csv_text(generated.records), encoding="utf-8", newline="")
reloaded = load_dataset(path, registry, card=generated.card)
assert reloaded.records == generated.records
print(manifest_json(reloaded.provenance))
```

No file is automatically read as a fallback if the requested path is missing,
malformed, not licensed, or not an exact replay of the reviewed generator.

## Supported formats

- **CSV:** local regular non-symlink file, strict UTF-8, exact ordered header,
  exactly 11 columns, strict integer/float parsing, no extra fields; canonical
  line endings are LF on generation. CRLF input is allowed; its raw SHA-256
  differs from the canonical CSV hash if its raw bytes differ.
- **Parquet:** same local contract via optional `pyarrow` dependency
  (`pip install -e '.[parquet]'` in an authorized hosted environment).
  Checks column order and Arrow physical types; rejects type coercion across
  string/integer/float columns.
- **Size limits:** 32 MiB bytes and 100,000 trial rows. These are engineering
  guardrails for small files, **not** a sandbox or a malicious-Arrow defense.
- **Permission:** file parsing is allowed only for an approved synthetic dataset
  card + registry entry. Parsed trial records must be exactly reproducible by
  `generate_trials` with the declared seed/shape/session. Even a forged checksum
  alone cannot bypass replay. No OpenNeuro or other network downloads.
  There is deliberately **no permitted real human dataset code path yet**.
- **Validation:** `validate_quality` checks missing IDs, invalid/empty/non-ASCII
  IDs, composite trial-key/order collisions, numeric ranges, finite values and
  invented reaction-time bounds 100–3000 ms. The PM-04 `validate_trials` and
  `validate_synthetic_dataset` checks are still applied. These latency limits
  are software plausibility rules, **not physiological exclusion thresholds**.

## Provenance manifest contract

`manifest_json(loaded.provenance)` produces JSON with source reference URL,
dataset ID, source version, metadata license, rights basis, consent boundary,
usage limitations, generator revision/seed, input format, transformations,
row count, canonical CSV digest and `raw_file_sha256`.

- `raw_file_sha256` is **null for direct generator output**: no raw file existed.
- `raw_file_sha256` for local CSV/Parquet is SHA-256 of the actual file bytes
  observed at load time; it is never a made-up placeholder or Git blob ID.
- `canonical_csv_sha256` comes from the verified dataset card and is
  independently recomputed by the existing schema validator. For Parquet and
  CRLF CSV it normally differs from the raw byte hash.
- `transformations` is an empty list for this v0 raw-to-record parsing path:
  file parsing is not claimed to be scientific preprocessing. Future filters,
  normalization, de-identification and joins need separately documented
  versioned transformations and post-transform hashes.
- Metadata `license="not-separately-specified"` for original synthetic output
  means **no independent dataset-license grant was inferred** from the
  repository's Apache-2.0 source-code license.

## Negative tests and acceptance gate

`tests/test_pm05_loaders.py` includes deterministic round trips,
raw-vs-canonical hashes, explicit fallback, metadata-only source denial,
empty/missing values, ID collisions, invalid latencies, out-of-range fields,
tampered checksums, forged-but-rehashed data, wrong CSV headers, large files,
optional Parquet and missing registry. When `pyarrow` is not installed,
the optional Parquet integration test is **skipped** rather than reported passed.

**GO for private code review:** only if hosted CI verifies this exact commit
on supported Python versions, including Ruff, strict mypy and pytest.

**NO-GO for public release/real participant data:** until the independent
rights, ethics/privacy, actual event-schema review, leak-free evaluation,
security and external-approval gates in [release-gates.md](release-gates.md)
are satisfied. Repository visibility must not change automatically.
