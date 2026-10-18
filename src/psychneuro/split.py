"""Deterministic, subject-held-out partitioning of validated synthetic trials.

The independent unit is the fictional participant, NOT a row or session label.
This module is a split/validation utility, not a fitted classifier or scoring API.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from typing import Literal

from .loaders import LoadedDataset
from .quality import validate_quality
from .schema import validate_synthetic_dataset

SplitName = Literal["train", "validation", "test"]
_METHOD = "participant-shuffle-v1"
_MAX_SEED = 2**64 - 1


@dataclass(frozen=True, slots=True)
class GroupSplit:
    """Frozen memberships plus row indices for a specific validated input hash."""

    dataset_id: str
    source_sha256: str
    seed: int
    method: str
    train_participants: tuple[str, ...]
    validation_participants: tuple[str, ...]
    test_participants: tuple[str, ...]
    train_indices: tuple[int, ...]
    validation_indices: tuple[int, ...]
    test_indices: tuple[int, ...]
    assignment_sha256: str


def _check_seed(seed: int) -> None:
    if type(seed) is not int or not 0 <= seed <= _MAX_SEED:
        raise ValueError("split seed must be an integer in [0, 2**64 - 1]")


def _validate_source(data: LoadedDataset) -> tuple[str, ...]:
    """Revalidate provenance and original data, not just a caller's dataclass."""
    validate_quality(data.records)
    checked = validate_synthetic_dataset(data.records, data.card)
    if data.schema != checked:
        raise ValueError("stale or inconsistent validated source metadata")
    if data.provenance.canonical_csv_sha256 != checked.source_sha256:
        raise ValueError("source manifest checksum mismatch")
    if (
        data.provenance.source_kind != "synthetic"
        or data.provenance.rights_basis != "synthetic-original"
        or not data.registry_entry.enabled
        or data.registry_entry.source_kind != "synthetic"
    ):
        raise ValueError("split requires an enabled, rights-cleared synthetic source")
    return tuple(sorted({row.participant_id for row in data.records}))


def _groups(
    participants: tuple[str, ...], seed: int
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Freeze counts by participants; preserve enough training groups for 5-fold CV."""
    _check_seed(seed)
    shuffled = list(participants)
    random.Random(seed).shuffle(shuffled)  # private RNG; never changes global state
    n_subjects = len(shuffled)
    n_test = max(2, math.ceil(n_subjects / 5))
    n_validation = max(2, math.ceil((n_subjects - n_test) / 4))
    if n_subjects - n_test - n_validation < 5:
        raise ValueError(
            "insufficient participants: require at least 5 train, "
            "2 validation and 2 test groups; default 5-fold CV is ineligible"
        )
    test = tuple(sorted(shuffled[:n_test]))
    validation = tuple(sorted(shuffled[n_test : n_test + n_validation]))
    train = tuple(sorted(shuffled[n_test + n_validation :]))
    return train, validation, test


def _digest(
    dataset_id: str,
    source_sha256: str,
    seed: int,
    train: tuple[str, ...],
    validation: tuple[str, ...],
    test: tuple[str, ...],
) -> str:
    payload = {
        "algorithm": _METHOD,
        "dataset_id": dataset_id,
        "source_sha256": source_sha256,
        "seed": seed,
        "groups": {"train": train, "validation": validation, "test": test},
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _indices(
    data: LoadedDataset,
    train: tuple[str, ...],
    validation: tuple[str, ...],
    test: tuple[str, ...],
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    by_subject: dict[str, SplitName] = {}
    partitions: tuple[tuple[SplitName, tuple[str, ...]], ...] = (
        ("train", train), ("validation", validation), ("test", test)
    )
    for name, subject_ids in partitions:
        for subject_id in subject_ids:
            if subject_id in by_subject:
                raise ValueError("participant leakage: group assigned twice")
            by_subject[subject_id] = name
    output: dict[SplitName, list[int]] = {"train": [], "validation": [], "test": []}
    for index, row in enumerate(data.records):
        assigned = by_subject.get(row.participant_id)
        if assigned is None:
            raise ValueError("unassigned participant")
        output[assigned].append(index)
    return tuple(output["train"]), tuple(output["validation"]), tuple(output["test"])


def create_group_split(data: LoadedDataset, *, seed: int = 42) -> GroupSplit:
    """Create a deterministic ~60/20/20 group split for an approved synthetic dataset.

    Test participants are chosen first. Validation participants come from the
    remaining pool. The fractions count distinct participants, not trial rows.
    Nothing in this function reads or optimizes outcomes from the held-out sets.
    """
    _check_seed(seed)
    participants = _validate_source(data)
    train, validation, test = _groups(participants, seed)
    train_idx, validation_idx, test_idx = _indices(data, train, validation, test)
    split = GroupSplit(
        dataset_id=data.schema.dataset_id,
        source_sha256=data.schema.source_sha256,
        seed=seed,
        method=_METHOD,
        train_participants=train,
        validation_participants=validation,
        test_participants=test,
        train_indices=train_idx,
        validation_indices=validation_idx,
        test_indices=test_idx,
        assignment_sha256=_digest(
            data.schema.dataset_id, data.schema.source_sha256, seed, train, validation, test
        ),
    )
    validate_group_split(data, split)
    return split


def validate_group_split(data: LoadedDataset, split: GroupSplit) -> None:
    """Fail closed on subject overlap, row leakage, altered membership and stale input."""
    participants = _validate_source(data)
    _check_seed(split.seed)
    if (
        split.method != _METHOD
        or split.dataset_id != data.schema.dataset_id
        or split.source_sha256 != data.schema.source_sha256
    ):
        raise ValueError("split algorithm, dataset or source hash mismatch")
    grouped = (
        split.train_participants, split.validation_participants, split.test_participants
    )
    sets = tuple(set(groups) for groups in grouped)
    if any(len(groups) != len(members) for groups, members in zip(grouped, sets, strict=True)):
        raise ValueError("duplicate participant inside split")
    if sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2]:
        raise ValueError("participant leakage across partitions")
    if sets[0] | sets[1] | sets[2] != set(participants):
        raise ValueError("missing or unknown participant in split")
    expected_groups = _groups(participants, split.seed)
    if grouped != expected_groups:
        raise ValueError("membership is not the deterministic seeded assignment")
    expected_indices = _indices(data, *expected_groups)
    actual_indices = (
        split.train_indices, split.validation_indices, split.test_indices
    )
    indices = [i for group in actual_indices for i in group]
    if any(type(i) is not int for i in indices):
        raise ValueError("split indices must be integers")
    if len(indices) != len(data.records) or set(indices) != set(range(len(data.records))):
        raise ValueError("row leakage, duplication or omitted trial in split")
    if actual_indices != expected_indices:
        raise ValueError("row-to-participant partition mapping mismatch")
    if split.assignment_sha256 != _digest(
        split.dataset_id, split.source_sha256, split.seed, *expected_groups
    ):
        raise ValueError("split assignment digest mismatch")
