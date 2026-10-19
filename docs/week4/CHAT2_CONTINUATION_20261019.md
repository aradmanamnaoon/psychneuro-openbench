# W04 Chat 2 continuation — verified private TypeScript hardening (2026-10-19)

**Scope:** private draft PR #18, on `review/w04-chat2-on-chat1-final-20261019`. W04 schedule stays 2026-11-05–11, Career Done unchecked; Academy untouched. No merge, workflow dispatch, deployment, clinical/human data, outreach or publication. **NO-GO** remains unchanged.

## Changes committed
- `apps/web/src/science.ts` now prevents conflicting aggregates for one deterministic run identifier (using explicit field-wise comparison independent of JS property insertion order).
- The display-only four-node P13 graph text now rejects duplicate node IDs, wrong source parents, missing edges, multiple/repeated edges, and out-of-order node kinds. **This is NOT cryptographic proof**: the Python verifier remains authoritative for metadata SHA-256 and root checks.
- `apps/web/tests/science.test.mjs` extends negative tests for chain topology and run identity.
- New `apps/web/tests/client.test.mjs` tests private origin/URL validation, browser same-origin, no-token and malformed run-ID fail-before-network, no-store/no-credentials GET, JSON POST without retries, and error-body/secret non-disclosure.
- Manual CI workflow now uses `npm ci --prefix apps/web --ignore-scripts --no-audit --no-fund` from the existing committed npm lockfile, then `npm run test --prefix apps/web` for the full typed client/science suite. Manual-only `workflow_dispatch` is preserved. Workflow **was not dispatched**.

## Observed local test evidence (not GitHub Actions)

Reconstructed scoped checkout in isolated local working directory, Node **22.16.0**, global `tsc` **5.8.3** (committed npm lockfile targets **5.9.3**, not installed/retested in this local run).

```bash
cd apps/web
tsc -p tsconfig.build.json
node --test tests/*.test.mjs
# 9 tests passed; 0 failed
tsc --noEmit -p tsconfig.build.json
# success
```

All **four** scoped TS files compiled/exercised locally match the corresponding GitHub private branch blobs exactly after updates:

| Path | Observed exact Git blob SHA |
| --- | --- |
| `apps/web/src/client.ts` | `9b8b592a5dc89bc129e809bf004d16152ce3b194` |
| `apps/web/src/science.ts` | `f23426a5ba7e60d5877ced57cecbf68e71a22bcd` |
| `apps/web/tests/client.test.mjs` | `3128ab840a759e81fc8a6c20c2c7ba5bf7d64fc1` |
| `apps/web/tests/science.test.mjs` | `ac6aef1e791110969da0e8a0036cc339e9f52aa2` |

The test output is for these files, not a complete repository clone or installed locked-dependency CI environment. JS fetch is stubbed for client unit tests; no real network/auth/browser execution is implied. Workflow syntax/locked npm installation is source-reviewed but **not observed in a runner**.

## Blocking acceptance gates

- No exact-HEAD **hosted** Python 3.11/3.12 and TypeScript lockfile/CI PASS; older W03 Actions cannot validate current W04 source.
- No full exact-HEAD Python pytest/Ruff/mypy, Docker image and migration/rollback rehearsal, SBOM/CVE/audit, performance under concurrent traffic, or independent accessibility/screen-reader verification.
- Static demo still uses CSP `unsafe-inline`; enterprise IAM, independent signed provenance and legal rights attestation absent.
- Synchronous W03 fit is not an interruptible, crash-resumable worker; P25-v2 job-state authorization and real process crash/restart equivalence need separate exact-source tests.
- Browser UI uses inline JS, not the compiled typed SDK; TypeScript tests do not establish that UI↔API contracts render correctly.

This work narrows TypeScript scientific display and client regression gaps **only**. Preserve draft/no-release status and require independent human review before any merge or externally visible claims.
