"""PM-12 private Streamlit research explorer: synthetic preview OR validated report.

Never mixes the fictional on-demand preview with held-out model evidence.
Never computes model scores from UI choices, auto-downloads data or retrains.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import altair as alt
import streamlit as st

from psychneuro.explorer import (
    DATA_MODES,
    PREVIEW_PARTICIPANTS,
    PREVIEW_SEEDS,
    PREVIEW_TRIALS_PER_PARTICIPANT,
    filter_report_scores,
    full_report_summary,
    nominal_uncertainty_intervals,
    prepare_synthetic_preview,
)
from psychneuro.reporting import METRICS, MODELS, ReportValidationError, build_bundle, parse_report
from psychneuro.ux import explain_scenario_failure, explain_upload_failure
from psychneuro.workflow import (
    SCENARIO_GENERATOR_SEEDS,
    SCENARIO_PARTICIPANTS,
    SCENARIO_REPEATS,
    SCENARIO_TRIALS,
    Scenario,
    ScenarioError,
    run_scenario,
)

st.set_page_config(page_title="PsychNeuro OpenBench — private review", layout="wide")
st.title("PsychNeuro OpenBench")
st.caption("Nonclinical private software preview. No hosted benchmark or clinical service.")
st.caption(
    "Getting started: choose a permitted source in the sidebar. The fictional "
    "preview needs no upload. A model run starts only after you submit the "
    "synthetic-only form. Headings, labels and result tables supplement charts."
)
st.warning(
    "Software evaluation only — NOT human neuroscience evidence, medical advice "
    "or a clinical prediction tool. Uploading an internally consistent JSON "
    "does not prove its originating GitHub CI run succeeded."
)

page = st.sidebar.radio(
    "Navigation",
    ("Overview", "Synthetic preview", "Results and charts", "Reports and lineage", "Limitations"),
)
source_mode = st.sidebar.selectbox("Permitted data source", DATA_MODES, index=0)
st.sidebar.caption(
    "No public or third-party datasets. Demo controls do not alter the locked "
    "PM-10 test split, model selection, or saved reports."
)
st.sidebar.caption(
    "Keyboard: use Tab and Shift+Tab through labeled controls, then Enter/Space "
    "to activate buttons. No response field is required for the preview."
)

if page == "Overview":
    st.subheader("From toy trial tables to inspectable benchmark evidence")
    st.write(
        "For psychology methods students, neuroinformatics analysts and "
        "ML reproducibility reviewers. Preview the original fictional generator "
        "or inspect a separately executed PM-10 synthetic report. No users, "
        "dataset permissions, study results or application deployment are implied."
    )

if page == "Limitations":
    st.subheader("Scientific, rights and privacy restrictions")
    st.write(
        "The only permitted preview source is the original invented two-choice "
        "generator. No raw human, patient, clinical, scraped or third-party data "
        "are supported or uploaded. Real behavioral data require separate legal "
        "and scientific approval. Synthetic correctness, response and latency "
        "are post-response values, forbidden as pre-response model features."
    )
    st.write(
        "Scores are balanced accuracy and macro F1 (unitless 0–1). "
        "Each chart point refers to a distinct seeded fictional cohort, not "
        "an independent participant study. Nominal uncertainty does not "
        "establish causation, statistical superiority or population validity."
    )
    st.write(
        "Small stimulus-condition slices are suppressed unless they have "
        "at least 10 fictional participants, at least 30 rows and both classes."
    )

if source_mode == DATA_MODES[0]:
    st.sidebar.subheader("Synthetic preview controls")
    seed = st.sidebar.selectbox("Toy generator seed (not a benchmark repeat)", PREVIEW_SEEDS)
    participants = st.sidebar.selectbox(
        "Fictional participants", PREVIEW_PARTICIPANTS, index=1
    )
    trials = st.sidebar.selectbox(
        "Trials per fictional participant", PREVIEW_TRIALS_PER_PARTICIPANT
    )
    st.divider()
    if page in ("Overview", "Synthetic preview"):
        preview = prepare_synthetic_preview(seed, participants, trials)
        st.subheader("Original synthetic source — pre-response fields only")
        st.caption(
            "Freshly generated fictional preview: NOT a model run, real dataset, "
            "holdout, sampled research cohort or demonstration of model accuracy."
        )
        st.write(
            f"Generator seed: {preview.seed}; fictional participants: "
            f"{preview.n_participants}; generated rows: {preview.n_trials}; "
            f"source rights: {preview.rights_basis}."
        )
        st.code(preview.source_sha256, language="text")
        st.caption("SHA-256 of the original generator's canonical CSV, not a CI attestation.")
        st.table([asdict(row) for row in preview.rows])
        st.caption(
            "First 12 rows; selected predictors only: synthetic cue (left/right), "
            "difficulty (unitless). Correctness, response and latency intentionally "
            "withheld to prevent presentation as pre-response predictors."
        )
    else:
        st.info(
            "No held-out model results are available in synthetic preview mode. "
            "Select 'Uploaded PM-10 report (results)' in the sidebar and supply "
            "a genuinely executed synthetic JSON artifact to enable comparisons."
        )
    st.stop()

st.divider()
report = None
is_live = source_mode == DATA_MODES[2]
if is_live:
    st.subheader("Execute a new fictional grouped-benchmark scenario")
    st.caption(
        "Explicit opt-in, synchronous computation using the project's ORIGINAL "
        "synthetic generator, rights-checked loader, participant-grouped baseline "
        "runner and repeated PM-10 report generator. Not an externally validated "
        "result or evidence about people. No hidden background jobs."
    )
    with st.sidebar.form("run_synthetic_scenario"):
        st.subheader("Run controls — synthetic only")
        run_seed = st.selectbox(
            "First fictional generator seed", SCENARIO_GENERATOR_SEEDS
        )
        run_participants = st.selectbox(
            "Fictional participants per cohort", SCENARIO_PARTICIPANTS
        )
        run_trials = st.selectbox(
            "Trials per fictional participant", SCENARIO_TRIALS
        )
        run_repeats = st.selectbox(
            "Predetermined seeded cohorts", SCENARIO_REPEATS, index=2
        )
        submitted = st.form_submit_button("Run synthetic benchmark", type="primary")
    st.sidebar.caption(
        "At most 3,000 fictional trials total. Models/features/CV selection, "
        "held-out group split and seed schedule are locked."
    )
    if submitted:
        # Remove old session evidence BEFORE a new run so exceptions cannot
        # accidentally leave old scores associated with updated controls.
        st.session_state.pop("pm13_last_report", None)
        st.session_state.pop("pm13_last_scenario", None)
        selected = Scenario(
            generator_seed=run_seed,
            n_participants=run_participants,
            trials_per_participant=run_trials,
            repeats=run_repeats,
        )
        try:
            with st.spinner("Computing the requested synthetic-only benchmark…"):
                result = run_scenario(selected, Path(__file__).resolve().parent)
        except (ScenarioError, ValueError) as exc:
            st.error(
                "Synthetic benchmark rejected or failed: "
                + explain_scenario_failure(exc)
            )
            st.stop()
        st.session_state["pm13_last_report"] = result
        st.session_state["pm13_last_scenario"] = asdict(selected)
    if st.sidebar.button("Discard session benchmark results"):
        st.session_state.pop("pm13_last_report", None)
        st.session_state.pop("pm13_last_scenario", None)
    candidate = st.session_state.get("pm13_last_report")
    if candidate is None:
        st.info(
            "No in-app run yet. Submit a bounded scenario to compute real "
            "synthetic-only baseline scores, optional uncertainty and downloads."
        )
        st.stop()
    try:
        report = parse_report(build_bundle(candidate).report_json)
        bundle = build_bundle(report)
    except (ValueError, TypeError) as exc:
        st.session_state.pop("pm13_last_report", None)
        st.error(
            "Saved session artifact was invalid and cleared. "
            + explain_upload_failure(exc)
        )
        st.stop()
    st.success(
        "In-app execution completed using the rights-checked synthetic pipeline. "
        "This is a local-to-app computation, NOT verified hosted CI evidence."
    )
    st.write(
        "Last SUBMITTED scenario (not the currently edited form):",
        st.session_state.get("pm13_last_scenario"),
    )
else:
    st.subheader("Review a separately executed PM-10 synthetic report")
    st.caption(
        "Upload ONLY a report.json from an authorized completed private PM-10 run "
        "(maximum 2 MB). No raw human data, datasets or unapproved sources. "
        "Uploaded report is parsed for structural consistency, NOT authenticated to CI."
    )
    uploaded = st.file_uploader(
        "Original PM-10 report.json",
        type=["json"],
        accept_multiple_files=False,
        max_upload_size=2,
    )
    if uploaded is None:
        st.info("No report uploaded; genuine result selectors, charts and exports unavailable.")
        st.stop()
    try:
        report = parse_report(uploaded.getvalue())
        bundle = build_bundle(report)
    except (ReportValidationError, ValueError) as exc:
        st.error(
            "Input rejected without plotting or exporting: "
            + explain_upload_failure(exc)
        )
        st.stop()
    st.success(
        "Source policy, protocol, seed order, score summary and internal hash are consistent."
    )

st.error(
    "INDEPENDENT HOSTED CI NOT VERIFIED BY THIS UI. Compare exact commit, "
    "workflow run logs and archived artifacts before reporting scientific or "
    "reproducibility evidence."
)
st.caption(
    f"PM-10 input SHA-256: {report['report_sha256']} · status: {report['status']} · "
    f"eligible fictional cohorts: {report['n_eligible']}/{report['n_requested']}"
)
if report["status"] != "complete":
    st.warning(
        "One or more predetermined synthetic repeats are INELIGIBLE. "
        "No zero imputation, selective replacement or hidden failure."
    )

if page in ("Overview", "Results and charts"):
    st.subheader("Held-out model scores — originally recorded synthetic repeats")
    metric = st.selectbox(
        "Predeclared evaluation metric",
        METRICS,
        format_func=lambda key: (
            "Balanced accuracy (unitless 0–1)"
            if key == "balanced_accuracy"
            else "Macro F1 (unitless 0–1)"
        ),
    )
    selected_models = st.multiselect(
        "Fixed baseline models and preselected policy",
        MODELS,
        default=MODELS,
        format_func=lambda key: (
            "CV-selected decision policy (not a third fit)"
            if key == "cv_selected_policy" else key
        ),
    )
    selected_repeats = st.multiselect(
        "Predeclared synthetic cohort repeats (visual filter only)",
        list(range(1, report["n_requested"] + 1)),
        default=list(range(1, report["n_requested"] + 1)),
    )
    rows = filter_report_scores(
        report,
        metric=metric,
        selected_models=selected_models,
        selected_repeats=selected_repeats,
    )
    st.caption(
        "These filters display recorded scores only; no model fitting, test "
        "peeking, retuning, resampling, significance test or recomputation of "
        "PM-10 uncertainty. 'CV-selected' reuses its chosen baseline's scores."
    )
    if not rows:
        st.info("No eligible results for these controls. No synthetic values were fabricated.")
    else:
        plot = (
            alt.Chart(alt.Data(values=rows))
            .mark_point(filled=True, size=100)
            .encode(
                x=alt.X("Repeat:O", title="Predetermined synthetic repeat"),
                y=alt.Y(
                    "Score:Q",
                    title=f"Held-out {metric} (unitless 0–1)",
                    scale=alt.Scale(domain=[0, 1]),
                ),
                color=alt.Color("Model:N", title="Baseline or selected policy"),
                shape=alt.Shape("Model:N", title="Model or policy"),
                tooltip=[
                    alt.Tooltip("Repeat:O", title="Repeat"),
                    alt.Tooltip("Model:N", title="Model/policy"),
                    alt.Tooltip("Score:Q", title="Unitless score", format=".4f"),
                ],
            )
            .properties(
                title="Held-out performance on invented synthetic cohort repeats",
                description=(
                    "Each point is an existing synthetic held-out model score; "
                    "score axis unitless 0 to 1, with identical data table below."
                ),
            )
        )
        st.altair_chart(plot, use_container_width=True)
        st.caption(
            "Text alternative: the static table below lists every plotted point "
            "by repeat, model/policy and unitless score. The plot is optional."
        )
        st.table(rows)
    st.subheader("Full-report descriptive uncertainty (not filter-dependent)")
    st.caption(
        "This summary always uses ALL eligible original repeats, even if "
        "selected_repeats above excludes some. No post hoc interval recomputation."
    )
    if selected_models:
        st.table(full_report_summary(report, metric, selected_models))
    else:
        st.info("Select at least one predeclared model or policy to display its summary.")
    st.caption(
        "Balanced accuracy is the average recall across classes 0 and 1. "
        "Macro F1 is the average of per-class F1 scores. "
        "SE and nominal CI refer to simulated cohort seeds, NOT human participants."
    )
    st.subheader("Nominal repeat-level uncertainty — original full report")
    st.caption(
        "A vertical line shows the UNCLIPPED approximate 95% Student-t interval "
        "around the mean across ELIGIBLE seeded synthetic cohorts. It may "
        "extend outside the theoretical score range [0, 1], so the interval "
        "axis is intentionally not truncated. This is not a human-population CI, "
        "statistical significance finding or calibrated model comparison."
    )
    interval_rows = nominal_uncertainty_intervals(report, metric, selected_models)
    if not interval_rows:
        st.info(
            "No eligible 95% interval for these models. At least 5 eligible "
            "synthetic cohort repeats are needed; unavailable intervals are N/A, "
            "not a fabricated zero-width bar."
        )
    else:
        data = alt.Data(values=interval_rows)
        base = alt.Chart(data).encode(
            x=alt.X("Model:N", title="Fixed baseline or training-CV-selected policy")
        )
        intervals = base.mark_rule(size=4).encode(
            y=alt.Y("Lower 95%:Q", title="Score / nominal interval (unitless)"),
            y2=alt.Y2("Upper 95%:Q"),
            tooltip=[
                alt.Tooltip("Model:N"),
                alt.Tooltip("Eligible repeats:Q", format="d"),
                alt.Tooltip("Mean:Q", format=".4f"),
                alt.Tooltip("Lower 95%:Q", format=".4f"),
                alt.Tooltip("Upper 95%:Q", format=".4f"),
            ],
        )
        means = base.mark_point(filled=True, size=140).encode(
            y=alt.Y("Mean:Q", title="Score / nominal interval (unitless)"),
            tooltip=[
                alt.Tooltip("Model:N"),
                alt.Tooltip("Mean:Q", format=".4f"),
            ],
        )
        st.altair_chart(
            (intervals + means).properties(
                title="Descriptive uncertainty across fictional cohort seeds",
                description="Nominal intervals and mean points, tabulated directly below.",
            ),
            use_container_width=True,
        )
        st.caption(
            "Text alternative: the static table below gives each model, "
            "eligible-repeat count, mean and unclipped nominal CI boundaries. "
            "Values are from the complete original report."
        )
        st.table(interval_rows)
    st.caption(
        "No probability of superiority, causal inference, clinical utility, "
        "independent human subjects, or empirical neuroscience claim is permitted."
    )

if page == "Reports and lineage":
    st.subheader("Canonical PM-10 source and deterministic PM-11 file checks")
    st.code(str(report["report_sha256"]), language="text")
    st.caption("Source self-checksum is not a cryptographic signature or independent verification.")
    st.json(json.loads(bundle.artifact_manifest.decode("utf-8")))
    st.caption(
        "Includes per-repeat synthetic source/split/manifest hashes, expected "
        "schema, export checksums, null hosted CI ID and unverified source commit."
    )

st.subheader("Download the complete original report and provenance exports")
st.caption(
    "Downloads are full-report exports from the checked source, not filtered "
    "to the selected chart points. No raw fictional trial rows are exported."
)
st.download_button(
    "PM-10 JSON report",
    data=bundle.report_json,
    file_name="report.json",
    mime="application/json",
    on_click="ignore",
)
st.download_button(
    "PM-11 Markdown report",
    data=bundle.report_markdown,
    file_name="report.md",
    mime="text/markdown",
    on_click="ignore",
)
st.download_button(
    "PM-11 artifact lineage manifest",
    data=bundle.artifact_manifest,
    file_name="artifact-manifest.json",
    mime="application/json",
    on_click="ignore",
)
