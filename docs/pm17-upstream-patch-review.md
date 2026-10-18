# PM-17 private upstream patch review — skrub #2340

**Date: 2026-10-17.** This is a **genuine upstream-targeted new-file
diff**, but only staged within the owner's PRIVATE
`psychneuro-openbench` feature branch. It has NOT been added to
`skrub-data/skrub`, submitted as a fork/PR, approved by a skrub
maintainer, executed with installed skrub or included in skrub's live
documentation. Do not represent it as an upstream contribution or
recognized collaboration.

- Actual upstream issue: [skrub#2340](https://github.com/skrub-data/skrub/issues/2340),
  an OPEN proposal already opened by `aradmanamnaoon` before PM-17.
  **No fresh message or PR was posted here.** Latest inspected issue
  had 0 comments (not approved).
- Actual upstream destination:
  `skrub/_docs/examples/02_data_ops/1170_group_aware_cross_validation.py`.
  The [upstream 02_data_ops directory](https://github.com/skrub-data/skrub/tree/main/skrub/_docs/examples/02_data_ops)
  currently contains numbered examples 1120 through 1160 and no
  1170 file at inspection time, so this is a **new-file proposal**,
  not a replacement of an upstream checked-in file.
- Private draft code:
  [1170_group_aware_cross_validation.py](../upstream-prototypes/skrub/1170_group_aware_cross_validation.py)
- Reviewable conventional Git patch:
  [1170_group_aware_cross_validation.patch](../upstream-prototypes/skrub/1170_group_aware_cross_validation.patch).
  The `diff --git` hunk explicitly targets the upstream 1170 path
  and contains no changes to another repository.
- Source API verification: skrub's current
  [tuning/validating guide](https://github.com/skrub-data/skrub/blob/main/skrub/_docs/modules/data_ops/validation/tuning_validating_data_ops.rst)
  documents `mark_as_X(cv=..., split_kwargs={"groups": ...})`,
  `DataOp.skb.apply`, `DataOp.skb.with_scoring("roc_auc")` and
  `DataOp.skb.cross_validate()`. Reviewed existing gallery
  [1140_subsampling.py](https://github.com/skrub-data/skrub/blob/main/skrub/_docs/examples/02_data_ops/1140_subsampling.py)
  for `# %%` layout and no output invented.
- Source design: deterministic NumPy seed 73 generates 32 fictional
  participant IDs times four rows, binary synthetic correct outcomes
  and stimulus condition/difficulty; no fetching, PID or target
  feature leakage. Check all 4 group folds for disjoint groups, and
  build a DataOps pipeline using `TableVectorizer` followed by
  `LogisticRegression`, scoring via documented `with_scoring` flow.
- AI transparency: this example and diff were prepared with
  generative AI. The owner is the reviewer. If the project accepts
  this after permission, upstream-specific rules and AI disclosure
  will be followed. No fabricated local/remote execution.

## Independent acceptance and actual status

| Check | Required observation | Current state |
| --- | --- | --- |
| Upstream issue status | #2340 open, no competing resolved PR; maintainer approves whether standalone gallery is wanted | **OPEN, 0 COMMENTS; SCOPE NOT APPROVED** |
| Source diff | New-file patch and complete candidate file exist, target path and hunk counts match | **SOURCE WRITTEN; SOURCE READ-BACK PENDING** |
| Syntax | Actual Python parsing/compilation under intended Python version | **NOT RUN** |
| DataOps API | Current upstream library imports, `GroupKFold` groups graph, `with_scoring` and `cross_validate` succeed | **NOT RUN** |
| Split integrity | All fold ID sets truly disjoint in code execution; neither `participant_id` nor `correct` in X | **SOURCE CHECKS WRITTEN, NOT RUN** |
| Statistical robustness | Seed independent from global RNG, all CV validation folds have both target labels or fail with an explicit known limitation | **NOT RUN** |
| Gallery/CI | Upstream formatting, docs build, lint and unit integration with current skrub | **NOT RUN** |
| Package rights | NumPy, pandas, scikit-learn, skrub available under appropriate license and dependencies; no real dataset | **PUBLIC SOURCE ONLY, INSTALL/DEPENDENCY REVIEW NOT COMPLETE** |
| Upstream permission | Owner approves individual public/fork/PR action AND skrub maintainers approve proposal scope | **NOT GIVEN** |
| Upstream result | PR URL, CI run, reviewer feedback, merged commit | **NONE** |

**Known API review:** The preexisting #2340 proposal text uses
`.skb.cross_validate(scoring="roc_auc")`, but the current official
skrub user guide documents
`.skb.with_scoring("roc_auc").skb.cross_validate()`.
The private candidate uses that documented spelling; runtime
correctness remains UNVERIFIED.

**No fork or upstream write:** Only an authorized connected GitHub
private write on `aradmanamnaoon/psychneuro-openbench` was performed.
There was no external GitHub fork tool/approval and no permission to
place code on the public skrub repository. A private branch containing
upstream-targeted diff is the non-destructive maximum possible now.

## Review decision

**GO:** Owner inspects the private candidate and compares against issue
scope/guidelines. **NO-GO:** public PR/fork/issue comment, code integration
claims, tested example, downstream neuroscience result or other contacts.
The user is not assigned coding or execution chores. Any later Actions
run must occur via an authorized connected remote capability/budget.
