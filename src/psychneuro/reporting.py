"""Fail-closed PM-10 report ingestion, accessible data views and reproducibility exports.

No benchmark is executed here. Numbers are NEVER fabricated: all displayed
values must come from a structurally valid PM-10 JSON payload. A self-checksum
detects accidental changes, not malicious fabrication or scientific validity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .config import CONFIG_VERSION
from .synthetic import SCHEMA_VERSION
from .uncertainty import summary_dict

REPORT_VERSION = "psychneuro-pm10-synthetic-repeat-v1"
EXPORT_VERSION = "psychneuro-pm11-report-bundle-v1"
MAX_INPUT_BYTES = 2_000_000
MODELS = ("dummy_prior", "logistic_regression", "cv_selected_policy")
METRICS = ("balanced_accuracy", "macro_f1")
_METRIC_LABELS = {
    "balanced_accuracy": "Balanced accuracy",
    "macro_f1": "Macro F1",
}
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class ReportValidationError(ValueError):
    """The input is unsupported, inconsistent or has failed integrity checks."""


@dataclass(frozen=True, slots=True)
class ExportBundle:
    report_json: bytes
    report_markdown: bytes
    artifact_manifest: bytes


def _mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReportValidationError(f"{name} must be an object")
    return cast(dict[str, Any], value)


def _integer(value: object, name: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ReportValidationError(f"{name} must be an integer >= {minimum}")
    return cast(int, value)


def _digest(value: object) -> str:
    try:
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ReportValidationError("report is not finite JSON") from exc
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha(value: object, name: str) -> str:
    if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
        raise ReportValidationError(f"{name} must be a 64-character lowercase SHA-256")
    return value


def _score(value: object, name: str) -> float:
    if type(value) not in (int, float):
        raise ReportValidationError(f"{name} must be a number")
    number = float(cast(float, value))
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise ReportValidationError(f"{name} must be finite and in [0, 1]")
    return number


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in pairs:
        if key in out:
            raise ReportValidationError(f"duplicate JSON field: {key}")
        out[key] = value
    return out


def _bad_json_constant(value: str) -> None:
    raise ReportValidationError(f"nonfinite JSON constant: {value}")


def parse_report(raw: bytes) -> dict[str, Any]:
    """Parse an uploaded/report file within a hard byte bound and validate it."""
    if not raw or len(raw) > MAX_INPUT_BYTES:
        raise ReportValidationError("report is empty or exceeds 2 MB")
    try:
        decoded = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_pairs,
            parse_constant=_bad_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReportValidationError("invalid UTF-8 PM-10 JSON report") from exc
    return validate_report(decoded)


def validate_report(value: object) -> dict[str, Any]:
    """Check exact protocol/rights, repeats, scores, summary and self-checksum.

    Integrity is NOT authenticity. Never equate an internally consistent input
    with an independently verified GitHub Actions run or scientific finding.
    """
    data = _mapping(value, "report")
    if data.get("report_version") != REPORT_VERSION:
        raise ReportValidationError("unsupported PM-10 report version")
    if data.get("source_policy") != "original synthetic only; no external or human data":
        raise ReportValidationError("non-synthetic or unverified data rights")
    if data.get("independence_unit") != "distinctly seeded synthetic cohort; not trial rows":
        raise ReportValidationError("unsupported independence unit")
    supplied = _sha(data.get("report_sha256"), "report_sha256")
    unsigned = {key: val for key, val in data.items() if key != "report_sha256"}
    if supplied != _digest(unsigned):
        raise ReportValidationError("PM-10 canonical report SHA-256 mismatch")

    config = _mapping(data.get("config"), "config")
    baseline = _mapping(config.get("baseline"), "baseline")
    if baseline.get("config_version") != CONFIG_VERSION:
        raise ReportValidationError("unexpected versioned baseline protocol")
    _sha(baseline.get("config_sha256"), "baseline config_sha256")
    requested = _integer(data.get("n_requested"), "n_requested", minimum=1)
    if requested > 20 or _integer(config.get("repeats"), "config.repeats") != requested:
        raise ReportValidationError("mismatched or excessive repeats")
    eligible = _integer(data.get("n_eligible"), "n_eligible")
    ineligible = _integer(data.get("n_ineligible"), "n_ineligible")
    if eligible + ineligible != requested:
        raise ReportValidationError("invalid eligibility denominator")
    expected_status = "complete" if eligible == requested else "incomplete"
    if data.get("status") != expected_status:
        raise ReportValidationError("inconsistent completion status")
    base_generator = _integer(baseline.get("generator_seed"), "generator_seed")
    base_split = _integer(baseline.get("split_seed"), "split_seed")
    if (
        base_generator + requested - 1 > 2**64 - 1
        or base_split + requested - 1 > 2**64 - 1
    ):
        raise ReportValidationError("invalid seed range")
    if baseline.get("cv_folds") != 5:
        raise ReportValidationError("unsupported grouped CV policy")
    if config.get("seed_rule") != (
        "generator_seed+index and split_seed+index, index starts at 0"
    ):
        raise ReportValidationError("unexpected seed schedule")

    runs = data.get("runs")
    if not isinstance(runs, list) or len(runs) != requested:
        raise ReportValidationError("missing or incomplete run records")
    collected: dict[str, dict[str, list[float]]] = {
        model: {metric: [] for metric in METRICS} for model in MODELS
    }
    observed_ok = 0
    for index, item in enumerate(runs, start=1):
        run = _mapping(item, f"runs[{index}]")
        if (
            _integer(run.get("repeat"), "repeat", minimum=1) != index
            or _integer(run.get("generator_seed"), "generator_seed") != base_generator + index - 1
            or _integer(run.get("split_seed"), "split_seed") != base_split + index - 1
        ):
            raise ReportValidationError("repeats are not in the predeclared seed order")
        for field in ("source_sha256", "split_sha256", "experiment_manifest_sha256"):
            _sha(run.get(field), field)
        if not isinstance(run.get("reasons"), list):
            raise ReportValidationError("missing reasons array")
        status = run.get("status")
        if status == "ineligible":
            if (
                run.get("selected_model") is not None
                or run.get("test_metrics") is not None
                or run.get("test_slice_errors") is not None
            ):
                raise ReportValidationError("ineligible repeat leaked scores")
            continue
        if status != "ok" or run.get("selected_model") not in MODELS[:2]:
            raise ReportValidationError("unknown or unselected repeat")
        observed_ok += 1
        metrics = _mapping(run.get("test_metrics"), "test_metrics")
        if set(metrics) != set(MODELS):
            raise ReportValidationError("missing a prespecified model score")
        for model in MODELS:
            values = _mapping(metrics[model], model)
            if set(values) != set(METRICS):
                raise ReportValidationError("unexpected metric columns")
            for metric in METRICS:
                collected[model][metric].append(_score(values[metric], metric))
        selected = cast(str, run["selected_model"])
        if metrics["cv_selected_policy"] != metrics[selected]:
            raise ReportValidationError("selected policy differs from preselected model")

        slices = run.get("test_slice_errors")
        if slices is not None:
            if not isinstance(slices, list) or len(slices) != 2:
                raise ReportValidationError("invalid fixed slice table")
            for pos, label in enumerate(("left", "right")):
                row = _mapping(slices[pos], "slice")
                if row.get("feature") != "stimulus_condition" or row.get("slice") != label:
                    raise ReportValidationError("unexpected slice axis")
                _integer(row.get("n_trials"), "slice.n_trials")
                _integer(row.get("n_participants"), "slice.n_participants")
                if row.get("status") == "suppressed":
                    if row.get("metrics") is not None:
                        raise ReportValidationError("suppressed slice exposed metrics")
                elif row.get("status") == "ok":
                    if (
                        row["n_participants"] < 10
                        or row["n_trials"] < 30
                        or not isinstance(row.get("metrics"), dict)
                    ):
                        raise ReportValidationError("insufficient slice sample")
                else:
                    raise ReportValidationError("unsupported slice status")
    if observed_ok != eligible:
        raise ReportValidationError("observed run eligibility mismatch")
    summaries = _mapping(data.get("summary"), "summary")
    if set(summaries) != set(MODELS):
        raise ReportValidationError("unexpected score summary models")
    for model in MODELS:
        by_metric = _mapping(summaries[model], "summary model")
        if set(by_metric) != set(METRICS):
            raise ReportValidationError("unexpected summary metrics")
        for metric in METRICS:
            if by_metric[metric] != summary_dict(collected[model][metric]):
                raise ReportValidationError("summary not derivable from valid repeats")
    return data


def chart_rows(report: dict[str, Any], metric: str) -> list[dict[str, str | int | float]]:
    """Chart rows only from observed, valid reports. No invented graph points."""
    valid = validate_report(report)
    if metric not in METRICS:
        raise ReportValidationError("unsupported chart metric")
    rows: list[dict[str, str | int | float]] = []
    for item in cast(list[dict[str, Any]], valid["runs"]):
        if item["status"] != "ok":
            continue
        for model in MODELS:
            rows.append({
                "Repeat": cast(int, item["repeat"]),
                "Model": model,
                "Score": _score(item["test_metrics"][model][metric], metric),
            })
    return rows


def render_markdown(report: dict[str, Any]) -> str:
    """Return narrative/table text whose numbers derive strictly from the input."""
    valid = validate_report(report)
    summary = cast(dict[str, Any], valid["summary"])
    lines = [
        "# PsychNeuro OpenBench — synthetic benchmark report",
        "",
        "**Nonclinical, synthetic software evidence ONLY.** This JSON's internal "
        "SHA-256 validates formatting/integrity, NOT authorship, CI execution or "
        "scientific validity.",
        "",
        f"- PM-10 protocol: `{REPORT_VERSION}`",
        f"- Report status: **{valid['status']}**",
        f"- Synthetic cohorts requested / eligible / ineligible: "
        f"**{valid['n_requested']} / {valid['n_eligible']} / {valid['n_ineligible']}**",
        f"- Original PM-10 payload SHA-256: `{valid['report_sha256']}`",
        f"- Fixed config SHA-256: `{valid['config']['baseline']['config_sha256']}`",
        "- Scoring: balanced accuracy and macro F1; both unitless (0–1).",
        "- Uncertainty: across distinct synthetic cohort seeds, not held-out "
        "participants or real-world populations.",
        "",
        "## Repeat-level synthetic held-out metrics",
        "",
        "| Repeat | Seed | CV-selected model | Balanced accuracy | Macro F1 |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for row in cast(list[dict[str, Any]], valid["runs"]):
        if row["status"] != "ok":
            lines.append(f"| {row['repeat']} | {row['generator_seed']} | N/A (ineligible) | N/A | N/A |")
        else:
            metrics = row["test_metrics"]["cv_selected_policy"]
            lines.append(
                f"| {row['repeat']} | {row['generator_seed']} | {row['selected_model']} | "
                f"{metrics['balanced_accuracy']:.4f} | {metrics['macro_f1']:.4f} |"
            )
    lines.extend([
        "",
        "## Descriptive repeat-level summary (NOT a significance test)",
        "",
        "| Policy/model | Metric (unitless) | Eligible repeats | Mean | SE | Nominal 95% CI |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ])
    for model in MODELS:
        for metric in METRICS:
            s = summary[model][metric]
            def fmt(value: float | None) -> str:
                return "N/A" if value is None else f"{value:.4f}"
            ci = (
                "N/A"
                if s["ci95_low"] is None
                else f"{fmt(s['ci95_low'])} to {fmt(s['ci95_high'])}"
            )
            lines.append(
                f"| {model} | {_METRIC_LABELS[metric]} | {s['n_repeats']} | "
                f"{fmt(s['mean'])} | {fmt(s['standard_error'])} | {ci} |"
            )
    lines.extend([
        "",
        "## Data lineage and interpretive constraints",
        "",
        "- Source rights: synthetic-original; no real participants or clinical data.",
        "- Fictional participants are held out by group within each repeat.",
        "- Model selection uses training-only CV, not held-out test results.",
        "- Slice scores are suppressed unless at least 10 distinct fictional participants, "
        "30 rows and both truth classes are available per subgroup.",
        "- Nominal t intervals use an approximation with >=5 eligible repeats; "
        "intervals are NOT calibrated human-population uncertainty estimates.",
        "- Numeric tables reflect the supplied artifact, NOT independent validation "
        "of the originating CI run. Reconcile repository commit and Actions artifacts.",
        "",
        "## Per-repeat provenance",
        "",
        "| Repeat | Synthetic dataset SHA-256 | Split SHA-256 | Experiment manifest SHA-256 |",
        "| --- | --- | --- | --- |",
    ])
    for row in cast(list[dict[str, Any]], valid["runs"]):
        lines.append(
            f"| {row['repeat']} | `{row['source_sha256']}` | "
            f"`{row['split_sha256']}` | `{row['experiment_manifest_sha256']}` |"
        )
    return "\n".join(lines) + "\n"


def build_bundle(report: dict[str, Any]) -> ExportBundle:
    """Deterministic JSON, Markdown and standalone file-hash lineage manifest."""
    valid = validate_report(report)
    raw = (json.dumps(valid, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    md = render_markdown(valid).encode("utf-8")
    provenance = [
        {
            "repeat": item["repeat"],
            "generator_seed": item["generator_seed"],
            "split_seed": item["split_seed"],
            "source_sha256": item["source_sha256"],
            "split_sha256": item["split_sha256"],
            "experiment_manifest_sha256": item["experiment_manifest_sha256"],
            "status": item["status"],
        }
        for item in cast(list[dict[str, Any]], valid["runs"])
    ]
    manifest = {
        "artifact_manifest_version": EXPORT_VERSION,
        "data_schema_version": SCHEMA_VERSION,
        "input_report_version": REPORT_VERSION,
        "input_report_canonical_sha256": valid["report_sha256"],
        "baseline_config_sha256": valid["config"]["baseline"]["config_sha256"],
        "rights_basis": "synthetic-original",
        "repeats": provenance,
        "artifacts": {
            "report.json": {"sha256": _hash_bytes(raw), "bytes": len(raw)},
            "report.md": {"sha256": _hash_bytes(md), "bytes": len(md)},
        },
        "ci_run_id": None,
        "ci_verification": "NOT VERIFIED: compare exact uploaded artifact with hosted logs",
        "security_note": "SHA-256 self-checks are NOT signatures, proof of CI or proof of science",
    }
    encoded = (json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n").encode(
        "utf-8"
    )
    return ExportBundle(raw, md, encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a verified-structure PM-10 JSON report")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        bundle = build_bundle(parse_report(args.input.read_bytes()))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in (
        ("report.json", bundle.report_json),
        ("report.md", bundle.report_markdown),
        ("artifact-manifest.json", bundle.artifact_manifest),
    ):
        (args.output_dir / name).write_bytes(value)
    print("Exported integrity-checked PM-10-derived report, Markdown and lineage manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
