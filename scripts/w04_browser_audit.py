"""Private, CPU-only browser acceptance: P25 → P1 → P13 → browser.

Run manually after: pip install -e '.[w03]' playwright==1.64.0
                  python -m playwright install chromium-headless-shell
                  npm ci --prefix apps/web
                  PYTHONPATH=src python scripts/w04_browser_audit.py
No remote deployment or user-supplied data is involved. Screenshots have a masked
fictional access token. No screen reader or human usability claim is made.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

from psychneuro.w03.contracts import ExperimentRequest
from psychneuro.w04.durable_bridge import source_sha256
from psychneuro.w04.policy_v2 import PolicyRecord, PolicyStore


def free_loopback_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def audit(output: Path) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    registry = root / "data" / "registry.json"
    token = secrets.token_urlsafe(48)
    permit_key = secrets.token_urlsafe(48)
    port = free_loopback_port()
    origin = f"http://127.0.0.1:{port}"
    output.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {
        "schema_version": "w04-browser-audit-1",
        "privacy": "single-host loopback; original fictional data only",
        "browser_mode": "Chromium headless with reduced-motion preference",
        "automation_scope": "not a manual screen-reader audit",
        "axe_tags": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
    }
    with tempfile.TemporaryDirectory() as work:
        db = Path(work) / "strict.sqlite"
        store = PolicyStore(db, permit_key=permit_key.encode())
        store.install(
            PolicyRecord(
                tenant="local",
                source_sha256=source_sha256(ExperimentRequest(), registry),
                actions=frozenset({"run", "read_aggregate", "export_aggregate"}),
                attestation_ref="local-fictional-browser-review-v1",
                retention_until_ns=time.time_ns() + 3_600_000_000_000,
            ),
            operator="fictional-browser-review",
        )
        env = dict(os.environ)
        env.update({
            "PYTHONPATH": str(root / "src"),
            "W04_DB_PATH": str(db),
            "W04_REGISTRY_PATH": str(registry),
            "W04_PRIVATE_TOKEN": token,
            "W04_P25_PERMIT_KEY": permit_key,
        })
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "psychneuro.w04.server_strict:app_factory",
             "--factory", "--host", "127.0.0.1", "--port", str(port)],
            cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            for _ in range(75):
                if process.poll() is not None:
                    raise RuntimeError("private review server terminated")
                try:
                    with urllib.request.urlopen(origin + "/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except OSError:
                    time.sleep(0.2)
            else:
                raise TimeoutError("private review server not ready")

            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                try:
                    page = browser.new_page(
                        viewport={"width": 1280, "height": 860},
                        reduced_motion="reduce", accept_downloads=True,
                    )
                    errors: list[str] = []
                    page.on("pageerror", lambda err: errors.append(str(err)))
                    page.goto(origin, wait_until="domcontentloaded")
                    assert page.get_by_role("heading", name="PsychNeuro W04 — private explorer").count() == 1
                    assert page.locator("#create-form").count() == 1
                    page.keyboard.press("Tab")
                    results["first_keyboard_focus"] = page.evaluate("document.activeElement.id")
                    assert results["first_keyboard_focus"] == "token"
                    page.get_by_label("Internal access token (not saved)").fill(token)
                    page.get_by_role("button", name="Preview dataset/run rights").click()
                    page.locator("#rights-display").get_by_text("ALLOWED", exact=False).wait_for(timeout=20000)
                    results["rights_preview"] = "allowed for explicit fictional fixture"

                    page.get_by_role("button", name="Execute W03 grouped benchmark").click()
                    for _ in range(300):
                        if len(page.locator("#run1").input_value()) == 64:
                            break
                        time.sleep(0.2)
                    else:
                        raise AssertionError("run not created: " + page.locator("#alert").inner_text())
                    page.locator("#scores table").wait_for(timeout=60000)
                    results["aggregate_table_rows"] = page.locator("#scores tbody tr").count()
                    results["verified_graph_nodes"] = page.locator("#graph li").count()
                    assert results["aggregate_table_rows"] == 1
                    assert results["verified_graph_nodes"] == 4

                    with page.expect_download(timeout=20000) as request:
                        page.get_by_role("button", name="Download A integrity-only JSON artifact").click()
                    receipt_path = Path(work) / "receipt.json"
                    request.value.save_as(str(receipt_path))
                    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                    assert receipt["schema_version"] == "w04-envelope-1"
                    page.locator("#receipt").set_input_files(str(receipt_path))
                    page.get_by_role("button", name="Verify receipt").click()
                    page.get_by_text("Receipt hash verification OK", exact=False).wait_for(timeout=20000)
                    results["receipt_verification"] = "integrity verified; no independent signature"

                    wrong = receipt.copy()
                    wrong["receipt_sha256"] = "0" * 64
                    bad_file = Path(work) / "tampered.json"
                    bad_file.write_text(json.dumps(wrong), encoding="utf-8")
                    page.locator("#receipt").set_input_files(str(bad_file))
                    page.get_by_role("button", name="Verify receipt").click()
                    page.get_by_text("Request rejected (422)", exact=False).wait_for(timeout=20000)
                    results["tampered_receipt"] = "rejected HTTP 422"

                    axe_file = root / "apps/web/node_modules/axe-core/axe.min.js"
                    if not axe_file.is_file():
                        raise RuntimeError("axe-core missing; install with npm ci --prefix apps/web")
                    page.add_script_tag(path=str(axe_file))
                    results["axe_violations"] = page.evaluate(
                        "async () => { const r=await axe.run(document,{runOnly:"
                        "{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});"
                        "return r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})); }"
                    )
                    results["desktop_document_overflow"] = page.evaluate(
                        "document.documentElement.scrollWidth > document.documentElement.clientWidth"
                    )
                    page.screenshot(path=str(output / "desktop.png"), full_page=True)
                    page.set_viewport_size({"width": 375, "height": 812})
                    results["mobile_document_width"] = page.evaluate("document.documentElement.scrollWidth")
                    results["mobile_document_overflow"] = page.evaluate(
                        "document.documentElement.scrollWidth > document.documentElement.clientWidth"
                    )
                    page.screenshot(path=str(output / "mobile.png"), full_page=True)
                    results["page_script_errors"] = len(errors)
                    if (results["axe_violations"] or results["desktop_document_overflow"]
                            or results["mobile_document_overflow"] or errors):
                        raise AssertionError("browser accessibility or JS gate failed")
                finally:
                    browser.close()
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    (output / "report.json").write_text(
        json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path, default=Path("artifacts/w04-browser-private"),
        help="Ignored local evidence directory; never paste test tokens into a repo",
    )
    args = parser.parse_args()
    print(json.dumps(audit(args.output_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
