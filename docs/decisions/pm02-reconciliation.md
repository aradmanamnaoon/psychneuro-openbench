# PM-02 decision ADR-0001 — canonical v0 synthetic foundation

**Date:** 2026-10-16. **Decision:** accept the **already hosted-tested `main` implementation** as the canonical PM-02 v0 engineering foundation. Preserve the alternate implementation for reference, but **do not merge** it into v0. **Status:** technical reconciliation complete; Apache-2.0 licensing decision recorded separately, while public publication approval is still required.

## Context and evidence

- [PM-01 scientific contract](../spec-v0.md) defines exactly one **synthetic-only** binary-outcome trial task with subject, session and trial keys; pre-response condition/difficulty; target `correct`; generated post-response data excluded from predictors. It does not require a specific number of sessions or a particular enum for the declared condition, so those are implementation decisions.
- [Canonical `main` source](../../src/psychneuro/synthetic.py) and [schema](../data-schema.md) expose `SyntheticConfig`, `generate_trials`, `validate_trials`, `to_csv_text`, and `dataset_card`, with schema version `0.1.0`. Default shape: **24 fictional participants × 20 trials, one named session within each participant = 480 records**. `stimulus_condition` is the left/right cue; `response_time_ms` uses milliseconds. Seed is an integer in [0, 2^64-1].
- [Alternate `pm-02/synthetic-foundation`](https://github.com/aradmanamnaoon/psychneuro-openbench/tree/pm-02/synthetic-foundation) exposes a different API (`generate_reaction_times`, `make_dataset_card`, `to_csv_bytes`), a different schema (`congruent/incongruent`, `stimulus_side`, `reaction_time_ms`, `seed`) and two sessions × ten trials per participant. It also changes seed bounds and generator parameters. It is **not** a drop-in replacement and has **not** been separately validated by the cited 46-test run.

## Alternatives considered

| Option | Pros | Cons | Decision |
| --- | --- | --- | --- |
| Retain `main` | Verified generator/test blobs; PM-03 regression tests target it; no breaking schema changes | No two-session demonstration yet | **CHOSEN for v0** |
| Replace with alternate branch | Additional session and congruency examples | Unverified against the main-line tests, breaks API/CSV/card, requires new migrations and hosted evidence | **REJECTED for v0** |
| Combine fields into current v0 | Richer illustrative protocol | Larger, untested scope and ambiguous version compatibility | Defer to explicitly versioned extension |

**Preservation:** do not delete the alternate branch, its code or earlier Notion attachments; mark them historical/proposed. New work starts from `main` (or a fresh feature branch based on it). Multi-session or congruency-specific extensions require their own schema version, migration rationale, negative tests and separate hosted evidence.

## Canonical v0 field/semantics freeze for downstream PM-03+

- Dataset is entirely synthetic. CSV column order is the `CSV_COLUMNS` tuple in `src/psychneuro/synthetic.py`, not the abandoned alternate schema.
- `participant_id` is the generalization group. `session_id` is **scoped to participant** and is currently the same literal label, `session-01`, in every participant. Thus the card's `n_sessions=24` refers to **24 distinct (participant_id, session_id) occurrences**, not 24 unique session labels or 24 per-participant sessions.
- `stimulus_condition` (`left`/`right`) and `difficulty` are allowed example pre-response predictors. `correct` is the target. `response`, `response_time_ms`, `participant_id`, `session_id`, `trial_id`, trial order and `generator_seed` must **not** be used as features in the proposed v0 correctness benchmark.
- `response_time_ms` is invented post-response duration in **milliseconds**. All values and effect parameters are arbitrary; there is no cognitive, clinical or physiological interpretation.
- The current generator validates its own configuration (short ASCII IDs) and emitted records; `validate_trials` is **not** a fully trusted external CSV/dataset admission layer. It checks nonempty IDs but does not validate every imported string's allowed character set. Untrusted imports require separate fail-closed parsing and provenance gates.
- Dataset card `source_sha256` is the SHA-256 over the UTF-8 encoded CSV text. It is not a hash of the machine, code, license, or scientific validity; full replay needs frozen environment, software versions, split assignments and downstream manifest.

## Independent engineering audit

- [Successful CI run `38864568384`](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38864568384): **46 tests passed on Python 3.11 and 46 on Python 3.12**, Ruff checks passed and strict mypy reported no issues on two source files.
- Confirmed exact Git blob identity across the CI audit branch and current `main`: `src/psychneuro/synthetic.py` at `6d51a40848a0c6fecf2d36bcba54c583b23af143`, `tests/test_synthetic.py` at `cf9d159f84917b3f7be57f3a1e175445fa2eb470`, and `tests/test_synthetic_pm03.py` at `beaad2362707e9a8851e057634b55ecdf2d56e92`. CI results pertain to these exact code/test blobs; **no new test is being claimed** for documentation changes.
- Reviewed [PM-03's independent backlog](../../docs/decisions/week1.md), [real GitHub issues #1–#6](https://github.com/aradmanamnaoon/psychneuro-openbench/issues), [source rights](../license-policy.md), and [private release gates](../release-gates.md).
- PM-02 scope P1-005–P1-008 is implemented and verified **as a narrow synthetic engineering foundation**. The contract's full evaluation pipeline (group holdout, baselines, uncertainty, run manifests) remains **out of scope for PM-02** and is not accepted as completed.

## Legal and approval gates

**Resolution (2026-10-16):** Apache License 2.0 was selected for the original project and is present in [LICENSE](../../LICENSE), with attribution in [NOTICE](../../NOTICE). Third-party contributions, datasets, dependencies and assets require independent rights review. At the time this ADR was written the repository was private; it is now public, but public source availability does not certify a versioned software release. See the [licensing decision log](../license-policy.md).

**Accepted scope:** Apache-2.0 for the original PM-02 code/documentation and synthetic-only development using the canonical `main` API and schema. **Not established:** verified integrated release, authorization for real-human data, biomedical effects, or scientific/clinical generalization claims. These require the current [release criteria](../release-gates.md).

**Disposition:** The PM-02 technical reconciliation and license selection are recorded as a narrow engineering milestone. Further evaluation, supported releases and data permissions remain independent decisions.
