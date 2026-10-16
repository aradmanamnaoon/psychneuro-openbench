"""PM-09 integration and adversarial configuration regression specifications.

All tests are written for future hosted CI; no test is claimed to have run.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest

from psychneuro.config import CONFIG_VERSION, load_baseline_config
from psychneuro.experiments import ExperimentConfig, run_experiment
from psychneuro.metrics import score_binary
from psychneuro.split import create_group_split
from psychneuro.loaders import load_dataset
from psychneuro.synthetic import SyntheticConfig

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "configs" / "baseline.json"
REGISTRY = REPO / "data" / "registry.json"


def _original() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(CONFIG.read_text(encoding="utf-8")))


def _write(tmp_path: Path, payload: dict[str, Any]) -> Path:
    output = tmp_path / "baseline.json"
    output.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return output


def test_versioned_baseline_is_accepted_and_checksum_is_stable(tmp_path: Path) -> None:
    first = load_baseline_config(CONFIG)
    second = load_baseline_config(CONFIG)
    assert first == second
    assert first.config_version == CONFIG_VERSION
    assert (first.generator_seed, first.split_seed, first.cv_folds) == (73, 42, 5)
    assert (first.n_participants, first.trials_per_participant) == (24, 20)
    assert len(first.config_sha256) == 64
    refmt = _write(tmp_path, _original())
    assert load_baseline_config(refmt).config_sha256 == first.config_sha256


@pytest.mark.parametrize(
    "field,value",
    [
        ("config_version", "psychneuro-baseline-v2"),
        ("source", "real_human"),
        ("metrics", {"primary": "accuracy", "secondary": "macro_f1", "labels": [0, 1]}),
        ("task", {"target": "correct", "predictors": ["response_time_ms"]}),
        ("selection", {"method": "choose_best_test"}),
    ],
)
def test_changed_protocol_is_rejected(tmp_path: Path, field: str, value: object) -> None:
    payload = _original()
    payload[field] = value
    with pytest.raises(ValueError, match="unsupported|protocol"):
        load_baseline_config(_write(tmp_path, payload))


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("dataset", "generator_seed", True),
        ("dataset", "generator_seed", -1),
        ("dataset", "generator_seed", 2**64),
        ("dataset", "n_participants", 8),
        ("dataset", "n_participants", 100_001),
        ("dataset", "trials_per_participant", 0),
        ("dataset", "trials_per_participant", 10_000),
        ("split", "seed", True),
        ("split", "seed", -1),
        ("split", "seed", 2**64),
        ("split", "cv_folds", 4),
        ("split", "method", "row_shuffle"),
    ],
)
def test_invalid_dimensions_and_split_rejected(
    tmp_path: Path, section: str, key: str, value: object
) -> None:
    payload = _original()
    payload[section][key] = value
    with pytest.raises(ValueError, match="integer|limit|unsupported|protocol"):
        load_baseline_config(_write(tmp_path, payload))


def test_unexpected_or_missing_key_rejected(tmp_path: Path) -> None:
    payload = _original()
    payload["dataset"]["participant_id"] = "real-patient"
    with pytest.raises(ValueError, match="unknown configuration keys"):
        load_baseline_config(_write(tmp_path, payload))
    del payload["dataset"]
    with pytest.raises(ValueError, match="unknown configuration keys"):
        load_baseline_config(_write(tmp_path, payload))


def test_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "dupe.json"
    path.write_text('{"config_version":"a","config_version":"b"}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate configuration key"):
        load_baseline_config(path)


def test_invalid_json_encoding_and_size_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_bytes(b"\xff")
    with pytest.raises(ValueError, match="UTF-8"):
        load_baseline_config(path)
    path.write_bytes(b" " * 16_385)
    with pytest.raises(ValueError, match="size limit"):
        load_baseline_config(path)


def test_missing_and_symlink_config_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="existing non-symlink"):
        load_baseline_config(tmp_path / "not-found.json")
    link = tmp_path / "linked.json"
    link.symlink_to(CONFIG)
    with pytest.raises(ValueError, match="non-symlink"):
        load_baseline_config(link)


def test_model_hyperparameters_are_not_silently_ignored(tmp_path: Path) -> None:
    payload = _original()
    payload["models"]["logistic_regression"]["C"] = 4.0
    with pytest.raises(ValueError, match="models.*protocol"):
        load_baseline_config(_write(tmp_path, payload))


def test_boolean_is_not_valid_class_label_or_prediction() -> None:
    with pytest.raises(ValueError, match="nonbinary"):
        score_binary([0, 1], [False, 1])  # type: ignore[list-item]


def test_versioned_config_is_recorded_in_manifest() -> None:
    cfg = load_baseline_config(CONFIG)
    config = ExperimentConfig(
        generator_seed=cfg.generator_seed,
        n_participants=cfg.n_participants,
        trials_per_participant=cfg.trials_per_participant,
        split_seed=cfg.split_seed,
        cv_folds=cfg.cv_folds,
        config_version=cfg.config_version,
        config_sha256=cfg.config_sha256,
    )
    result = run_experiment(config, REGISTRY)
    assert result["configuration"]["config_version"] == CONFIG_VERSION  # type: ignore[index]
    assert result["configuration"]["config_sha256"] == cfg.config_sha256  # type: ignore[index]
    integrity = dict(result)
    recorded = cast(str, integrity.pop("manifest_sha256"))
    canonical = json.dumps(integrity, sort_keys=True, separators=(",", ":"), allow_nan=False)
    assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == recorded


def test_holdout_subjects_disjoint_from_all_cv_rows() -> None:
    data = load_dataset(
        SyntheticConfig(seed=73, n_participants=24, trials_per_participant=20), REGISTRY
    )
    split = create_group_split(data, seed=42)
    result = run_experiment(ExperimentConfig(), REGISTRY)
    all_training = set(split.train_indices)
    all_val = set(split.validation_indices)
    all_test = set(split.test_indices)
    assert not (all_training & all_val or all_training & all_test or all_val & all_test)
    for fold in cast(list[dict[str, Any]], result["cv_folds"]):
        left = set(fold["train_indices"])
        right = set(fold["validation_indices"])
        assert not (left & right)
        assert left | right == all_training
        assert not (left | right) & (all_val | all_test)
    assert result["split"]["assignment_sha256"] == split.assignment_sha256  # type: ignore[index]


def test_cv_ineligible_never_exposes_holdout_scores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Force invalid CV truth coverage without reading test labels.
    import psychneuro.experiments as experiments

    calls: list[tuple[int, ...]] = []

    def artificial_bad_fold(
        name: object, data: object, fit: tuple[int, ...], evaluate: tuple[int, ...]
    ) -> object:
        calls.append(evaluate)
        return score_binary([0, 0], [0, 0])

    monkeypatch.setattr(experiments, "_fit_evaluate", artificial_bad_fold)
    result = run_experiment(ExperimentConfig(), REGISTRY)
    assert result["status"] == "ineligible"
    assert result["selected_model"] is None
    assert result["validation_metrics"] is None
    assert result["test_metrics"] is None
    assert len(calls) == 2  # one failing first fold per candidate
    split = cast(dict[str, Any], result["split"])
    training = set(split["train_indices"])
    assert all(set(x) <= training for x in calls)


def test_no_human_data_or_external_registry_enabled() -> None:
    config = load_baseline_config(CONFIG)
    assert config.config_version == CONFIG_VERSION
    data = load_dataset(
        SyntheticConfig(seed=config.generator_seed, n_participants=9, trials_per_participant=2),
        REGISTRY,
    )
    assert data.card["source_kind"] == "synthetic"
    assert data.card["rights_basis"] == "synthetic-original"
    assert data.provenance.raw_file_sha256 is None


def test_copying_config_does_not_change_reference_file(tmp_path: Path) -> None:
    reference = _original()
    cloned = copy.deepcopy(reference)
    cloned["dataset"]["generator_seed"] = 999
    alternate = load_baseline_config(_write(tmp_path, cloned))
    original = load_baseline_config(CONFIG)
    assert alternate.generator_seed == 999
    assert alternate.config_sha256 != original.config_sha256
