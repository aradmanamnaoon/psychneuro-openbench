"""PM-12: bounded synthetic preview and strictly artifact-derived comparison controls.

No private, clinical or external data acquisition. Preview rows contain only
the two pre-response predictors from the original synthetic generator.
Neither a preview nor a UI filter retrains/tunes the benchmark.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .reporting import METRICS, MODELS, ReportValidationError, chart_rows, validate_report
from .synthetic import SyntheticConfig, dataset_card, generate_trials

PREVIEW_SEEDS = (73, 74, 75)
PREVIEW_PARTICIPANTS = (6, 12, 24)
PREVIEW_TRIALS_PER_PARTICIPANT = (8, 20)
PREVIEW_MAX_ROWS = 1000
DATA_MODES = ("Original synthetic preview (no model scores)", "Uploaded PM-10 report (results)")


@dataclass(frozen=True, slots=True)
class PreviewRow:
    fictional_participant_id: str
    trial_order: int
    difficulty_unitless: float
    stimulus_condition: str


@dataclass(frozen=True, slots=True)
class SyntheticPreview:
    seed: int
    n_participants: int
    trials_per_participant: int
    n_trials: int
    source_sha256: str
    rights_basis: str
    rows: tuple[PreviewRow, ...]


def prepare_synthetic_preview(
    seed: int, n_participants: int, trials_per_participant: int
) -> SyntheticPreview:
    """Use ONLY original, size-capped, preapproved demonstration inputs.

    Preview exposes no response, correctness, latency or model results.
    This is a local source generation inside the authorized *future* app,
    not a benchmark execution and not a sample from real people.
    """
    if (
        type(seed) is not int or seed not in PREVIEW_SEEDS
        or type(n_participants) is not int or n_participants not in PREVIEW_PARTICIPANTS
        or type(trials_per_participant) is not int
        or trials_per_participant not in PREVIEW_TRIALS_PER_PARTICIPANT
    ):
        raise ValueError("preview inputs must match the fixed original-synthetic UI choices")
    if n_participants * trials_per_participant > PREVIEW_MAX_ROWS:
        raise ValueError("synthetic preview row cap exceeded")
    config = SyntheticConfig(
        seed=seed,
        n_participants=n_participants,
        trials_per_participant=trials_per_participant,
    )
    trials = generate_trials(config)
    card = dataset_card(config, trials)
    if (
        card["source_kind"] != "synthetic"
        or card["rights_basis"] != "synthetic-original"
        or not card["synthetic"]
        or card["n_trials"] != len(trials)
    ):
        raise ValueError("synthetic preview did not meet source-rights contract")
    rows = tuple(
        PreviewRow(
            fictional_participant_id=trial.participant_id,
            trial_order=trial.trial_order,
            difficulty_unitless=trial.difficulty,
            stimulus_condition=trial.stimulus_condition,
        )
        for trial in trials[:12]
    )
    return SyntheticPreview(
        seed=seed,
        n_participants=n_participants,
        trials_per_participant=trials_per_participant,
        n_trials=len(trials),
        source_sha256=card["source_sha256"],
        rights_basis=card["rights_basis"],
        rows=rows,
    )


def filter_report_scores(
    report: dict[str, object],
    *,
    metric: str,
    selected_models: Sequence[str],
    selected_repeats: Sequence[int],
) -> list[dict[str, str | int | float]]:
    """Filter a genuine-format report without computing or inventing scores.

    Distinct model values are point comparisons, not significance testing.
    The selected CV policy is displayed as a decision rule, not a third fit.
    """
    valid = validate_report(report)
    if metric not in METRICS:
        raise ReportValidationError("unknown prespecified score")
    if (
        any(type(name) is not str or name not in MODELS for name in selected_models)
        or len(set(selected_models)) != len(selected_models)
    ):
        raise ReportValidationError("model controls contain an unknown or duplicate model")
    requested = valid["n_requested"]
    if (
        any(type(index) is not int or not 1 <= index <= requested for index in selected_repeats)
        or len(set(selected_repeats)) != len(selected_repeats)
    ):
        raise ReportValidationError("repeat controls contain an unknown or duplicate repeat")
    accepted_models = set(selected_models)
    accepted_repeats = set(selected_repeats)
    return [
        row
        for row in chart_rows(valid, metric)
        if row["Model"] in accepted_models and row["Repeat"] in accepted_repeats
    ]


def full_report_summary(
    report: dict[str, object], metric: str, models: Sequence[str]
) -> list[dict[str, object]]:
    """Unfiltered PM-10 aggregate; never recompute uncertainty after UI filtering."""
    valid = validate_report(report)
    if metric not in METRICS or any(m not in MODELS for m in models):
        raise ReportValidationError("unknown metric or model")
    if len(set(models)) != len(models):
        raise ReportValidationError("duplicate model requested")
    summary = valid["summary"]
    return [
        {
            "Model / policy": name,
            "Metric (unitless 0–1)": metric,
            "Eligible synthetic cohorts (full report)": summary[name][metric]["n_repeats"],
            "Mean (full report)": summary[name][metric]["mean"],
            "SE (full report)": summary[name][metric]["standard_error"],
            "Nominal 95% lower (full report)": summary[name][metric]["ci95_low"],
            "Nominal 95% upper (full report)": summary[name][metric]["ci95_high"],
        }
        for name in models
    ]
