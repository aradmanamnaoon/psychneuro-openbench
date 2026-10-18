# PM-17 — Eight active upstream OSS projects and live contribution needs

**Source snapshot: 2026-10-17 UTC; PRIVATE research only, NO OUTREACH.**
Eight GitHub repository records were inspected via connected GitHub
read-only API: each has a real public source, SPDX repository-license field,
nonzero issue queue and recent repo push. Individual issue status was
separately read **by its exact GitHub REST issue record**, because GitHub
search results can be stale and GitHub's open-issue count includes PRs.
Maintainer contribution instructions were read or identified from the actual
project's current source/official docs. This does **not** imply permission
to publish a patch, use a third-party dataset or claim upstream endorsement.

| Relevant upstream | GitHub-verified license and activity | Real issue / current state | Actual maintainer instructions and triage judgment |
| --- | --- | --- | --- |
| [skrub](https://github.com/skrub-data/skrub) — dataframe ML, DataOps and leakage-safe validation | **BSD-3-Clause**, pushed **Oct 16, 2026** | [#2340 — synthetic group-aware DataOps CV gallery proposal](https://github.com/skrub-data/skrub/issues/2340) **OPEN** (Oct 17), author is the project's GitHub account `aradmanamnaoon` | [CONTRIBUTING.rst](https://github.com/skrub-data/skrub/blob/main/CONTRIBUTING.rst) **requires issue discussion and maintainer approval before writing/opening PR**. The existing DataOps [user guide](https://github.com/skrub-data/skrub/blob/main/skrub/_docs/modules/data_ops/validation/tuning_validating_data_ops.rst) already shows `mark_as_X(cv=..., split_kwargs={"groups": ...})`; avoid redundant examples without confirmation. **Best small prototype fit; no maintainer reply yet**. |
| [scikit-learn](https://github.com/scikit-learn/scikit-learn) — evaluation and grouped CV | **BSD-3-Clause**, pushed **Oct 16, 2026** | [#34507 — productive code review example in contributor guide](https://github.com/scikit-learn/scikit-learn/issues/34507) **OPEN**, but issue explicitly says **NOT READY FOR PR** | [Developer contributing guide](https://scikit-learn.org/dev/developers/contributing.html) / [CONTRIBUTING.md](https://github.com/scikit-learn/scikit-learn/blob/main/CONTRIBUTING.md); maintainer agreement needed before trying this documentation task. **Not a ready-to-submit opportunity.** |
| [Nilearn](https://github.com/nilearn/nilearn) — neuroimaging decoding/data preprocessing | **BSD-3-Clause**, pushed **Oct 16, 2026** | [#6499 — illustrate why standardization changes decoding outcomes](https://github.com/nilearn/nilearn/issues/6499) **OPEN**, last updated Sep 25 | [CONTRIBUTING.rst](https://github.com/nilearn/nilearn/blob/main/CONTRIBUTING.rst) expects documentation discussion, human review, **explicit AI-tool disclosure** and rejects fully automated AI-generated PRs/comments. **Second scoped candidate; no patch submitted.** |
| [MNE-Python](https://github.com/mne-tools/mne-python) — EEG/MEG signal processing | **BSD-3-Clause**, pushed **Oct 15, 2026** | [#13707 — reorganize Decoding/MVPA documentation](https://github.com/mne-tools/mne-python/issues/13707) **OPEN**, last updated Jun 6 | [CONTRIBUTING.md](https://github.com/mne-tools/mne-python/blob/main/CONTRIBUTING.md) explicitly restricts **fully automated AI contributions** and requires human domain judgment. Scope awaits maintainer feedback; **no AI-automated issue/PR**. |
| [MNE-BIDS](https://github.com/mne-tools/mne-bids) — reproducible EEG/BIDS provenance | **BSD-3-Clause**, pushed **Oct 16, 2026** | [#1664 — check event-duration units and warnings](https://github.com/mne-tools/mne-bids/issues/1664) **OPEN**, updated Sep 21 | [CONTRIBUTING.md](https://github.com/mne-tools/mne-bids/blob/main/CONTRIBUTING.md) outlines contribution style, tests and first-time workflow. True recording/unit edge cases require test fixtures and careful ethics; **not a trivial patch**. |
| [Fairlearn](https://github.com/fairlearn/fairlearn) — fairness metric interpretation and evaluation | **MIT**, pushed **Oct 16, 2026** | [#1614 — explain fairness moments, objective vs constraint](https://github.com/fairlearn/fairlearn/issues/1614) **OPEN**, updated Mar 13 | [Official contributor guide](https://fairlearn.org/main/contributor_guide/index.html) (linked from [README](https://github.com/fairlearn/fairlearn/blob/main/README.rst)); research definitions need evidence and maintainer scoping; **not ready as tiny one-file patch**. |
| [Braindecode](https://github.com/braindecode/braindecode) — EEG/fNIRS deep-learning models | **BSD-3-Clause**, pushed **Oct 16, 2026** | [#1398 — fNIRS modality model integration](https://github.com/braindecode/braindecode/issues/1398) **OPEN**, updated Oct 13 | [CONTRIBUTING.md](https://github.com/braindecode/braindecode/blob/master/CONTRIBUTING.md) asks contributors to coordinate issue ownership. Model ports need original source/architecture/dataset review; **large, research-heavy; not a beginner issue**. |
| [NeuroKit2](https://github.com/neuropsychology/NeuroKit) — neurophysiological signal QC | **MIT**, pushed **Oct 1, 2026** | [#1208 — multifractal DFA depends on input amplitude units](https://github.com/neuropsychology/NeuroKit/issues/1208) **OPEN**, updated Sep 25 | [Official contributing guide](https://neuropsychology.github.io/NeuroKit/resources/contributing.html) from [README](https://github.com/neuropsychology/NeuroKit/blob/master/README.rst); numerical stability and EEG-volt scaling need careful analysis and testing; **high-risk for an unexecuted patch**. |

**Methods and caveats.** Exact repository data are a dated snapshot, **not**
a guarantee the issue is still unassigned or will accept a PR. License
SPDX values reflect repo metadata, not legal clearance of all third-party
dependencies, datasets or models. Do not claim GitHub stars, acceptance,
maintainer willingness, collaborations or study users. Before any future
issue comment/PR, recheck current issue status, open PR duplicates,
guidelines and participant-consent/rights boundaries. In this mission, no
comments, invitations, forks, external branches, PRs or public site changes
were made.

## P1-071 — Two selected, testable opportunities

### A. skrub DataOps grouped cross-validation gallery — #2340 (priority)

**Real upstream issue:** [skrub-data/skrub#2340](https://github.com/skrub-data/skrub/issues/2340), already opened by the user's GitHub account at 07:50 UTC Oct 17. This mission **did not post it**. It requests a tutorial for repeated fictional observations (32 groups x four records), group-disjoint `GroupKFold(n_splits=4)`, no group ID/outcome in the input predictors, training-inside-fold `TableVectorizer` + `LogisticRegression`, and a correct DataOps scoring invocation.

**Specific reviewable path:** the private original-new-file candidate
[1170_group_aware_cross_validation.py](../upstream-prototypes/skrub/1170_group_aware_cross_validation.py)
and [upstream new-file .patch](../upstream-prototypes/skrub/1170_group_aware_cross_validation.patch)
target upstream `skrub/_docs/examples/02_data_ops/1170_group_aware_cross_validation.py`.
This is a *real proposed code diff* staged only in PsychNeuro OpenBench's
**PRIVATE** branch, **not** a branch of skrub or a GitHub fork, and upstream
maintainers have not approved the scope.

**Acceptance on a future owner- and maintainer-approved upstream runner:**
1. Gallery Python syntax and project docstyle checks pass, imports exist on
   current skrub `main`; no HTTP/dataset fetch.
2. Assert all four `GroupKFold` splits have disjoint participant IDs, and
   group ID and `correct` are absent from model features.
3. Ensure `mark_as_X(cv=..., split_kwargs={"groups": groups})` uses a DataOp
   group vector matching the existing official user guide.
4. `TableVectorizer` fits within validation folds and
   `predictions.skb.with_scoring("roc_auc").skb.cross_validate()` works with
   the exact current API; a gallery build processes the output without error.
5. No scientific performance, clinical, participant or comparative benefit
   asserted. Mark actual execution evidence **NOT RUN** in this project.
6. Obtain skrub maintainer scope approval on existing issue **before** any
   external fork or PR. The suggestion may instead belong in the current
   user-guide paragraph, in which case re-scope rather than posting a
   redundant gallery page.

### B. Nilearn standardization interpretation — #6499 (backup)

**Real issue:** [nilearn#6499](https://github.com/nilearn/nilearn/issues/6499)
still OPEN (Sep 25 last update). It seeks a clearer explanation of the
preprocessing/standardization choice in decoding examples. **Proposed
narrower intervention after maintainer guidance:** add a short source-linked
user-guide subsection explaining *why* `standardize` changes decoding
results, and exactly where scaling is fit when train/test splitting is
applied. Use one original-synthetic no-download example and warn about
preprocessing fit leakage.

**Acceptance specification:** existing nilearn docs build; code snippet
reproduces using an allowed synthetic fixture; no globally fitted
scaler before cross-validation; clarity about `zscore_sample`, `psc`,
`None` and currently deprecated boolean aliases if documented in the
target module; no invented change in real study prediction. **Not yet
implemented** because the exact target guide placement and explanation
need maintainer consent and Nilearn prohibits fully automated AI PRs.
A human subject-matter reviewer must understand and take responsibility
for an AI-aided patch and **disclose AI use** as required by its guide.

## Selection decision

Prioritize A for a **PRIVATE prototype only** because its synthetic,
leakage-safe source aligns with existing OpenBench evaluation controls and
there is already a specific matching proposal issue. Do not pretend that
the existing issue's earlier local testing or claims were reproduced in
this mission; this PM-17 work used no Python/CLI/IDE/Docker, and **no
integration tests were run**. Hold B pending focused upstream guidance.

**External action GO/NO-GO:** private draft review GO. External issue
comment, fork, upstream PR, maintainer contact, public change, scientific
claim or funded hosting NO-GO absent explicit owner permission and
project-specific maintainer/AI policy compliance.
