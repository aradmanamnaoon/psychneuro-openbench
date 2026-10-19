# W04 Chat 2 strict P25-v2/P1/P13 integration — additional implementation evidence

**2026-10-19. Private only, no merge or deployment. Release NO-GO.** This document supplements `CHAT2_PRODUCT_VALIDATION_HANDOFF.md`; older evidence describes the pre-hardening version.

## Implementation on PR #18

- `src/psychneuro/w04/durable_bridge.py`: short-lived scoped v2 P25 permits; P25 source SHA pinned to the exact synthetic generator configuration and original W03 registry; post-fit/pre-persistence revalidation.
- `src/psychneuro/w04/policy_snapshot.py`: validated P25 policy snapshot lookup, verifies the event chain and stored hash chain; no client-side rights attestation accepted.
- `src/psychneuro/w03/service.py`: optional `before_persist` callback for a permission check after fitting and before calling the existing immutable P13 `RunStore.put`. W03 calls without this argument remain unchanged.
- `src/psychneuro/w04/strict_facade.py`: opt-in FastAPI 0.4.3, separate from legacy product tests; server-side internal actor mapping, tenant/owner guard, synthetic W03 grouped benchmark, P13 graph and split, receipt import/export/verify and comparisons. The strict app exposes no v1 endpoints or compute worker.
- `src/psychneuro/w04/server_strict.py` and Dockerfile: the container starts only with TWO independent 32+ character secret values (browser operator token and P25 HMAC permit key). It installs no grant automatically.
- `src/psychneuro/w04/provision_private.py`: explicit privileged operator-only command, original synthetic fixture identity, attestation reference and 24-hour grant; no public or human data grant.
- `tests/test_w04_strict_product.py`: source-based positive acceptance plus tamper, wrong seed, missing token and revoked policy tests. **Not executed on the complete repository SHA**.

## Operator-only local rehearsal (NOT executed)

```bash
cp .env.example .env
# Put independent freshly generated values in W04_PRIVATE_TOKEN and W04_P25_PERMIT_KEY.
docker compose --env-file .env build
docker compose --env-file .env run --rm --no-deps api \
  python -m psychneuro.w04.provision_private \
  --operator private-reviewer --attestation-ref fictional-fixture-reviewed-v1 \
  --acknowledge-internal-only
docker compose --env-file .env up -d
curl -fsS http://127.0.0.1:18080/health
docker compose --env-file .env down
```

No real dataset, no external host port, no third-party secrets, no logged tokens. Operator must verify source ownership, SHA, consent applicability and permissions before signing off; the `attestation_ref` is descriptive internal metadata, not legal rights evidence. Newly issued permits expire within 60 seconds. This first implementation authorizes only one exact source configuration per tenant; alternate seeds/participant counts are denied until an appropriate separate operator grant. A revoked or expired grant is denied on subsequent reads and before W03 storage, but persistence across crash during fit is not a worker checkpoint.

## Observed tests, with limits

- Local **isolated** `/mnt/data/w04_chat2` TypeScript `tsc -p apps/web/tsconfig.build.json` returned exit 0; `node --test apps/web/tests/science.test.mjs` reported **4 passed, 0 failed** on Node 22.16.0. This excludes the private checkout's `client.ts` and all new strict Python source.
- Local one-thread presentation-helper microbenchmark, 10,000 iterations, warmup 1,000, AMD EPYC 9V74: **median 0.952 μs, p95 2.453 μs, RSS 32,768,000 B** on this run. It is not API latency or browser load. Earlier CSV 1.141/2.383 μs reflects a different local run.
- Full Python 3.11/3.12 `pytest`, Ruff, mypy, native TypeScript SDK build, Docker build/migration, actual browser keyboard/axe/assistive technology, HTTP performance, SBOM/vulnerability inventory, provenance trust anchor, and real job-worker recovery: **NOT RUN / BLOCKED**. No W04 GitHub Actions workflow was dispatched by Chat 2.

## Important remaining defects and security work

1. Existing browser catalog script expects `catalog.datasets[0].id` while strict facade presently returns `catalog.dataset_id`; the *rights-preview* browser flow needs a contract-alignment fix and an actual walkthrough before claiming UI success. Do not hide this discrepancy.
2. Existing inline script/style CSP remains `unsafe-inline`; no actual WCAG certification or screenshot was produced. Static internal access tokens are not production IAM.
3. Durable v2 jobs have leases, fences, cancellation/retry and metadata checkpoints, but **no active computation worker** and no interrupted-fit resume equivalence. The strict UI deliberately removes older metadata job controls rather than pretending they cancel fitting.
4. SHA chain receipts are tamper-evident only relative to a trusted externally retained root; there is **no independent signature**. P25 local attestation is not a rightsholder license.
5. Comparison is descriptive only (same-source fictional participants); no p-value, confidence interval or large-scale claim.
6. W03-run insertion followed by separate tenant ACL claim is not one atomic transaction; a concurrent cross-tenant same-run identity may consume CPU before denial. Strict facade denies access but atomic ownership and reconciler need more work.
7. No pinned Python transitive hashes, Node lockfile or actual SBOM/CVE scan. Use manual GitHub workflow only when the owner has verified free runner availability and approves it.

## Chat 3 gate

Re-run exact-head full Python/TS checks, fix browser catalog contract, assert replay/idempotency and cross-tenant ownership on real W03 source, prove revocation during fitting prevents persistence, test corrupt SQLite/receipt import, add and validate real fenced worker and cancellation, run real local-only browser/axe and Docker with CPU/perf sampling, inspect original GA1–GA8 draft evidence. Keep sole W04 Career card on **2026-11-05**, `Done=unchecked`; Academy unchanged, learner combined <=10h/day.

**Conclusion: IMPLEMENTATION PARTIAL / NO-GO. No W04 hosted PASS, real-browser proof, actual worker recovery, clinical validation or release.**
