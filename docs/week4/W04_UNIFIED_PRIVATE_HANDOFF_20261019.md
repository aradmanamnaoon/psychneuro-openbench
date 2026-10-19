# W04 unified private review branch — integration handoff (2026-10-19)

**Status: PRIVATE / DRAFT / NO-GO.** Preparation for the scheduled 2026-11-05–11-11 W04 mission. No merge, public release, human/clinical data, deploy, spending, outreach or Academy changes. Career Done must remain unchecked.

## Source lineage and reconciliation

This branch started from the exact independent Chat3 review head `1bf73f96c03b2e7c5a81fc4313da0b06b37f90de` (private draft PR #22), **not** from main. An explicit single-parent Git tree commit overlaid 12 reviewed GitHub blob objects from private Chat2 worker/UI branch PR #23 and Chat2 TS-security PR #18. It is **not a merge** of PR histories and does not assert code/test equivalence of divergent branches.

- Inherited Chat3 atomic run-store / tenant ACL, P25/P13 worker, QA and GA1–GA8 reviewer files remain intact.
- Overlaid `src/psychneuro/w03/service.py` from Chat2 worker branch for typed `RunSink` and optional `on_fit_complete` injection.
- Overlaid authenticated `/w04/v3/jobs` router with create/status/cancel/resume/receipt and corresponding real synthetic W03 test; operator-only CLI continues to run separately (no browser-triggered privileged worker).
- Overlaid Chat2 durable queue browser controls, private Playwright script, typed worker SDK and a local-only SBOM inventory script.
- Overlaid newer Chat2 scientific presenter topology/identity checks and 9-test scoped TypeScript regression suite.
- Narrow new strict facade changes: `OwnerBoundRunStore` makes W03 persistence+ACL claim one SQLite transaction; arbitrary checksum-only artifact import now returns **403**, including for maintainers. An externally authenticated signer/root and rights authority are NOT available.
- Same-origin static CSS/JS assets are now served from strict private FastAPI, with **no inline script/style** and CSP `script-src 'self'; style-src 'self'`. Browser audit asserts the live response header and uses a separate CSP-bypass context solely for injected axe-core inspection; the actual interaction page remains CSP-enforced.
- New `tests/test_w04_strict_security_unified.py` asserts tenant collision atomicity, denied unsigned import, no-inline assets and token non-disclosure.

## Honest execution status

**Code review and GitHub write/readback are confirmed. No new exact unified-branch pytest, Ruff, mypy, TS compilation, Docker build, Chromium/axe, remote Python 3.11/3.12 hosted CI, SBOM CVE scan or independent security review executed in this reconciliation turn.** Do not carry forward historic `400 passed` on the unmodified Chat3 ancestor as an exact-HEAD result for this branch.

Prior scoped observations remain branch/SHA-bound: Chat3 had `400 passed` local Python 3.13 on its earlier source; Chat2 had 9 passing TS tests on its earlier `client.ts` without worker methods. Neither alone validates the new unified tree. Chat3 push-triggered hosted run #39282517739 was most recently **queued**, not PASS, and belongs to a different SHA.

### Required local-only validation (NOT RUN here)

```sh
python -m pip install -e '.[dev,benchmark,w03,ui,parquet]'
python -m pytest -q
python -m ruff check .
python -m mypy --python-version 3.11 src
npm ci --prefix apps/web --ignore-scripts --no-audit --no-fund
npm run test --prefix apps/web
# After private-only policy/source verification and browser dependencies:
PYTHONPATH=src python scripts/w04_browser_audit.py
# Rehearse DB backup/restore, crash/restart, and dependency audit separately.
```

### Release-blocking gates

- **G1**: observe exact-HEAD hosted 3.11/3.12 Python + TypeScript CI, signed logs and artifact hashes.
- **G2**: actual restart/reclaim-after-process-kill with representative lease expiry; no claim of in-fit checkpoint resume.
- **G3**: independent external root/rights authority and legal check before any real-data use or artifact import; checksum alone is not authenticity.
- **G4**: production identity/token lifecycle, vulnerability policy/SBOM, migration/rollback drill and security review.
- **G5**: real keyboard/screen-reader/a11y/browser/mobile walkthrough on unified source, privacy and performance under concurrency.
- **G6**: no release-grade multi-dataset licenses/consent, no human study, no official independent acceptance, no scientifically generalizable inference.

**E1–E14 and GA1–GA8 remain preparatory deliverables; rubric threshold and all hard gates are not met. Always NO-GO.**
