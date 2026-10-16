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

Synthetic data only. No human participant records, real-life validity, clinical claims or independent adoption. The **group-held-out benchmarking engine has not been built**; baseline scores/uncertainty are not measured. Source-code license is undecided, and a future real dataset requires explicit rights and privacy checks.

## Next actions / release gate

After supplemental quality checks genuinely pass: place compatible tests and this ledger on `main` without replacing the validated generator or making the repository public; record run URL/commit and preserve alternate branches. Continue to the subject-held-out leakage engine, then simple matching-fold baselines. No PR, public release, or website/profile change without owner approval.

## Verified PM-03 integration CI (2026-10-16)

- Dedicated audit branch: [`ci/pm03-quality-audit`](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/ci/pm03-quality-audit) at commit [`f0fb8a9`](https://github.com/aradmanamnaoon/psychneuro-openbench/commit/f0fb8a928f6e6c7ff83689a29a6546bd9c3a44dc).
- [**Completed successful hosted run 38864568384**](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38864568384), jobs `116854322772` (Python 3.11) and `116854323176` (Python 3.12); both job logs fetched and inspected.
- **Python 3.11:** 46 pytest passed in 0.19s, Ruff all checks passed, mypy no issues in 2 source files.
- **Python 3.12:** 46 pytest passed in 0.08s, Ruff all checks passed, mypy no issues in 2 source files.
- The same audited PM-03 supplemental-test blob was promoted to `main`; the main branch's workflow stays **manual-only**. The test counts do **not** imply a group-aware ML benchmark, a real dataset or a browser application exists.
- Existing six GitHub issues and the old PM-03 draft branch remain preserved. Neither alternate PM-02 code nor stale PM-03 README was blindly merged. Repository is still PRIVATE and release remains gated by `docs/release-gates.md`.
