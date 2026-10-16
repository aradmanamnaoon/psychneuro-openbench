"""PM-06 ingestion regressions: malformed, empty, duplicate and unsafe fixtures.

These tests use only original synthetic trial records. They never open external data.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from psychneuro.loaders import load_dataset
from psychneuro.quality import DataQualityError
from psychneuro.synthetic import (
    CSV_COLUMNS,
    SyntheticConfig,
    dataset_card,
    generate_trials,
    to_csv_text,
)

REGISTRY = Path(__file__).resolve().parents[1] / "data" / "registry.json"


@pytest.fixture
def config() -> SyntheticConfig:
    return SyntheticConfig(seed=73, n_participants=2, trials_per_participant=3)


def _table(config: SyntheticConfig) -> list[list[str]]:
    return list(csv.reader(io.StringIO(to_csv_text(generate_trials(config)))))


def _save(tmp_path: Path, rows: list[list[str]]) -> Path:
    path = tmp_path / "pilot.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        csv.writer(stream, lineterminator="\n").writerows(rows)
    return path


def _load(path: Path, config: SyntheticConfig) -> None:
    load_dataset(path, REGISTRY, card=dataset_card(config, generate_trials(config)))


def test_malformed_unterminated_quoted_csv_rejected(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    path = tmp_path / "bad.csv"
    path.write_text(to_csv_text(generate_trials(config)) + '"unterminated', encoding="utf-8")
    with pytest.raises(ValueError, match="malformed CSV"):
        _load(path, config)


def test_invalid_utf8_never_silently_replaced(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    path = tmp_path / "bad.csv"
    path.write_bytes(to_csv_text(generate_trials(config)).encode("utf-8") + b"\xff")
    with pytest.raises(UnicodeDecodeError):
        _load(path, config)


def test_header_only_dataset_is_rejected_with_quality_counts(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    path = _save(tmp_path, [list(CSV_COLUMNS)])
    with pytest.raises(DataQualityError) as error:
        _load(path, config)
    assert error.value.summary.n_trials == 0
    assert not error.value.summary.valid


@pytest.mark.parametrize("operation", ["short", "long"])
def test_ragged_csv_row_fails_before_validation(
    tmp_path: Path, config: SyntheticConfig, operation: str
) -> None:
    rows = _table(config)
    if operation == "short":
        rows[1].pop()
    else:
        rows[1].append("unexpected")
    with pytest.raises(ValueError, match="wrong number of fields"):
        _load(_save(tmp_path, rows), config)


def test_duplicate_composite_trial_key_is_reported(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    rows = _table(config)
    rows[2] = rows[1].copy()
    with pytest.raises(DataQualityError) as error:
        _load(_save(tmp_path, rows), config)
    assert error.value.summary.duplicate_trial_keys == 1
    assert error.value.summary.duplicate_trial_orders >= 1


def test_duplicate_order_with_distinct_trial_id_is_reported(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    rows = _table(config)
    order_index = rows[0].index("trial_order")
    assert rows[1][rows[0].index("trial_id")] != rows[2][rows[0].index("trial_id")]
    rows[2][order_index] = rows[1][order_index]
    with pytest.raises(DataQualityError) as error:
        _load(_save(tmp_path, rows), config)
    assert error.value.summary.duplicate_trial_keys == 0
    assert error.value.summary.duplicate_trial_orders == 1


def test_noninteger_trial_order_fails_strict_parse(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    rows = _table(config)
    rows[1][rows[0].index("trial_order")] = "1.5"
    with pytest.raises(ValueError, match="invalid integer"):
        _load(_save(tmp_path, rows), config)


def test_infinite_response_time_rejected_with_audit_count(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    rows = _table(config)
    rows[1][rows[0].index("response_time_ms")] = "inf"
    with pytest.raises(DataQualityError) as error:
        _load(_save(tmp_path, rows), config)
    assert error.value.summary.invalid_response_times == 1


def test_inconsistent_correct_response_fails_closed(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    rows = _table(config)
    rows[1][rows[0].index("correct")] = (
        "0" if rows[1][rows[0].index("correct")] == "1" else "1"
    )
    with pytest.raises(DataQualityError) as error:
        _load(_save(tmp_path, rows), config)
    assert any("response disagrees" in e for e in error.value.summary.errors)


def test_symlink_input_is_denied_before_reading(
    tmp_path: Path, config: SyntheticConfig
) -> None:
    actual = tmp_path / "real.csv"
    actual.write_text(to_csv_text(generate_trials(config)), encoding="utf-8")
    link = tmp_path / "alias.csv"
    link.symlink_to(actual)
    with pytest.raises(ValueError, match="non-symlink"):
        _load(link, config)
