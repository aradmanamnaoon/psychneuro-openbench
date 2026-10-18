# Week 2 PM22–PM42 engineering audit and acceptance ledger

**Date created 2026-10-18; scheduled 2026-10-22–28 queue is FLEXIBLE, not proof that five missions were accomplished each calendar day.** All narrative/source decisions are AI-assisted. Original repo is private, all external participant sources disabled; no public release, unapproved outreach or spending. The CI run for the first tested Week 2 controls is [39111357989](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111357989) on SHA 36dbf9a8c37e8f5bf55576dd7f8456433d5b1c81: both Python 3.11/3.12 SUCCESS, 335 pytest passed each, Ruff and strict mypy 21 source files pass, 10 original synthetic archives. A newer Week 2 scenario demo has separate exact-SHA CI; verify its conclusion before upgrading its rows. This document is a **requirements/evidence ledger, not proof of every scientific task fully done**.

## PM-22 — source / commit / CI provenance audit

- Reused original v0 private repository https://github.com/aradmanamnaoon/psychneuro-openbench and reference branch W01 code audited by [run 39109383260](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39109383260), SHA 2479f0d322b3179c30b64673f8beac584a4ba162 (318 pytest per Python, real hosted CI). W02 forked from W01 documentation head 3e44d94509dc83c02be85a781e28a9204c0b5bd8; initial W02 code 250edb3b2b9c1a4eafdc228ca201a0043a9e27f4 had [run 39111068691 FAILURE](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111068691) with 334 passing + 1 test-assertion mismatch per Python; correction at SHA 36dbf9a8c37e8f5bf55576dd7f8456433d5b1c81 then [run 39111357989 PASS](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111357989).
- Verified reference artifacts: config [baseline.json](../../configs/baseline.json), original-synthetic [registry.json](../../data/registry.json), [split code](../../src/psychneuro/split.py), [evaluation code](../../src/psychneuro/experiments.py), [original W01 methodological report](../pm19-independent-qa-2026-10-18.md). Human-in-the-loop code review not claimed; no source outside inspected repository exhaustively audited; GitHub run artifact retention is time-limited.
- This is a **dated inventory** of relevant branches and evidence, not a claim to have enumerated all history of every remote branch/commit. PASS: exact referenced source checks, source links; PARTIAL: independent reviewer provenance signature and full-history enumeration.

## PM-23 — source-rights and provenance register

