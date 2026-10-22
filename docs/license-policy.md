# Software and dataset rights policy — PM-02 licensing decision

**Decision recorded 2026-10-16:** The project owner delegated the final PM-02 decision and accepted the prior recommendation: **Apache License, Version 2.0 (Apache-2.0)** for the project's original source code and documentation. The repository's top-level [LICENSE](../LICENSE) contains the complete license; [NOTICE](../NOTICE) records initial attribution. This is a **software license grant** to recipients of the licensed work, including anyone later given repository access. It is not merely a proposed license.

**Source visibility and release readiness are separate:** The repository is currently **public** and its original source code is licensed under Apache-2.0. Public source availability does not establish that the integrated software has passed [release acceptance](release-gates.md), received third-party data redistribution clearance or been packaged as a stable release.

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

The earlier PM-02 licensing review compared permissive licensing approaches and selected Apache-2.0 for the original code and documentation. This decision is documented through [ADR-0001](decisions/pm02-reconciliation.md) and the [LICENSE](../LICENSE) and [NOTICE](../NOTICE) files. The decision does not certify downstream dependencies, bundled assets or external datasets. [Hosted quality run](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38864568384) confirmed the previous pinned synthetic generator/test blobs on Python 3.11 and 3.12, with 46 tests per environment and passing Ruff/mypy; no fresh CI is attributed to this documentation/license commit.

**Release readiness:** Additional integration, methodology, security, dependency and usability checks remain necessary before declaring the entire research workbench a verified release. See the [release checklist](release-gates.md).
