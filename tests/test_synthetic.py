"""Provisional synthetic-generator contract tests for PsychNeuro OpenBench.

PM-03 isolated branch: tests are NOT VERIFIED or RUN, because PM-02 has not
committed its generator/API. The adapter below must be reconciled with the
real PM-02 implementation before this suite can be an acceptance gate.

Target: v0 proposed schema in docs/spec-v0.md; synthetic correctness
classification from pre-response features (nonclinical).
"""
from __future__ import annotations

import math
import random
from collections.abc import Mapping
from typing import Any

import pytest

REQUIRED_FIELDS = {
    "dataset_id",
    "participant_id",
    "session_id",
    "trial_id",
    "trial_order",
    "stimulus_condition",
    "difficulty",
    "correct",
}


def make_rows(
    *,
    seed: int = 123,
    participants: int = 4,
    trials: int = 6,
    conditions: tuple[str, ...] = ("easy", "hard"),
) -> list[Mapping[str, Any]]:
    """Integration seam: adapt the call signature to PM-02 before accepting CI."""
    try:
        from psychneuro.synthetic import generate_trials
    except ImportError as exc:
        pytest.fail(
            "PM-02 synthetic generator is not integrated; expected "
            "psychneuro.synthetic.generate_trials or an updated adapter: "
            f"{exc}",
            pytrace=False,
        )
    rows = list(
        generate_trials(
            seed=seed,
            n_participants=participants,
            trials_per_participant=trials,
            stimulus_conditions=conditions,
        )
    )
    assert all(isinstance(row, Mapping) for row in rows), (
        "Generator should yield mappings; update adapter if PM-02 uses typed records."
    )
    return rows


def test_same_seed_and_configuration_replay_exactly() -> None:
    assert make_rows(seed=71) == make_rows(seed=71)


def test_nontrivial_distinct_seeds_change_some_synthetic_output() -> None:
    assert make_rows(seed=71, participants=15, trials=30) != make_rows(
        seed=72, participants=15, trials=30
    )


def test_cardinality_and_composite_identity() -> None:
    rows = make_rows(participants=3, trials=5)
    assert len(rows) == 15
    assert len({row["participant_id"] for row in rows}) == 3
    keys = {
        (row["dataset_id"], row["participant_id"], row["session_id"], row["trial_id"])
        for row in rows
    }
    assert len(keys) == len(rows)


def test_required_schema_fields_present() -> None:
    rows = make_rows()
    assert rows
    for row in rows:
        assert REQUIRED_FIELDS <= row.keys()


def test_per_session_trial_order_is_positive_unique_integer() -> None:
    rows = make_rows()
    seen: set[tuple[object, object, object, int]] = set()
    for row in rows:
        order = row["trial_order"]
        assert isinstance(order, int) and not isinstance(order, bool)
        assert order >= 1
        key = (row["dataset_id"], row["participant_id"], row["session_id"], order)
        assert key not in seen
        seen.add(key)


def test_correct_is_binary_integer_not_boolean() -> None:
    for row in make_rows():
        assert type(row["correct"]) is int
        assert row["correct"] in (0, 1)


def test_difficulty_is_finite_pretrial_feature() -> None:
    for row in make_rows():
        value = row["difficulty"]
        assert isinstance(value, (int, float)) and not isinstance(value, bool)
        assert math.isfinite(value)


def test_condition_values_are_declared() -> None:
    assert {row["stimulus_condition"] for row in make_rows()} <= {"easy", "hard"}


def test_generating_rows_does_not_consume_global_random_state() -> None:
    before = random.getstate()
    make_rows(seed=303)
    assert random.getstate() == before


@pytest.mark.parametrize(
    ("participants", "trials"),
    [(0, 1), (-1, 1), (1, 0), (1, -2)],
)
def test_reject_nonpositive_counts(participants: int, trials: int) -> None:
    with pytest.raises((ValueError, TypeError)):
        make_rows(participants=participants, trials=trials)


def test_reject_empty_conditions() -> None:
    with pytest.raises((ValueError, TypeError)):
        make_rows(conditions=())


@pytest.mark.parametrize("seed", [True, "13", None])
def test_reject_seed_that_is_not_integer(seed: object) -> None:
    with pytest.raises((ValueError, TypeError)):
        make_rows(seed=seed)  # type: ignore[arg-type]


def test_minimal_valid_sample() -> None:
    rows = make_rows(participants=1, trials=1)
    assert len(rows) == 1
    assert REQUIRED_FIELDS <= rows[0].keys()
