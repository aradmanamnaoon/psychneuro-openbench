"""PM-16 static source-contract checks for private newcomer documentation.

These are pytest test SPECIFICATIONS, not proof of execution. Avoid network,
hosted run dispatch, real participant data and automatic external outreach.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISSUE_TEMPLATES = ROOT / ".github" / "ISSUE_TEMPLATE"
REQUIRED_DOCS = (
    "CONTRIBUTING.md",
    "docs/reproducibility.md",
    "docs/use-cases.md",
    "docs/faq.md",
    "docs/tutorial.md",
    "docs/release-gates.md",
    "docs/pm15-host-runbook.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/improvement.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
)


def test_contributor_and_research_docs_exist_at_real_repo_paths() -> None:
    for path in REQUIRED_DOCS:
        full = ROOT / path
        assert full.is_file(), f"PM-16 document path missing: {path}"
        assert len(full.read_text(encoding="utf-8")) > 80, path


def test_contributor_guide_preserves_private_and_scientific_gates() -> None:
    text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    for required in (
        "PRIVATE", "synthetic", "participant", "CONTRIBUTING",
        "docs/reproducibility.md", "data/registry.json",
        "configs/baseline.json", "tests/", "reviewer",
        "NOT RUN", "owner approval", "default branch",
    ):
        assert required.lower() in text.lower(), required
    for forbidden in ("share.streamlit.io/", "patient_records.csv", "sk_test_"):
        assert forbidden not in text


def test_issue_markdown_templates_have_supported_frontmatter_and_no_external_scopes() -> None:
    for name in ("bug_report.md", "improvement.md"):
        text = (ISSUE_TEMPLATES / name).read_text(encoding="utf-8")
        assert text.startswith("---\n")
        frontmatter = text.split("---", 2)[1]
        for field in ("name:", "about:", "title:"):
            assert re.search(rf"(?m)^{field}", frontmatter), (name, field)
        assert "No" in text or "no" in text
        assert "synthetic" in text.lower()
        assert "NOT RUN" in text or "BLOCKED" in text
    chooser = (ISSUE_TEMPLATES / "config.yml").read_text(encoding="utf-8")
    assert "blank_issues_enabled: true" in chooser
    assert "contact_links:" not in chooser


def test_pr_review_checklist_is_a_template_not_an_approval() -> None:
    text = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
    for phrase in (
        "exact", "pytest", "ruff", "mypy", "synthetic",
        "privacy", "participant", "owner approval", "NOT RUN",
    ):
        assert phrase.lower() in text.lower()
    assert "A prepared PR template is not PR permission." in text


def test_new_guides_explicitly_disclaim_unverified_hosted_and_clinical_claims() -> None:
    for name in ("reproducibility.md", "use-cases.md", "faq.md"):
        content = (ROOT / "docs" / name).read_text(encoding="utf-8").lower()
        assert "not" in content and "synthetic" in content
        assert "private" in content and "human" in content
        assert "ci" in content
    repro = (ROOT / "docs/reproducibility.md").read_text(encoding="utf-8")
    assert "python -m psychneuro.pipeline --config configs/baseline.json" in repro
    assert "cmp artifacts/pm10/report.json artifacts/pm13/report.json" in repro
    assert "NOT RUN" in repro
    faq = (ROOT / "docs/faq.md").read_text(encoding="utf-8")
    assert "No verified live URL exists" in faq


def test_existing_workflow_remains_manual_only_and_owner_spend_gated() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "profile_small_synthetic:" in workflow
    assert "default: false" in workflow
    assert re.search(r"(?m)^\s*run: python -m pytest -q\s*$", workflow)
    assert "python -m ruff check ." in workflow
    assert "python -m mypy src" in workflow


def test_first_issue_is_real_and_documented_without_public_invitation() -> None:
    contributor = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "The repo must stay PRIVATE" in contributor
    # This asserts source policy only. Exact live issue labels/URL are verified
    # separately through GitHub, not faked by this offline source check.
