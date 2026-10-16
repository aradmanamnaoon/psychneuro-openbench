"""Fixture/seed/schema assertions for the toy generator."""

from __future__ import annotations

import csv
import hashlib
import io
import math
import random
from collections import Counter
from dataclasses import FrozenInstanceError, asdict

import pytest

from psychneuro.synthetic import (
    MAX_ROWS,
    TrialRecord,
    generate_reaction_times,
    make_dataset_card,
    to_csv_bytes,
)


def test_default_size_matches_pm01_contract() -> None:
    assert len(generate_reaction_times(seed=42)) == 24 * 2 * 10


def test_same_seed_gives_equal_ordered_rows_and_bytes() -> None:
    a = generate_reaction_times(seed=417)
    b = generate_reaction_times(seed=417)
    assert a == b
    assert to_csv_bytes(a) == to_csv_bytes(b)


def test_other_seed_differs() -> None:
    assert generate_reaction_times(seed=1) != generate_reaction_times(seed=2)


def test_unique_composite_key_and_trial_order() -> None:
    rows = generate_reaction_times(seed=3, n_participants=3, n_sessions=2, trials_per_session=7)
    keys = [(r.dataset_id, r.participant_id, r.session_id, r.trial_id) for r in rows]
    assert len(set(keys)) == len(keys)
    for pid in {r.participant_id for r in rows}:
        for sid in {r.session_id for r in rows}:
            assert [r.trial_order for r in rows if r.participant_id == pid
                    and r.session_id == sid] == list(range(1, 8))


@pytest.mark.parametrize("n", [1, 2, 3, 9, 10, 11])
def test_condition_balance_per_participant_and_session(n: int) -> None:
    rows = generate_reaction_times(seed=19, n_participants=2, n_sessions=2, trials_per_session=n)
    for pid in {r.participant_id for r in rows}:
        for sid in {r.session_id for r in rows}:
            counts = Counter(r.stimulus_condition for r in rows if
                             r.participant_id == pid and r.session_id == sid)
            assert abs(counts["congruent"] - counts["incongruent"]) <= 1


def test_units_domains_and_no_missing_values() -> None:
    rows = generate_reaction_times(seed=24)
    assert all(isinstance(row, TrialRecord) for row in rows)
    assert all(math.isfinite(row.difficulty) and 0.0 <= row.difficulty <= 1.0
               for row in rows)
    assert all(math.isfinite(row.reaction_time_ms) and row.reaction_time_ms > 120.0
               for row in rows)
    assert {row.correct for row in rows} <= {0, 1}
    assert {row.seed for row in rows} == {24}
    assert all(row.participant_id.startswith("sub-") for row in rows)
    assert all((row.response == row.stimulus_side) == bool(row.correct) for row in rows)


def test_csv_is_utf8_lf_with_schema_order() -> None:
    rows = generate_reaction_times(seed=8, n_participants=1, n_sessions=1, trials_per_session=2)
    data = to_csv_bytes(rows)
    assert b"\r" not in data
    parsed = list(csv.DictReader(io.StringIO(data.decode("utf-8"))))
    assert len(parsed) == 2
    assert parsed[0]["dataset_id"] == rows[0].dataset_id
    assert parsed[0]["trial_order"] == "1"


def test_dataset_card_has_content_digest_and_rights() -> None:
    rows = generate_reaction_times(seed=7, n_participants=2, n_sessions=3, trials_per_session=4)
    card = make_dataset_card(rows)
    assert card["source_sha256"] == hashlib.sha256(to_csv_bytes(rows)).hexdigest()
    assert card["n_participants"] == 2
    assert card["n_sessions"] == 6
    assert card["n_trials"] == 24
    assert card["synthetic"] is True
    assert card["rights_basis"] == "synthetic-original"
    assert card["feature_availability"]["reaction_time_ms"] == "post-response-excluded"


def test_dataset_card_different_seed_changes_digest() -> None:
    assert (make_dataset_card(generate_reaction_times(seed=1))["source_sha256"]
            != make_dataset_card(generate_reaction_times(seed=2))["source_sha256"])


def test_no_global_rng_mutation() -> None:
    before = random.getstate()
    generate_reaction_times(seed=98)
    assert random.getstate() == before


def test_smallest_fixture_and_frozen_rows() -> None:
    row, = generate_reaction_times(seed=0, n_participants=1, n_sessions=1, trials_per_session=1)
    assert row.trial_order == 1
    assert asdict(row)["correct"] in (0, 1)
    with pytest.raises(FrozenInstanceError):
        row.seed = 7  # type: ignore[misc]


@pytest.mark.parametrize("seed", [-1, 2**32])
def test_bad_seed_range(seed: int) -> None:
    with pytest.raises(ValueError):
        generate_reaction_times(seed=seed)


@pytest.mark.parametrize("seed", [True, 1.0, "4", None])
def test_bad_seed_type(seed: object) -> None:
    with pytest.raises(TypeError):
        generate_reaction_times(seed=seed)  # type: ignore[arg-type]


@pytest.mark.parametrize("kwargs", [
    {"n_participants": 0}, {"n_participants": -1},
    {"n_sessions": 0}, {"trials_per_session": -2},
])
def test_nonpositive_size(kwargs: dict[str, int]) -> None:
    with pytest.raises(ValueError):
        generate_reaction_times(seed=4, **kwargs)


@pytest.mark.parametrize("kwargs", [
    {"n_participants": True}, {"n_sessions": 0.5}, {"trials_per_session": "5"},
])
def test_nonnumeric_size(kwargs: dict[str, object]) -> None:
    with pytest.raises(TypeError):
        generate_reaction_times(seed=4, **kwargs)  # type: ignore[arg-type]


def test_max_rows_guard() -> None:
    with pytest.raises(ValueError):
        generate_reaction_times(seed=8, n_participants=MAX_ROWS, n_sessions=2)


@pytest.mark.parametrize("dataset_id", ["", " space", "=FORMULA", "../bad", "⚡", "a" * 65])
def test_invalid_dataset_id(dataset_id: str) -> None:
    with pytest.raises(ValueError):
        generate_reaction_times(seed=0, dataset_id=dataset_id)


def test_card_rejects_empty_and_mixed_provenance() -> None:
    with pytest.raises(ValueError):
        make_dataset_card([])
    a = generate_reaction_times(seed=1, n_participants=1, n_sessions=1, trials_per_session=1)
    b = generate_reaction_times(seed=2, n_participants=1, n_sessions=1, trials_per_session=1)
    with pytest.raises(ValueError):
        make_dataset_card(a + b)
