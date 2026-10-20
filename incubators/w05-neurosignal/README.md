# NeuroSignal Atlas + EvalOps Rig + NeuroStream DSP Runtime — W05 private incubation

> **Private, synthetic-first, nonclinical developer preview.** This is an additive W05 isolated subtree for review, not an announcement of three finished products. No human data, clinical inference, auto-publication or unrestricted external ingestion.

## Real vertical slice

`P2 rights-gated metadata + lazy samples → P2 preprocessing provenance → P26 causal FIR chunk stream and independent O(NK) convolution oracle → P2 Welch PSD → P14 leakage preflight / independently grouped bootstrap CI → SHA-256 evidence JSON`.

The `run_synthetic()` example uses a known 10-Hz sinusoid with small seeded Gaussian noise, native volts and an explicit CC0 synthetic origin. Its P14 sample scores are **invented deliberately**, only to exercise evaluation plumbing; no empirical cognitive/neural result is asserted.

## Quickstart (from this folder)

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
neurosignal demo --seed 42 --samples 4096 --chunk-size 333 > /tmp/w05-evidence.json
```

Optional format adapters require `pip install -e '.[eeg,nwb]'`. Only manually approved *readable files* inside an explicitly selected root, with user-supplied SHA-256/license/authorization evidence, can be opened. No dataset URLs are fetched. NWB support is untested where PyNWB is absent; do not claim otherwise.

## API (loopback only)

```bash
export NEUROSIGNAL_LOCAL_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export NEUROSIGNAL_DB_PATH='./.private_w05/jobs.sqlite3'
export NEUROSIGNAL_LOCAL_TENANT='lab-A'
uvicorn neurosignal.service:app --host 127.0.0.1 --port 8010
```

`GET /openapi.json`, `POST /v1/demo`, `POST /v1/jobs`, `GET /v1/jobs/{job_id}`, and `POST /v1/jobs/{job_id}/cancel`. Except for `/healthz`/OpenAPI, endpoints require a bearer token plus `X-Tenant`. **The job API has an idempotent durable queue but no always-running hosted worker**; `neurosignal worker --db ... --tenant ... --job ...` manually performs a *fixed* synthetic demo. The worker reads the queued synthetic demo parameters; it is a single-process operator-invoked worker, not a continuously running scheduler or arbitrary signal-job runtime. This is explicitly a backlog item.

## Scientific limitations

- Zero-phase filtering, offline bad-channel interpolation, ICA, referencing policies, baseline-corrected ERPs, STFT significance testing and resampling are not implemented. Only causal FIR is chunk-boundary invariant; average reference must use stable good-channel selection.
- MNE may upsample EDF channels with mixed physical sample rates. Reject or separately normalize mixed-rate inputs in production rather than assuming metadata checks can infer original sampling rates after import.
- NWB ecephys is not equivalent to human-scalp EEG; metadata distinctions and electrode positions require a future NWB ontology and real rights-reviewed fixture.
- Percentile bootstrap CIs here target mean *group-level synthetic score*, not calibrated classification probability nor rigorous subject-level hypothesis tests. Sparse samples and model selection invalidate naïve uncertainty claims.
- SQLite durable transitions are local/single-node; no distributed worker pool, production identity provider, replay-safe arbitrary signal checkpoints or remote backpressure gate is provided.
- This isolated subtree does not alter the W04 P1/P13/P25 core, and no public release or merge is authorized.
