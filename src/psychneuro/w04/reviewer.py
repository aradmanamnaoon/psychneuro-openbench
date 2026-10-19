"""Offline, read-only reviewer for internally exported W03 synthetic aggregates.

Hashes check consistency; they cannot establish authorship, legal rights, signed
attestation or scientific validity. No network operations or raw trial exports.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from psychneuro.w03.contracts import RunResult
from psychneuro.w04.receipt_v3 import ReceiptError, verify_record

MAX_RECORD_BYTES = 250_000
MAX_OUTPUT_BYTES = 128_000
_SHA = re.compile(r"[a-f0-9]{64}\Z")
WARNING = "Integrity checked, NOT independently authenticated, approved or clinically valid."


class ReviewError(ValueError):
    """Unsupported W03 report or unsafe reviewer input."""


@dataclass(frozen=True, slots=True)
class Review:
    run_id: str
    provenance_root: str
    source_sha256: str
    split_sha256: str
    train_groups: int
    test_groups: int
    outer_balanced_accuracy: float
    dummy_outer_balanced_accuracy: float
    sealed_test_balanced_accuracy: float
    selected_c: float


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReviewError("duplicate JSON field")
        result[key] = value
    return result


def _nonfinite(_: str) -> None:
    raise ReviewError("NaN and infinity are forbidden")


def parse_record(raw: bytes, *, expected_root: str | None = None) -> Review:
    """Validate byte, graph, schema and optional externally supplied root pin.

    The caller must obtain a pin from a separately authenticated channel.
    A root read from the same untrusted report does NOT establish authenticity.
    """
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_RECORD_BYTES:
        raise ReviewError("record empty or exceeds limit")
    if expected_root is not None and (
        not isinstance(expected_root, str) or _SHA.fullmatch(expected_root) is None
    ):
        raise ReviewError("malformed expected root")
    try:
        record = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique, parse_constant=_nonfinite
        )
    except (UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ReviewError("invalid aggregate JSON") from exc
    if not isinstance(record, dict):
        raise ReviewError("aggregate must be an object")
    try:
        root, run_id = verify_record(record)
        if expected_root is not None and root != expected_root:
            raise ReviewError("external root checksum mismatch")
        result = RunResult.model_validate(record["result"])
        if result.provenance_root != root or result.run_id != run_id:
            raise ReviewError("inconsistent W03 identity")
        return Review(
            run_id=run_id,
            provenance_root=root,
            source_sha256=result.source_sha256,
            split_sha256=result.split_sha256,
            train_groups=result.n_train_groups,
            test_groups=result.n_test_groups,
            outer_balanced_accuracy=result.outer_balanced_accuracy,
            dummy_outer_balanced_accuracy=result.dummy_outer_balanced_accuracy,
            sealed_test_balanced_accuracy=result.test_balanced_accuracy,
            selected_c=result.selected_c,
        )
    except ReviewError:
        raise
    except (ReceiptError, KeyError, TypeError, ValueError, AttributeError) as exc:
        raise ReviewError("scientific or graph validation failed") from exc


def load_record(path: Path, *, expected_root: str | None = None) -> Review:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_RECORD_BYTES:
        raise ReviewError("only bounded local non-symlink aggregate files are accepted")
    with path.open("rb") as file:
        return parse_record(file.read(MAX_RECORD_BYTES + 1), expected_root=expected_root)


def comparison(left: Review, right: Review) -> dict[str, Any]:
    same_source = left.source_sha256 == right.source_sha256
    same_split = same_source and left.split_sha256 == right.split_sha256
    return {
        "same_source": same_source,
        "same_split": same_split,
        "test_difference": right.sealed_test_balanced_accuracy - left.sealed_test_balanced_accuracy,
        "interpretation": (
            "Identical source and participant-split digests; descriptive difference "
            "only. No paired predictions or inferential statistics are available."
            if same_split else
            "Different data or participant splits. Scores are NOT a controlled "
            "head-to-head comparison; no model ranking is justified."
        ),
    }


def data(left: Review, right: Review | None = None) -> dict[str, Any]:
    output: dict[str, Any] = {
        "schema_version": "psychneuro-offline-review-1",
        "scope": "fictional W03 participant-level experiment summaries only",
        "warning": WARNING,
        "first": asdict(left),
        "limitations": [
            "Original synthetic participants only; no human or clinical validity.",
            "Self-consistent hashes cannot authenticate a source or claim dataset rights.",
            "Aggregates alone cannot support a paired statistical comparison.",
        ],
    }
    if right is not None:
        output["second"] = asdict(right)
        output["comparison"] = comparison(left, right)
    return output


def as_json(left: Review, right: Review | None = None) -> bytes:
    return (json.dumps(data(left, right), sort_keys=True, indent=2, allow_nan=False) +
            "\n").encode("utf-8")


def as_markdown(left: Review, right: Review | None = None) -> bytes:
    rows = [
        "# PsychNeuro OpenBench — offline research review", "",
        "**PRIVATE · SYNTHETIC · INTEGRITY-ONLY**", "", WARNING, "",
        "| Metric | Run A | Run B |", "| --- | ---: | ---: |",
    ]
    for title, field in [
        ("Outer balanced accuracy", "outer_balanced_accuracy"),
        ("Grouped dummy baseline", "dummy_outer_balanced_accuracy"),
        ("Sealed test balanced accuracy", "sealed_test_balanced_accuracy"),
        ("Training participant groups", "train_groups"),
        ("Test participant groups", "test_groups"),
        ("Chosen regularization", "selected_c"),
    ]:
        second = getattr(right, field) if right else "—"
        rows.append(f"| {title} | {getattr(left, field)} | {second} |")
    rows.extend(["", "## Source and replay identities", ""])
    for label, item in (("A", left), ("B", right)):
        if item is None:
            continue
        rows.extend([
            f"- Run {label}: {item.run_id}",
            f"- Source {label}: {item.source_sha256}",
            f"- Split {label}: {item.split_sha256}",
            f"- Root {label}: {item.provenance_root}",
        ])
    if right:
        rows.extend(["", "## Comparison", "", comparison(left, right)["interpretation"]])
    rows.extend([
        "", "## Scientific limitations", "",
        "- Fictional data; no claim about human behavior, disease, or neuroscience.",
        "- A checksum alone does not prove authorship or an independent signature.",
        "- No paired predictions or uncertainty interval are provided.",
        "- Access and redistribution rights require separate authorization.", "",
    ])
    return "\n".join(rows).encode("utf-8")


def as_html(left: Review, right: Review | None = None) -> bytes:
    """Portable accessible static page: no JavaScript, CDN, images or network."""
    def esc(value: object) -> str:
        return html.escape(str(value), quote=True)
    metrics = [
        ("Outer balanced accuracy", "outer_balanced_accuracy"),
        ("Grouped dummy baseline", "dummy_outer_balanced_accuracy"),
        ("Sealed test balanced accuracy", "sealed_test_balanced_accuracy"),
        ("Training participant groups", "train_groups"),
        ("Test participant groups", "test_groups"),
        ("Chosen regularization", "selected_c"),
    ]
    rows = "".join(
        "<tr><th scope='row'>" + esc(title) + "</th><td>" + esc(getattr(left, key))
        + "</td><td>" + (esc(getattr(right, key)) if right else "—") + "</td></tr>"
        for title, key in metrics
    )
    cards = ""
    for label, item in (("A", left), ("B", right)):
        if item is None:
            continue
        cards += ("<section><h3>Run " + label + "</h3><dl>"
                  "<dt>Run identity</dt><dd><code>" + esc(item.run_id) + "</code></dd>"
                  "<dt>Source digest</dt><dd><code>" + esc(item.source_sha256) + "</code></dd>"
                  "<dt>Split digest</dt><dd><code>" + esc(item.split_sha256) + "</code></dd>"
                  "<dt>Provenance root</dt><dd><code>" + esc(item.provenance_root)
                  + "</code></dd></dl></section>")
    compare_html = (
        "<section><h2>Comparison limits</h2><p>" +
        esc(comparison(left, right)["interpretation"]) + "</p></section>"
        if right else ""
    )
    page = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; "
        "style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'\">"
        "<title>PsychNeuro Research Review</title><style>"
        "body{background:#f2f5fa;color:#152239;font:1rem/1.6 system-ui,sans-serif;margin:0}"
        "main{max-width:66rem;margin:auto;padding:clamp(1rem,4vw,3rem)}"
        "header{background:#142039;color:white;padding:2rem;border-radius:1rem}"
        "h1{font-size:clamp(1.8rem,4vw,2.6rem);line-height:1.15}"
        "header p{color:#dbe7ff}section{background:white;border:1px solid #d6deec;"
        "padding:1.25rem;border-radius:1rem;margin:1.2rem 0;overflow-wrap:anywhere}"
        "table{width:100%;border-collapse:collapse}th,td{padding:.65rem;text-align:left;"
        "border-bottom:1px solid #c9d2e4}dt{font-weight:bold;margin-top:.5rem}"
        "dd{margin:0}code{overflow-wrap:anywhere}.scroll{overflow-x:auto}"
        ".warning{border-left:.4rem solid #b05500}"
        "@media print{body{background:white}header{background:white;color:black}"
        "header p{color:black}section{break-inside:avoid}}</style></head><body>"
        "<main><header><p>PRIVATE · SYNTHETIC ONLY · OFFLINE</p>"
        "<h1>From scores to defensible evidence.</h1>"
        "<p>A network-free, read-only summary of supplied aggregate experiments.</p>"
        "</header><section class='warning' role='note'><h2>Evidence boundary</h2><p>"
        + esc(WARNING) + "</p></section>"
        "<section><h2>Research scorecard</h2><div class='scroll'><table>"
        "<caption>Grouped W03 scientific metrics</caption>"
        "<thead><tr><th scope='col'>Metric</th><th scope='col'>Run A</th>"
        "<th scope='col'>Run B</th></tr></thead><tbody>" + rows +
        "</tbody></table></div></section><h2>Replay identities</h2>" + cards +
        compare_html + "<section><h2>Read before citing</h2><ul>"
        "<li>Only fictional participants; not clinical evidence.</li>"
        "<li>Digest checks do not prove independent authorship or data rights.</li>"
        "<li>Different group splits must not be compared as a controlled test.</li>"
        "<li>Independent security, reproducibility and accessibility gates remain.</li>"
        "</ul></section></main></body></html>"
    )
    return page.encode("utf-8")


def write_private_new(path: Path, content: bytes) -> None:
    """Create once with restrictive mode, never silently overwrite a report."""
    if len(content) > MAX_OUTPUT_BYTES or not path.parent.is_dir():
        raise ReviewError("unsafe destination or excessive output")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline W03 synthetic aggregate inspector")
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--expected-root", type=str)
    parser.add_argument("--format", choices=("html", "markdown", "json"), default="html")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        first = load_record(args.record, expected_root=args.expected_root)
        second = load_record(args.compare) if args.compare else None
        builders = {"html": as_html, "markdown": as_markdown, "json": as_json}
        output = builders[args.format](first, second)
        if len(output) > MAX_OUTPUT_BYTES:
            raise ReviewError("excessive output")
        if args.output:
            write_private_new(args.output, output)
        else:
            sys.stdout.buffer.write(output)
        return 0
    except (ReviewError, OSError):
        print("Offline W03 review refused; input, output or integrity gate failed.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
