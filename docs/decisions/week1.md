# Week 1 engineering decisions and verification — 2026-10-16

> **Private / pre-release.** This ledger separates completed source work from tests actually executed and features not yet built. Public release requires [the explicit release gate](../release-gates.md) and owner approval.

## Branch reconciliation

- **Canonical current implementation:** `main` uses `SyntheticConfig`, `generate_trials`, `validate_trials`, `to_csv_text` and `dataset_card` from [src/psychneuro/synthetic.py](../../src/psychneuro/synthetic.py). It produces **one synthetic session per participant** with bounded synthetic left/right trials, post-response latency in milliseconds, and no clinical claims.
- **Preserved alternative (not merged):** [`pm-02/synthetic-foundation`](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm-02/synthetic-foundation) defines a different, multi-session `generate_reaction_times` API, a `congruent/incongruent` task, and a `reaction_time_ms` field. These schemes must not be silently conflated. The alternate implementation is neither discarded nor scientifically accepted.
- **Preserved PM-03 history:** [`pm03-quality-foundation`](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm03-quality-foundation) holds draft README/ledger, an optional Python matrix workflow and independent regression tests. Supplemental tests are being integrated using their exact Git blob, rather than copying outdated draft README/CI claims.
- **Owner release policy:** keep repository private until the full research-software requirements are implemented, verified and explicitly approved for public visibility. Documentation polish or passing toy tests alone is insufficient.

## Actual engineering evidence

- [PM-01 benchmark spec](../spec-v0.md) committed in [2103ef2](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/2103ef2e638257dd85518e6bceacf53722dd849b).
- [Generator foundation](../../src/psychneuro/synthetic.py), [original tests](../../tests/test_synthetic.py), [schema](../data-schema.md) and [rights policy](../license-policy.md) are actual GitHub files.
- [Hosted successful PM-02 run 38863471313](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313): **31 pytest passed**, Ruff passed, strict mypy passed on Python 3.11, applying exactly the [validated source/test Git blobs](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/ee9eb00f2579a95c404d0ba2f332e7a28d7d502d).
- [Expanded README](../../README.md) and [release gate document](../release-gates.md) committed during private development.
- **Additional PM-03 tests:** [tests/test_synthetic_pm03.py](../../tests/test_synthetic_pm03.py) includes independent CSV schema, seed-hash, bad/missing dataset card, invalid order, mixed seed, forbidden category, latency/provenance and identifier boundary checks. Keep test status separate from the older 31-test result until a new Actions job is inspected.

## Existing backlog (do not duplicate)

