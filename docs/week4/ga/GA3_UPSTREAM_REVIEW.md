# GA3 — skrub upstream contribution readiness and private reproducer

**Confirmed upstream problem:** [skrub issue #2340](https://github.com/skrub-data/skrub/issues/2340), “DOC proposal: Group-aware DataOps cross-validation example for repeated observations”, open, zero comments as inspected 2026-10-19. Note: **the issue was opened by the repository owner**, not by an independent maintainer; there is NO recorded maintainer endorsement. Candidate location: `skrub/_docs/examples/02_data_ops/1170_group_aware_cross_validation.py`. Existing group-aware split guidance is in [tuning_validating_data_ops.rst](https://github.com/skrub-data/skrub/blob/main/skrub/_docs/modules/data_ops/validation/tuning_validating_data_ops.rst).

**Contributor policy:** [CONTRIBUTING.rst](https://github.com/skrub-data/skrub/blob/main/CONTRIBUTING.rst) says discuss enhancements and obtain maintainers' approval before coding/opening PR; PRs must reference issue, tests plus docs build expected. No specific AI-generated-content ban was found in the inspected guide; **absence of a mention is not permission or an exhaustive AI policy audit**. Check current instructions prior to any submission.

**Existing private patch/reproducer:** `tests/test_w03_upstream_reproducer.py`, `upstream-prototypes/skrub/1170_group_aware_cross_validation.py`, `upstream-prototypes/skrub/1170_group_aware_cross_validation.patch` on accessible W03 branch. They demonstrate row-wise `KFold` mixing fictional subjects while `GroupKFold` holds participant groups apart. Previous W03 memo reports 2 standalone tests passing; **independent current-run skrub integration NOT RUN**. No newly tested upstream-API patch is asserted here, and no upstream PR created.

**Runnable private reproducer (numpy + scikit-learn only):**
```python
import numpy as np
from sklearn.model_selection import GroupKFold, KFold
groups = np.repeat(np.arange(16), 6)
X = np.arange(groups.size).reshape(-1, 1)
y = (np.arange(groups.size) % 2).astype(int)
random_folds = list(KFold(4, shuffle=True, random_state=73).split(X, y))
grouped_folds = list(GroupKFold(4).split(X, y, groups))
assert any(set(groups[a]) & set(groups[b]) for a,b in random_folds)
assert all(not (set(groups[a]) & set(groups[b])) for a,b in grouped_folds)
```
Run: `python path/to/reproducer.py` (offline, entirely fictional). A valid future acceptance test must execute the true DataOps `mark_as_X(cv=GroupKFold(...), split_kwargs={'groups': groups_op})` path, confirm no target/ID feature contamination, version against current skrub, run the gallery and lint/docs build. Suggested contribution is documentation/error-prevention, not a new performance record or acknowledged upstream impact.

**Decision:** NO-GO for public PR; maintainer scope approval, contributor current-policy check, real upstream dependency testing and explicit user approval missing. A private, verified reproducible proposal remains worthwhile.

**Chat3 additional regression file (private branch):** `tests/test_w04_independent_oracles.py` demonstrates the grouped CV negative control on **three** preregistered synthetic seeds (17,73,101) and an independent confusion-matrix BA oracle on four vectors. Actually executed in a standalone Python3.13.5 environment: **7 passed in 1.43s**; source SHA-256 `79877d59f7200c742c40d7109bdfab9eeb5513754e0b7e440b03923a2a4024a9`. It does not run skrub/DataOps or the actual GitHub integrated pipeline, and cannot be presented as an accepted upstream contribution.
