"""Synthetic, nonclinical behavioral choice-task data.

The parameters here are arbitrary demonstration parameters, not estimates of
human reaction time, cognition, behavior, or diagnosis. The synthetic binary
target is correctness; difficulty and condition are pre-response predictors.

Reproducibility: a separate random.Random(seed) is created for every call.
Results are deterministic on a pinned Python/runtime/source revision.
Random sampling implementation details are not guaranteed across versions.
"""

from __future__ import annotations

import csv
import hashlib
import io
import math
import random
import re
from dataclasses import asdict, dataclass, fields
from typing import Literal, TypeAlias

Condition: TypeAlias = Literal["congruent", "incongruent"]
Side: TypeAlias = Literal["left", "right"]

SCHEMA_VERSION = "0.0.1-draft"
GENERATOR_REVISION = "pm-02-v0.0.1"
MAX_ROWS = 100_000
_DATASET_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")


@dataclass(frozen=True, slots=True)
class TrialRecord:
    """One wholly invented trial; IDs are synthetic opaque labels."""

    dataset_id: str
    participant_id: str
    session_id: str
    trial_id: str
    trial_order: int
    stimulus_condition: Condition
    difficulty: float
    stimulus_side: Side
    response: Side
    correct: int
    reaction_time_ms: float
    seed: int


def generate_reaction_times(
    *,
    seed: int,
    n_participants: int = 24,
    n_sessions: int = 2,
    trials_per_session: int = 10,
    dataset_id: str = "synthetic-rt-v0",
) -> list[TrialRecord]:
    """Generate reproducible, balanced trial-level synthetic example records.

    Generates n_participants * n_sessions * trials_per_session rows, bounded
    to MAX_ROWS. trial_order restarts at 1 within each participant/session.
    Conditions are balanced within one per participant/session.

    Simulated correctness probabilities and reaction-time parameters are
    invented; do not use generated scores as cognitive or clinical evidence.
    """
    if type(seed) is not int:
        raise TypeError("seed must be an int, not a bool")
    if not 0 <= seed < 2**32:
        raise ValueError("seed must be in [0, 2**32 - 1]")

    for name, value in (
        ("n_participants", n_participants),
        ("n_sessions", n_sessions),
        ("trials_per_session", trials_per_session),
    ):
        if type(value) is not int:
            raise TypeError(f"{name} must be an int, not a bool")
        if value <= 0:
            raise ValueError(f"{name} must be positive")

    if (
        n_participants * n_sessions * trials_per_session > MAX_ROWS
    ):
        raise ValueError(f"at most {MAX_ROWS} rows may be generated per call")

    if not isinstance(dataset_id, str):
        raise TypeError("dataset_id must be a string")
    if not _DATASET_ID_PATTERN.fullmatch(dataset_id):
        raise ValueError("dataset_id must be 1-64 safe ASCII token characters")

    rng = random.Random(seed)
    rows: list[TrialRecord] = []

    for participant_index in range(1, n_participants + 1):
        participant_id = f"sub-{participant_index:04d}"
        participant_shift = rng.gauss(0.0, 0.10)

        for session_index in range(1, n_sessions + 1):
            session_id = f"ses-{session_index:02d}"
            n_a = trials_per_session // 2
            conditions: list[Condition] = (
                ["congruent"] * n_a
                + ["incongruent"] * (trials_per_session - n_a)
            )
            rng.shuffle(conditions)

            for trial_order, condition in enumerate(conditions, start=1):
                # Available before the response: a declared, invented difficulty.
                difficulty = rng.randrange(101) / 100.0
                stimulus_side: Side = (
                    "left" if rng.random() < 0.5 else "right"
                )
                probability_correct = (
                    0.94
                    - (0.09 if condition == "incongruent" else 0.0)
                    - 0.08 * difficulty
                )
                correct = int(rng.random() < probability_correct)
                response: Side = (
                    stimulus_side
                    if correct
                    else ("right" if stimulus_side == "left" else "left")
                )

                # Post-response diagnostic field; NEVER train using this value.
                log_delay = (
                    math.log(320.0)
                    + participant_shift
                    + (0.10 if condition == "incongruent" else 0.0)
                    + 0.20 * difficulty
                    + rng.gauss(0.0, 0.22)
                )
                reaction_time_ms = 120.0 + math.exp(log_delay)
                if not math.isfinite(reaction_time_ms):
                    raise ArithmeticError("non-finite generated reaction time")

                rows.append(
                    TrialRecord(
                        dataset_id=dataset_id,
                        participant_id=participant_id,
                        session_id=session_id,
                        trial_id=f"tr-{trial_order:04d}",
                        trial_order=trial_order,
                        stimulus_condition=condition,
                        difficulty=difficulty,
                        stimulus_side=stimulus_side,
                        response=response,
                        correct=correct,
                        reaction_time_ms=reaction_time_ms,
                        seed=seed,
                    )
                )

    return rows


