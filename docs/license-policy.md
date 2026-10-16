# Source/data license and rights policy — awaiting owner decision

The PM-02 implementation is authored original code in the owner's **private**
repository. **No open-source license grant is made by this file**. Do not publish
or redistribute it under MIT, Apache-2.0, GPL, or any other license until the
owner explicitly approves a license policy. Do not create a LICENSE file yet.

Runtime code requires the Python standard library only. Optional developer
packages are resolved through PyPI by the project's hosted CI. Their current
licenses have not been individually verified here; do not suggest this amounts
to approval of arbitrary dependencies or their licenses.

The generated dataset is algorithmically invented from scratch; it contains
no personally identifying fields, human participant records, clinical labels,
or third-party protected study data. No human-subject consent or empirical
effect validity is inferred. Future real datasets require independent source,
license/legal basis, access, consent, de-identification, and redistribution
review *before* ingestion.

The GitHub workflow uses standard-hosted Ubuntu and is initially defined as
**manual dispatch only**, because private-repository Actions minutes can
exceed free allowance. There is no hosted execution claim without an actual
runner and logs.

References:
- https://docs.python.org/3/library/random.html#notes-on-reproducibility
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
