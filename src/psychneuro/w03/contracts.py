"""Versioned, reject-unknown-fields Pydantic contracts for synthetic experiments."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

FeatureName = Literal["difficulty", "stimulus_condition"]


class ExperimentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    generator_seed: int = Field(default=73, ge=0, le=2**64 - 1)
    split_seed: int = Field(default=42, ge=0, le=2**64 - 1)
    n_participants: int = Field(default=36, ge=24, le=80)
    trials_per_participant: int = Field(default=12, ge=8, le=40)
    outer_folds: Literal[3] = 3
    inner_folds: Literal[2] = 2
    predictors: tuple[FeatureName, FeatureName] = ("difficulty", "stimulus_condition")

    @field_validator("predictors")
    @classmethod
    def frozen_predictors(cls, value: tuple[FeatureName, FeatureName]) -> tuple[FeatureName, FeatureName]:
        if value != ("difficulty", "stimulus_condition"):
            raise ValueError("predictors must be the fixed pre-response allowlist")
        return value


class RunResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    schema_version: Literal["w03-engine-1"] = "w03-engine-1"
    run_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    split_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    provenance_root: str = Field(pattern=r"^[a-f0-9]{64}$")
    rights: Literal["internal-synthetic-only"] = "internal-synthetic-only"
    n_train_groups: int = Field(ge=1)
    n_test_groups: int = Field(ge=1)
    outer_balanced_accuracy: float = Field(ge=0, le=1)
    dummy_outer_balanced_accuracy: float = Field(ge=0, le=1)
    test_balanced_accuracy: float = Field(ge=0, le=1)
    selected_c: float = Field(ge=0.1, le=1.0)

    @field_validator("selected_c")
    @classmethod
    def fixed_regularization_grid(cls, value: float) -> float:
        if value not in (0.1, 1.0):
            raise ValueError("selected C must be one of the prespecified choices")
        return value
