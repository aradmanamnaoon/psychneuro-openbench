"""PM-03 additional tests for the actual PM-02 synthetic generator interface.

The generator is an engineering fixture for invented records, not an empirical
or clinical behavioral model. Real hosted CI results are still required.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
from dataclasses import replace

import pytest

from psychneuro.synthetic import (
    CSV_COLUMNS,
    SyntheticConfig,
    dataset_card,
    generate_trials,
    to_csv_text,
    validate_trials,
)


def test_generated_rows_match_normative_v0_field_order() -> None:
    config = SyntheticConfig(seed=103, n_participants=2, trials_per_participant=3)
    rows = list(csv.DictReader(io.StringIO(to_csv_text(generate_trials(config)))))
    assert len(rows) == 6
    assert tuple(rows[0].keys()) == CSV_COLUMNS
    assert all(row["dataset_id"] == config.dataset_id for row in rows)


def test_different_seeds_change_csv_and_source_digest() -> None:
    config_a = SyntheticConfig(seed=103, n_participants=3, trials_per_participant=12)
    config_b = replace(config_a, seed=104)
    records_a, records_b = generate_trials(config_a), generate_trials(config_b)
    assert to_csv_text(records_a) != to_csv_text(records_b)
    assert dataset_card(config_a, records_a)["source_sha256"] != dataset_card(
        config_b, records_b
    )["source_sha256"]


def test_dataset_card_hash_matches_exact_exported_utf8_bytes() -> None:
    config = SyntheticConfig(seed=105, n_participants=2, trials_per_participant=3)
    records = generate_trials(config)
    actual = hashlib.sha256(to_csv_text(records).encode("utf-8")).hexdigest()
    assert dataset_card(config, records)["source_sha256"] == actual
    assert dataset_card(config, records)["rights_basis"] == "synthetic-original"


def test_dataset_card_rejects_dataset_id_mismatch() -> None:
    config = SyntheticConfig(seed=106, n_participants=2, trials_per_participant=3)
    records = generate_trials(config)
    with pytest.raises(ValueError, match="declared"):
        dataset_card(replace(config, dataset_id="different-dataset"), records)


def test_dataset_card_rejects_missing_trials() -> None:
    config = SyntheticConfig(seed=107, n_participants=2, trials_per_participant=3)
    records = generate_trials(config)
    with pytest.raises(ValueError, match="do not match"):
        dataset_card(config, records[:-1])


def test_validation_rejects_noncontiguous_trial_orders() -> None:
    config = SyntheticConfig(seed=108, n_participants=1, trials_per_participant=4)
    records = generate_trials(config)
    with pytest.raises(ValueError, match="contiguous"):
        validate_trials((records[0], records[2]))


def test_validation_rejects_mixed_seeds() -> None:
    records = list(generate_trials(SyntheticConfig(seed=109, n_participants=1, trials_per_participant=3)))
    records[1] = replace(records[1], generator_seed=110)
    with pytest.raises(ValueError, match="one dataset_id and seed"):
        validate_trials(records)


def test_validation_rejects_unknown_stimulus_condition() -> None:
    records = list(generate_trials(SyntheticConfig(seed=111, n_participants=1, trials_per_participant=3)))
    records[0] = replace(records[0], stimulus_condition="unknown")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="choice"):
        validate_trials(records)


def test_validation_rejects_nonbinary_correctness() -> None:
    records = list(generate_trials(SyntheticConfig(seed=112, n_participants=1, trials_per_participant=3)))
    records[0] = replace(records[0], correct=2)
    with pytest.raises(ValueError, match="binary"):
        validate_trials(records)


def test_validation_rejects_nonfinite_difficulty_and_latency() -> None:
    records = list(generate_trials(SyntheticConfig(seed=113, n_participants=1, trials_per_participant=3)))
    records[0] = replace(records[0], difficulty=float("inf"))
    with pytest.raises(ValueError, match="difficulty"):
        validate_trials(records)
    records[0] = replace(records[0], difficulty=0.5, response_time_ms=float("nan"))
    with pytest.raises(ValueError, match="response_time_ms"):
        validate_trials(records)


def test_generated_latency_is_finite_positive_and_never_a_predictor() -> None:
    records = generate_trials(SyntheticConfig(seed=114, n_participants=2, trials_per_participant=4))
    assert all(math.isfinite(r.response_time_ms) and r.response_time_ms > 0 for r in records)
    card = dataset_card(SyntheticConfig(seed=114, n_participants=2, trials_per_participant=4), records)
    assert card["feature_availability"]["response_time_ms"].startswith("post-response")
    assert card["feature_availability"]["correct"].startswith("target")


@pytest.mark.parametrize("session", ["", "../traversal", "contains space", "é"])
def test_rejects_invalid_session_identifier(session: str) -> None:
    with pytest.raises(ValueError, match="session_id"):
        generate_trials(SyntheticConfig(session_id=session))
