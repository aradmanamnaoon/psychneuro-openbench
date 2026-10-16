"""Nonclinical behavioral trial simulation and schema contracts."""

from .synthetic import (
    SyntheticConfig,
    TrialRecord,
    dataset_card,
    generate_trials,
    to_csv_text,
    validate_trials,
)

__all__ = [
    "SyntheticConfig",
    "TrialRecord",
    "dataset_card",
    "generate_trials",
    "to_csv_text",
    "validate_trials",
]

__version__ = "0.1.0.dev0"
