# GA6 — prospective user value, reproducibility and APPROVAL-ONLY portfolio materials

## Case study: preventing plausible-but-false scientific results
**Starting risk:** repeated records from the same fictional participant can cross row-wise random folds. A simple digest verifies bytes, not the owner's entitlement or truth of reported metrics. The code therefore separates source identity, group split checks, fitted pipelines and artifact verification.

**Observed/inspected evidence:** W03 [PR 13](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/13) source shows train-only `StandardScaler`/`OneHotEncoder` within sklearn `Pipeline`, `GroupKFold`, logistic-vs-dummy and a versioned P13 four-node digest DAG; archived [W03 exact-code CI run 39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934) reports 349 passing pytest on two Python versions and **both models 0.5 balanced accuracy** on artificial data. W04 original [PR 14](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/14) was synthetic-only with no hosted PR-head run returned when checked. Independent private reviewer improved schema validation and added an externally supplied pinned-digest check; sandbox targeted tests are documented in Chat 3 final gate, not independent external certification.

## Reproducible review runbook — commands conditional on checkout
1. Select/check exact W03 PR head and W04 independent review head; **do not pretend two divergent unmerged branches are automatically integrated**.
2. Verify source code and environment: `git rev-parse HEAD`; `python -VV`; `python -m pip freeze`; compare to lockfile if present.
3. With local private repository and synthetic registry only, after reviewing dependencies: `python -m pip install -e '.[dev,w03]'`; `python -m pytest -q tests/test_w04_interop.py`; `python -m pytest -q tests/test_w03_integrated.py`; `python -m ruff check src/psychneuro/interop_v1.py tests/test_w04_interop.py`; `python -m mypy --strict src/psychneuro/interop_v1.py`. These are **commands to run**, not pass assertions.
4. Check negative vectors: modified metric with old digest rejects; malformed digest and duplicate group reject; forge metric + recompute digest: passes integrity but fails if compared against a separately trusted precommitted digest.
5. Execute W03 registry-backed service in isolated synthetic environment only; compare emitted SHA, seed, group counts, CI artifact and metrics; explain discrepancies and numerical library versions. No result is accepted from logs alone.

## Factual public-facing bullet drafts (PRIVATE — approval required)
- “Built a private synthetic scientific-ML prototype with participant-grouped nested cross-validation, a dummy baseline and train-fold-only preprocessing.” [Source: W03 PR 13]
- “Developed test cases for participant overlap, duplicate rows, malformed result artifacts and hash-integrity limitations.” [Source: W03 PR 13; independent W04 review branch]
- “Documented a reproducibility and rights threat model that distinguishes a locally valid SHA-256 digest from an externally trusted provenance attestation.” [Source: W04 private audit]

**NOT ALLOWED:** published software, independent scientific validation, clinical improvement, secure production tenancy, real user adoption, accepted manuscript, external review, scholarship or maintainers' recommendation.

## Prospective-user validation rubric — no interviews conducted
Identify potential academic *roles*, not harvested names: methodological neuroimaging scientists, reproducibility engineers, research software maintainers, IRB/data stewards, graduate methods educators. Five questions for opt-in future interviews (user approval first): (1) which existing workflow permits group contamination? (2) which minimum evidence is needed to reproduce a run? (3) who attests a license and who can revoke it? (4) would the failure messages change a decision? (5) what is the minimum acceptable setup cost? Record expected and observed task-completion, false accept/reject rates, clean setup time, rights-denial latency and qualitative confusion **only after actual sessions**. Do not invent interviews/metrics.

## Original 3–5 minute simple-English script — 'The data leak that makes an AI look brilliant'
Imagine you're studying how people answer memory questions. You have ten people, and each person answers many questions. You want to test whether your model can predict answers for **new people**.

A common mistake is to mix all the answers together and randomly split the rows. One person's answers can now appear in both training and testing. The model might recognize little habits of that person. It looks clever—but maybe it's just seeing the same person twice.

Think about a school exam. If a student practises with nearly the same questions they will see on the final exam, the score doesn't tell you how they handle truly new questions. The number is real, but its meaning is wrong.

Here's a safer idea. Split by **person**, not by answer. Keep every answer from one person entirely in training or entirely in testing. That is called a grouped split.

Now there's another trap: suppose we use testing data to choose our model settings. We're secretly learning from the exam again. So we choose settings using only the training people, with another grouped split inside. That's the idea behind nested cross-validation.

My tiny synthetic project uses imaginary people to demonstrate these checks. It doesn't prove anything about real memory or brains. It tests whether the software follows its own rules.

But one more thing: suppose we save a result with a SHA-256 hash. A hash is like a fingerprint for a file. If someone edits the file without updating the fingerprint, we can notice. Great! Yet an attacker can edit the result and compute a **new** fingerprint too. So a fingerprint alone doesn't tell us who created the result or whether the creator had permission to use the data.

For serious research, we need two questions: **Did we test on genuinely independent people?** And **can we trust who authorized and recorded this result?**

So when someone says their AI achieved a beautiful accuracy score, ask about the groups, the model selection and the evidence trail. Good science is not just a high score. It's a score you can explain—and a result you can try to disprove.

## Optional original short hooks — not published
**Video 2, 'Can you fake a hash?':** “A checksum can tell you whether bytes changed. It cannot tell you whether the person who wrote those bytes is telling the truth. Watch me change an invented score, recompute its hash and explain why an independently stored digest or signature matters.”
**Video 3, 'Why five CV folds are not five experiments':** “When our training sets overlap, the five test scores are related. Pretending five related scores are five independent studies can give misleading uncertainty. Let's compare what one fold measures with what a true new-cohort replication would measure.”

No user course work, R lesson, shooting, publishing or content distribution has been marked completed.
