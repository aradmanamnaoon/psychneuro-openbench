# PsychNeuro OpenBench — Week 1 internal engineering case study

**Reviewed 2026-10-18 · AI-assisted documentation · PRIVATE, SOURCE-LEVEL STATUS.**
Not a peer-reviewed manuscript, clinical tool, completed user study, product launch, public demo or scientifically validated ML benchmark. The audit target was `pm17/upstream-oss-research-patch` at `ba4bafcdf4ffa3e76b927139ac23e753d0546074`; independently recorded PM-19–21 reviews are on private `review/pm19-pm21-independent-gates-20261018`. These files are work products, not evidence of execution on an actual machine.

## Research-software problem

Repeated task trials are dependent within subjects. A row-random split can leak one participant's behavior into training and evaluation; a model can also cheat by using outcomes or response-time variables that arise *after* the event it supposedly predicts. Merely reporting high classification accuracy fails to disclose rights, split independence, feature timing, or whether the evaluation was reproducible.

**Intended audience:** behavioral/psychology methods learners, computational neuroscience labs planning defensible ML exercises, and reproducibility-minded ML reviewers. **Narrow current supported use case:** synthetic fictional binary trial-correctness prediction. No empirical human, diagnostic or clinical claims.

## Repository methods and concrete evidence

1. **Source legitimacy:** `data/registry.json` and `src/psychneuro/registry.py` enable `psychneuro-synthetic-v0` from an original seeded Python generator. Six external OpenNeuro sources are **disabled metadata**; files are not fetched and no participant analysis has occurred. [Data candidate/rights report](dataset-candidate-audit.md). The generator's produced CSV digest is computed per export, not a static hash for all seeds. Its synthetic record data license remains unspecified; [private rights issue #9](https://github.com/aradmanamnaoon/psychneuro-openbench/issues/9) tracks that decision.
2. **Data/QC:** `src/psychneuro/{schema,quality,loaders}.py` and corresponding tests specify deterministic trial generation, source identity, malformed/schema/duplicate/missingness guards. Fictional subject identifiers are not actual participants.
3. **Leakage discipline:** `src/psychneuro/split.py` creates group-held-out **train/validation/test** partitions keyed on fictional `participant_id`, validates disjointness, complete index mapping and assignment/source digests. At default 24 fictional subjects the source/test specification expects **14 training, 5 validation, 5 test subjects**, not 480 independent observations. [Split protocol](split-design.md).
4. **Pre-response feature policy:** `src/psychneuro/baselines.py` allowlists `difficulty` and `stimulus_condition`; `response`, reaction time, target `correct`, group ID and aggregate target statistics are prohibited. A fresh fold-local scikit-learn `Pipeline` includes `StandardScaler` and `OneHotEncoder`; `GroupKFold(5)` operates on training participants only. Models are `DummyClassifier(strategy="prior")` and fixed logistic regression; the training-CV comparison chooses a model before evaluating the held-out test. [Protocol](evaluation-protocol.md).
5. **Honest metrics:** `src/psychneuro/metrics.py` specifies binary balanced accuracy, macro F1, per-class support and 2×2 confusion counts; missing/single-class truth produces undefined/null scores. The repeated pipeline `src/psychneuro/pipeline.py` uses predetermined synthetic seeds and discloses ineligible runs rather than treating them as zero or filtering them silently.
6. **Uncertainty:** `src/psychneuro/uncertainty.py` provides descriptive sample SD/SE and a *nominal approximate* Student-t interval when there are at least five eligible independently seeded synthetic cohort repeats. It is **not** a participant confidence interval, hypothesis test, neuroscience result or proof of nominal coverage. The small default held-out cohort cannot support reliable real-population generalization.
7. **User-facing design:** `app.py`, `src/psychneuro/{explorer,workflow,reporting}.py` and `docs/pm15-browser-smoke.md` specify Streamlit source selection, explicitly submitted bounded synthetic benchmark, charts with tables and reproducibility exports. **No private/public deployment exists and all 20 scripted browser checks were NOT RUN**.

