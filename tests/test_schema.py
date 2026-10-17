"""Fail-closed rights, source identity and feature timing schema regression tests."""

from __future__ import annotations

from dataclasses import replace

import pytest

from psychneuro.schema import validate_predictor_columns, validate_synthetic_dataset
from psychneuro.synthetic import SyntheticConfig, dataset_card, generate_trials


def _fixture() -> tuple[tuple[object, ...], dict[str, object]]:
    config = SyntheticConfig(seed=15, n_participants=3, trials_per_participant=4)
    records = generate_trials(config)
    card: dict[str, object] = dict(dataset_card(config, records))
    return records, card


def test_valid_synthetic_fixture_identity() -> None:
    records, card = _fixture()
    summary = validate_synthetic_dataset(records, card)  # type: ignore[arg-type]
    assert summary.n_participants == 3
    assert summary.n_sessions == 3
    assert summary.n_trials == 12
    assert summary.source_sha256 == card["source_sha256"]


@pytest.mark.parametrize(
    "key", ["synthetic", "source_kind", "rights_basis", "source_url_or_generator"]
)
def test_external_or_false_rights_fail_closed(key: str) -> None:
    records, card = _fixture()
    card[key] = False if key == "synthetic" else "external"
    with pytest.raises(ValueError, match="synthetic|unapproved|unknown"):
        validate_synthetic_dataset(records, card)  # type: ignore[arg-type]


def test_missing_rights_rejected() -> None:
    records, card = _fixture()
    del card["rights_basis"]
    with pytest.raises(ValueError, match="rights_basis"):
        validate_synthetic_dataset(records, card)  # type: ignore[arg-type]


def test_source_digest_tampering_rejected() -> None:
    records, card = _fixture()
    card["source_sha256"] = "a" * 64
    with pytest.raises(ValueError, match="checksum mismatch"):
        validate_synthetic_dataset(records, card)  # type: ignore[arg-type]


def test_card_group_count_tampering_rejected() -> None:
    records, card = _fixture()
    card["n_participants"] = 5
    with pytest.raises(ValueError, match="participant count"):
        validate_synthetic_dataset(records, card)  # type: ignore[arg-type]


def test_record_identity_tampering_rejected() -> None:
    records, card = _fixture()
    altered = list(records)
    altered[0] = replace(altered[0], generator_seed=456)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="seed|identity"):
        validate_synthetic_dataset(altered, card)  # type: ignore[arg-type]


def test_post_response_or_id_predictors_rejected() -> None:
    for col in ("correct", "response", "response_time_ms", "participant_id", "trial_id"):
        with pytest.raises(ValueError, match="forbidden"):
            validate_predictor_columns(("difficulty", col))


def test_only_pre_response_predictors_accepted() -> None:
    assert validate_predictor_columns(["stimulus_condition", "difficulty"]) == (
        "stimulus_condition",
        "difficulty",
    )


def test_missing_feature_availability_rejected() -> None:
    records, card = _fixture()
    card["feature_availability"] = {}
    with pytest.raises(ValueError, match="feature availability"):
        validate_synthetic_dataset(records, card)  # type: ignore[arg-type]


def test_false_safe_postresponse_declaration_rejected() -> None:
    records, card = _fixture()
    availability = dict(card["feature_availability"])  # type: ignore[arg-type]
    availability["response_time_ms"] = "pre-response"
    card["feature_availability"] = availability
    with pytest.raises(ValueError, match="forbidden post-outcome"):
        validate_synthetic_dataset(records, card)  # type: ignore[arg-type]


def test_duplicate_predictor_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        validate_predictor_columns(["difficulty", "difficulty"])


def test_missing_synthetic_attestation_rejected() -> None:
    records, card = _fixture()
    del card["synthetic"]
    with pytest.raises(ValueError, match="only synthetic"):
        validate_synthetic_dataset(records, card)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["difficulty", "response_time_ms"])
def test_boolean_numeric_feature_rejected(field: str) -> None:
    records, card = _fixture()
    altered = list(records)
    altered[0] = replace(altered[0], **{field: True})  # type: ignore[arg-type]
    with pytest.raises(ValueError, match=field):
        validate_synthetic_dataset(altered, card)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["difficulty", "response_time_ms"])
def test_integer_instead_of_float_feature_rejected(field: str) -> None:
    records, card = _fixture()
    altered = list(records)
    altered[0] = replace(altered[0], **{field: 1})  # type: ignore[arg-type]
    with pytest.raises(ValueError, match=field):
        validate_synthetic_dataset(altered, card)  # type: ignore[arg-type]
