"""PM-06 exploration artifact contracts; fictional records only."""
from __future__ import annotations

import json
from pathlib import Path

from psychneuro.explore import explore
from psychneuro.synthetic import SyntheticConfig

REGISTRY = Path(__file__).resolve().parents[1] / "data" / "registry.json"


def test_exploration_manifest_and_group_counts(tmp_path: Path) -> None:
    output = tmp_path / "first"
    explore(SyntheticConfig(seed=73, n_participants=2, trials_per_participant=4), REGISTRY, output)
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert summary["source_kind"] == "synthetic"
    assert summary["n_trials"] == 8
    assert sum(group["n_trials"] for group in summary["difficulty_groups"]) == 8
    assert manifest["n_trials"] == summary["n_trials"]
    assert manifest["raw_file_sha256"] is None
    assert manifest["source_kind"] == "synthetic"
    assert manifest["generator_seed"] == 73
    assert len(manifest["canonical_csv_sha256"]) == 64
    assert manifest["transformations"] == []


def test_exploration_outputs_are_byte_reproducible(tmp_path: Path) -> None:
    config = SyntheticConfig(seed=19, n_participants=3, trials_per_participant=4)
    left, right = tmp_path / "a", tmp_path / "b"
    explore(config, REGISTRY, left)
    explore(config, REGISTRY, right)
    expected = {
        "summary.json", "manifest.json",
        "difficulty_summary.csv", "accuracy_by_difficulty.svg",
    }
    assert {p.name for p in left.iterdir()} == expected
    for filename in sorted(expected):
        assert (left / filename).read_bytes() == (right / filename).read_bytes()
    svg = (left / "accuracy_by_difficulty.svg").read_text(encoding="utf-8")
    assert "Synthetic fixtures only" in svg
    assert "not human performance" in svg
