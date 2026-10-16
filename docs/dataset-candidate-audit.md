# PM-04 — Versioned research dataset rights and suitability audit

**Reviewed:** 2026-10-16 (official landing-page metadata; not raw files). **Decision:** only original, reproducibly generated synthetic data may enter the v0 benchmark. The six sources below are *candidates for future adapters*, not six approved ingested datasets. The rights observations do not establish ethics approval for this project, a safe target variable, or participant-level data cleanliness.

## Six concrete sources — published metadata, not permission to ingest

| Dataset and fixed snapshot | Modality / known task | Participants; published size | Snapshot's posted data license | Verified variables vs unknown event fields | Restrictions / decision |
| --- | --- | --- | --- | --- | --- |
| [ds000001 v1.0.0](https://openneuro.org/datasets/ds000001/versions/1.0.0) | fMRI / balloon analogue risk task | 16; 133 files, 2.25 GB | CC0 on snapshot; older README mentions PDDL | Published task and `participants.tsv` filename; **trial response/onset column names not inspected** | Full fMRI dataset, rights metadata only; exclude real-subject ingestion |
| [ds000003 v1.0.0](https://openneuro.org/datasets/ds000003/versions/1.0.0) | fMRI / rhyme judgment | 13; 57 files, 391.09 MB | CC0 on snapshot, older README PDDL | Published task and `participants.tsv`; **event columns unverified** | Snapshot reports BIDS validation error; require event/label audit |
| [ds000005 historical snapshot](https://openneuro.org/datasets/ds000005/versions/57fed2b8cce88d000bc17596/metadata) | MRI/BOLD / mixed gambles | 16; **snapshot size not established** | Historical snapshot reports PDDL 1.0 | Gain/loss choice task described in [OpenfMRI](https://openfmri.org/dataset/ds000005/); **exact per-trial columns not inspected** | Snapshot has no minted DOI in displayed record; cannot safely map task labels without file review |
| [ds000007 snapshot 00001](https://openneuro.org/datasets/ds000007/versions/00001) | MRI / Stop Manual, Stop Vocal, Stop Word | 20; 442 files, 3.26 GB | PDDL 1.0 | Published task names and `participants.tsv`; **stop-signal trial/response columns unverified** | Snapshot BIDS error; discussions mention item identifiers missing; reject for immediate tabular benchmark |
| [ds000008 snapshot 00001](https://openneuro.org/datasets/ds000008/versions/00001) | MRI / conditional/unconditional stopping | 14; 192 files, 2.01 GB | PDDL 1.0 | Published task names and `participants.tsv`; **event columns unverified** | Snapshot BIDS error, historical missing-onset correction; no ingest |
| [ds000117 v1.0.4](https://openneuro.org/datasets/ds000117/versions/1.0.4) | MRI + MEG / face recognition | 16, two sessions; **snapshot size not established** | CC0 on snapshot | Published face-recognition task; **event columns unverified** | Multimodal source vastly exceeds v0 tabular scope; no ingest |

**Meaning of "variables":** the table records observable task labels and published file *names* only. It intentionally does not assert that any `events.tsv` contains fields `response`, `correct`, `difficulty` or `response_time_ms`. Those are *our synthetic schema columns*, not established columns from these six real datasets. Participant counts are OpenNeuro metadata, not verified usable sample sizes after missing-data exclusions. Sizes reflect the version's landing page where available; an unspecified size is **unknown**, not zero.

## Actual rights and consent boundary

1. Public OpenNeuro snapshot rights are stated as CC0 or historical Open Data Commons PDDL. These labels generally support broad copyright/database use, but are **not** a statement about consent, privacy, institutional research authorization, suitability, completeness, or a waiver of ethical responsibilities. CC0 is not a blanket permission to republish identifiable data or to attempt re-identification.
2. The [OpenNeuro FAQ](https://docs.openneuro.org/faq), [public dataset guide](https://docs.openneuro.org/user-guide/), and [dataset portal](https://openneuro.org/) state versioned snapshot and licensing rules. The sign-in terms include an undertaking to have appropriate institutional permissions for secondary analysis and not to re-identify participants. These have **not** been attested to for this project; no download or real-data transformation took place.
3. Older README text may say PDDL while later version-specific metadata says CC0 (e.g. ds000001/ds000003). This is recorded as a **version-history rights discrepancy**, not silently merged into a single global license.
4. Reuse must preserve provenance, source-version citation, any requested scholarly acknowledgements, and applicable privacy/consent and institutional rules. A paper citation, DOI, or a public license **does not** verify the event-file semantics or grant permission to claim clinical/behavioral validity.
5. [ds000030](https://openneuro.org/datasets/ds000030/versions/1.0.0) has neuropsychiatric context; explicitly excluded from the nonclinical initial scope.

## Decision record for P1-015

**ACCEPT as sole enabled v0 source:** `psychneuro-synthetic-v0`, an internally generated toy task with invented subjects and responses. `source_kind=synthetic`, `rights_basis=synthetic-original`; the external candidate entries are registered only as **disabled metadata**. Synthetic records are not from real participants, so participant consent is **not applicable to this generated dataset**. This does not confer a separate public dataset license: `license=not-separately-specified`. Code is Apache-2.0, but original generated records do not automatically inherit that software license. A SHA-256 of the exported CSV bytes is included in each generated dataset card, not in the static catalog.

**NO-GO for real data:** no downloading, auto-fetch, CSV parsing, external feature mapping, redistribution, participant outcome modeling, scientific estimation, medical research inference or publicity on any of the six sources. The [registry](../data/registry.json) is a discovery ledger, not an approval manifest. The code-level [registry loader](../src/psychneuro/registry.py) fails closed on attempts to enable human-source entries.

**Next real-data admission gate:** choose one versioned source *after* explicitly documenting applicable secondary-analysis authorization, consent/ethics conditions, snapshot-specific license/terms, privacy review, BIDS validity, task event columns including missing values and response timing, leakage hazard, participant grouping, transformation recipe, a safe, version-pinned source checksum and any required citation. Perform a separate authorization review before ingesting even one real row.

## Evidence and limitations

Primary source: the six versioned [OpenNeuro](https://openneuro.org/) pages above, plus [OpenNeuro access documentation](https://docs.openneuro.org/api.html) and [BIDS specification](https://bids-specification.readthedocs.io/). Snapshot page figures were independently checked, but event files, sample-level consent attestations and exact downloaded bytes were **not** reviewed. No human participant records are stored in the repo. CI of these new registry changes is not implied by older PM-02/PM-03 runs.

**Review gate:** synthetic-only development is authorized in the private repository; external data, clinical applicability and public release remain NO-GO.
