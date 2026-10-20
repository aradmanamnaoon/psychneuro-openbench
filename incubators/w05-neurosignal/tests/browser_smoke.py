"""Optional real headless Chromium check against loopback-only real uvicorn server."""
from __future__ import annotations

import os
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def smoke() -> None:
    token = secrets.token_urlsafe(25)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).parents[1] / "src"),
           "NEUROSIGNAL_LOCAL_TOKEN": token}
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "neurosignal.service:app",
                                "--host", "127.0.0.1", "--port", str(port)],
                               env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        import urllib.request
        for _ in range(40):
            if process.poll() is not None:
                raise RuntimeError("uvicorn exited before test")
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=.5)
                break
            except Exception:
                time.sleep(.1)
        else:
            raise RuntimeError("localhost server not available")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path="/usr/bin/chromium",
                                        args=["--no-sandbox", "--no-proxy-server", "--proxy-bypass-list=<-loopback>"])
            try:
                page = browser.new_page()
                page.goto(f"http://127.0.0.1:{port}/")
                assert page.title() == "NeuroSignal W05 Synthetic Lab"
                page.get_by_label("Local API token (not stored)").fill(token)
                page.get_by_role("button", name="Run synthetic pipeline").click()
                page.get_by_role("status").get_by_text("Synthetic demonstration finished", exact=False).wait_for(timeout=12000)
                result = page.locator("#result").inner_text()
                assert '"synthetic_only": true' in result
                assert '"dominant_frequency_hz": 10' in result
                print("REAL_CHROMIUM_UI_SMOKE=PASS; HEADLESS_LOOPBACK_ONLY")
            finally:
                browser.close()
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()


if __name__ == "__main__":
    smoke()