| Registry classification | Source and permission state | Allowed right now | Blocker |
| --- | --- | --- | --- |
| psychneuro-synthetic-v0 | Locally generated original fictional behavioral records; enabled=true; rights_basis synthetic-original; licence says NOT separately specified | Internal CI software testing, no real-participant data | Rights-holder explicit permission/data licence for separate distributed generated exports (#9). |
| OpenNeuro ds000001, ds000003, ds000005, ds000007, ds000008, ds000117 | Six external human-neural metadata entries, differing metadata-reported licences, all disabled | Metadata inventory only, no fetch/ingest/redistribution | Independent terms, consent, secondary-use ethics/privacy and field-level task suitability. |

Never silently equate Apache-2.0 **code** licence to generated-record redistribution grant; exact source metadata in [registry](../../data/registry.json). PASS registry audit; BLOCKED rights approval for outward data release.

## PM-24 — fixed benchmark QA contract / negative-control matrix

| Test requirement | Concrete reference | Executed status |
| --- | --- | --- |
| Subject-held-out row and group disjointness | split.py create_group_split/validate_group_split; tests/test_splits.py; newly tests/test_week2_controls.py contamination negative fixture | PASS on W02 hosted CI |
| Pre-response only predictors | schema.py gate forbids response, response_time_ms, correct and participant_id | PASS |
| Fixed model-selection protocol | configs/baseline.json; baselines.py/experiments.py training-only 5-fold CV and grouped holdout | PASS on synthetic original |
| Reference metrics, units, undefined denominators | metrics.py, tests/test_pm08_experiments.py and new Week 2 hand cases | PASS |
| Replayed seed and manifest | fixed generator/split seeds and source SHA, repeated in controlled fixtures | PASS; independent cross-run environment lock not fully complete |
| Null controls | Week 2 *frozen prediction*, within-participant label permutation | PASS for conditional diagnostic ONLY; genuine refit permutation with matched training CV not implemented |
| Independent subject uncertainty | W02 participant bootstrap for >=10 fictional groups; five-group holdout must suppress | PASS as fixed-prediction demonstration; not valid refitted-model interval |
| Missingness / distribution shifts | malformed/nonfinite, provenance-invalid altered records tested | PASS guard; NOT RUN quantitative predictive robustness under approved relabelled shift |
| API/web/real user security/accessibility | source-only docs, AppTest simulation and release checklist | NOT RUN actual hosted B01–B20; no physical browser/screen reader host |

These are falsifiable acceptance criteria. No hidden-p-value inference, human sample size/clinical performance, or blind release acceptance.

## PM-25 — loader quality and error handling

Source under src/psychneuro/loaders.py, quality.py and tests/test_loaders.py, test_pm05_loaders.py, test_week2_controls.py. Signed original synthetic data accepted; missing/duplicate identifiers, wrong-type columns, NaN/nonfinite, invalid response time, altered CSV digest, malformed contents and external sources fail closed. A source-tampered shift fixture triggered exact expected 'CSV data checksum mismatch' in first W02 CI; test assertion was corrected to accept this *properly blocked* code path, not to waive the guard. PASS tested subset. Remaining risk: no security review of uploaded file processing under a deployed multiuser app.

## PM-26 — participant grouping integrity

Tests explicitly reject the same fictional group across partitions, duplicated row indices, altered split membership and changed source digest. Seed 42 on default n=24 yields 14 train, 5 validation, 5 test fictional participants. Error-case fixture deliberately introduces train ID into test group, validate_group_split raises participant leakage. PASS source/test contract, not independent real participant leakage validation.

## PM-27 — seed and configuration versioning

Versioned baseline v1 at configs/baseline.json; split seed 42, generator seed 73, five-fold training CV. Same inputs/seed reproduce records/split IDs and per-suite results. Experiment manifests record Python version (therefore SHA differs across 3.11/3.12 by design). Dependencies installed under exact direct requirements in CI and pip check. PASS deterministic fixture assertions, PARTIAL fully locked transitive environment and independent different-host replays.

## PM-28 — hand-worked metric reference and units

- Fixture y_true 0,0,0,1 with constant predicted 0 gives TN=3, FP=0, FN=1, TP=0; balanced accuracy 0.5, macro F1 3/7, prevalence 0.25.
- Perfect 0/1 classification gives balanced accuracy=macro F1=1.0; a single truth class makes both UNDEFINED/NULL; no nonsense 0.0 imputation. Reaction time is a **post-response descriptive measurement in milliseconds**, never predictor. Tests in tests/test_pm08_experiments.py and tests/test_week2_controls.py PASS. RT outliers/nonfinite rejected, no age/clinical cutoff.

## PM-29 — two baseline comparison protocol

Use the *same* participant-disjoint training/held-out source for dummy-prior and logistic regression, train only on authorized pre-response difficulty and stimulus condition, and do NOT select a model on held-out test results. Earlier fully executed W01 benchmark CI confirms original code; additional Week 2 standalone control demonstration builds two predeclared models for 60 wholly fictional subjects and 12 held-out subjects, pending verification of its own exact CI. Its test numbers are strictly simulated and not estimates of human treatment effects. PASS for reference W01, and pending new W02 held-out report if dedicated CI passes.

## PM-30 — independent participant cluster bootstrap: implementation and limits

New week2_controls.py contains participant_bootstrap_ci with 400 deterministic, participant-*cluster* resamples (not naive row bootstrap); it recomputes metric with **fixed prior predictions**, has explicit minimum 10 distinct fictional subjects, rejects invalid IDs/seeds/budgets and suppresses tests on five-person held-out cohorts, empty/two-class invalid data and too many ineligible resamples. Dedicated reference fixtures check perfect predictions yield [1,1] percentile bounds. PASS code/unit tests at W02 CI; NOT a refitted model CI, human/generalizable interval or calibrated inferential coverage.

## PM-31 — typed read-only API design / threat model (SPEC ONLY, NO SERVER)

An optional future /v1/reports endpoint can expose **only** precomputed, reviewed synthetic-only reports with exact version/repository release SHA and allowlisted stable fields. No POST/PUT/PATCH/DELETE, no fetching caller URLs, no filesystem path selection, no browsing of internal locations. Require authentication before any private reports, bounded payload <=128 kB, fixed depth ≤8, strict content-type, no unknown fields, non-finite numbers rejected, rate limits, CORS deny-by-default, credential-safe logging with no per-user input body, normalized 400/403/404/413 errors; origin, version, manifest signature and content hash verified by trusted service, not a client-provided checksum alone. Threats: report-ID enumeration, IDOR, secret-bearing logs, HTML/script injection in model cards, zip bombs/decompression, hidden real participant metadata, forged provenance, cross-session access, vendor lock-in. Test cases: unauthorized GET must 403/404; private report ID access cannot cross principals; 1MB payload must reject; disallowed method 405; unchanged hashed signed report deterministic; malformed JSON 400. **All hosted/API tests NOT RUN**: no web service was deployed or approved. Deliverable is review-ready threat specification, not implemented endpoints.

## PM-32 — original generator privacy / ranges

synthetic.py generates wholly fictional participants with local seeded RNG, bounded count MAX_TRIALS, correct consistent response, nonnegative finite reaction time and validated difficulty. No human identifier lookup, raw participant records or clinical inference. tests/test_synthetic.py and new Week 2 negative fixtures PASS. This is a software provenance/privacy guard, not security certification or consent authorization.

## PM-33 — newcomer private reproducibility quickstart

1. Review [README](../../README.md), [code license](../../LICENSE), [rights metadata](../../data/registry.json), [baseline config](../../configs/baseline.json) and [CI exact run](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111357989) before reproducing. Repository access is required while private.
2. CI's own environment uses Python 3.11 and 3.12 on ubuntu-latest, source checkout of exact SHA, installation from pyproject's dev/benchmark/parquet/ui extras and pinned requirements; no private or paid local install was performed by this assistant.
3. For a capable voluntary reviewer (NOT a requirement for the user): clone permitted access, check out exact SHA, use an isolated Python virtual env, follow the current .github/workflows/ci.yml exact commands; run python -m pytest -q, python -m ruff check ., python -m mypy src, then synthetic-only in-app/report commands documented in workflow. Compare the printed commit SHA and source/config hashes, *within each environment*, not between Python 3.11 and 3.12.
4. Expected verified reference: 335 passed per Python in W02 first successful run, Ruff pass, mypy 21 source files, ten versioned CI archives. Any new implementation commit requires rerunning the exact CI and inspecting results; no one has independently verified a clean-room public install.

Troubleshooting: no private repository permission (request appropriate authenticated reviewer grant); missing extras (use CI pins); wrong Python version (environment-hash differs), no rights clearance (don't bypass), no private deployed app (source-only browser review). **PASS prepared onboarding note / actual independent newcomer test NOT RUN.**

## PM-34 — null/permutation controls

Week 2 code uses within-fictional-participant label permutations while keeping predictions fixed. It holds participant IDs, class support, number of rows, seed and pre-response features constant and exposes all diagnostic null draws. PASS unit invariants and reproducibility; NOT a full model-refitting permutation test and not a valid trained-model p-value. Full fold-matched training-pipeline null remains future work.

## PM-35 — missingness and shift stress

New negative fixtures reject nonfinite difficulty, NaN or infinite/negative RT, invalid IDs, altered signed original source contents; synthetic difficulty=0.8 shifted rows are **not** inadvertently accepted with the original digest. The generator and loader preserve fail-closed behavior. PASS input provenance/stress *guards*; NOT RUN separately licensed shifted-source performance experiment or full imbalance benchmarking.

## PM-36 — hosted CI packaging, lint, type

[Actual run 39111357989](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39111357989) successfully installed development dependencies, performed 335 pytest tests per interpreter, Ruff all checks, mypy no issues in 21 source files, and uploaded ten original synthetic artifacts. Exact candidate code SHA 36dbf9a8c37e8f5bf55576dd7f8456433d5b1c81. Latest added standalone demonstration requires its own new CI success to claim resulting artifact. PASS prior exact candidate, newer changes PENDING.

## PM-37 — four research-figure evidence cards (specification; figure export NOT requested)

1. **Study source/provenance diagram:** question: was each fictional cohort generated with permitted source/version? Nodes: registry rights, generator seed, source CSV SHA, split assignment SHA, report SHA, interpreter version. Observable output: string digests (no graphical performance results). Omit external human data.
2. **Group split diagram:** question: are participants independent between train/validation/test? Unit: fictional participant, count default 14/5/5 for 24. Graph: split group sets and disjoint arrows, not 480 individual independent nodes. Fail case: same subject crosses boundary and validation rejects.
3. **Balanced accuracy vs macro-F1 evidence card:** question: how does reference dummy compare with interpretable logistic baseline? Unit: unitless 0–1; report confusion/class supports, selected training policy, held-out provenance. Source only real emitted CI artifact, no inferred 95% human error bars. Null and undefined values printed, not hidden.
4. **Synthetic uncertainty chart spec:** independent unit: *synthetic cohort seed* for original repeat-based intervals, separately *fictional participant cluster with frozen predictions* for Week 2 demonstration. Do not combine two interval concepts in one unlabeled bar or infer population confidence.

Any actual plotted values must be generated strictly from real output JSON via logged code before publication. Figure images weren't rendered or externally published. PASS source-traceable figure briefs; NOT RUN visual export/independent checking.

## PM-38 — dataset + baseline model cards (two evidence-backed drafts)

**Dataset card v0:** Original fictional behavioral trials, source synthetic.py and source digest per run. Fields: dataset, subject/session/trial IDs, order, stimulus condition, difficulty, correct, response, response_time_ms, generator seed; exactly two predictors available pre-response. Test default 24 fictional participants ×20 trials =480 rows, 14 train/5 validation/5 test distinct groups. Consent: no real people; licence for generated records not separately granted, no public redistribution authorization; six OpenNeuro metadata sources disabled. Risk: toy generator distribution may make dummy unexpectedly competitive; no behavioral/medical transfer.

**Model card v0:** Binary correctness (synthetic) with dummy-prior comparator and scikit-learn logistic regression over pre-response difficulty and condition. Evaluation: train-only 5-fold CV, participant held-out validation/test, balanced accuracy and macro-F1 with support/confusion, invalid/undefined scores suppressed. Developer/test environment version & hashes in experiment manifest. Limits: synthetic cohort, small subject holdouts, no held-out model selection, no inference about real neurons or therapy; W02 bootstrap conditional fixed predictions. Both drafts cite source baselines.py/metrics.py/experiments.py. PASS prepared cards; no independent fair-use / validity attestation or publication.

## PM-39 — independent reproduction bundle checklist

Core files: pyproject.toml, requirements.txt, configs/baseline.json, data/registry.json, src/psychneuro/{synthetic,loaders,split,baselines,metrics,experiments,reporting,week2_controls}.py, tests and CI workflow. Reference code SHA and GitHub run URL printed in this ledger. Source lineage: original generator revision/seed 73, group assignment 42, CSV SHA computed from original export, config SHA in report. Original W02 ten GitHub artifacts are seven-day retention: download internally if needed before expiry. A future separate host must reproduce on a declared identical environment and verify report+files against one canonical run; differences in Python interpreter version legitimately alter manifest/report SHA. PASS reference versioned evidence list; **independent outside-CI rerun and signed attestation NOT RUN**.

## PM-40 — adversarial integrity risks: severity and actual evidence

| Risk | Severity | Current evidence | Residual |
| --- | --- | --- | --- |
| Human/source rights bypass | CRITICAL for public release | Registry disables six external sources; source-hash fixture rejects altered generated records | Generated export licence and host-level data-path checks pending |
| Repeated-participant leakage | HIGH | Negative group overlap and index tampering must raise in hosted tests | Independent adversarial API/browser verification absent |
| Post-response target leakage | HIGH | Pre-response feature allowlist tests; response/RT omitted | New features/time signals need future precommit audit |
| Fabricated report provenance | HIGH | Canonical JSON SHA and hosted CI evidence | User-provided hash alone is NOT authenticated run attestation |
| Cross-user PII or accidental metadata in deployment | HIGH | Reports fail closed on sensitive fields | Private host/log/identity isolation NOT RUN |
| Null-model p-value overstatement | HIGH | Diagnostic labelled frozen/no refitting/no p-value | True permutation inference and multiple testing calibration NOT RUN |
| Distribution shift / model stability | MEDIUM | Malformed/shifted data provenance guards passed | Quantitative under-shift accuracy and uncertainty NOT RUN |
| Accessibility/touch/screen-reader | MEDIUM | Source Streamlit AppTest checks, browser smoke plan | Actual private screen reader B01–B20 NOT RUN |

**Review decision:** PASS source-level synthetic integrity subset; NOT independent security signoff.

## PM-41 — accessible synthetic-only demonstration readiness (NO PUBLIC HOST)

Proposed checklist: specific access-controlled host SHA and permission model; B01–B20 from docs/pm15-browser-smoke.md; desktop 1440 and mobile 320/375/768/1024 and 200% zoom; keyboard tab order and focus; named assistive technology, version/browser, contrast computed; inaccessible controls and downloadable PII blocked; invalid-size/malformed JSON and rights guard; cross-session leakage safe; no hidden analytics; run logs sanitized; threat review and researcher feedback captured with consent. Current tally **0/20 actually run**, no deployed URL, no verified live mobile or screen-reader capture. Source-ready for private review ONLY.

## PM-42 — W02 release decision / Week 3 backlog

**Private scientific software CI gate GO for exactly verified candidate, external/public release NO-GO.** Reasons: unresolved generated export rights (#9), absence of private-host accessibility/privacy checks (#8), lack of independent review of broad W01 changes, no signed report provenance (#6), real-user expert feedback zero, no clinical/empirical generalization, no release owner approval. Private repo and unmerged draft remain unchanged.

Week 3 carryover in priority order:
1. Independent generated-original dataset export licensing decision; no external humans.
2. Secure private demo controlled access and *actual* B01–B20/assistive tech/privacy evidence.
3. Full fold-preserving permuted-label TRAINING refits (not just frozen diagnostic), with precommitted analysis plan.
4. Held-out missingness/shift analysis with *new* allowed generated-source provenance; do not tamper signed original data.
5. Independent same-version run reproducibility and full environment/commit attestation; reviewer-packaged bundles.
6. Meaningful human review of extensive code, model assumptions and methods; resolve private PR and active issues.
7. Correct accessibility/performance or threat bugs only after concrete reproducible observations.
8. Only then decide any separately approved public release, outreach, profiles or scholarly submission.

## Scope and code evidence

This audited technical plan was authored with AI assistance; GitHub Actions successes are actually externally executed, and records marked NOT RUN have no invented outputs. No owner actions or Academy learning completion are inferred. The scheduled Week 2 dates are **not** actual completed timestamps. See also [GA Week 2 paper and funding matrix](ga08a-ga10b.md), [GA ethics, labs and career ledger](ga11a-ga14b.md), and [earlier W01 NO-GO](../pm20-competitive-release-gate-2026-10-18.md).

## Final exact-code Week 2 hosted verification — supersedes pending lines above
On 2026-10-18 [real GitHub Actions #39112127659](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39112127659) at source SHA `dd79565e07923b35db7a7f09e0724a8c0594158e` completed **SUCCESS on both Python 3.11 and Python 3.12**: **336 pytest PASS per interpreter**, Ruff PASS, strict mypy PASS across **22 source files**, original rights-checked synthetic PM06–PM13 export/replay pipeline PASS, plus actual execution of `python -m psychneuro.week2_demo --output-dir artifacts/week2`. Logs state `status=synthetic_only unit=fictional_participant` and `test_participants=12`. **12 genuine archives** uploaded, including `week2-subject-bootstrap-frozen-null-3.11` and `-3.12`. The new demo fits predeclared dummy and logistic estimators on exactly the **same disjoint train groups** and checks held-out scores, a fixed-prediction **cluster bootstrap with 12 fictional held-out groups**, and **100 frozen-prediction within-group label permutations**; it does *not* select on test set, refit within bootstrap/permutation, provide a valid refit p-value, or establish scientific effect in humans. The report also includes source/split digests and post-response latency as descriptive-only. See [week2_demo.py](../../src/psychneuro/week2_demo.py) and [test_week2_demo.py](../../tests/test_week2_demo.py).
**Update PM-29, PM-30, PM-34, PM-36, PM-39:** real executed 60-subject/12-held-out-subject simulation with artifact files now VERIFIED as source/CI subgate; full retrained null p-value, independent outside-GitHub reproduction, rights and public-demo checks still OPEN. No code changed after this exact run: later commits are documentation only. Release decision **NO-GO** remains unchanged.
