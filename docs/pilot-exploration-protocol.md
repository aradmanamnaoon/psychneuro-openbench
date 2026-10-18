# PM-06 — reproducible synthetic pilot exploration

**Status: IMPLEMENTED SOURCE / NOT EXECUTED.** This is an execution
protocol, NOT an analysis report. Do not invent output statistics, hashes,
figures, log lines, success statuses or GitHub Actions run IDs.

## Source and analysis plan

Input is the [in-repository generator](../src/psychneuro/synthetic.py) only.
The rights-gated [loader](../src/psychneuro/loaders.py) checks original
synthetic provenance, schema, integrity and quality before any summary.
Source parameters are fixed: seed **73**, 12 invented participant IDs, 20
invented trials per ID, one session each. **240** is a design-derived
expected record count, not an observed executed result. Schema and generator
revision: 0.1.0. No network dataset download or human records.

The [exploration module](../src/psychneuro/explore.py) computes:
counts and fractions correct by artificial difficulty; invented latency
mean/median by difficulty; aggregate accuracy, latency and validator
counts; a source manifest with dynamically computed canonical CSV hash.
The SVG chart explicitly labels results as invented software fixtures.

## Hosted execution plan (NOT RUN)

The following steps are intended for an approved hosted GitHub Actions job
on the exact PM-06 commit. They must not be represented as completed until
there is a matching run with reviewed job logs.

~~~bash
python -m pip install --disable-pip-version-check -e '.[dev,parquet]'
python -m pytest -q
python -m ruff check .
python -m mypy src
python -m psychneuro.explore --seed 73 --participants 12 --trials-per-participant 20 --registry data/registry.json --output-dir artifacts/pm06
~~~

Expected output *paths*, which do not constitute evidence of execution:
- `artifacts/pm06/summary.json` — observed aggregate and grouped summaries
- `artifacts/pm06/manifest.json` — observed source URL, rights boundary,
  generator revision, seed, source hash and transformations
- `artifacts/pm06/difficulty_summary.csv` — aggregate grouped data
- `artifacts/pm06/accuracy_by_difficulty.svg` — aggregate synthetic-only figure

A real run must record exact Git SHA, branch/ref, workflow URL, job IDs,
Python version, test count and skips, Ruff/mypy outcomes, artifact checksums,
and the observed manifest. For generated input the raw-file SHA must be
`null`; it must **never** be invented. Count checks include:
`sum(difficulty_groups.n_trials) == summary.n_trials` and
`summary.n_trials == manifest.n_trials`.

## Scientific interpretation and approvals

Plots, invented response times, and accuracy are not evidence about actual
human cognition, neurological processes, clinical outcomes, or model
generalization. The analysis uses no random train/test split and reports no
predictive model score. The current CI workflow is manual-only to avoid
unattended private-runner charges. Triggering hosted CI is contingent on
an authorized GitHub Actions dispatch capability and approved free/paid usage;
it is not silently turned on. No PR, publication, outreach or external data
ingestion is authorized by this document.
