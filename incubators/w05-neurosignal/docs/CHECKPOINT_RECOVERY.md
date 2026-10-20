# W05 checkpoint recovery contract — reviewer addendum

## Boundaries

`CheckpointStore` provides single-host SQLite transactional persistence of P26 `CausalFIR` state. Key `(tenant, stream_id)` identifies the state. Stored data contain schema-versioned coefficients, channel count, filter delay line, next sample position, and SHA-256 of a canonical JSON payload.

**Explicitly NOT claimed:** distributed exactly-once semantics, output commit coordination, signed provenance, multi-tenant authorization by itself, automatic retry scheduling, replicated state, cross-process performance SLA, or clinical fitness. The caller MUST authenticate the tenant, use trusted stream identifiers, and ensure each input block is processed only once from the last committed source position.

## Recovery protocol

1. Obtain an exclusive per-stream lease through the existing fenced job store (external requirement: couple lease token to checkpoint writes before distributed deployment).
2. Resolve tenant and stream from authenticated application identity, not arbitrary user-supplied headers.
3. Open `CheckpointStore`; restore using the expected FIR coefficients and channel count, rejecting mismatches.
4. Resume source input from `restored.next_sample`. Do NOT replay earlier blocks to the restored filter.
5. Process a chunk, commit its output to an idempotent destination, then commit checkpoint. On a crash between output and checkpoint, replay and upsert the output by stable chunk ID; otherwise delivery can duplicate.
6. On checkpoint integrity failure, stop and quarantine. Never silently rewind a production stream.

## Negative cases already encoded in tests

- Identical position + hash is idempotent.
- Identical position + different hash fails.
- Backwards sample position fails.
- Foreign tenant cannot read checkpoint.
- Different FIR coefficients or channel count fail.
- Corrupted SQLite payload fails digest validation.
- Reconstructed FIR output is compared to an independent time-domain convolution oracle.

## Remaining hard gates

Implement fencing-token-aware checkpoint transactions, output acknowledgements, crash/fault injection across processes, rights revocation and retention, encrypted storage/secrets, recovery instrumentation and RSS/latency load tests. Perform real accessible browser testing, independent neurophysiology/statistical review, licensed source-format checks, dependency locking/SBOM and verified clean deployment+rollback.

**Release decision: NO-GO** until all hard gates are verified. Historical CI status belongs to an exact commit SHA, not branch state; use the PR's newest Actions run for proof.
