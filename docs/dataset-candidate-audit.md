# PM-04 — Dataset source rights and suitability audit

**Audit date:** 2026-10-16. **Decision:** v0 remains **synthetic-only**. This is a desktop review of primary *published dataset metadata*, NOT a download, integrity check of individual event files, human-subject ethical approval, or grant of permission to process participant records. Sources must be reconfirmed at the exact version before any real adapter work.

## Six specific public research data candidates

| Source / fixed version | Modality and task | Public metadata participant count | Size reported by source | Posted rights | Suitability for synthetic tabular v0 |
| --- | --- | --- | --- | --- | --- |
| [OpenNeuro ds000001 v1.0.0](https://openneuro.org/datasets/ds000001/versions/1.0.0) | MRI; Balloon Analog Risk-taking | 16 | 2.25 GB | CC0; historical README additionally mentions Open Data Commons PDDL 1.0 | **Not activated**; real participant fMRI, would require version-pinned trial/event extraction and feature-availability audit |
| [OpenNeuro ds000003 v1.0.0](https://openneuro.org/datasets/ds000003/versions/1.0.0) | MRI; rhyme judgment | 13 | 391.09 MB | CC0 | **Not activated**; incompatible imaging collection, event columns not verified |
| [OpenNeuro ds000005 archived snapshot](https://openneuro.org/datasets/ds000005/versions/57fed2b8cce88d000bc17596/metadata) | MRI; mixed gambles | 16 | **Unverified** | Historical README PDDL 1.0 (archive metadata) | **Not activated**; event schema and current snapshot status unverified |
| [OpenNeuro ds000007 archived snapshot](https://openneuro.org/datasets/ds000007/versions/00001) | MRI; spoken/manual stop-signal | 20 | 3.26 GB | PDDL 1.0 | **Not activated**; modality mismatch and per-event response fields need inspection |
| [OpenNeuro ds000008 archived snapshot](https://openneuro.org/datasets/ds000008/versions/00001) | MRI; unconditional/conditional stop-signal | 14 | 2.01 GB | PDDL 1.0 | **Not activated**; real data, no full column audit yet |
| [OpenNeuro ds000117 v1.0.4](https://openneuro.org/datasets/ds000117/versions/1.0.4) | MRI + MEG; face processing | 16; two sessions | **Unverified** | CC0 | **Not activated**; substantial electrophysiological data and imaging outside initial tabular scope |

**Observed source metadata** for these values is on each linked dataset page. Most sources are fMRI studies with behavioral tasks, not ready-to-use correctness-labelled synthetic CSVs. No direct claim is made about specific event-file variables before downloading/inspecting a *permission-cleared* small event file in a subsequent approved milestone. Terms, subject-level privacy considerations, event labels, quality and BIDS warnings require dataset-by-dataset review despite public listing.

### Explicit exclusions and hazards

- [OpenNeuro ds000030 v1.0.0](https://openneuro.org/datasets/ds000030/versions/1.0.0) reports 272 participants and behavioral task modalities with clinical-neuropsychiatric context. **Excluded from the nonclinical v0** regardless of CC0 metadata.
- A publication, DOI, CC0/PDDL label or OpenNeuro hosting is **not proof** that a given export is scientifically suitable for a new ML task, free of identifying details, or fully compliant with institutional ethics requirements.
- Software dependencies' licenses and dataset source rights are separate. Do not infer universal license grants; record rights per dataset version.
- No real dataset was downloaded, transformed, placed in GitHub, processed in CI, or added as `enabled` to the data registry.

## Selection decision

**Selected for v0:** original deterministic **`psychneuro-synthetic-v0`** generator, no patient/real participants, original synthetic records with declared rights basis and exact CSV bytes SHA-256. It is the only enabled source in [data/registry.json](../data/registry.json).

Why: supports subject-key and target-leakage engineering tests without real participant privacy risks or uncertain BIDS-event semantics. The v0 research specification requires no actual human performance claims. Public datasets are valuable later *only* after a separate rights/privacy/feature-timing/subject grouping gate.

**Next rights gate before real-source selection:** inspect the fixed snapshot's `dataset_description.json`, `participants.tsv`, representative `events.tsv` (without copying identifiable rows into repo), uploader terms, task response definitions, consent/ethics requirements, and transformations required for schema mapping; record a content checksum. If any of these are unknown, reject ingestion by default.

### Primary sources

- [Official OpenNeuro API and snapshot documentation](https://docs.openneuro.org/api.html)
- [OpenNeuro user guide on public datasets and versioned snapshots](https://docs.openneuro.org/user-guide/)
- [OpenNeuro FAQ and legal/privacy notes](https://docs.openneuro.org/faq)
- [BIDS specification](https://bids-specification.readthedocs.io/)

**No clinical diagnosis, treatment advice, patient records or public-release claim.**
