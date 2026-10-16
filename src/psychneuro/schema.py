"""Fail-closed metadata and predictor contract for *synthetic* v0 trials.

Does not import, download or process any real participant dataset.
Candidate external datasets stay disabled regardless of their posted licenses.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .synthetic import SCHEMA_VERSION, TrialRecord, to_csv_text, validate_trials

_ALLOWED_PREDICTORS = frozenset({"difficulty", "stimulus_condition"})
_REQUIRED_STRINGS = (
    "dataset_id",
    "title",
    "source_kind",
    "source_url_or_generator",
    "generator_revision",
    "source_sha256",
    "rights_basis",
    "usage_limitations",
    "target_definition",
)
_REQUIRED_COUNTS = ("generator_seed", "n_participants", "n_sessions", "n_trials")
_REQUIRED_RECORD_FIELDS = frozenset(
    {
        "dataset_id",
        "participant_id",
        "session_id",
        "trial_id",
        "trial_order",
        "stimulus_condition",
        "difficulty",
        "correct",
        "response",
        "response_time_ms",
        "generator_seed",
    }
)


@dataclass(frozen=True, slots=True)
class ValidatedDataset:
    """Recorded input identity, not permission to conduct a human study."""

    dataset_id: str
    n_participants: int
    n_sessions: int
    n_trials: int
    source_sha256: str


def validate_predictor_columns(columns: Sequence[str]) -> tuple[str, ...]:
    """Only the two approved pre-response synthetic fields may be predictors."""
    if not columns or any(not isinstance(col, str) for col in columns):
        raise ValueError("predictor columns must be nonempty strings")
    if len(set(columns)) != len(columns):
        raise ValueError("duplicate predictor column")
    rejected = set(columns).difference(_ALLOWED_PREDICTORS)
    if rejected:
        raise ValueError(
            "forbidden or unknown predictor(s): " + ", ".join(sorted(rejected))
        )
    return tuple(columns)


def _required_string(card: Mapping[str, object], name: str) -> str:
    value = card.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing/invalid {name} in dataset card")
    return value


def _required_int(card: Mapping[str, object], name: str, *, allow_zero: bool = False) -> int:
    value = card.get(name)
    if type(value) is not int:
        raise ValueError(f"missing/invalid integer {name} in dataset card")
    if value < 0 if allow_zero else value <= 0:
        raise ValueError(f"invalid count {name} in dataset card")
    return value


def validate_synthetic_dataset(
    records: Sequence[TrialRecord],
    card: Mapping[str, object],
) -> ValidatedDataset:
    """Validate source rights, field-time policy and exact serialized input identity.

    This is a strict internal v0 contract, not a general-purpose external loader.
    An input labeled external, real, restricted or unlicensed MUST be rejected.
    """
    validate_trials(records)
    if _required_string(card, "schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported schema_version")
    for key in _REQUIRED_STRINGS:
        _required_string(card, key)
    if card.get("synthetic") is not True:
        raise ValueError("only synthetic records are permitted in v0")
    if card["source_kind"] != "synthetic" or card["rights_basis"] != "synthetic-original":
        raise ValueError("unapproved source or missing synthetic rights basis")
    if card["source_url_or_generator"] != "psychneuro.synthetic.generate_trials":
        raise ValueError("unknown generator origin; external ingestion disabled")
    if card["generator_revision"] != SCHEMA_VERSION:
        raise ValueError("unsupported generator revision")

    seed = _required_int(card, "generator_seed", allow_zero=True)
    n_participants = _required_int(card, "n_participants")
    n_sessions = _required_int(card, "n_sessions")
    n_trials = _required_int(card, "n_trials")
    dataset_id = _required_string(card, "dataset_id")
    if dataset_id != records[0].dataset_id or any(
        rec.dataset_id != dataset_id or rec.generator_seed != seed for rec in records
    ):
        raise ValueError("record/card identity or seed mismatch")
    if len(records) != n_trials:
        raise ValueError("record/card trial count mismatch")
    if len({rec.participant_id for rec in records}) != n_participants:
        raise ValueError("record/card participant count mismatch")
    if len({(rec.participant_id, rec.session_id) for rec in records}) != n_sessions:
        raise ValueError("record/card session count mismatch")

    definitions = card.get("field_definitions")
    if not isinstance(definitions, Mapping) or not all(
        isinstance(definitions.get(col), str) and definitions.get(col)
        for col in ("stimulus_condition", "difficulty", "correct", "response", "response_time_ms")
    ):
        raise ValueError("missing field definitions")
    availability = card.get("feature_availability")
    if not isinstance(availability, Mapping) or not all(
        isinstance(availability.get(col), str) and availability.get(col)
        for col in _REQUIRED_RECORD_FIELDS.intersection(
            {"stimulus_condition", "difficulty", "correct", "response", "response_time_ms"}
        )
    ):
        raise ValueError("missing feature availability declarations")
    for col in _ALLOWED_PREDICTORS:
        declaration = availability.get(col)
        if not isinstance(declaration, str) or not declaration.startswith("pre-response"):
            raise ValueError(f"pre-response predictor declaration missing: {col}")
    for col, required_prefix in (
        ("correct", "target"),
        ("response", "post-response"),
        ("response_time_ms", "post-response"),
    ):
        declaration = availability.get(col)
        if not isinstance(declaration, str) or not declaration.startswith(required_prefix):
            raise ValueError(f"forbidden post-outcome field marked safe: {col}")

    digest = _required_string(card, "source_sha256")
    if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("invalid source_sha256")
    actual = hashlib.sha256(to_csv_text(records).encode("utf-8")).hexdigest()
    if actual != digest:
        raise ValueError("CSV data checksum mismatch")
    transforms = card.get("transforms")
    if transforms != []:
        raise ValueError("unapproved transforms in synthetic v0 card")
    return ValidatedDataset(
        dataset_id=dataset_id,
        n_participants=n_participants,
        n_sessions=n_sessions,
        n_trials=n_trials,
        source_sha256=digest,
    )