## What was actually validated versus authored

**Validated on actual GitHub-hosted older code:** [PM-02 GitHub Actions run 38863471313](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38863471313) — 31 tests passed, Ruff/mypy passed, **older PM-02 branch**. [PM-04 run 38874446677](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677) — 80 tests passed, Ruff passed, mypy passed on 4 source files, **older PM-04 branch**. The [prior failed PM-04 run](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874202366) exposed two Ruff TRY004 violations that were fixed for the later passing PM-04 verification.

**NOT validated:** PM-06–PM-17 current development branch, Python 3.11/3.12 exact-candidate CI, live benchmark outputs, streamed UI, downloaded/verified CI report artifacts, end-to-end source reproducibility, external data rights/consent, comprehensive dependency/secret scan, runtime security, CPU/memory budgets, accessibility, real user demand. The [PM-19 audit](pm19-independent-qa-2026-10-18.md) inventories these as blockers. No runtime results are invented in this case study.

## Real comparative landscape, not false novelty

- [MOABB](https://moabb.neurotechx.com/docs/README.html) already supports broad EEG/BCI benchmarking, with actual [cross-subject evaluation](https://moabb.neurotechx.com/docs/generated/moabb.evaluations.CrossSubjectEvaluation.html) and cross-session schemes. OpenBench is **not** the first subject-aware neuroscience ML benchmark.
- [NeuroBench](https://neurobench.readthedocs.io/en/latest/) already provides neuroscience/neuromorphic benchmark interfaces with datasets/models/preprocessing and metrics; OpenBench's candidate focus is a narrow pedagogical/behavioral **audit trail**, not new benchmarking mathematics.
- [scikit-learn grouped cross-validation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html) and [common-pitfalls documentation](https://scikit-learn.org/stable/common_pitfalls.html) already establish group separation and train-only preprocessing. OpenBench integrates these **known principles**, not novel methods.
- OpenNeuro's [FAQ](https://docs.openneuro.org/faq) and [sign-in conditions](https://openneuro.org/) emphasize data permissions and privacy. Public metadata/licensing does not authorize claiming consent or human behavioral validity.

**Differentiation hypothesis:** a compact, rights-denying-by-default, fully synthetic behavioral-trial walkthrough coupling group-safe training, explicit leakage guards, null metrics, descriptive seed variability and digest-linked reporting in one UI. This is an *untested user-value hypothesis*. No measured superiority or independent user feedback exists.

## Limitations and reproducibility checklist

- `pyproject.toml` is at `0.1.0.dev0`, not a published release. Main still lacks reviewed PM-17 integration; no release/tag.
- Reproducible build needs an *actual* committed candidate SHA, frozen config, exact dependency resolution and host versions, matching trial/source/group/run/export hashes, and completed CI with downloadable outputs.
- A self-declared SHA-256 checksum provides accidental corruption detection, not authenticated provenance. A green older pipeline cannot certify the full browser or security surface.
- The same held-out synthetic generator reused during development can induce adaptive test selection; perform precommitted final protocol and independent validation rather than cherry-picking repeated seeds.
- No real clinical/psychological inference follows from artificial outcomes, even if every source test passes.
- Real dataset import requires separate legal/consent/ethics, schema, label and privacy checks; until then external entries stay disabled.

## Decision and transparent authorship

**NO-GO for public release.** Real users and feedback cannot be reported without their actual participation. The internal technical audit, source comparison and language in this case study were **substantially prepared with generative AI under human owner review**; no AI-written text should imply human validation, original empirical discovery or independent third-party endorsement. Future public disclosures must follow the specific venue/project transparency requirements. See [PM-20 release gate](pm20-competitive-release-gate-2026-10-18.md) and [PM-21 retrospective](pm21-internal-pilot-retrospective-2026-10-18.md).
