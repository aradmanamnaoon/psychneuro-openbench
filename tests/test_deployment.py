"""PM-15 source-only deployment preflight contracts (pytest NOT RUN here).

Do not equate static repository checks with a host deployment, security scan
or complete transitive-lock reproducibility test.
"""
from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRECT_REQUIREMENTS = {
    ".",
    "streamlit==1.58.0",
    "altair==5.5.0",
    "scikit-learn==1.8.0",
}


def _requirements() -> set[str]:
    raw = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    return {
        line.strip()
        for line in raw.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def test_only_original_project_and_three_pinned_direct_dependencies() -> None:
    assert _requirements() == EXPECTED_DIRECT_REQUIREMENTS
    assert not any(
        "://" in req or req.startswith(("git+", "-e", "--index", "--extra"))
        for req in _requirements()
    )


def test_python_312_is_supported_by_project_metadata() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["requires-python"] == ">=3.11"
    assert pyproject["project"]["version"] == "0.1.0.dev0"
    assert "streamlit>=1.58,<2" in pyproject["project"]["optional-dependencies"]["ui"]
    assert "scikit-learn>=1.5,<2" in pyproject["project"]["optional-dependencies"]["benchmark"]


def test_cloud_app_config_keeps_security_defaults_and_two_megabyte_cap() -> None:
    config = tomllib.loads(
        (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    )
    assert config["server"]["enableCORS"] is True
    assert config["server"]["enableXsrfProtection"] is True
    assert config["server"]["maxUploadSize"] == 2
    assert config["server"]["enableStaticServing"] is False
    assert config["client"]["showErrorDetails"] == "none"
    assert config["browser"]["gatherUsageStats"] is False
    assert not any(key.lower() in ("address", "port", "baseurlpath") for key in config["server"])


def test_repo_license_and_notice_exist_without_public_release_permission() -> None:
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
    gates = (ROOT / "docs" / "release-gates.md").read_text(encoding="utf-8")
    assert "Apache License" in license_text
    assert "Version 2.0" in license_text
    assert "PsychNeuro OpenBench" in notice
    assert "PRIVATE" in gates
    assert "explicit" in gates.lower()


def test_dataset_registry_disables_human_ingestion_and_downloads() -> None:
    registry = json.loads((ROOT / "data" / "registry.json").read_text(encoding="utf-8"))
    assert registry["policy"] == "deny_external_sources_by_default"
    all_entries = registry["entries"]
    assert len([x for x in all_entries if x["enabled"]]) == 1
    for entry in all_entries:
        assert entry["download_allowed"] is False
        assert entry["participant_data_ingestion_allowed"] is False
        if entry["enabled"]:
            assert entry["source_kind"] == "synthetic"
            assert entry["rights_basis"] == "synthetic-original"


def test_gitignore_excludes_secrets_and_pipeline_outputs() -> None:
    ignored = set((ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())
    for required in (
        ".env", ".env.*", ".streamlit/secrets.toml", "*.pem",
        "artifacts/", "*.egg-info/", "__pycache__/",
    ):
        assert required in ignored


def test_deployment_remains_approval_gated_and_no_fake_url_in_docs() -> None:
    runbook = (ROOT / "docs" / "pm15-host-runbook.md").read_text(encoding="utf-8")
    assert "LIVE URL: NONE / BLOCKED" in runbook
    assert "one private app" in runbook
    assert "repo" in runbook
    assert "DO NOT deploy" in runbook
