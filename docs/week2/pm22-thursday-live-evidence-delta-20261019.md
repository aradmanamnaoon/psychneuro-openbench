# PM-22 — W02 Thursday evidence delta (read-only audit)

**Captured:** 2026-10-19 UTC; **scheduled queue:** 2026-10-22 (not yet performed as learner study). **Scope:** existing private `aradmanamnaoon/psychneuro-openbench`. This supplements, does not replace, the 2026-10-19 [Notion-attached full-history manifest](https://app.notion.com/p/3fc977a963b281029afdf24cf13a0e15), the [PM22–42 register](pm22-pm42-evidence.md), and [draft PR #11](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/11). Audit data retrieved through authenticated GitHub repository/branches/actions/job-log reads. This document does **not** attest independent experiment reproduction.

## Live identity, status and evidence

| Check | Direct observation | Decision |
| --- | --- | --- |
| Repository/access | [Private repository](https://github.com/aradmanamnaoon/psychneuro-openbench), connected account push permission | READ verified; NO release |
| Branch inventory | 24 current refs from [branches REST list](https://api.github.com/repos/aradmanamnaoon/psychneuro-openbench/branches?per_page=100), including `main` at `944559a98386dd7c40ea9511ec9857d0714d3ca2` and original W02 branch at `46333ba12da7f56e13bdb548af08937e525057d4` | PASS for point-in-time branch list; does not certify all reachable commits |
| PR #11 | [Draft, open and unmerged](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/11), head `46333ba12da7f56e13bdb548af08937e525057d4`, base `review/pm19-pm21-independent-gates-20261018` | PASS metadata only, NOT approved merge |
| Actions | 16 [observed historical workflow runs](https://github.com/aradmanamnaoon/psychneuro-openbench/actions) through 2026-10-18: 7 success, 9 failure | PASS run metadata enumeration, not all artifact contents |
| Latest successful exact-code CI | [run 39112127659](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39112127659), `push`, 2026-10-18 08:36:54 UTC, tested `dd79565e07923b35db7a7f09e0724a8c0594158e` | PASS **only** at that SHA |
| Latest W02 branch/PR head | `46333ba12da7f56e13bdb548af08937e525057d4`, later documentation change | **NOT RUN** exact-head CI, no CI claim for this head |
| Output artifacts | 12 metadata-listed from run 39112127659, none expired at read time, expiration 2026-10-25 ~08:38 UTC | Metadata PASS; archive download/hash revalidation NOT RUN |
| Critical issue | [#9 generated-export rights](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/9), [#8 live browser/accessibility](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/8) | BLOCKED for release |

## Reproducible CI and scientific baseline

Verified from [two hosted job logs](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39112127659) (jobs `117630310301` / `117630310097`):

- Python **3.11.17** and **3.12.15**, separately: `python -m pytest -q` -> **336 passed** (5.64 s and 6.56 s respectively).
- `python -m ruff check .` -> `All checks passed!`; `python -m mypy src` completed with success in both jobs, exact diagnostics beyond exit status not independently transcribed.
- Installed tool versions in log: `pytest 9.1.1`, `ruff 0.17.1`, `mypy 1.20.2`. Scientific dependencies vary by Python build (e.g. numpy 2.4.6 vs 2.5.4), so bytewise hashes **across Python versions** must not be assumed equal.
- `configs/baseline.json`: original fictional `n_participants=24`, `trials_per_participant=20`, generator seed **73**, participant split seed **42**, training-only CV **5** folds; prior dummy vs `lbfgs` logistic (`C=1`, `max_iter=1000`, RNG 42), pre-response predictors `difficulty` and `stimulus_condition`, primary balanced accuracy and secondary macro-F1. Held-out test is an audit-once partition, **not** the model-selection set.
- Group-overlap negative fixtures, predictor allowlist, invalid/undefined metric denominators, deterministic participant-bootstrap bounds, within-participant frozen-prediction nulls and provenance shift guards are in [week2 test source](../../tests/test_week2_controls.py) and [implementation](../../src/psychneuro/week2_controls.py). The permutation control **does not refit** trained models and provides no calibrated model-comparison p-value. Bootstrap confidence intervals are **conditional on fixed predictions**, not population/clinical inference.
- `data/registry.json` reports **one internal original-synthetic** source with `license=not-separately-specified`; six external human-neuro entries are all `enabled=false`, `download_allowed=false`, `participant_data_ingestion_allowed=false`. An Apache-2.0 source-code licence must not be promoted to unapproved exported-data rights.

## Prior outcomes remain visible (do not cherry-pick)

| Run | Commit prefix | Observed conclusion |
| --- | --- | --- |
| [39112127659](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39112127659) | dd79565e | SUCCESS |
| [39111357989](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111357989) | 36dbf9a8 | SUCCESS |
| [39111068691](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111068691) | 250edb3b | FAILURE |
| [39109383260](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39109383260) | 2479f0d3 | SUCCESS |
| [39109196766](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39109196766) | 7bde3a75 | FAILURE |
| [39109048291](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39109048291) | 3f3041e9 | FAILURE |
| [39108935161](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39108935161) | 0a6efdd1 | FAILURE |
| [39108357175](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39108357175) | c4a687b5 | FAILURE |
| [39108122761](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39108122761) | ba92175a | FAILURE |
| [38874446677](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677) | 6f63804b | SUCCESS |
| [38874202366](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874202366) | bffef4b1 | FAILURE |
| [38865440963](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38865440963) | 6d513f7e | SUCCESS |
| [38864568384](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38864568384) | f0fb8a92 | SUCCESS |
| [38863471313](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313) | 76acb869 | SUCCESS |
| [38863401519](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863401519) | f671f38f | FAILURE |
| [38863252315](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863252315) | 24ab27d1 | FAILURE |

## Current acceptance, gap and next reproducible action

1. **PM-22: PARTIAL / Needs Review.** A previously attached W01/W02 expanded manifest claims 229 unique reachable commits across 24 refs; **that graph count was not re-enumerated in this audit**. This live delta independently checks 24 refs, 16 run metadata records, both successful job logs, config and registry.
2. Test all branch heads/commit ancestry against the attached manifest with a complete paginated Git refs/commit graph and independently reviewed data export hashes; then capture a signed reviewer note. No CI at post-test docs-only head; do not spend CI minutes just to claim docs are tested. This evidence-only branch is intentionally outside the two CI push filters in `.github/workflows/ci.yml`.
3. **PM-23: BLOCKED** pending rights-holder decision about separate redistribution licence of fictional generated exports. External human entries remain disabled. **PM-24: Verified Done (existing)** at the already tested baseline contract, not a claim of real-data empirical validity.
4. No publishing, outreach, actual participants, Academy attendance, inference about the learner, branch merge, PR opening or author-review signoff was performed by this audit.

**Method:** live private GitHub connector reads on 2026-10-19; no GitHub CLI or local runtime required of the human reviewer. Source claims are only as strong as linked GitHub/Notion state at capture time.
