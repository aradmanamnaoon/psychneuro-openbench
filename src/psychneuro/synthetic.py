"""Reproducible, entirely fictional behavioral trials.

The values are a software test fixture, not estimates of human behavior.
The response, response time and correctness become available after each trial:
do not use any of them to predict pre-response correctness.
"""

from __future__ import annotations

import csv
import hashlib
import io
import math
import random
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Literal, TypedDict

Side = Literal["left", "right"]

CSV_COLUMNS = (
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
)
SCHEMA_VERSION = "0.1.0"
MAX_TRIALS = 100_000


@dataclass(frozen=True, slots=True)
class SyntheticConfig:
    """Seeded generation settings; all records are nonclinical and invented."""

    seed: int = 42
    n_participants: int = 24
    trials_per_participant: int = 20
    dataset_id: str = "psychneuro-synthetic-v0"
    session_id: str = "session-01"


@dataclass(frozen=True, slots=True)
class TrialRecord:
    dataset_id: str
    participant_id: str
    session_id: str
    trial_id: str
    trial_order: int
    stimulus_condition: Side
    difficulty: float
    correct: int
    response: Side
    response_time_ms: float
    generator_seed: int


class DatasetCard(TypedDict):
    schema_version: str
    dataset_id: str
    title: str
    source_kind: str
    source_url_or_generator: str
    generator_revision: str
    source_sha256: str
    rights_basis: str
    usage_limitations: str
    synthetic: bool
    generator_seed: int
    n_participants: int
    n_sessions: int
    n_trials: int
    field_definitions: dict[str, str]
    target_definition: str
    feature_availability: dict[str, str]
    transforms: list[str]


def _check_config(config: SyntheticConfig) -> None:
    if type(config.seed) is not int or not (0 <= config.seed <= 2**64 - 1):
        raise ValueError("seed must be a nonnegative integer within 64 bits")
    for field, value in (
        ("n_participants", config.n_participants),
        ("trials_per_participant", config.trials_per_participant),
    ):
        if type(value) is not int or value <= 0:
            raise ValueError(f"{field} must be a positive integer")
    if config.n_participants * config.trials_per_participant > MAX_TRIALS:
        raise ValueError(f"generated trial count may not exceed {MAX_TRIALS}")
    for identifier_name, identifier in (
        ("dataset_id", config.dataset_id),
        ("session_id", config.session_id),
    ):
        if not isinstance(identifier, str) or re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", identifier
        ) is None:
            raise ValueError(f"{identifier_name} must be a short nonempty ASCII identifier")


def generate_trials(config: SyntheticConfig | None = None) -> tuple[TrialRecord, ...]:
    """Create repeatable toy choices using a local RNG, without global RNG state."""
    if config is None:
        config = SyntheticConfig()
    _check_config(config)
    rng = random.Random(config.seed)
    trials: list[TrialRecord] = []
    for participant_index in range(1, config.n_participants + 1):
        participant_id = f"synthetic-{participant_index:05d}"
        synthetic_ability = rng.uniform(-0.10, 0.10)
        for trial_order in range(1, config.trials_per_participant + 1):
            condition: Side = "left" if trial_order % 2 else "right"
            difficulty = round(0.2 + 0.2 * ((trial_order - 1) % 4), 2)
            probability = max(0.05, min(0.95, 0.86 - 0.35 * difficulty + synthetic_ability))
            correct = int(rng.random() < probability)
            response: Side = condition if correct else ("right" if condition == "left" else "left")
            latency = round(
                400.0 + difficulty * 280.0 + rng.uniform(0.0, 150.0) + 40.0 * (1 - correct),
                3,
            )
            trials.append(
                TrialRecord(
                    dataset_id=config.dataset_id,
                    participant_id=participant_id,
                    session_id=config.session_id,
                    trial_id=f"trial-{trial_order:05d}",
                    trial_order=trial_order,
                    stimulus_condition=condition,
                    difficulty=difficulty,
                    correct=correct,
                    response=response,
                    response_time_ms=latency,
                    generator_seed=config.seed,
                )
            )
    output = tuple(trials)
    validate_trials(output)
    return output


