# W04 integration slice — experimental, unreleased

Date prepared: 2026-10-19. Scheduled W04: 2026-11-05.
Branch is unmerged and does not certify release readiness.

## Contract DAG
Source dataset → P25 rights authorization (fail-closed) → P1 participant-split validation → P13 canonical JSON event + SHA-256 integrity digest → review/export.

## Implemented here
- P25 typed decision with explicit verified rights, revocation, human-data authorization, action scope and source-hash formatting.
- P1 group-overlap/duplicates/empty-partition sentinel.
- P13 event integrity hash on serialized event; negative tamper check.
- Synthetic only; contract versions p25.v1 and interop.v1.

## Commands
`python -m pytest -q tests/test_w04_interop.py`
`python -m ruff check src/psychneuro/rights_v1.py src/psychneuro/interop_v1.py tests/test_w04_interop.py`
`python -m mypy --strict src/psychneuro/rights_v1.py src/psychneuro/interop_v1.py`

## Critical limitations
- A SHA-256 digest is tamper-evident only relative to an independently trusted digest; an adversary who rewrites both can forge it.
- Rights verification is a caller-supplied boolean: not evidence of a valid license or a complete legal consent/ethics workflow. Human datasets remain out of scope.
- No distributed persistence, revocation propagation, signatures, encryption, durable jobs, independent oracle, scientific estimation, UI, production API, load test or deployed E2E.
- `accuracy` here is an input fixture, not a measured model result.
- Review threat boundaries and authenticate dataset authorization before integrating with any real inputs.

## Next gates
1. Attach a validated, immutable rights attestation and approval provenance, with negative policies for NC/ND/SA and purpose constraints.
2. Wire P1's actual benchmark outputs and P13 signed/checkpointed provenance store to this contract.
3. DB migrations, API, browser display, group split verifier against raw inputs and independent statistical baseline.
4. CI review on branch, property/adversarial tests, artifact comparison, restore/restart, safe rollback, independent review, approval before public release.

Release decision: **NO-GO**.