def to_csv_bytes(rows: list[TrialRecord]) -> bytes:
    """Serialize ordered records to UTF-8 CSV with LF line endings.

    Floats use Python's canonical str(float) representation on the current
    runtime. This format is deterministic for a pinned Python version;
    it is not claimed version-independent.
    """
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=[field.name for field in fields(TrialRecord)],
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(asdict(row))
    return output.getvalue().encode("utf-8")


def make_dataset_card(rows: list[TrialRecord]) -> dict[str, object]:
    """Return a rights-clear, provenance-linked synthetic dataset card.

    This is a draft PM-02 contract. Its field-level semantics require PM-01
    review before becoming a frozen schema; no real data are ingested.
    """
    if not rows:
        raise ValueError("cannot create a card for an empty dataset")
    dataset_ids = {row.dataset_id for row in rows}
    seeds = {row.seed for row in rows}
    if len(dataset_ids) != 1 or len(seeds) != 1:
        raise ValueError("all records must have one dataset_id and seed")

    participants = {row.participant_id for row in rows}
    sessions = {(row.participant_id, row.session_id) for row in rows}
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset_id": rows[0].dataset_id,
        "title": "Fictional nonclinical choice-task trial example",
        "source_kind": "synthetic",
        "source_url_or_generator": "psychneuro.synthetic.generate_reaction_times",
        "generator_revision": GENERATOR_REVISION,
        "source_sha256": hashlib.sha256(to_csv_bytes(rows)).hexdigest(),
        "rights_basis": "synthetic-original",
        "usage_limitations": (
            "Toy demonstration only; no human/clinical validity or inference"
        ),
        "synthetic": True,
        "generator_seed": rows[0].seed,
        "n_participants": len(participants),
        "n_sessions": len(sessions),
        "n_trials": len(rows),
        "field_definitions": {
            "dataset_id": "synthetic dataset name; string",
            "participant_id": "invented participant group label; string",
            "session_id": "invented session label within participant; string",
            "trial_id": "trial key within participant/session; string",
            "trial_order": "1-based trial number in session; integer",
            "stimulus_condition": "congruent or incongruent; categorical",
            "difficulty": "invented pre-response difficulty [0,1]; float",
            "stimulus_side": "invented pre-response side; categorical",
            "response": "invented post-response side; categorical",
            "correct": "invented binary outcome 0/1; integer",
            "reaction_time_ms": "invented post-response duration; milliseconds",
            "seed": "unsigned 32-bit generator seed; integer",
        },
        "target_definition": "correct: synthetic binary response correctness",
        "feature_availability": {
            "stimulus_condition": "pre-response",
            "difficulty": "pre-response",
            "stimulus_side": "pre-response",
            "response": "post-response-excluded",
            "reaction_time_ms": "post-response-excluded",
            "correct": "target-excluded",
            "participant_id": "split-only-excluded",
            "session_id": "split-only-excluded",
            "trial_id": "id-excluded",
        },
        "transforms": [],
    }
