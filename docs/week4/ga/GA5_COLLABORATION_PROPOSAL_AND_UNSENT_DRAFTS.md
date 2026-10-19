# GA5 — one-page research-software collaboration proposal and UNSENT outreach
**Private writing draft, NOT sent.** No confirmed supervisor, engagement, external peer review, sponsorship, funding, appointment or recommendation.

## Proposal — 'How should research pipelines prove participant isolation and revocable dataset use?'
**Research question:** Can a compact, versioned test harness distinguish (i) structurally valid integrity digests from (ii) authenticated, current rights-granted execution, while detecting participant leakage in grouped behavioral ML before reporting descriptive performance?

**Problem/evidence:** [W03 PR 13](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/13) contains a documented private synthetic 3/2 nested GroupKFold pipeline and an earlier reported [GitHub Actions run 39228198934](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39228198934) on exact code SHA `4eeb17845dac7641b75d9a8164f125db6c213659`, which reported 349 passing tests each on Python 3.11/3.12 and 0.5 heldout balanced accuracy on invented data. Those logs predate W04 and must not certify W04. [W04 PR 14](https://github.com/aradmanamnaoon/psychneuro-openbench/pull/14) implements a separate rights/artifact toy contract. Independent W04 review branch adds negative verifier tests. These are *software examples*, not psychological discoveries or externally reviewed results.

**Six-to-eight-week prospective plan (conditional on real consent to collaborate):**
- Weeks 1–2: lock data contract, map threats, define known-good and known-bad synthetic fixtures, verify source hashes against a trusted registry and reproducible pinned environment.
- Weeks 3–4: test participant/site/temporal split violations, outcome-derived predictors and train/test preprocessing leakage; code a second independent oracle for confusion matrices and baseline. Register every failure as machine-readable evidence.
- Weeks 5–6: implement explicit scoped rights attestations and a revocation test with event versioning, key/actor ownership, and tenant-scoped audit checks. Threat-test coherent forgery and rebuilds; run exact-commit CI.
- Weeks 7–8: a small reproducibility study across declared seed sets/versions with a blinded adversarial test pack, a documentation-quality example, and a no-go/go scientific QA report. Only after permission, consider upstream documentation contribution.

**Division of work:** Independent project contributor owns coding, synthetic fixtures, tests, CI records, provenance/rights implementation and documentation; prospective methods collaborator critiques research question, threat assumptions, estimand, data rights and scientific generalization; optional maintainer validates API/docs conventions. No expectation of unpaid labour, endorsement, external resources or co-authorship before agreement.

**Deliverables:** exact reproducibility lock + SHA, test vectors and oracles, end-to-end denial cases, metrics table with sampling-unit caveats, rights/security review, open methodology appendix, private PR (owner-reviewed) and an honest non-empirical educational artifact. Hard stop: no real human input before independent rights/ethics approval; no published repo/paper/PR without separate consent. Risks: structured dependence beyond participant, unverified grant booleans, attacker-controlled hashes, budget/hosted CI and uncertain maintainer interest.

## Distinct individualized UNSENT draft A — Osnabrück Institute of Cognitive Science programme/lab coordinator
Subject: Potential methods feedback on group-leakage-safe cognitive ML benchmarks

Hello,

I’m an independent AI engineer preparing for formal cognitive-science study. I built a private, synthetic-only Python test harness for repeated-trial group leakage and provenance. I’m interested in whether the threat tests capture realistic methodological mistakes in cognitive-science workflows. Your interdisciplinary Cognitive Science programme at Osnabrück makes this a particularly relevant direction for me. If appropriate, could you point me to publicly available methodological guidelines or the right research group to follow? I’m not claiming human findings or asking for funded supervision; I would value brief guidance. I can share a concise non-sensitive protocol after permission.

Thank you.

## Distinct individualized UNSENT draft B — Tübingen Graduate Training Centre neuroscience methods
Subject: Question on falsification tests for grouped neuroscience model validation

Hello,

I’m developing an internal, synthetic benchmark that treats participant independence and provenance verification as software acceptance gates. Tübingen's research-focused Neural Information Processing and Neural & Behavioural Science training tracks are closely aligned with the validation problems I hope to study formally. Is there a methods reading list or publicly documented standard you recommend for nested grouped cross-validation and distribution-shift checks? No human dataset or clinical performance claims are involved. This is a request for guidance, not an affiliation or endorsement.

Kind regards.

## Distinct individualized UNSENT draft C — skrub maintainers, only after approval
Subject: Follow-up proposal for group-aware DataOps example (#2340)

Hello skrub maintainers,

I saw the existing DataOps guide correctly documents group-aware splitting through `mark_as_X`. I prepared a synthetic repeated-observation demonstration and negative control showing why row-wise splits leak participant identity. Issue #2340 proposes an optional gallery example but has not been accepted. Would you prefer a smaller documentation clarification instead? I will first verify the current DataOps API, run the gallery and comply with your contribution policy, and will not open a PR without scope approval.

Regards.

**Approval gates:** exact recipients and preferred medium must be confirmed by the user; do not send, recruit, publicize, assert interest or promise work on behalf of an academic or maintainer.
