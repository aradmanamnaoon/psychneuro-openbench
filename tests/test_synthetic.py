"""Authored acceptance tests; no execution result is implied by this file."""

from dataclasses import replace
import csv
import hashlib
import io
import math
import random

import pytest

from psychneuro.synthetic import (
    MAX_TRIALS,
    SyntheticConfig,
    dataset_card,
    generate_trials,
    to_csv_text,
    validate_trials,
)


def test_shape_ids_and_contiguous_orders() -> None:
    records = generate_trials(SyntheticConfig(seed=11, n_participants=4, trials_per_participant=8))
    assert len(records) == 32
    assert len({row.participant_id for row in records}) == 4
    assert len({(r.participant_id, r.session_id, r.trial_id) for r in records}) == 32
    for participant_id in {r.participant_id for r in records}:
        assert [r.trial_order for r in records if r.participant_id == participant_id] == list(
            range(1, 9)
        )


def test_same_seed_gives_identical_records_and_csv() -> None:
    config = SyntheticConfig(seed=44)
    assert generate_trials(config) == generate_trials(config)
    assert to_csv_text(generate_trials(config)) == to_csv_text(generate_trials(config))


def test_different_seed_changes_records() -> None:
    left = generate_trials(SyntheticConfig(seed=1))
    right = generate_trials(SyntheticConfig(seed=2))
    assert left != right


def test_does_not_mutate_global_rng() -> None:
    random.seed(889)
    state = random.getstate()
    generate_trials(SyntheticConfig(seed=889))
    assert random.getstate() == state


def test_all_trials_are_fictional_consistent_and_finite() -> None:
    records = generate_trials()
    assert all(r.participant_id.startswith("synthetic-") for r in records)
    assert all(r.correct == int(r.response == r.stimulus_condition) for r in records)
    assert all(math.isfinite(r.response_time_ms) and r.response_time_ms > 0 for r in records)
    assert all(0.0 <= r.difficulty <= 1.0 for r in records)
    assert {r.stimulus_condition for r in records} == {"left", "right"}


@pytest.mark.parametrize("seed", [-1, True, 1.5, "3", 2**64])
def test_seed_rejection(seed: object) -> None:
    with pytest.raises(ValueError, match="seed"):
        generate_trials(SyntheticConfig(seed=seed))  # type: ignore[arg-type]


@pytest.mark.parametrize("n_participants,trials", [(0, 2), (2, 0), (-1, 1), (2, -1), (True, 2)])
def test_invalid_sizes(n_participants: object, trials: object) -> None:
    with pytest.raises(ValueError):
        generate_trials(SyntheticConfig(n_participants=n_participants, trials_per_participant=trials))  # type: ignore[arg-type]


def test_memory_bound() -> None:
    with pytest.raises(ValueError, match="exceed"):
        generate_trials(SyntheticConfig(n_participants=MAX_TRIALS, trials_per_participant=2))


@pytest.mark.parametrize("identifier", ["", "bad space", "../escape", "é"])
def test_invalid_dataset_id(identifier: str) -> None:
    with pytest.raises(ValueError, match="dataset_id"):
        generate_trials(SyntheticConfig(dataset_id=identifier))


def test_reject_duplicate_trial_key() -> None:
    records = list(generate_trials(SyntheticConfig(n_participants=2, trials_per_participant=4)))
    records[1] = replace(records[1], trial_id=records[0].trial_id)
    with pytest.raises(ValueError, match="duplicate composite"):
        validate_trials(records)


def test_reject_wrong_response_correctness() -> None:
    records = list(generate_trials(SyntheticConfig(n_participants=1, trials_per_participant=4)))
    records[0] = replace(records[0], correct=1 - records[0].correct)
    with pytest.raises(ValueError, match="disagrees"):
        validate_trials(records)


@pytest.mark.parametrize("bad_latency", [0.0, -2.0, float("inf"), float("nan")])
def test_reject_bad_latency(bad_latency: float) -> None:
    records = list(generate_trials(SyntheticConfig(n_participants=1, trials_per_participant=4)))
    records[0] = replace(records[0], response_time_ms=bad_latency)
    with pytest.raises(ValueError, match="response_time_ms"):
        validate_trials(records)


def test_reject_bad_trial_order() -> None:
    records = list(generate_trials(SyntheticConfig(n_participants=1, trials_per_participant=4)))
    records[0] = replace(records[0], trial_order=2)
    with pytest.raises(ValueError, match="duplicate trial order"):
        validate_trials(records)


def test_csv_and_card_digest_match_source_bytes() -> None:
    config = SyntheticConfig(seed=3, n_participants=3, trials_per_participant=4)
    records = generate_trials(config)
    csv_text = to_csv_text(records)
    parsed = list(csv.DictReader(io.StringIO(csv_text)))
    card = dataset_card(config, records)
    assert len(parsed) == 12
    assert card["source_sha256"] == hashlib.sha256(csv_text.encode("utf-8")).hexdigest()
    assert card["source_kind"] == "synthetic" and card["synthetic"] is True
    assert card["n_participants"] == 3


def test_card_rejects_wrong_source_config() -> None:
    config = SyntheticConfig(seed=3, n_participants=1, trials_per_participant=2)
    records = generate_trials(config)
    with pytest.raises(ValueError, match="declared"):
        dataset_card(replace(config, seed=4), records)


def test_empty_records_rejected() -> None:
    with pytest.raises(ValueError, match="no trial"):
        validate_trials([])


def test_trial_value_validation_rejects_nan_difficulty() -> None:
    records = list(generate_trials(SyntheticConfig(n_participants=1, trials_per_participant=2)))
    records[0] = replace(records[0], difficulty=float("nan"))
    with pytest.raises(ValueError, match="difficulty"):
        validate_trials(records)
