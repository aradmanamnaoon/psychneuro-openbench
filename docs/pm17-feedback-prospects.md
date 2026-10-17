# PM-17 — Twelve verifiable specialist feedback prospects (NO CONTACT)

**Researched 2026-10-17.** These are *public technical
research/contributor* references, **not** private contacts, consenting
interviewees, existing collaborators, invitation commitments or an
outreach list to execute automatically. The owner has **not** approved
new external outreach, emails, GitHub comments, LinkedIn messages,
private-data access or PRs in this mission. Nothing was sent, and nobody
has agreed to review PsychNeuro OpenBench.

## Public work and one relevant, non-spam feedback question each

| Person, public evidence | Verified research/software connection | One narrowly useful, opt-in feedback question (not a message to send) |
| --- | --- | --- |
| **1. Gaël Varoquaux** — [scikit-learn maintainer list](https://scikit-learn.org/dev/about.html) | Scikit-learn core maintainer; work concerns statistical learning and design for trustworthy ML; [skrub](https://github.com/skrub-data/skrub) is the DataOps source discussed in PM-17 | Would the fictional repeated-participant `GroupKFold` example add value beyond skrub's existing DataOps grouped-split guide? First wait for scope feedback in [#2340](https://github.com/skrub-data/skrub/issues/2340), never presume endorsement |
| **2. Guillaume Lemaitre** — [scikit-learn maintainer list](https://scikit-learn.org/dev/about.html) | Scikit-learn core maintainer associated with classification/model evaluation and developer guidance | Is the OpenBench explanation of training-CV-selected baseline versus fixed held-out model clearer if shown as an explicit selection rule rather than a third fitted model? |
| **3. Olivier Grisel** — [scikit-learn maintainer list](https://scikit-learn.org/dev/about.html) | Scikit-learn core maintainer and developer of ML workflows | Which first-run reproducibility artifact is most useful for independently spotting leakage-prone preprocessing in a grouped synthetic-only comparison? |
| **4. Alexandre Gramfort** — [MNE-Python public pinned project and profile](https://github.com/agramfort) and [scikit-learn team](https://scikit-learn.org/dev/about.html) | Public MNE-Python and scikit-learn work spans electrophysiology and ML | Does the first-user guide adequately distinguish synthetic grouped-leakage software checks from scientifically valid EEG/MEG participant generalization? |
| **5. Elizabeth DuPre** — [Nilearn core team](https://nilearn.github.io/stable/authors.html), [standardization issue #6499](https://github.com/nilearn/nilearn/issues/6499) | Public neuroimaging decoding documentation work; #6499 was opened by `emdupre` | What is the smallest scientifically responsible illustration of fold-fitted standardization, without implying that a fictional experiment predicts clinical outcomes? |
| **6. Rémi Gau** — [Nilearn core team](https://nilearn.github.io/stable/authors.html), [public contributor career page](https://remi-gau.github.io/) | Nilearn maintainer and research-software engineer; source/rights and neuroimaging methods knowledge | Is the report's separation between self-consistent JSON SHA and independently verifiable CI provenance sufficiently explicit for external reviewers? |
| **7. Bertrand Thirion** — [Nilearn core team](https://nilearn.github.io/stable/authors.html) | Neuroimaging methods researcher and Nilearn core developer | Which scientific caveat is missing from the explanation that nominal intervals over **simulated generator seeds** are not human-population confidence intervals? |
| **8. Dominique Makowski** — [NeuroKit authors/maintainers](https://neuropsychology.github.io/NeuroKit/authors.html) | NeuroKit2 maintainer and author associated with neurophysiological research software | Are OpenBench's documentation boundaries between signal processing measurement units, toy binary behavior data and actual experimental validity unambiguous? |
| **9. Danielle Benesch** — [NeuroKit current maintainers](https://neuropsychology.github.io/NeuroKit/authors.html) | Public maintainer of open neurophysiological tools | Can a newcomer reproduce *one entirely synthetic* provenance-and-QC scenario from the written tutorial without needing a medical dataset or secret credentials? |
| **10. Eric Larson** — [MNE-BIDS JOSS author credit](https://github.com/mne-tools/mne-bids/blob/main/README.md) and [BIDS sidecar issue #1557](https://github.com/mne-tools/mne-bids/issues/1557) | MNE-BIDS technical author; data lineage and electrophysiology format tooling | Which one manifest field would make the distinction between source rights, source version and synthetic generator SHA easier to audit without exposing raw participant rows? |
| **11. Robin Tibor Schirrmeister** — [Braindecode issue #375](https://github.com/braindecode/braindecode/issues/375) by `robintibor` and [Braindecode project](https://github.com/braindecode/braindecode) | Public involvement in EEG decoding research software | Is the model-card warning adequate that simple synthetic grouped performance is no evidence of cross-subject EEG decoder validity? |
| **12. Bruno Aristimunha** — [MNE-BIDS #1664](https://github.com/mne-tools/mne-bids/issues/1664) by `bruAristimunha` and [Braindecode model work](https://github.com/braindecode/braindecode/issues/1398) | Public work on event-unit checks and neurophysiology model integration | Would an explicit timing-and-units validation example help users avoid conflating task event metadata with approved pre-response predictors? |

**Grounding level:** Maintainer role is asserted only where an official
project team list verifies it. The precise questions above are *proposed
research prompts*, not evidence these experts would welcome being
contacted, approve the prototype or see it as useful. Only work/public
issue/team URLs appear; no inferred personal email, private contact
data, citizenship, age, location or other sensitive profiles are
collected. At the time of inspection, team listings and repo issues
were publicly accessible; memberships may change.

## Respectful feedback process if separately authorized later

1. Identify the exact validated *artifact* and one question: real
   code review, provenance field or pedagogical usability, not a generic
   request for stars, endorsements, invitations, citations or fame.
2. Recheck source and community norms. **Scikit-learn explicitly advises
   against emailing individual maintainers for ordinary support**:
   [official About/team page](https://scikit-learn.org/dev/about.html).
   Nilearn and MNE-Python prohibit fully automated AI issue/PR submission
   and demand human judgment, with AI disclosure where relevant. skrub
   requires proposal discussion before any PR; the existing
   [skrub issue #2340](https://github.com/skrub-data/skrub/issues/2340)
   remains unanswered, and must not be treated as approval.
3. Prefer an opt-in *public technical discussion channel* advertised
   by the project instead of unsolicited personal DMs, and send only
   after the owner approves the **individual** external action and its
   actual text. No repeated follow-ups without a response invitation,
   bulk mail or speculative collaboration claims.
4. Ask about one verifiable design choice, explain openly that AI
   helped research/prepare code and that hosted integration is **NOT
   RUN**, and offer a low-pressure decline/ignore option.
5. Record whether a response really arrived before reporting user
   discovery. Twelve possible public specialists are **not** twelve
   users, interviews, letters of recommendation, relationships,
   research collaborators or verified demand.

### Current outcome and gates

- **12/12** public specialist/work examples collected from official
  team documentation and real GitHub issues, with specific focused
  feedback questions.
- **0 contacts attempted; 0 replies, interviews, endorsements or
  collaborations verified.**
- Real external user discovery **BLOCKED** by the absence of a
  scientifically verified public or private reviewer artifact and
  separate permission for outreach.

**GO:** private research review and discussion planning.
**NO-GO:** external messages, invitations, public GitHub issue comments,
PRs, paid services or publicity.
