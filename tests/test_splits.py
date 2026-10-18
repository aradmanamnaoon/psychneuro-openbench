"""PM-07 grouped-holdout contract tests; all fixtures are wholly fictional."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from psychneuro.loaders import LoadedDataset, load_dataset
from psychneuro.quality import DataQualityError
from psychneuro.schema import validate_predictor_columns
from psychneuro.split import create_group_split, validate_group_split
from psychneuro.synthetic import SyntheticConfig

REGISTRY = Path(__file__).resolve().parents[1] / "data" / "registry.json"


@pytest.fixture
def data() -> LoadedDataset:
    return load_dataset(
        SyntheticConfig(seed=73, n_participants=24, trials_per_participant=6),
        REGISTRY,
    )


def test_default_group_counts_and_complete_row_coverage(data: LoadedDataset) -> None:
    result = create_group_split(data, seed=42)
    assert tuple(map(len, (
        result.train_participants, result.validation_participants, result.test_participants
    ))) == (14, 5, 5)
    assert tuple(map(len, (
        result.train_indices, result.validation_indices, result.test_indices
    ))) == (84, 30, 30)
    assert sorted(
        result.train_indices + result.validation_indices + result.test_indices
    ) == list(range(len(data.records)))
    validate_group_split(data, result)


def test_no_participant_can_cross_boundaries(data: LoadedDataset) -> None:
    split = create_group_split(data)
    groups = (
        set(split.train_participants),
        set(split.validation_participants),
        set(split.test_participants),
    )
    assert not groups[0] & groups[1]
    assert not groups[0] & groups[2]
    assert not groups[1] & groups[2]
    assert groups[0] | groups[1] | groups[2] == {
        row.participant_id for row in data.records
    }


def test_split_is_repeatable_without_global_rng_state(data: LoadedDataset) -> None:
    first = create_group_split(data, seed=182)
    second = create_group_split(data, seed=182)
    assert first == second
    assert len(first.assignment_sha256) == 64


def test_shared_session_label_is_not_used_as_global_group(data: LoadedDataset) -> None:
    assert {row.session_id for row in data.records} == {"session-01"}
    split = create_group_split(data)
    assert split.train_indices and split.validation_indices and split.test_indices
    # Every session row is assigned by its owning participant.
    for indices, members in (
        (split.train_indices, split.train_participants),
        (split.validation_indices, split.validation_participants),
        (split.test_indices, split.test_participants),
    ):
        assert {data.records[i].participant_id for i in indices} == set(members)


def test_seed_selection_is_independent_of_synthetic_generator_seed(
    data: LoadedDataset,
) -> None:
    new_data = load_dataset(
        SyntheticConfig(seed=99, n_participants=24, trials_per_participant=6),
        REGISTRY,
    )
    first = create_group_split(data, seed=7)
    second = create_group_split(new_data, seed=7)
    assert first.train_participants == second.train_participants
    assert first.validation_participants == second.validation_participants
    assert first.test_participants == second.test_participants
    assert first.source_sha256 != second.source_sha256
    assert first.assignment_sha256 != second.assignment_sha256


@pytest.mark.parametrize("seed", [-1, 2**64, True, 0.5, "42"])
def test_invalid_split_seeds_rejected(data: LoadedDataset, seed: object) -> None:
    with pytest.raises(ValueError, match="split seed"):
        create_group_split(data, seed=seed)  # type: ignore[arg-type]


@pytest.mark.parametrize("subjects", [1, 2, 3, 6, 8])
def test_insufficient_groups_fail_explicitly(subjects: int) -> None:
    data = load_dataset(
        SyntheticConfig(seed=13, n_participants=subjects, trials_per_participant=3),
        REGISTRY,
    )
    with pytest.raises(ValueError, match="insufficient participants"):
        create_group_split(data)


def test_minimum_supported_nine_groups() -> None:
    data = load_dataset(
        SyntheticConfig(seed=13, n_participants=9, trials_per_participant=2), REGISTRY
    )
    split = create_group_split(data)
    assert (
        len(split.train_participants),
        len(split.validation_participants),
        len(split.test_participants),
    ) == (5, 2, 2)


def test_overlapping_participant_cannot_be_accepted(data: LoadedDataset) -> None:
    split = create_group_split(data)
    tampered = replace(
        split,
        validation_participants=(
            split.train_participants[0], *split.validation_participants[1:]
        ),
    )
    with pytest.raises(ValueError, match="participant leakage"):
        validate_group_split(data, tampered)


def test_repeated_participant_inside_partition_rejected(data: LoadedDataset) -> None:
    split = create_group_split(data)
    tampered = replace(
        split, test_participants=(
            split.test_participants[0], split.test_participants[0],
            *split.test_participants[2:],
        )
    )
    with pytest.raises(ValueError, match="duplicate participant"):
        validate_group_split(data, tampered)


def test_duplicate_row_index_across_partitions_rejected(data: LoadedDataset) -> None:
    split = create_group_split(data)
    tampered = replace(
        split, test_indices=(split.train_indices[0], *split.test_indices[1:])
    )
    with pytest.raises(ValueError, match="row leakage"):
        validate_group_split(data, tampered)


def test_missing_row_index_rejected(data: LoadedDataset) -> None:
    split = create_group_split(data)
    tampered = replace(split, validation_indices=split.validation_indices[:-1])
    with pytest.raises(ValueError, match="row leakage"):
        validate_group_split(data, tampered)


def test_swapped_rows_cannot_mask_subject_leakage(data: LoadedDataset) -> None:
    split = create_group_split(data)
    tampered = replace(
        split,
        train_indices=(split.test_indices[0], *split.train_indices[1:]),
        test_indices=(split.train_indices[0], *split.test_indices[1:]),
    )
    with pytest.raises(ValueError, match="row-to-participant"):
        validate_group_split(data, tampered)


def test_changed_digest_rejected(data: LoadedDataset) -> None:
    split = create_group_split(data)
    with pytest.raises(ValueError, match="digest mismatch"):
        validate_group_split(data, replace(split, assignment_sha256="0" * 64))


def test_changed_source_hash_or_dataset_rejected(data: LoadedDataset) -> None:
    split = create_group_split(data)
    with pytest.raises(ValueError, match="source hash mismatch"):
        validate_group_split(data, replace(split, source_sha256="0" * 64))
    with pytest.raises(ValueError, match="dataset"):
        validate_group_split(data, replace(split, dataset_id="another-dataset"))


def test_manifest_rejected_for_different_generator_input(data: LoadedDataset) -> None:
    split = create_group_split(data)
    other = load_dataset(
        SyntheticConfig(seed=74, n_participants=24, trials_per_participant=6),
        REGISTRY,
    )
    with pytest.raises(ValueError, match="source hash mismatch"):
        validate_group_split(other, split)


def test_altered_seed_membership_rejected(data: LoadedDataset) -> None:
    split = create_group_split(data, seed=42)
    with pytest.raises(ValueError, match="deterministic seeded assignment"):
        validate_group_split(data, replace(split, seed=43))


def test_duplicate_trial_record_fails_before_split(data: LoadedDataset) -> None:
    rows = list(data.records)
    rows[1] = rows[0]
    forged = replace(data, records=tuple(rows))
    with pytest.raises(DataQualityError):
        create_group_split(forged)


def test_modified_card_or_input_is_rejected(data: LoadedDataset) -> None:
    card = dict(data.card)
    card["rights_basis"] = "unknown"
    with pytest.raises(ValueError, match="synthetic rights basis"):
        create_group_split(replace(data, card=card))  # type: ignore[arg-type]


def test_pre_response_feature_gate_remains_strict() -> None:
    assert validate_predictor_columns(("difficulty", "stimulus_condition")) == (
        "difficulty", "stimulus_condition"
    )
    for unsafe in ("response", "response_time_ms", "correct", "participant_id"):
        with pytest.raises(ValueError, match="forbidden"):
            validate_predictor_columns(("difficulty", unsafe))
