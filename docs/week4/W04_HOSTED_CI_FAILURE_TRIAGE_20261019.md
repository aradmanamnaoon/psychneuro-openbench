# W04 hosted Python CI triage — observed ancestor run 2026-10-19

**Scope warning:** GitHub Actions [run #39282517739](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39282517739) executed **ancestor Chat3 source SHA `1bf73f96c03b2e7c5a81fc4313da0b06b37f90de`**. This is **NOT** an exact unified branch result. It triggered on a private review-branch push; no publication or deployment.

## Observed hosted results

| Job | Environment | Pytest | Ruff | Mypy | Whole job |
| --- | --- | --- | --- | --- | --- |
| review (3.11), job 118159420899 | Python 3.11.17 | **467 passed in 8.75s** | 2 errors | not reached | **FAILURE** |
| review (3.12), job 118159421203 | Python 3.12 | **467 passed in 14.66s** | 2 errors | not reached | **FAILURE** |
| typescript-science, job 118159421211 | Node 22.23.3, committed lockfile workflow | **4 TS tests passed** | n/a | n/a | **SUCCESS** |

Python jobs failed during `python -m ruff check .`; all 467 Python tests were already green on the ancestor. The workflow shell `set -e` did **not** execute `mypy` after the Ruff failure, so no hosted mypy PASS exists.

### Root-cause details from both hosted logs

Exactly two Ruff findings were observed in `benchmarks/measure_w04.py`:

1. **I001** — source import ordering. `from psychneuro.w04.rights import Action, Principal, W03_INTERNAL, decide` must be `W03_INTERNAL, Action, Principal, decide`.
2. **F401** — unused `import statistics`.

Both were corrected in the new **unified private review branch** commit `4e9f8cdd604b4c1c36129ec53fc3c134533faf0b`, without touching benchmark computation. **Fix not retested on GitHub; no green CI is claimed.**

The unified source adds worker router, strict non-inline browser CSP, atomic sync tenant ownership and new tests not present in the run above. **Its complete Python tests, lint, type check and browser/Docker are still unverified.** No independently attested P25 rights, signed signer identity or human study. Maintain **NO-GO**.

## Evidence links

- [Hosted Actions run](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39282517739) (source SHA immutable).
- [Private reconciled review PR](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/24).
- [W04 unified handoff](W04_UNIFIED_PRIVATE_HANDOFF_20261019.md).

**Repeat exact-HEAD CI under an entitlement-verified, explicitly free/private runner before any release gate can pass.**
