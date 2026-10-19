"""Offline review negative/security tests: all records are fictional W03 envelopes."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path

import pytest

from psychneuro.w04 import reviewer
from psychneuro.w04.receipt_v3 import digest


def _record(seed: int = 73) -> dict[str, object]:
    source = hashlib.sha256(f"source-{seed}".encode()).hexdigest()
    split = hashlib.sha256(f"split-{seed}".encode()).hexdigest()
    request = {
        "generator_seed": seed, "split_seed": 42, "n_participants": 36,
        "trials_per_participant": 12, "outer_folds": 3, "inner_folds": 2,
        "predictors": ["difficulty", "stimulus_condition"],
    }
    run_id = digest({
        "contract": "w03-engine-1", "request": request, "source": source, "split": split
    })
    result = {
        "schema_version": "w03-engine-1", "run_id": run_id,
        "source_sha256": source, "split_sha256": split,
        "rights": "internal-synthetic-only", "n_train_groups": 21,
        "n_test_groups": 8, "outer_balanced_accuracy": 0.5,
        "dummy_outer_balanced_accuracy": 0.5,
        "test_balanced_accuracy": 0.5, "selected_c": 0.1,
    }
    metadata = [
        {"source_sha256": source, "rights": "internal-synthetic-only", "seed": seed},
        {"split_sha256": split, "seed": 42, "train_groups": 21, "test_groups": 8},
        {"selected_c": 0.1, "model_spec_only": True,
         "trained_model_bytes_hash": None,
         "predictors": ["difficulty", "stimulus_condition"]},
        {"result_sha256": digest(result), "request": request, "benchmark": {
            "outer_scores": [0.5, 0.5, 0.5],
            "dummy_outer_scores": [0.5, 0.5, 0.5],
            "outer_selected_c": [0.1, 0.1, 0.1], "final_c": 0.1,
            "sealed_test_balanced_accuracy": 0.5,
            "metric": "balanced_accuracy", "unit": "fictional_participant",
        }},
    ]
    nodes: list[dict[str, object]] = []
    for kind, entry in zip(("source", "split", "model", "benchmark"), metadata):
        parents = [nodes[-1]["sha256"]] if nodes else []
        sha = digest({"kind": kind, "parents": parents, "metadata": entry})
        nodes.append({
            "kind": kind, "parents": parents, "metadata": entry, "sha256": sha,
        })
    root = str(nodes[-1]["sha256"])
    return {
        "run_id": run_id, "provenance_root": root,
        "nodes": nodes, "rights": "internal-synthetic-only",
        "result": {**result, "provenance_root": root},
    }


def _raw(seed: int = 73) -> bytes:
    return json.dumps(_record(seed), sort_keys=True).encode()


def test_valid_fictional_record_and_replay_root() -> None:
    original = _record()
    checked = reviewer.parse_record(_raw(), expected_root=str(original["provenance_root"]))
    assert checked.train_groups == 21
    assert checked.test_groups == 8
    assert checked.selected_c == 0.1
    assert checked.outer_balanced_accuracy == checked.dummy_outer_balanced_accuracy
    assert checked.provenance_root == original["provenance_root"]
    assert reviewer.parse_record(_raw()) == checked


@pytest.mark.parametrize("bad", [
    b"", b"[]", b"{}", b"\xff", b'{"a":1,"a":2}',
    b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}',
    b" " * (reviewer.MAX_RECORD_BYTES + 1),
])
def test_invalid_json_or_size_fails_closed(bad: bytes) -> None:
    with pytest.raises(reviewer.ReviewError):
        reviewer.parse_record(bad)


def test_checksum_pin_requires_separately_supplied_matching_root() -> None:
    with pytest.raises(reviewer.ReviewError, match="external root"):
        reviewer.parse_record(_raw(), expected_root="a" * 64)
    for invalid in ("A" * 64, "abc", "../x", ""):
        with pytest.raises(reviewer.ReviewError):
            reviewer.parse_record(_raw(), expected_root=invalid)


@pytest.mark.parametrize("change", [
    lambda r: r.update(rights="public"),
    lambda r: r["nodes"][0]["metadata"].update(seed=11),
    lambda r: r["nodes"][2]["metadata"].update(predictors=["response_time_ms"]),
    lambda r: r["nodes"][3]["metadata"]["benchmark"].update(metric="accuracy"),
    lambda r: r["result"].update(outer_balanced_accuracy=0.99),
    lambda r: r["result"].update(n_train_groups=0),
])
def test_mutated_scientific_graph_is_rejected(change) -> None:
    record = copy.deepcopy(_record())
    change(record)
    with pytest.raises(reviewer.ReviewError):
        reviewer.parse_record(json.dumps(record).encode())


def test_descriptive_comparison_refuses_unmatched_data() -> None:
    same = reviewer.parse_record(_raw())
    different = reviewer.parse_record(_raw(99))
    assert reviewer.comparison(same, same)["same_split"] is True
    outcome = reviewer.comparison(same, different)
    assert outcome["same_split"] is False
    assert "NOT a controlled" in outcome["interpretation"]


def test_all_output_forms_have_limits_and_no_untrusted_html() -> None:
    a, b = reviewer.parse_record(_raw()), reviewer.parse_record(_raw(99))
    as_html = reviewer.as_html(a, b).decode()
    as_md = reviewer.as_markdown(a, b).decode()
    as_json = json.loads(reviewer.as_json(a, b))
    assert "<script" not in as_html.lower()
    assert "http://" not in as_html and "https://" not in as_html
    assert "default-src 'none'" in as_html
    assert "Run A" in as_html and "Run B" in as_html
    assert "NOT a controlled" in as_md
    assert as_json["schema_version"] == "psychneuro-offline-review-1"
    assert as_json["comparison"]["same_split"] is False
    assert all(len(payload) < reviewer.MAX_OUTPUT_BYTES for payload in (
        reviewer.as_html(a, b), reviewer.as_markdown(a, b), reviewer.as_json(a, b)
    ))


def test_local_loader_refuses_symlink_and_oversized_file(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    source.write_bytes(_raw())
    assert reviewer.load_record(source).train_groups == 21
    alias = tmp_path / "symlink.json"
    try:
        alias.symlink_to(source)
    except (NotImplementedError, OSError):
        pass
    else:
        with pytest.raises(reviewer.ReviewError):
            reviewer.load_record(alias)
    large = tmp_path / "huge.json"
    large.write_bytes(b" " * (reviewer.MAX_RECORD_BYTES + 1))
    with pytest.raises(reviewer.ReviewError):
        reviewer.load_record(large)


def test_output_never_overwrites_and_defaults_to_private(tmp_path: Path) -> None:
    path = tmp_path / "offline.html"
    data = b"<html>fictional</html>"
    reviewer.write_private_new(path, data)
    assert path.read_bytes() == data
    if os.name == "posix":
        assert path.stat().st_mode & 0o077 == 0
    with pytest.raises(FileExistsError):
        reviewer.write_private_new(path, b"overwrite")
    assert path.read_bytes() == data
    with pytest.raises(reviewer.ReviewError):
        reviewer.write_private_new(tmp_path / "big.html", b"x" * 128_001)


def test_cli_generates_local_html_and_json_without_network(tmp_path: Path) -> None:
    source = tmp_path / "valid.json"
    source.write_bytes(_raw())
    html = tmp_path / "review.html"
    result = reviewer.main(["--record", str(source), "--output", str(html)])
    assert result == 0
    assert b"From scores to defensible evidence" in html.read_bytes()
    report = tmp_path / "review.json"
    assert reviewer.main([
        "--record", str(source), "--format", "json", "--output", str(report),
    ]) == 0
    assert json.loads(report.read_bytes())["first"]["test_groups"] == 8
    assert reviewer.main(["--record", str(source), "--output", str(html)]) == 2


def test_cli_malformed_input_does_not_create_output(tmp_path: Path) -> None:
    wrong = tmp_path / "bad.json"
    wrong.write_text('{"rights":"human","secret":"do-not-print"}')
    destination = tmp_path / "should-not-exist.html"
    assert reviewer.main(["--record", str(wrong), "--output", str(destination)]) == 2
    assert not destination.exists()
