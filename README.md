# PsychNeuro OpenBench

**Experimental, private, nonclinical research software. Not a release.**

PsychNeuro OpenBench aims to give psychology methods students, computational
neuroscience research assistants, and ML reproducibility reviewers a transparent
behavioral ML benchmark pipeline: safe trial schemas, subject-held-out splits,
transparent baselines, reproducible artifacts, and documented source rights.

**PM-02 provides only the typed synthetic-foundation vertical slice:**
- Standard-library synthetic binary choice-task trial generator with isolated
  deterministic seed and explicitly invented parameters.
- 24 × 2 × 10 default synthetic trials, composite participant/session/trial IDs,
  declared pre-response predictors, binary correctness and reaction-time metadata.
- Canonical UTF-8 CSV bytes and synthetic dataset provenance card.
- Draft schema, code provenance and licensing policy; authored test fixtures.
- GitHub Actions workflow configured for **manual execution only** until billing
  quota and authorization are checked. No CI success is claimed from its presence.

The scientific requirements contract is at [docs/spec-v0.md](docs/spec-v0.md).
All generated outcomes/latencies are fabricated and are **not** measures of real
human behavior, clinical efficacy, psychology effect sizes or patient diagnosis.

### Example (only after an authorized Python installation)

\`\`\`python
from psychneuro import generate_reaction_times, make_dataset_card, to_csv_bytes

trials = generate_reaction_times(seed=42)
assert len(trials) == 480
card = make_dataset_card(trials)
csv_data = to_csv_bytes(trials)
\`\`\`

No real participant or patient data should be processed in this v0 milestone.
The model/evaluation pipeline, group split validator, real-data adapters and
published reproducibility guarantees do **not** exist yet.

**Licensing:** Not released or openly licensed; see
[docs/license-policy.md](docs/license-policy.md). No website/profile claims or
public publication authorized.
