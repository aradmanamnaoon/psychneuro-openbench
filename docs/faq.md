# Frequently asked questions — PsychNeuro OpenBench

**PM-16 / 2026-10-17:** This FAQ covers the private, **source-only**
nonclinical synthetic preview. It does not imply an accessible deployment,
a passed current-commit CI run, real users, screenshots or empirical model
results. The repository and app are **NOT publicly released**.

### What does this project do, and who should use it?

PsychNeuro OpenBench aims to help psychology methods students, neuroscience
ML analysts and reproducibility reviewers inspect source rights, data
validation, participant-disjoint splits, simple baseline models and report
lineage. Current data are *only invented two-choice trial records*; no
human neuroscience findings or clinical services are provided. See
[use cases](use-cases.md) and [scientific v0 scope](spec-v0.md).

### Can I try a public or free live demo?

**No verified live URL exists.** Streamlit Community Cloud is merely a
proposed host. The private repository, exact-commit hosted CI, owner-approved
OAuth/privacy and actual browser smoke tests are release blockers. Never
postulate a URL or create a public fork to get around the permission gate.
See [host/approval runbook](pm15-host-runbook.md).

### Does the app run the baseline models or just show a mock chart?

PM-13 source has a synchronous **Run synthetic benchmark** form connected
to the original generator/rights-gated loader and grouped baseline pipeline.
It also supports a model-free fictional preview and read-only inspection
of uploaded original-format PM-10 reports. The code exists, but no
end-to-end current-branch browser or hosted test has passed here. Mock
scores in unit-test fixtures are **not** measured research results.

### What data may I upload? Are public OpenNeuro entries supported?

The permitted upload is only an unmodified, validated **PM-10 original
synthetic `report.json`** under 2 MB, from an already executed and
independently checked run. **Never upload actual human/patient records,
trial-level CSV/Parquet, medical images, scraped data or another group's
experimental datasets.** External OpenNeuro entries in `data/registry.json`
are disabled rights-review metadata; a published license does not automatically
clear research privacy, ethics, task mapping or redistribution. Unauthorized
text can reach an app server before a validator rejects it, so do not
mistake the source guard for a complete hosting privacy control.

### How are the models and targets chosen?

The frozen v1 config specifies `dummy_prior` and
`logistic_regression`; binary correctness is the target, synthetic
stimulus condition and difficulty are predictors available prior to the
response. Never use reaction time, response or a target-derived field as
a pre-response feature. Training-only five-fold grouped CV chooses one
policy, then held-out test metrics are recorded. `cv_selected_policy`
is a **selected baseline policy**, not an independent third estimator.

### What does "participant held out" mean for toy trials?

The intended grouped split keeps all rows from each fictional participant
in one partition instead of distributing their trials across train and
test. That defends against a specific within-person data-leakage risk but
does **not** mean a trained model generalizes to real participants.

### What do balanced accuracy and macro F1 tell me?

They are dimensionless numbers from 0 to 1 evaluating a binary synthetic
correctness task. Balanced accuracy averages class recalls; macro F1
averages per-class F1. Neither proves causation, neural mechanisms, a
clinical outcome, accurate individual diagnosis or improvement against
unrelated research cohorts.

### Why are some results or confidence intervals unavailable?

The pipeline records the requested number of distinct synthetic seed
cohorts and separately counts ineligible repeats. Unscorable runs are
**not** replaced by zeros, hidden or retried selectively. The nominal
95% Student-t interval for seeded simulator cohorts is available only
when **at least five eligible repeats** exist, and even then it is
not an interval for an actual human population. No p-value, winner claim
or "95% certainty this model generalizes" is justified.

### Can I rerun the experiment and check the same outputs?

The [reproducibility guide](reproducibility.md) lists the exact currently
configured hosted commands and artifact comparison gates. They are
**source-backed, not currently evidence-backed by a clean PM-16 hosted run**.
Review exact GitHub commit, Actions URL, interpreter, resolved dependencies,
synthetic registry, group split digests, per-repeat eligibility and
actual report/artifact SHA values before a replay claim. A JSON
self-hash is not independent proof of a CI run.

### Are software and data licenses identical?

No. The repository's project-authored code/documentation is Apache-2.0
with a NOTICE file, which does not grant license or consent for
external participant data, imported models/assets or third-party binary
dependencies. See [rights policy](license-policy.md).

### Why can't I submit a pull request or find new issue templates right now?

The GitHub repository remains private pending the owner's explicit
publication approval. PM-16 is preparing CONTRIBUTING and issue/PR
templates on a **feature branch**; GitHub does not show those templates
in its new-issue/PR UI until they exist on the **default branch**. No
PR, merge, public invitation or repository-visibility change is authorized.
Existing and newly created issues remain private to authorized repository
members, and an issue being tagged `good first issue` is not an invitation
to external contributors.

### How do I report a bug, reproducibility failure or security problem?

Authorized GitHub collaborators can use the templates after an
owner-approved integration, or an existing private issue beforehand.
Include exact branch/commit, expected vs actual behavior, sanitized
synthetic-only inputs and real logs when available; never include tokens,
credentials, raw human trial records, personal/medical data or public
link shares. A security report should avoid disclosing exploit details
in a broadly visible issue; use the owner's approved confidential channel.
See [CONTRIBUTING](../CONTRIBUTING.md), the private
[release gate](release-gates.md) and
[PM-15 security/privacy audit](pm15-security-privacy-audit.md).

### Which parts have actually been tested?

Only historical, specifically linked generator-level GitHub Actions runs
on older code have published passing logs in the internal README.
**No exact-commit PM-10–16 full benchmark, dependency-lock install,
privacy/host assessment, browser/mobile accessibility test, streamed
model result, screenshot or public demo has been verified here.** The
documentation and test scripts are not substitutes for these checks.

### Will this automatically contact researchers, deploy apps or publish results?

**No.** Public GitHub changes, PRs, public/third-party deployment,
outreach, website/profile changes, spending and login/OAuth grants
require separate explicit authorization. The project owner is the
reviewer; background or local technical work is not being delegated
as a substitute for permitted connected-tool implementation.
