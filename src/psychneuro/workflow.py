"""PM-13 bounded, synchronous synthetic generator -> loader -> benchmark -> report.

Uses the original rights-gated synthetic generator and participant-grouped
baseline runner, not a mock or a second scoring path. The app invokes this
function only after an explicit click; no training on page load/rerun.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import BaselineConfig, load_baseline_config
from .pipeline import PipelineConfig, run_pipeline
from .reporting import build_bundle, validate_report

SCENARIO_GENERATOR_SEEDS = (73, 101)
SCENARIO_PARTICIPANTS = (24, 30)
SCENARIO_TRIALS = (20,)
SCENARIO_REPEATS = (1, 3, 5)
SCENARIO_SPLIT_SEED = 42
SCENARIO_MAX_TOTAL_TRIALS = 3_000
SCENARIO_VERSION = "pm13-original-synthetic-exploratory-v1"


class ScenarioError(ValueError):
    """Scenario cannot be run safely with this locked synthetic-only contract."""


@dataclass(frozen=True, slots=True)
class Scenario:
    generator_seed: int = 73
    n_participants: int = 24
    trials_per_participant: int = 20
    repeats: int = 5


def _scenario_baseline(scenario: Scenario, baseline_path: Path) -> BaselineConfig:
    """Hash exact JSON protocol with selected seed/dimensions, without file writes.

    All estimators, features, metric formulas, group split policy and selection
    rules come unchanged from the validated versioned repository configuration.
    """
    if (
        type(scenario.generator_seed) is not int
        or scenario.generator_seed not in SCENARIO_GENERATOR_SEEDS
        or type(scenario.n_participants) is not int
        or scenario.n_participants not in SCENARIO_PARTICIPANTS
        or type(scenario.trials_per_participant) is not int
        or scenario.trials_per_participant not in SCENARIO_TRIALS
        or type(scenario.repeats) is not int
        or scenario.repeats not in SCENARIO_REPEATS
    ):
        raise ScenarioError("scenario settings must use approved synthetic-only choices")
    total = (
        scenario.n_participants * scenario.trials_per_participant * scenario.repeats
    )
    if total > SCENARIO_MAX_TOTAL_TRIALS:
        raise ScenarioError("scenario exceeds the synchronous synthetic trial budget")
    try:
        frozen = load_baseline_config(baseline_path)
        original_bytes = baseline_path.read_bytes()
        protocol = json.loads(original_bytes.decode("utf-8"))
    except (ValueError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScenarioError("versioned baseline configuration cannot be verified") from exc
    original_canonical = json.dumps(
        protocol, sort_keys=True, ensure_ascii=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    if hashlib.sha256(original_canonical).hexdigest() != frozen.config_sha256:
        raise ScenarioError("baseline source changed while reading")
    if (
        protocol["dataset"]["generator_seed"] != frozen.generator_seed
        or protocol["dataset"]["n_participants"] != frozen.n_participants
        or protocol["dataset"]["trials_per_participant"] != frozen.trials_per_participant
        or protocol["split"]["seed"] != frozen.split_seed
    ):
        raise ScenarioError("baseline source does not match validated protocol")
    if frozen.split_seed != SCENARIO_SPLIT_SEED:
        raise ScenarioError("scenario uses a different locked split-seed protocol")
    protocol["dataset"]["generator_seed"] = scenario.generator_seed
    protocol["dataset"]["n_participants"] = scenario.n_participants
    protocol["dataset"]["trials_per_participant"] = scenario.trials_per_participant
    updated_canonical = json.dumps(
        protocol, sort_keys=True, ensure_ascii=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return BaselineConfig(
        config_version=frozen.config_version,
        config_sha256=hashlib.sha256(updated_canonical).hexdigest(),
        generator_seed=scenario.generator_seed,
        n_participants=scenario.n_participants,
        trials_per_participant=scenario.trials_per_participant,
        split_seed=frozen.split_seed,
        cv_folds=frozen.cv_folds,
    )


def run_scenario(scenario: Scenario, project_root: Path) -> dict[str, Any]:
    """Execute one explicitly requested scenario; return ONLY genuine computed output.

    An incomplete benchmark is returned with N/A/eligibility evidence, not forced
    into apparently successful results. Failures must not create downloads.
    """
    if not isinstance(project_root, Path):
        raise ScenarioError("project root must be a trusted repository Path")
    baseline = _scenario_baseline(scenario, project_root / "configs" / "baseline.json")
    registry = project_root / "data" / "registry.json"
    if not registry.is_file() or registry.is_symlink():
        raise ScenarioError("synthetic-only dataset registry is missing or unsafe")
    try:
        raw = run_pipeline(PipelineConfig(baseline, scenario.repeats), registry)
        validated = validate_report(raw)
        build_bundle(validated)  # integrity/export validation, no file or network side effects
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        raise ScenarioError("synthetic workflow failed; no report is available") from exc
    return validated


def main() -> int:
    """Strictly bounded hosted-CI proof path; not run in this conversation."""
    parser = argparse.ArgumentParser(description="Synthetic-only in-app runner CI equivalent")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--generator-seed", type=int, default=73)
    parser.add_argument("--participants", type=int, default=24)
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    scenario = Scenario(
        generator_seed=args.generator_seed,
        n_participants=args.participants,
        trials_per_participant=args.trials,
        repeats=args.repeats,
    )
    try:
        # A wheel install moves __file__ into site-packages; use the caller's
        # trusted repository working directory for its versioned config/registry.
        report = run_scenario(scenario, Path.cwd())
        bundle = build_bundle(report)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    output: Path = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    for name, content in (
        ("report.json", bundle.report_json),
        ("report.md", bundle.report_markdown),
        ("artifact-manifest.json", bundle.artifact_manifest),
    ):
        (output / name).write_bytes(content)
    print(f"status={report['status']} report_sha256={report['report_sha256']}")
    return 0 if report["status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
