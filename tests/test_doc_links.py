"""Offline local-link QA for PM-16 issue #7 (no network or external data).

A scoped first pass over PM-13..16 user-facing docs and root onboarding.
Hosted execution has NOT been observed.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/reproducibility.md",
    "docs/use-cases.md",
    "docs/faq.md",
    "docs/tutorial.md",
    "docs/pm13-live-workflow.md",
    "docs/pm14-a11y-errors-performance.md",
    "docs/pm15-host-runbook.md",
    "docs/pm15-security-privacy-audit.md",
    "docs/pm15-browser-smoke.md",
    "docs/pm15-changelog.md",
    "docs/pm16-issue-map.md",
)
_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_FENCE = re.compile(r"^\s*("\x60" r"{3,}|~{3,})")
_INLINE_CODE = re.compile(r"\x60[^\x60]*\x60")


def _relative_targets(markdown: str) -> list[tuple[int, str]]:
    """Ignore fenced examples, inline code, anchors and remote links."""
    inside_fence = ""
    found: list[tuple[int, str]] = []
    for line_num, raw in enumerate(markdown.splitlines(), start=1):
        fence = _FENCE.match(raw)
        if fence:
            marker = fence.group(1)
            if not inside_fence:
                inside_fence = marker[0]
            elif inside_fence == marker[0]:
                inside_fence = ""
            continue
        if inside_fence:
            continue
        line = _INLINE_CODE.sub("", raw)
        for match in _LINK.finditer(line):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            parts = urlsplit(target)
            if (
                not parts.path or target.startswith(("#", "//"))
                or parts.scheme or parts.netloc
            ):
                continue
            path = unquote(parts.path)
            if path and not path.startswith("/"):
                found.append((line_num, path))
    return found


def _broken_links(file: Path, root: Path) -> list[str]:
    repo_root = root.resolve()
    missing: list[str] = []
    for line_num, path in _relative_targets(file.read_text(encoding="utf-8")):
        destination = (file.parent / path).resolve()
        if not destination.is_relative_to(repo_root) or not destination.exists():
            missing.append(f"{file.relative_to(root)}:{line_num}: {path}")
    return missing


def test_reviewed_user_facing_docs_have_no_broken_local_links() -> None:
    broken: list[str] = []
    for local in REVIEWED:
        file = ROOT / local
        assert file.is_file(), local
        broken.extend(_broken_links(file, ROOT))
    assert not broken, "Invalid local Markdown links:\n" + "\n".join(broken)


def test_reject_missing_local_path_with_precise_location(tmp_path: Path) -> None:
    doc = tmp_path / "guide.md"
    doc.write_text("# Heading\n[bad](missing.md)\n", encoding="utf-8")
    assert _broken_links(doc, tmp_path) == ["guide.md:2: missing.md"]


def test_accept_local_path_and_exclude_remote_and_code(tmp_path: Path) -> None:
    (tmp_path / "ok.md").write_text("ok", encoding="utf-8")
    doc = tmp_path / "guide.md"
    tick = chr(96)
    doc.write_text(
        "\n".join([
            "# Links",
            "[exists](ok.md#start)",
            "[web](https://example.org/path)",
            "[email](mailto:reviewer@example.org)",
            "[local heading](#links)",
            tick + "[fake](missing.md)" + tick,
            tick * 3 + "markdown",
            "[ignored fenced example](another-missing.md)",
            tick * 3,
            "![same local image-like path](ok.md)",
        ]) + "\n",
        encoding="utf-8",
    )
    assert _broken_links(doc, tmp_path) == []


def test_refuse_path_outside_project_even_when_target_exists(tmp_path: Path) -> None:
    subtree = tmp_path / "docs"
    subtree.mkdir()
    file = subtree / "guide.md"
    file.write_text("[bad](../../outside-project.tmp)\n", encoding="utf-8")
    assert _broken_links(file, tmp_path) == [
        "docs/guide.md:1: ../../outside-project.tmp"
    ]
