# W04 Chat 2 — private P1×P13×P25 product architecture / manual runbook

**Scheduled W04:** 2026-11-05–11; **implementation started 2026-10-19.** **Release NO-GO**. This is a dependent addition to the existing W03 engine and preparatory W04 code. No human, clinical, participant, or licensed third-party datasets.

## Grounded architecture and contract DAG

`W03 original synthetic registry → P25 explicit rights decision → W03 grouped train-only nested CV → immutable SQLite RunStore → P13 four-node source/split/model/benchmark SHA graph → W04 tenant/owner ACL → v2 HTTPS-internal REST read/compare/split/artifact → accessible browser`.

- P1: `ExperimentRequest` strict Pydantic (seed, groups, folds); `RunResult` (`w03-engine-1`) stores balanced accuracy, dummy baseline, fixed regularization, train/test group count and hashes. Requests are synchronous, *not cancellable workers*.
- P13: W03 `verify_serialized` checks parent ordering, four distinct node hashes and canonical digest; artifact `w04-envelope-1` checks checksum and payload before import/export. A matching SHA is **not** signer identity.
- P25: `p25-rights-1` server-controlled synthetic-only action grant with revocation, expiry, consent/source checks. No client-supplied license claim; no approval for raw data export.
- W04 v2: `/w04/v2/catalog`, `rights/preview`, `runs`, `runs/{id}`, `runs/{id}/split`, `runs/{id}/graph`, `runs/{id}/artifact`, `artifacts/verify`, `artifacts/import`, `compare`. Typed TS client lives at `apps/web/src/client.ts`. Machine errors use `w04-error-2` with `W04_FORBIDDEN/NOT_FOUND/CONFLICT/INVALID`; FastAPI request-validation and legacy v1 errors remain framework-shaped (compatibility gap).
- Tenancy: operator config assigns `Principal.tenant`, `subject`, `role`; claims immutable run ownership in `w04_run_acl`. Same-tenant owner or maintainer can read; import requires maintainer and matching claim; unknown/foreign run is denied. Cross-tenant identical deterministic run IDs collide (fail closed), not namespace-isolated. Existing v1 job API uses compound tenant+subject owner but there is **no** production multiuser auth/session, token rotation or storage encryption.
- Concurrency: W03 SQLite immutable run IDs, W04 SQLite transactionally allocated owner row and metadata job CAS revision. The claim and run insert are not in one transaction: crash/reconciliation gap **BLOCKED**. No worker, lease expiry/reclaim, job-computation cancellation or completed restart equivalence claim.

## Safe local-only run

```bash
cp .env.example .env
python -c 'import secrets; print(secrets.token_urlsafe(48))'
# Paste output into W04_PRIVATE_TOKEN in .env; never commit/log token.
docker compose --env-file .env build
docker compose --env-file .env up -d
docker compose --env-file .env ps
# Browser on same host only: http://127.0.0.1:18080
docker compose --env-file .env down
# Rollback code: stop, restore prior commit/image, preserve SQLite volume.
# No automatic destructive schema rollback; back up the named volume/DB before upgrade.
```

Image tag (`python:3.12.7-slim-bookworm`) and transitive dependencies are **not digest/hash locked**; Docker and smoke not run in this chat. Never expose the demo publicly, use real records, or interpret a GET /health as security readiness.

## Threat / accessibility / budgets

- UI semantic labels, descriptive tabular comparator, text graph, non-color-only state, visible focus, role status updates, responsive CSS, reduced-motion preference and `textContent` escaping. **No real browser/axe/screen-reader walkthrough performed**, so WCAG is an acceptance target, not certified.
- Unauthorized bearer requests, role denial, foreign tenant, overwritten/forged receipt, revoked grant, swapped SQLite graph, repeated/replayed IDs: require negative verification; host only on loopback; no third-party fonts, scripts or trackers; internal token entered at runtime and never saved. Existing inline JS CSP `unsafe-inline` is a **remaining hardening blocker**.
- Container CPU=1, RAM=768MiB, 128 PIDs, no public host port, 24–80 fictional groups and 8–40 trials/group; no load/capacity guarantee. O(participants×trials×folds×candidate fits) training cost; dashboard table O(2) runs, DAG four nodes.
- CI is manual `workflow_dispatch` to avoid unapproved compute; prior W03 SHA tests are historical only. No hosted v2 tests or perf claimed.

## Scientific interpretation

Model and dummy outer grouped balanced accuracy share folds; sealed holdout test is a single fixed fictional split, not generalization to humans. Reusing a run on another random seed creates a descriptive comparison, **not** a paired uncertainty estimate or significance test. Train-only preprocessing, group isolation and right-source verification come from existing W03 code and must be rechecked at exact W04 head. The 36 fictional participants are not a large-scale sample.

## Migration and rollback

New `w04_run_acl` table created by SQLite `CREATE TABLE IF NOT EXISTS`; **no numbered migration framework**. Pre-existing W03 runs have no owner claim and are denied by v1/v2 reads until deliberately bound to a trusted principal; preserve original W03 DB and back it up before staging. Revert the code by resetting *a separate checkout* to previous commit after `docker compose down`; do not downgrade data blindly. Rights ledger, W03 storage, new ACL claim need independent multi-connection failure/recovery tests.

## Hard-gate inventory

Hosted exact SHA CI, real-browser keyboard/axe/screen-reader and mobile, Docker smoke, SBOM/lock/vulnerability scan, true CPU p95/load/RSS, worker restart equivalence, distributed migration rollback, production auth and legal review: **NOT OBSERVED / BLOCKED**. Nothing here authorizes merge/public deployment or scientific claims. This architecture/documentation is provisional until independent review.
