# Offline scientific evidence reviewer · W04

**Private, synthetic-only development tool. Not clinical, independently authenticated,
or approved for unlicensed/human participant data.**

The reviewer accepts an already-authorized W03 aggregate record (not trial rows)
and produces a portable, local HTML, Markdown, or JSON evidence summary.
It reads existing files and does not access the network.

## Why it matters

A score without its independence unit, provenance and baseline is easy to
misinterpret. The reviewer surfaces the grouped dummy baseline, nested outer
balanced accuracy, sealed held-out result, group counts, regularization choice,
source digest, split digest, run digest and provenance root.

## Quickstart

Run this only in a private checkout containing W03 and W04 source.

~~~bash
python -m pip install -e '.[w03,benchmark,dev]'

python -m psychneuro.w04.reviewer \
  --record private-w03-aggregate.json \
  --format html \
  --output internal-review.html

python -m psychneuro.w04.reviewer \
  --record private-w03-aggregate.json \
  --compare second-authorized-aggregate.json \
  --format markdown \
  --output internal-comparison.md

python -m psychneuro.w04.reviewer \
  --record private-w03-aggregate.json \
  --format json \
  --output internal-review.json
~~~

The files must be real W03 private synthetic records obtained from an approved
internal environment, not the raw participant-level dataset and not an invented
JSON example. The root can optionally be checked against a separately obtained
known checksum using `--expected-root`. Do not confuse a supplied root from
the same document with independent authenticity.

## Accepted contract

- Exactly four P13 source/split/model/benchmark nodes in a valid ordered chain.
- The existing W04 receipt verifier checks version, model metadata, rights,
  run fingerprint, split and source relationships and reported scores.
- The typed W03 result is additionally validated with `RunResult`.
- At most 250,000 bytes of UTF-8 JSON with unique keys and finite numbers.
- Original fictional synthetic source only, never real participant records.

The input reader refuses symlinks and oversized files. The output writer
creates a new file exclusively and uses 0600 permissions on POSIX. Existing
reports are not silently replaced. CLI errors do not print record content.

The HTML is standalone, has a restrictive CSP and uses escaped content. It
loads no JavaScript, external style, image, font, CDN, tracking or API.

## Interpreting two runs

When source and participant-split SHA-256 match, differences are **descriptive
only**. Without paired trial/participant-level predictions, there is no valid
paired hypothesis test or confidence interval. If the source or split differs,
the report explicitly warns that the two numbers are **not a controlled
head-to-head comparison**. Do not rank models by that difference.

## Important trust limits

| Verified locally | Not guaranteed |
| --- | --- |
| JSON structure and size | Who authored the bytes |
| SHA-256 graph consistency | A trusted external digital signature |
| Synthetic version/rights claim | Actual authorization/consent |
| W03 statistical metric constraints | Human/clinical validity |
| Participant split identity digest | Original dataset integrity outside the record |
| Static report XSS escaping | Accessibility tested by a real screen reader |
| Non-overwriting local output | Encrypted storage or secure remote deployment |

Hashes do not prevent a malicious producer from coherently replacing both the
data and hashes. The optional Ed25519 anchor verifier in
`src/psychneuro/w04/anchor_v1.py` requires externally retained public keys
and monotonic sequence floors; this reviewer intentionally does not assume
such a trust channel exists. Operator P25 permissions are required *before*
receiving and sharing records. The CLI itself grants no rights.

## QA

~~~bash
python -m pytest -q tests/test_w04_reviewer.py
python -m ruff check src/psychneuro/w04/reviewer.py tests/test_w04_reviewer.py
python -m mypy src/psychneuro/w04/reviewer.py
~~~

Negative cases include malformed/duplicate/nonfinite JSON, tampered science,
wrong trust root, oversized input, symlink input, output overwrite, permissions,
and source/split mismatch. **Tests have been added; exact-head CI success is not
yet claimed.** Verify actual logs before any release decision.

See the [scientific protocol](spec-v0.md), [source](../src/psychneuro/w04/reviewer.py),
[tests](../tests/test_w04_reviewer.py), [W04 independent reviewer packet](week4/W04_INDEPENDENT_REVIEWER_PACKET.md),
and [release gates](release-gates.md).
