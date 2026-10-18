"""Generate deterministic *synthetic-only* pilot exploration artifacts.

No real participants, external downloads, clinical inference, or modeling.
This module emits artifacts only when explicitly executed in an authorized host.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from statistics import mean, median

from .loaders import load_dataset, manifest_json
from .synthetic import SyntheticConfig, TrialRecord


def _difficulty_groups(records: tuple[TrialRecord, ...]) -> list[dict[str, float | int]]:
    grouped: dict[float, list[TrialRecord]] = defaultdict(list)
    for record in records:
        grouped[record.difficulty].append(record)
    return [
        {
            "difficulty": level,
            "n_trials": len(trials),
            "mean_correct": mean(row.correct for row in trials),
            "mean_response_time_ms": mean(row.response_time_ms for row in trials),
            "median_response_time_ms": median(row.response_time_ms for row in trials),
        }
        for level, trials in sorted(grouped.items())
    ]


def _svg(groups: list[dict[str, float | int]]) -> str:
    """No external rendering library; plot observed synthetic group means only."""
    width, height = 760, 370
    plot_left, plot_top, plot_width, plot_height = 95, 65, 600, 230
    bar_slot = plot_width / max(len(groups), 1)
    bars: list[str] = []
    for index, group in enumerate(groups):
        accuracy = float(group["mean_correct"])
        x = plot_left + index * bar_slot + bar_slot * 0.2
        bar_width = bar_slot * 0.6
        y = plot_top + (1.0 - accuracy) * plot_height
        bar_height = accuracy * plot_height
        bars.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" '
            f'height="{bar_height:.2f}" fill="#365e85"/>'
        )
        bars.append(
            f'<text x="{x + bar_width / 2:.2f}" y="{plot_top + plot_height + 23}" '
            f'text-anchor="middle" font-size="14">{float(group["difficulty"]):.2f}</text>'
        )
        bars.append(
            f'<text x="{x + bar_width / 2:.2f}" y="{max(50, y - 9):.2f}" '
            f'text-anchor="middle" font-size="13">{accuracy:.3f}</text>'
        )
    ticks: list[str] = []
    for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = plot_top + (1.0 - fraction) * plot_height
        ticks.append(
            f'<line x1="{plot_left}" y1="{y:.2f}" x2="{plot_left + plot_width}" '
            f'y2="{y:.2f}" stroke="#bdc5cc" stroke-width="1"/>'
            f'<text x="{plot_left - 12}" y="{y + 5:.2f}" '
            f'text-anchor="end" font-size="13">{fraction:.2f}</text>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Synthetic accuracy by artificial difficulty">\n'
        '<title>Invented-trial accuracy by synthetic difficulty</title>\n'
        '<rect width="100%" height="100%" fill="white"/>\n'
        '<text x="380" y="30" text-anchor="middle" font-size="19">'
        'Synthetic fixtures only — not human performance</text>\n'
        + "\n".join(ticks + bars)
        + '\n<text x="380" y="354" text-anchor="middle" font-size="16">'
        'Artificial difficulty (unitless)</text>\n</svg>\n'
    )


def explore(config: SyntheticConfig, registry_path: Path, output_dir: Path) -> None:
    """Validate using the production rights gate before producing descriptive files."""
    loaded = load_dataset(config, registry_path)
    rows = loaded.records
    grouped = _difficulty_groups(rows)
    summary = {
        "source_kind": "synthetic",
        "dataset_id": loaded.schema.dataset_id,
        "generator_seed": config.seed,
        "n_trials": len(rows),
        "n_participants": loaded.quality.n_participants,
        "n_sessions": loaded.quality.n_sessions,
        "accuracy": mean(row.correct for row in rows),
        "mean_response_time_ms": mean(row.response_time_ms for row in rows),
        "median_response_time_ms": median(row.response_time_ms for row in rows),
        "quality": asdict(loaded.quality),
        "difficulty_groups": grouped,
        "interpretation": (
            "Invented software fixtures. These are not empirical findings, "
            "human reaction times, estimates, or claims of model performance."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "manifest.json").write_text(
        manifest_json(loaded.provenance), encoding="utf-8"
    )
    with (output_dir / "difficulty_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "difficulty", "n_trials", "mean_correct",
                "mean_response_time_ms", "median_response_time_ms",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(grouped)
    (output_dir / "accuracy_by_difficulty.svg").write_text(
        _svg(grouped), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=73)
    parser.add_argument("--participants", type=int, default=12)
    parser.add_argument("--trials-per-participant", type=int, default=20)
    parser.add_argument("--registry", type=Path, default=Path("data/registry.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/pm06"))
    args = parser.parse_args()
    explore(
        SyntheticConfig(
            seed=args.seed,
            n_participants=args.participants,
            trials_per_participant=args.trials_per_participant,
        ),
        args.registry,
        args.output_dir,
    )


if __name__ == "__main__":
    main()
