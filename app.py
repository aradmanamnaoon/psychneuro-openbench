"""Private Streamlit shell for authentic, uploaded PM-10 result artifacts only.

Start only in an authorized hosted environment after verification; no service is
deployed by committing this file. No synthetic values are generated in the UI.
"""
from __future__ import annotations

import json

import altair as alt
import streamlit as st

from psychneuro.reporting import (
    METRICS,
    ReportValidationError,
    build_bundle,
    chart_rows,
    parse_report,
)

st.set_page_config(page_title="PsychNeuro OpenBench — private review", layout="wide")
st.title("PsychNeuro OpenBench")
st.caption("Private, nonclinical research-software review. No live benchmark is running.")
st.warning(
    "Engineering preview — NOT clinical or empirical neuroscience evidence. "
    "Uploaded artifact checksums are self-consistency checks, not independent "
    "verification of GitHub Actions or research validity."
)

page = st.sidebar.radio(
    "Navigation",
    ("Overview", "Results and charts", "Reports and lineage", "Limitations"),
)
st.sidebar.caption("No accounts, research data uploads or background model jobs required.")

if page == "Overview":
    st.subheader("From trial validation to traceable reports")
    st.write(
        "This workbench is intended for psychology methods students, "
        "computational neuroscience analysts and ML reproducibility reviewers. "
        "It displays validated original-synthetic PM-10 output only. "
        "A real hosted run must exist before any measured charts or exports appear."
    )

if page == "Limitations":
    st.subheader("Scientific and data-rights boundaries")
    st.write(
        "Only invented behavioral trial cohorts are supported. Fictional "
        "participants are held out within a repeat; seed-distinct simulated "
        "cohorts are not independent human samples. Balanced accuracy and "
        "macro F1 are unitless. Approximate uncertainty is conditional on "
        "the generator and does not establish significance, generalization, "
        "causality, human behavior or clinical utility."
    )
    st.write(
        "Predeclared left/right stimulus-condition subgroup results are "
        "suppressed when there are fewer than 10 independent fictional "
        "participants, fewer than 30 rows or only one truth class."
    )

st.divider()
st.subheader("Load an actual PM-10 report artifact")
st.caption(
    "Upload ONLY report.json from a completed, authorized private GitHub Actions "
    "run or other genuinely executed PM-10 pipeline. No example metrics are bundled."
)
uploaded = st.file_uploader(
    "PM-10 report.json (JSON, max 2 MB)",
    type=["json"],
    accept_multiple_files=False,
    max_upload_size=2,
)
if uploaded is None:
    st.info("No result artifact loaded. Charts and downloads remain unavailable.")
    st.stop()

try:
    report = parse_report(uploaded.getvalue())
    bundle = build_bundle(report)
except (ReportValidationError, ValueError) as exc:
    st.error(f"Input rejected; no charts or exports created: {exc}")
    st.stop()

st.success("PM-10 format, rights declaration, seed counts and internal SHA-256 verified.")
st.error(
    "HOSTED CI NOT VERIFIED by this application. Compare the source commit, "
    "workflow run logs and archived artifact checksum independently before "
    "using this as software validation evidence."
)
st.caption(
    "Report status: "
    + str(report["status"])
    + " · synthetic repeats eligible: "
    + str(report["n_eligible"])
    + "/"
    + str(report["n_requested"])
)
if report["status"] != "complete":
    st.warning("At least one repeat was ineligible; no missing values were filled in.")

if page in ("Overview", "Results and charts"):
    st.subheader("Synthetic repeat-level held-out model comparison")
    metric = st.selectbox(
        "Metric to inspect",
        METRICS,
        format_func=lambda key: (
            "Balanced accuracy (unitless 0–1)"
            if key == "balanced_accuracy"
            else "Macro F1 (unitless 0–1)"
        ),
    )
    rows = chart_rows(report, metric)
    if not rows:
        st.info("No eligible synthetic repeats: numerical charts suppressed.")
    else:
        chart = (
            alt.Chart(rows)
            .mark_point(filled=True, size=100)
            .encode(
                x=alt.X("Repeat:O", title="Predeclared synthetic cohort repeat"),
                y=alt.Y(
                    "Score:Q",
                    title="Held-out " + str(metric) + " (unitless 0–1)",
                    scale=alt.Scale(domain=[0, 1]),
                ),
                color=alt.Color("Model:N", title="Fixed model or CV-selected policy"),
                shape=alt.Shape("Model:N", title="Model / policy"),
                tooltip=[
                    alt.Tooltip("Repeat:O", title="Repeat"),
                    alt.Tooltip("Model:N", title="Model or policy"),
                    alt.Tooltip("Score:Q", title="Score (unitless)", format=".4f"),
                ],
            )
            .properties(
                title="Original synthetic held-out scores by predeclared repeat",
                description=(
                    "Each mark is one model/policy on one synthetic repeat. "
                    "The vertical axis is unitless 0 to 1; axes do not imply "
                    "human generalization or statistically significant differences."
                ),
            )
        )
        st.altair_chart(chart, use_container_width=True)
        st.caption(
            "Accessible numerical alternative: table below contains all charted "
            "points. A score is a synthetic held-out value, not a scientific effect."
        )
        st.dataframe(rows, hide_index=True, use_container_width=True)
    st.caption(
        "Balanced accuracy = average of the two class recalls. "
        "Macro F1 = unweighted mean of class-wise F1. "
        "The CV-selected policy is not a third separately fitted estimator."
    )

if page == "Reports and lineage":
    st.subheader("Inspect the same authenticated-format source")
    st.code(str(report["report_sha256"]), language="text")
    st.caption("Canonical report payload SHA-256. Self-checksum is not an authenticity proof.")
    manifest = json.loads(bundle.artifact_manifest.decode("utf-8"))
    st.json(manifest)
    st.caption(
        "Manifest includes source/split/experiment SHA-256, schema/config versions, "
        "and exact export file digests. CI run ID is null until externally verified."
    )

st.subheader("Reproducibility exports from this uploaded input")
st.download_button(
    "Download validated PM-10 JSON",
    data=bundle.report_json,
    file_name="report.json",
    mime="application/json",
    on_click="ignore",
)
st.download_button(
    "Download accessible Markdown report",
    data=bundle.report_markdown,
    file_name="report.md",
    mime="text/markdown",
    on_click="ignore",
)
st.download_button(
    "Download artifact lineage manifest",
    data=bundle.artifact_manifest,
    file_name="artifact-manifest.json",
    mime="application/json",
    on_click="ignore",
)