1. [#1 synthetic schema and card invariants](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/1)
2. [#2 seeded reproducibility / edge-case testing](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/2)
3. [#3 subject-level leakage prevention](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/3)
4. [#4 shared-fold transparent baselines](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/4)
5. [#5 lawful provenance and rights registry](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/5)
6. [#6 canonical run manifest and audit evidence](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/6)

## Scientific boundaries

Synthetic data only. No human participant records, real-life validity, clinical claims or independent adoption. The **group-held-out benchmarking engine has not been built**; baseline scores/uncertainty are not measured. Original source code has an Apache-2.0 license, distinct from dataset licenses, and a future real dataset requires explicit rights and privacy checks.

## Next actions / release gate

After supplemental quality checks genuinely pass: place compatible tests and this ledger on `main` without replacing the validated generator or making the repository public; record run URL/commit and preserve alternate branches. Continue to the subject-held-out leakage engine, then simple matching-fold baselines. No PR, public release, or website/profile change without owner approval.

## Verified PM-03 integration CI (2026-10-16)

- Dedicated audit branch: [`ci/pm03-quality-audit`](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/ci/pm03-quality-audit) at commit [`f0fb8a9`](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/f0fb8a928f6e6c7ff83689a29a6546bd9c3a44dc).
- [**Completed successful hosted run 38864568384**](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38864568384), jobs `116854322772` (Python 3.11) and `116854323176` (Python 3.12); both job logs fetched and inspected.
- **Python 3.11:** 46 pytest passed in 0.19s, Ruff all checks passed, mypy no issues in 2 source files.
- **Python 3.12:** 46 pytest passed in 0.08s, Ruff all checks passed, mypy no issues in 2 source files.
- The same audited PM-03 supplemental-test blob was promoted to `main`; the main branch's workflow stays **manual-only**. The test counts do **not** imply a group-aware ML benchmark, a real dataset or a browser application exists.
- Existing six GitHub issues and the old PM-03 draft branch remain preserved. Neither alternate PM-02 code nor stale PM-03 README was blindly merged. Repository is still PRIVATE and release remains gated by `docs/release-gates.md`.

## PM-04 provenance, source-rights, and schema check — 2026-10-16

- [Dataset candidate research](../dataset-candidate-audit.md) inspects six fixed-version OpenNeuro task datasets, including license/participant counts and explicit unknowns; all six are **not enabled**, and a clinical-context candidate is excluded. No downloads, human record operations, or clinical inference were performed.
- [Source validation](../../src/psychneuro/schema.py) and [synthetic registry](../../data/registry.json) implement a fail-closed synthetic-only gate. [Additional negative tests](../../tests/test_schema.py) cover rejected external rights, tampered source hashes, bad counts and illegal post-response predictors.
- Actual one-off private [PM-04 GitHub Actions run 38865440963](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38865440963): `completed/success`, **60 pytest passed in 0.15s**, Ruff passed, mypy no issues in **3 source files** on GitHub-hosted Python 3.11; logs fetched and checked. The actual audited branch was [`ci/pm04-schema-audit`](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/ci/pm04-schema-audit), commit [6d513f7](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/6d513f7e7f670b6fedd00da0bc06e4043dd6913d).
- Only verified source/test/artifact blob content is promoted to `main`; the default workflow remains manual-only. Source-rights vetting for actual study-level data and participant confidentiality remains future work.


## Final PM-04 rights/schema/registry verification and private-main integration (2026-10-16)

- **Implementation:** [private `main` integration commit](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/1a02163fb474bee0cdd2f418d304c22dc4dff392) includes source and tests for the verified synthetic-only v0 provenance registry, six disabled published-source metadata records, strict numerical feature validation, source origin/snapshot checks, documentation and rejected-import test cases. All real study datasets remain unapproved for ingestion.
- **Initial explicitly authorized 4-minute-capped GitHub Actions run:** [#38874202366](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874202366) passed **80 pytest tests**, then failed on two Ruff `TRY004` invalid-exception-type findings. Mypy did not execute in that failed attempt. The defects were corrected using `TypeError` in `registry.py`; no failing test result was concealed or described as success.
- **Corrective hosted verification:** [#38874446677](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677), GitHub runner job `116885991972`, commit `6f63804b5c476a689085b0ce8080452f2181d572`, Python 3.11: **80 pytest passed in 0.13s; Ruff: all checks passed; strict mypy: no issues in 4 source files.** Full logs retrieved and inspected.
- **Immutable-code identity:** The eight changed source/test/registry/research files have matching Git blob SHA values on `pm-04/rights-registry-validation` and the successful `ci/pm04-final-verification` run. The CI branch differs only in its one-off workflow file; `main` preserves the original manual-dispatch-only workflow and received a **fast-forward** to the verified source branch.
- **Legal/consent boundary:** Software is Apache-2.0; that does not license any third-party dataset. Synthetic fixture records are invented; their data license has not been separately declared. All six real study datasets remain disabled without participant consent/ethics and snapshot event-file suitability reviews. No human data, clinical claims, external communications, new public release or website/profile changes.
- **Review status:** PM-04 complete for its narrow P1-014 through P1-017 acceptance requirements. This does **not** prove empirical benchmark validity, full-product completion, or readiness to publicly release. PM-05 (source-aware CSV/Parquet and validation pipeline) can move to Ready for private engineering only, with its own future CI and rights gates.
