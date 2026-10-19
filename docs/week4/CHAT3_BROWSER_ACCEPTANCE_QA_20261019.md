# W04 private Chromium and accessibility automation: executed 2026-10-19

**Status: observed local test PASS; overall release NO-GO.** Source revision `bd1f56866357a7108aa29c51cb7bf81cdcc573b7`. An independent native Git blob check found **18/18** relevant local source/test/registry/TypeScript files identical to GitHub. This is a synthetic-only local loopback test, NOT public deployment.

Run locally with dependencies installed:

```bash
npm ci --prefix apps/web --ignore-scripts --no-audit --no-fund
npm run typecheck --prefix apps/web
npm test --prefix apps/web
# Observed Node v20.20.2, TypeScript 5.9.3, all 4 tests PASSED
python -m pip install playwright==1.64.0
python -m playwright install chromium-headless-shell
PYTHONPATH=src python scripts/w04_browser_audit.py --output-dir artifacts/w04-browser-local
# Observed process exit 0
```

Actual Chromium 156.0.8078.4 headless shell results:

| Check | Observed |
|---|---|
| First keyboard focus | Internal token input |
| Fictional P25 rights preview | Allowed |
| W03 grouped benchmark | 1 aggregate table row |
| P13 provenance presentation | 4 ordered nodes |
| Receipt JSON export/verification | Passed, integrity ONLY |
| Modified receipt verification | HTTP 422 rejection |
| Axe WCAG2 A/AA and WCAG2.1 A/AA | 0 violations |
| Script errors | 0 |
| Horizontal overflow desktop/mobile | None |
| Mobile document width | 375 px |

Raw values and environment: `benchmarks/w04_chat3_browser_axe_observed_20261019.json`. Desktop screenshot SHA256 `312cd126cb861625754871ea63a0338a751bdf4964e74465fc938ae8dad92048`; mobile SHA256 `f273651ddddf3e4a0348a1ac19b9c61885999008cf7abb1a003995b00ce26a08`. Screenshots remained in the isolated sandbox, not uploaded as new private Git blobs.

**Boundary:** Test drives strict-facade synchronous W03 integration, not the distinct operator-only v4 queued worker. No actual worker OS-process kill, human screen-reader audit, production stress/security testing, independent signing root, third-party source permission or human-data validation. Initial execution failed because the sandbox lacked FastAPI/Uvicorn; after installing runtime dependencies it passed. Do not represent a zero-axe-violations result as WCAG certification.

**Release:** E9 remains PARTIAL with verified automated browser coverage; E8 worker PARTIAL with 66 local tests, E12 hosted CI/recovery BLOCKED. PR #22 PRIVATE DRAFT/unmerged; W04 Thursday 2026-11-05 In Progress, Done unchecked; Academy untouched; NO-GO.