def validate_trials(records: Sequence[TrialRecord]) -> None:
    """Fail closed for invalid trial keys, values, and post-response consistency."""
    if not records:
        raise ValueError("no trial records")
    dataset_ids: set[str] = set()
    keys: set[tuple[str, str, str, str]] = set()
    orders: dict[tuple[str, str, str], set[int]] = {}
    seeds: set[int] = set()
    for row in records:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (row.dataset_id, row.participant_id, row.session_id, row.trial_id)
        ):
            raise ValueError("empty dataset/participant/session/trial identifier")
        key = (row.dataset_id, row.participant_id, row.session_id, row.trial_id)
        if key in keys:
            raise ValueError("duplicate composite trial key")
        keys.add(key)
        dataset_ids.add(row.dataset_id)
        seeds.add(row.generator_seed)
        if type(row.trial_order) is not int or row.trial_order <= 0:
            raise ValueError("trial_order must be positive integer")
        group = (row.dataset_id, row.participant_id, row.session_id)
        group_orders = orders.setdefault(group, set())
        if row.trial_order in group_orders:
            raise ValueError("duplicate trial order within session")
        group_orders.add(row.trial_order)
        if row.stimulus_condition not in ("left", "right") or row.response not in (
            "left", "right"
        ):
            raise ValueError("choice must be left or right")
        if type(row.correct) is not int or row.correct not in (0, 1):
            raise ValueError("correct must be binary integer")
        if row.correct != int(row.response == row.stimulus_condition):
            raise ValueError("response disagrees with correctness")
        if type(row.difficulty) is not float or not math.isfinite(
            row.difficulty
        ) or not 0.0 <= row.difficulty <= 1.0:
            raise ValueError("difficulty must be finite in [0, 1]")
        if type(row.response_time_ms) is not float or not math.isfinite(
            row.response_time_ms
        ) or row.response_time_ms <= 0.0:
            raise ValueError("response_time_ms must be positive finite milliseconds")
        if type(row.generator_seed) is not int or not 0 <= row.generator_seed <= 2**64 - 1:
            raise ValueError("invalid generator seed")
    if len(dataset_ids) != 1 or len(seeds) != 1:
        raise ValueError("a generated dataset must have one dataset_id and seed")
    for group_orders in orders.values():
        if sorted(group_orders) != list(range(1, len(group_orders) + 1)):
            raise ValueError("trial orders must start at 1 and be contiguous")


def to_csv_text(records: Sequence[TrialRecord]) -> str:
    """Serialize canonical UTF-8-friendly CSV with LF newlines and stable columns."""
    validate_trials(records)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in records:
        writer.writerow(asdict(row))
    return output.getvalue()


def dataset_card(config: SyntheticConfig, records: Sequence[TrialRecord]) -> DatasetCard:
    """Build the source rights card and exact SHA-256 of serialized CSV bytes."""
    _check_config(config)
    if len(records) != config.n_participants * config.trials_per_participant:
        raise ValueError("records do not match generator configuration")
    if any(
        row.dataset_id != config.dataset_id
        or row.session_id != config.session_id
        or row.generator_seed != config.seed
        for row in records
    ):
        raise ValueError("records do not match declared dataset/session/seed")
    if len({row.participant_id for row in records}) != config.n_participants:
        raise ValueError("participant count does not match configuration")
    canonical_csv = to_csv_text(records).encode("utf-8")
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset_id": config.dataset_id,
        "title": "Entirely synthetic two-choice response task",
        "source_kind": "synthetic",
        "source_url_or_generator": "psychneuro.synthetic.generate_trials",
        "generator_revision": SCHEMA_VERSION,
        "source_sha256": hashlib.sha256(canonical_csv).hexdigest(),
        "rights_basis": "synthetic-original",
        "usage_limitations": "Engineering-only synthetic demo; not real behavioral evidence",
        "synthetic": True,
        "generator_seed": config.seed,
        "n_participants": config.n_participants,
        "n_sessions": config.n_participants,
        "n_trials": len(records),
        "field_definitions": {
            "stimulus_condition": "Synthetic displayed left/right cue",
            "difficulty": "Pretrial artificial number, unitless 0..1",
            "response": "Artificial chosen side after trial",
            "response_time_ms": "Artificial latency in milliseconds, post-response",
            "correct": "Binary correctness derived from synthetic response",
        },
        "target_definition": "correct (0 or 1); not a clinical or human outcome",
        "feature_availability": {
            "stimulus_condition": "pre-response; permitted predictor",
            "difficulty": "pre-response; permitted predictor",
            "response": "post-response; prohibited predictor",
            "response_time_ms": "post-response; prohibited predictor",
            "correct": "target; prohibited predictor",
            "participant_id": "group identifier only; prohibited predictor",
            "trial_id": "identifier only; prohibited predictor",
        },
        "transforms": [],
    }
