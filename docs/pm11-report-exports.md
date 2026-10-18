# PM-11 — Results view, report exports and artifact lineage (PRIVATE)

**2026-10-17 evidence: SOURCE CODE COMMITTED. Hosted PM-08/09/10/11 pytest, Ruff, mypy, actual benchmark, rendered charts, browser UI and report exports NOT RUN.** Do not report passing tests, observed accuracy, UI deployment or research outcomes. Private GitHub repository is not approved for publication.

## User and scientific scope

PsychNeuro OpenBench is a nonclinical, synthetic-first behavioral ML benchmarking workbench for psychology methods students, computational neuroscience researchers and ML reproducibility reviewers. Model scores alone are insufficient: data rights, pre-response predictor availability, participant-held-out grouping, training-only preprocessing, source versions, null uncertainty and precise artifact lineage must remain inspectable.

Read [PM-10 methodology](pm10-statistical-pipeline.md) and [model card](model-card.md) first. PM-10 remains **Blocked** pending hosted verification. This mission can be written independently but cannot be called scientifically Verified Done without an actual compliant PM-10 artifact.

## Traceability to original requirements

| Original task | New implementation and acceptance boundary |
| --- | --- |
| P1-044: charts | [app.py](../app.py) renders **only uploaded, checksum-and-schema-validated PM-10 JSON** using Altair, with named unitless (0–1) axes, accessible tooltip legends and exact-point table. No sample/dummy values appear on launch. Chart is unavailable until an executed report exists. |
| P1-045: export | [reporting.py](../src/psychneuro/reporting.py) converts the same validated input to deterministic **report.json** and **report.md**, with actual per-seed numbers only when supplied. [Regression tests](../tests/test_reporting.py) use **artificial test fixtures**, not reported findings. A publicly usable rendered *measured* example does NOT exist yet. |
| P1-046: manifest | Creates **artifact-manifest.json** with export version, *expected* schema version (not attested by input), baseline hash, original PM-10 canonical digest, source/split/experiment manifest hashes by repeat, exact SHA-256 and byte counts for JSON/Markdown, and null CI/code commit IDs when not independently verified. |
| P1-047: browser shell | Streamlit navigation for overview, results, lineage/downloads and scientific limitations, explicit nonclinical disclaimer, <=2 MB report upload, invalid-data rejection, true no-results state. Source is NOT a hosted application or end-to-end deployed product. |

## Strict input contract

An input is accepted only if it matches `psychneuro-pm10-synthetic-repeat-v1`, contains the fixed synthetic-original rights statement, known configuration/version and predeclared seed schedule, has a matching canonical `report_sha256`, and has consistent eligibility counts and `summary_dict` scores recomputed from per-repeat held-out scores. Model selection must match one of the prespecified training-selected models; negative/NaN/out-of-range scores, orphan run records, malformed JSON or wrong source hashes are rejected. Suppressed slices must have `metrics: null`. Ineligible runs remain in the denominator but contribute **no** numeric chart points.

**Security limitation:** A SHA-256 checksum in a freely editable JSON can be recomputed by an attacker. Internal consistency does **not** establish true code execution, unchanged upstream CI, provenance authenticity, dataset consent, statistical calibration or clinical validity. The artifact manifest intentionally states `ci_run_id: null` and `source_commit_sha: null` until corroborated independently. Its schema version is the *current package expectation*, since PM-10 did not embed a verified runtime schema version.

Charts only use real input values; they do not create or smooth simulated data. The display's accessibility baseline is explicit axis/metric units, descriptions, tooltip and tabular equivalent; **actual keyboard/screen-reader browser QA is NOT RUN**.

## Reproducibility usage on an authorized environment (not done here)

The existing manual-only workflow at [.github/workflows/ci.yml](../.github/workflows/ci.yml) is configured to produce `artifacts/pm10/report.json` via the frozen grouped synthetic benchmark, then run:

```sh
python -m psychneuro.reporting --input artifacts/pm10/report.json --output-dir artifacts/pm11
```

Expected artifacts **if execution completes**:

```plain
artifacts/pm11/report.json
artifacts/pm11/report.md
artifacts/pm11/artifact-manifest.json
```

The optional **free open-source** UI dependency group is `.[ui]` (Streamlit + Altair). In an authorized environment the shell would be started with:

```sh
python -m streamlit run app.py
```

No device-side install, public hosting, PR, paid service, browser launch, real-data upload or CI dispatch has been performed through this mission. The only acceptable future chart input is an independently inspected authentic hosted report artifact. Do not create an example with invented model metrics: current CI artifacts from PM-04 verify earlier code, not the PM-10 statistical workload.

## Exact acceptance and GO/NO-GO gates

- [x] Source-only implementation of 4 original deliverables on PM-11 private branch, layered over exact PM-10 head.
- [ ] Execute **exact PM-11 branch SHA** in authorized GitHub Actions on Python 3.11/3.12, inspect job logs for `pytest -q`, Ruff, strict mypy and all inherited PM-08/09/10 tests; resolve failures. **NOT RUN.**
- [ ] Verify the real PM-10 report file against source manifest, actual synthetic rights, non-overlapping participants, no bad score/performance claims, correct null subgroup handling. **NOT RUN.**
- [ ] Execute PM-11 export, check all reported SHA-256 and expected artifact contents, verify actual Markdown contains only reported measurements; store/run-link, checksum and environment. **NOT RUN.**
- [ ] Launch app privately (authorized host) and check input rejection, no-results state, keyboard/screen-reader alternative, charts and download bytes against actual artifacts. **NOT RUN.**
- [ ] Review private software, data licensing, security, release checklist and obtain fresh approval for any public change. **NO-GO.**

**Current gate:** GO for private code review; **NO-GO for Verified Done, reproducibility claim, scientific findings or public visibility**. Manual private GitHub Actions may consume quota; no dispatch from the currently connected GitHub MCP is available, so hosted QA requires separate approved mechanism and budget verification. Continue dependency closure first; next consolidated mission may be prepared in source-only mode only after its prerequisites are checked.

## Primary references

- [Streamlit file uploader](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader) and [download button](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button) for guarded downloads and upload constraints.
- [Vega-Altair encodings](https://altair-viz.github.io/user_guide/encodings/index.html) for visible axes, tooltips and legend encodings.
- [scikit-learn leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html), [GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html), and [balanced accuracy](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html).
