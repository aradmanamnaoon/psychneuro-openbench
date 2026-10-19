# W04 private research-experience delivery · 2026-10-19

**State:** implemented on a new private review branch; **DRAFT / NO-GO / no merge or release**.

Parent integration branch: `review/w04-unified-private-20261019`, head observed
`6e1867ac8adbe7cf10f0b3df2eb43bca9bb698cb` at branch creation.
This continuation is additive to the existing integrated W03/W04 work and
does not silently merge earlier divergent research branches into `main`.

## Why these changes

The original default-branch README described a limited synthetic generator.
The W04 unified branch already contained much more Python/TypeScript software,
but its README continued to refer to many implemented components as future work.
Scientists also lacked a simple network-free way to inspect internally
authorized aggregate evidence with clear caveats.

## Changes in this review slice

- Replaced the repository README with an accurate, engaging architecture and
  onboarding landing page, synthetic W03 walkthrough and W04 hard-gate summary.
- Added a bounded read-only W03 aggregate reviewer, producing attractive,
  accessible, standalone HTML plus JSON and Markdown exports.
- Reused the existing W04 strict P13/P25 receipt verifier and W03 Pydantic
  scientific-result contract rather than inventing an incompatible record.
- Added explicit source/split mismatch warnings for descriptive comparisons.
- Added synthetic security and correctness regression tests, including bad JSON,
  duplicate keys, nonfinite values, mutation, symlink refusal and private writes.
- Corrected an existing Python development dependency typo from `httpx2` to `httpx`.
- Documented operator trust obligations and the reviewer interface in
  `docs/offline-reviewer.md`.

## Code-size evidence

Prior integrated W04 source tree (SHA cited above): 113 tracked `.py`, `.ts`
or `.mjs` files in total, including application source, executable benchmarks,
test code and one upstream prototype. Counting each file's newline-delimited
lines through the connected GitHub file/blob reader gave:

| Source-file index | Lines |
| --- | ---: |
| 0–18 | 2,609 |
| 19–37 | 2,464 |
| 38–56 | 2,679 |
| 57–75 | 2,863 |
| 76–94 | 2,536 |
| 95–112 | 2,156 |
| **Total before review slice** | **15,307** |

The new Python reviewer and tests add ~492 tracked code lines, putting the
private integrated feature line at about **15,800 lines of Python/TS code and
tests**. This is not a measure of code quality, feature completeness or total
production-ready code. It excludes the README, docs, assets and config; it
includes test code, comments and blank lines.

## What has / has not been verified

**Observed in this continuation:**
- GitHub existing private branch metadata, files and source contracts fetched.
- New reviewer, negative tests, docs and README committed to GitHub.
- Connector-level comparison of feature branch vs parent reports no behind
  commits and only the intended five changed paths.
- Prior 113 code file contents were fetched in bounded batches for the count.

**Not observed on the exact feature-branch head:**
- `pytest`, `ruff` or strict `mypy` return codes;
- Python 3.11 and 3.12 clean environment installation;
- browser keyboard/axe/screen reader/mobile tests;
- reproducible fitted-worker crash/restore/provisioning test;
- signed root authenticity, operator rights approvals or source export rights;
- production security, load/performance and dependency scanning;
- independent scientific reviewer approval.

Historical W04 ancestor hosted successes and failures may be consulted through
the W04 PRs, but **are not** exact-head verification for this implementation.
Do not mark the review work or project release complete based on code volume.

## Remaining release blockers

1. Full exact-head hosted Python and TypeScript test/typing/security logs.
2. Physical worker interruption and SQLite backup/restore against this exact
   integrated code state.
3. Independently held provenance signer roots, rights authority and licensing.
4. Actual secure private deployment and user-facing accessibility verification.
5. Independent methods/security review and separate explicit release decision.

The repository remains PRIVATE. No human/third-party dataset was downloaded,
no paid compute initiated, no public host deployed, and no GitHub `main`
commit or release tag was altered.

Related: [release gates](release-gates.md),
[reviewer guide](offline-reviewer.md),
[W04 independent handoff](week4/W04_INDEPENDENT_REVIEWER_PACKET.md).
