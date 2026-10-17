"""CI-generated, nonclinical verification sidecar; never self-attests success.

This module must run *inside an actual authorized GitHub Actions job* AFTER
the benchmark, tests, report export and byte comparisons. A returned JSON
sidecar is evidence only when independently matched to the real run/log SHA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .reporting import build_bundle, parse_report

_SHA = re.compile(r"[0-9a-f]{40}\Z")
_RUN = re.compile(r"[1-9][0-9]{0,19}\Z")
_REPO = "aradmanamnaoon/psychneuro-openbench"
_PATHS = (
    "artifacts/pm10/report.json",
    "artifacts/pm11/report.json",
    "artifacts/pm11/report.md",
    "artifacts/pm11/artifact-manifest.json",
    "artifacts/pm13/report.json",
    "artifacts/pm13/report.md",
    "artifacts/pm13/artifact-manifest.json",
    "artifacts/verification/resolved-dependencies.txt",
)


def create_verification_sidecar(
    project_root: Path, environment: Mapping[str, str]
) -> dict[str, Any]:
    """Verify original-synthetic export bytes and identify hosting evidence.

    Do not accept a user-specified input path, dataset or remote URL.
    The sidecar is not a signature and cannot verify the GitHub-hosted job
    conclusively without a separate read of the provider's logs and job API.
    """
    commit = environment.get("GITHUB_SHA", "")
    run_id = environment.get("GITHUB_RUN_ID", "")
    if (
        environment.get("GITHUB_ACTIONS") != "true"
        or environment.get("GITHUB_REPOSITORY") != _REPO
        or _SHA.fullmatch(commit) is None
        or _RUN.fullmatch(run_id) is None
    ):
        raise ValueError("real GitHub Actions run identity required for a sidecar")
    blobs: dict[str, bytes] = {}
    for relative in _PATHS:
        location = project_root / relative
        if not location.is_file() or location.is_symlink():
            raise ValueError("missing or unsafe verified pipeline output")
        if location.stat().st_size > 2_000_000:
            raise ValueError("verification input exceeds configured limit")
        blobs[relative] = location.read_bytes()

    pm10 = parse_report(blobs["artifacts/pm10/report.json"])
    pm13 = parse_report(blobs["artifacts/pm13/report.json"])
    if pm10["status"] != "complete" or pm13["status"] != "complete":
        raise ValueError("ineligible synthetic cohorts prevent completed release check")
    if pm10 != pm13:
        raise ValueError("PM-10 and PM-13 reports do not match")
    bundle = build_bundle(pm10)
    expected = {
        "artifacts/pm11/report.json": bundle.report_json,
        "artifacts/pm11/report.md": bundle.report_markdown,
        "artifacts/pm11/artifact-manifest.json": bundle.artifact_manifest,
        "artifacts/pm13/report.json": bundle.report_json,
        "artifacts/pm13/report.md": bundle.report_markdown,
        "artifacts/pm13/artifact-manifest.json": bundle.artifact_manifest,
    }
    for path, value in expected.items():
        if blobs[path] != value:
            raise ValueError("report or manifest failed exact export-byte comparison")
    result = {
        "schema": "psychneuro-private-ci-evidence-v1",
        "attestation_type": "unsigned CI-produced artifact; independent logs required",
        "github_commit": commit,
        "github_run_id": run_id,
        "github_run_url": f"https://github.com/{_REPO}/actions/runs/{run_id}",
        "github_repository": _REPO,
        "python_version": platform.python_version(),
        "source_rights": "synthetic-original",
        "report_status": "complete",
        "n_eligible_fictional_cohorts": pm10["n_eligible"],
        "n_requested_fictional_cohorts": pm10["n_requested"],
        "report_sha256": pm10["report_sha256"],
        "file_sha256": {
            relative: hashlib.sha256(blobs[relative]).hexdigest()
            for relative in _PATHS
        },
        "limits": (
            "This is neither cryptographic proof of a CI run nor independent "
            "privacy, reproducibility, human-generalization or clinical validation. "
            "Verify the exact SHA and hosted logs on GitHub."
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Original-synthetic CI evidence sidecar")
    parser.add_argument(
        "--output", type=Path,
        default=Path("artifacts/verification/ci-evidence.json"),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    result = create_verification_sidecar(root, os.environ)
    output: Path = args.output
    if output.resolve() != (
        root / "artifacts/verification/ci-evidence.json"
    ).resolve():
        parser.error("output must use the fixed private verification artifact path")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("Private CI evidence sidecar created; independently verify run and SHA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
