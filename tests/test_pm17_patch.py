"""PM-17 private upstream-prototype integrity checks — specs, NOT RUN.

No direct dependency on skrub or network access. A syntactic source review
does not prove the external library's runtime semantics, gallery build,
scientific relevance, or maintainer approval.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_PATH = "skrub/_docs/examples/02_data_ops/1170_group_aware_cross_validation.py"
CANDIDATE = ROOT / "upstream-prototypes" / "skrub" / "1170_group_aware_cross_validation.py"
PATCH = ROOT / "upstream-prototypes" / "skrub" / "1170_group_aware_cross_validation.patch"


def test_reviewable_git_patch_matches_original_candidate_bytes() -> None:
    source = CANDIDATE.read_text(encoding="utf-8")
    patch = PATCH.read_text(encoding="utf-8")
    lines = source.splitlines()
    header = (
        f"diff --git a/{UPSTREAM_PATH} b/{UPSTREAM_PATH}\n"
        "new file mode 100644\n"
        "--- /dev/null\n"
        f"+++ b/{UPSTREAM_PATH}\n"
        f"@@ -0,0 +1,{len(lines)} @@\n"
    )
    assert patch.startswith(header)
    assert patch == header + "".join("+" + line + "\n" for line in lines)
    assert source.endswith("\n")


def test_synthetic_gallery_holds_group_split_safety_contract() -> None:
    source = CANDIDATE.read_text(encoding="utf-8")
    assert "np.random.default_rng(73)" in source
    assert "np.repeat(np.arange(32), 4)" in source
    assert "GroupKFold(n_splits=4)" in source
    assert "train_groups.isdisjoint(validation_groups)" in source
    assert 'data[["condition", "difficulty"]].skb.mark_as_X(' in source
    assert 'groups = data["participant_id"]' in source
    assert 'y = data["correct"].skb.mark_as_y()' in source
    assert 'split_kwargs={"groups": groups}' in source
    assert 'with_scoring("roc_auc").skb.cross_validate()' in source
    assert "skrub.TableVectorizer()" in source
    assert "LogisticRegression(max_iter=1000)" in source
    assert "fetch_" not in source
    assert "read_csv" not in source
    assert "train_test_split" not in source


def test_no_upstream_submission_or_fake_success_in_patch_review() -> None:
    memo = (ROOT / "docs" / "pm17-upstream-patch-review.md").read_text(encoding="utf-8")
    assert "SCOPE NOT APPROVED" in memo
    assert "NO-GO" in memo
    assert "NOT RUN" in memo
    assert "no permission" in memo.lower()
