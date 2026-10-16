# Software and dataset rights policy — PM-02 licensing decision

**Decision recorded 2026-10-16:** The project owner delegated the final PM-02 decision and accepted the prior recommendation: **Apache License, Version 2.0 (Apache-2.0)** for the project's original source code and documentation. The repository's top-level [LICENSE](../LICENSE) contains the complete license; [NOTICE](../NOTICE) records initial attribution. This is a **software license grant** to recipients of the licensed work, including anyone later given repository access. It is not merely a proposed license.

**Privacy and publication are separate:** The repository remains **PRIVATE** during development. Having an Apache-2.0 license does not make the repository public, authorize package distribution, permit outreach, or trigger a release. Making the repository public remains conditional on [release readiness checks](release-gates.md) **and a new, separate explicit owner approval**.

## Why Apache-2.0

Apache-2.0 allows broad academic and commercial research-software reuse while including an express patent-license provision, applicable attribution requirements, and a disclaimer of warranties. MIT and BSD-3-Clause were considered as shorter permissive alternatives; neither provides the same explicit Apache patent-license structure. See [the Apache Software Foundation's guidance](https://www.apache.org/legal/apply-license.html) and [canonical license text](https://www.apache.org/licenses/LICENSE-2.0.txt).

## Separate permissions and limitations

- **Project code and documentation:** Apache-2.0 subject to notices. The initial authorship attribution is recorded in [NOTICE](../NOTICE); future contributors must hold rights to their contributions, preserve applicable notices, and review the licensing of included third-party material.
- **Synthetic data:** The current generator outputs fully invented trial records. `rights_basis: synthetic-original` describes **data provenance**, not a promise about behavioral validity or the license of any later third-party dataset. Code-license permissions and data-use permissions are distinct.
- **External datasets:** Do not import, download, redistribute, or publish third-party behavioral/neuroscience data until the individual source's precise permission, version, privacy, ethics, and allowed uses have been reviewed. Merely listing a dataset in a registry does **not** confer reuse rights.
- **Dependencies:** Current runtime generator uses Python's standard library, but developer/CI dependencies and any later vendored, binary, dataset or model assets require their own attribution and license review before a public distribution. This task does not represent an exhaustive redistribution clearance.
- **Scientific and clinical claims:** No clinical, diagnostic, treatment, patient, neurological or empirical human-performance representations are licensed or validated merely because the source code is permissively licensed.
- **Project name/trademarks:** Apache-2.0 does not grant trademark rights beyond the license's terms. No implied endorsements, independent review, publications, or external collaborators.

## Decision trail

The earlier PM-02 draft proposed Apache-2.0 while waiting for owner authorization. The owner then instructed: **“do what's best. just finish the task”**, following the explicit offer to choose Apache-2.0 and accept PM-02. This instruction resolves the **software-license selection for the private PM-02 foundation only**, not the separate *make public* gate. [ADR-0001](decisions/pm02-reconciliation.md) freezes the canonical synthetic v0 schema and records the technical review. [Hosted quality run](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38864568384) confirmed the previous pinned synthetic generator/test blobs on Python 3.11 and 3.12, with 46 tests per environment and passing Ruff/mypy; no fresh CI is attributed to this documentation/license commit.

**Release remains blocked** until the full platform, end-to-end group-safe benchmark, genuine release-candidate CI, dataset/dependency rights, security, documentation, external review and explicit publication authorization are complete.
