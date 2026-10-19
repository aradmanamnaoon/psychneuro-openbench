# W04 Chat 3 — authenticated P13/P25 anchor verifier continuation

**Date:** 2026-10-19. **Private draft only. Overall NO-GO.**

## Implemented verifier, original test results and exact Git object check

Recovered an earlier Chat1 original-synthetic, offline Ed25519 verification source archive from the user's connected file Library. Checked the archive contents directly in a local isolated Python environment with Python **3.13.5**, Pydantic **2.13.5**, and `cryptography` **46.0.4**:

```text
PYTHONPATH=src python -m pytest -q tests/test_w04_anchor_v1.py
.................        [100%]
17 passed in 0.10s
```

The **exact, byte-for-byte Git blob objects** of the tested archive source and tests were compared with the newly committed GitHub private draft branch:

| File | Independent local and GitHub Git blob SHA-1 |
| --- | --- |
| `src/psychneuro/w04/anchor_v1.py` | `a94d7bc494c447948e4bad2e02687bca30fa5f6e` |
| `tests/test_w04_anchor_v1.py` | `304280fc708a47200e5b3d5f27a691784f8320bc` |

This **proves only** the local isolated 17-test Ed25519 verifier result on that source, *not* an entire W04 hosted matrix pass or the new guarded-import tests. In the repository, the private `anchor` extra and dev extra now request the separately versioned `cryptography==50.0.2`, which was **not** the cryptography 46.0.4 used for local QA; that pinned version requires its own hosted validation and software supply-chain scan.

### Verified verifier behavior in these isolated cases

- Explicit, independently supplied `key_id` → 32-byte Ed25519 public-key mapping; no keys selected from untrusted receipts.
- Signature verified over canonical, domain-separated bytes binding tenant/dataset/purpose, policy revision/hash, run ID, provenance root, receipt checksum, sequence and issued/expiry.
- Rejects mismatched receipt fields, corrupted signatures, unpinned keys, expired/future/overlong anchors, sequence rollback and improperly typed/malformed fields.
- Cryptographic *verification* only. The module neither issues signatures nor takes custody of a real root, determines legal data rights, grants consent, or signs records.

## Newly coded, NOT YET TESTED, integration boundary

`src/psychneuro/w04/receipt_guard_v3.py` adds `import_authorized_anchored`, which (1) matches a live P25 `read_aggregate` permit to the actual tenant/subject/dataset/purpose, (2) validates the live permit, (3) rejects obsolete policy revision, (4) validates the independently pinned Ed25519 anchor, (5) re-verifies receipt checksum, W03 graph, tenant, P25 policy checksum and externally signed P13 root, and (6) **revalidates P25 after the crypto/content work before returning an in-memory record**. It does not persist, expose a public endpoint, or enable human data import.

`tests/test_w04_anchored_receipt_guard_v6.py` adds synthetic signed success, wrong-key denial, post-verification revocation refusal and stale policy denial. These four new tests have **not been executed**; do not incorporate them in the above 17 PASS count.

## Missing trust boundary before any release

- Independent real signing authority/key handling (offline signer or HSM), authenticated public-key distribution and rotation (with revocation).
- Immutable, independently controlled monotonic sequence floor (not stored alongside the signature or in the same mutable SQLite database).
- Valid rights/consent/ethics/dataset grant from an authorized source, not a manually chosen string.
- Evidence that entire private application/export/import workflow rejects replacement of an entire coherent report plus root and consent claims, including real process fault recovery.
- Complete latest-HEAD CI and independent human scientific/security/accessibility reviews.

A successful local signature fixture is **not** a legal or scientific authorization. Keep PR DRAFT, the repository PRIVATE, no merge/release/deployment/outreach/human datasets, and W04 Notion Status In Progress, Done unchecked.

## Subsequent local scoped signed-import run (2026-10-19)

Reconstructed the newly integrated `receipt_guard_v3.py` deterministically from the archived Chat1 source and the committed additions and checked that its local Git blob SHA exactly matches GitHub `0529490b1c3fe96e9891c9cac4a4133d9ffa5fbc`. The added test module also matches its GitHub blob `53d60a989d972481e4250d79efda2fe3c154111b`. The anchor verifier source/test exact hashes and original `receipt_v3.py` module SHA also matched the GitHub private sources.

Executed on **Python 3.13.5**, local `cryptography 46.0.4`, Pydantic 2.13.5:

```text
PYTHONPATH=src python -m pytest -q tests/test_w04_anchor_v1.py tests/test_w04_anchored_receipt_guard_v6.py
.....................                                                    [100%]
21 passed in 0.11s
```

**Scoped evidence limitation:** the local `test_w04_receipt_v3.py` helper supplying synthetic `make_receipt` came from the Chat1 archive, while the current PR has a later version of that test helper. The 21-pass outcome is independently observed for the reconstructed source/test pair and synthetic helper, **not an exact-current-HEAD whole-repo 21-test rerun, nor pinned cryptography 50.0.2 validation**. The newly added four guarded-import checks are part of this 21 count (not an extra 21). All previously listed external key-custody/rights/release blockers remain.
