# PM-15 — Private zero-cost host configuration and blocked browser-only runbook

**2026-10-17: PROPOSED SOURCE FILES ONLY; NOT INSTALLED, TESTED, DEPLOYED OR APPROVED.**
There is no live demo URL. Repository `aradmanamnaoon/psychneuro-openbench` is private. The **PM-14 prerequisite remains Blocked**: zero recent hosted PM-14 workflow runs. DO NOT deploy or change GitHub visibility, enable public access, invite external viewers, grant OAuth scope, pay, or create a new account without explicit owner authorization.

## Host choice, limitations and why no live URL

The **candidate** is [Streamlit Community Cloud](https://share.streamlit.io/), not an installed ChatGPT plugin. It can build a Streamlit app from a GitHub repository with a `requirements.txt` and optional `.streamlit/config.toml`. Its current docs state that the service is free for community apps; a PRIVATE-repository deployment inherits privacy and requires GitHub authentication for administrators. Deploying from a PRIVATE repository **requests GitHub's broad `repo` OAuth permission** and grants Cloud a GitHub deploy key; this is a security permission review, NOT implied by a connected ChatGPT GitHub plugin. Only repo admins can deploy/delete. The Community Cloud workspace allows **one private app at a time** and lets viewers with approved email access sign in. Access to the Cloud has NOT been connected here.

The service is shared, throttled and not guaranteed. Its documented resources can vary, historically about 0.078–2 CPU cores, 690 MB–2.7 GB RAM, max storage 50 GB, with apps hibernating after 12 hours without traffic. These are **provider-published approximations, not measured allocations** for this account. Heavy scikit-learn installs or a 5-seed run could fail or exhaust quota. Do not treat 'free' as permission to consume private Actions/hosting resources. Cloud may change limits/terms; confirm pricing and capacity at the actual future authorization gate. Users of private apps may have workspace analytics/viewer-sharing implications.

References read 2026-10-17:
- https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account
- https://docs.streamlit.io/deploy/streamlit-community-cloud/status
- https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
- https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.github.com/en/billing/concepts/product-billing/github-actions

## Candidate configuration and validation status

| Setting | Committed intent | Evidence |
| --- | --- | --- |
| Repository / branch | `aradmanamnaoon/psychneuro-openbench` / `pm15/private-host-preflight` | PRIVATE code branch, not merged/released |
| Entry point | `app.py` (repository root) | Existing Streamlit code inspected; never launched here |
| Python | 3.12 selected in future Cloud **Advanced settings** | UI selection required; cannot pin server interpreter solely by app requirements |
| Requirements | root [requirements.txt](../requirements.txt) with root project `.`, `streamlit==1.58.0`, `altair==5.5.0`, `scikit-learn==1.8.0` | These three direct versions exist on PyPI, **resolver/install/runtime NOT TESTED** |
| Application settings | root [`.streamlit/config.toml`](../.streamlit/config.toml): XSRF/CORS enabled, upload limit 2 MB, exception detail hidden, static serving disabled | TOML committed, Streamlit compatibility NOT tested |
| Source/data rights | Only locally generated original synthetic; source registry denies real/clinical participant inputs | Programmatic policy in prior PM, browser/host enforcement NOT independently verified |
| Secrets | NONE required or permitted for v0; never commit or paste credentials | No hosted secrets configured |
| Dependency supply chain | Direct top-level pins only; transitive dependency versions/hashes still unresolved | NOT reproducible full lock/SBOM or security audit |
| Deployment address | No app created | **LIVE URL: NONE / BLOCKED** |

A source-only `requirements.txt` with exact direct pins does not establish a full lock, compatibility, missing native library tests, or installation success. For the installed `psychneuro` package, the single `.` requirement is intentional; the app imports it from the private repository. The CI dependency resolver is currently UNRUN for this branch.

## Exact future browser-only authorization and deployment sequence (NOT performed)

**Gate 0: permissions.** The owner must separately approve (a) private GitHub Actions usage or provide existing passing exact-commit logs, (b) connecting Streamlit to private GitHub source with broad `repo` scope, and (c) making a PRIVATE Cloud app. These are separate from public-release approval. Confirm free-tier pricing, the repository owner workspace, and Cloud's one-private-app limit before clicking any action.

**Gate 1: test evidence, must happen BEFORE deployment.** Through the normal GitHub website, open `https://github.com/aradmanamnaoon/psychneuro-openbench/actions/workflows/ci.yml`. The workflow is `workflow_dispatch` only; if the owner has expressly authorized the private runner minutes, select **Run workflow**, choose EXACT branch `pm15/private-host-preflight`, leave `profile_small_synthetic` **OFF** unless separately approved, and start once. Check both Python 3.11/3.12 runs, all pytest/Ruff/mypy, installation validation, PM-10→PM-13 report/export byte consistency and actual artifact/log URLs. **If any fail or the Actions UI does not permit dispatch, STOP; no deployment.** Do not assume the most recent commit passed if a run belongs to an earlier SHA. Never log or download raw human data.

**Gate 2: private host account and repository connection.** Visit `https://share.streamlit.io/` in an ordinary browser and use the official **Continue with GitHub** login if approved. The Cloud owner is the GitHub repository admin; login cannot be completed by the GitHub connector. If private repo is unavailable: workspace **Settings → Linked accounts → Source control → Connect**, review the official Streamlit OAuth scope **`repo` and deploy-key access**, and authorize **only after explicit consent**. If the owner refuses broad GitHub access, STOP; there is no preapproved alternative private host. Do NOT make the repository public to work around missing permissions.

**Gate 3: private-app build.** In the matching owner workspace select **Create app → Yup, I have an app**, enter the exact private repository, branch `pm15/private-host-preflight`, file `app.py`, Python **3.12** under **Advanced settings**, and **NO secrets**. Confirm privacy **Only specific people can view this app** and that no public/searchable option is enabled; when provider requires deployment before sharing configuration is visible, do not proceed without verifying the private-repo default and owner permission. Start deployment only with explicit approval, confirm build logs and that the full private app is inaccessible to unsigned viewers. **Do not invent or predict a URL**; record it ONLY after Cloud assigns and the browser actually loads it.

**Gate 4: actual private browser/mobile QA.** Run the entire [PM-15 18-case browser script](pm15-browser-smoke.md) at the assigned private URL, dated with exact deployment commit and browser versions. Use desktop and mobile/narrow viewport, keyboard-only navigation, screen reader where feasible, invalid data, 1-repeat N/A uncertainty, 5-repeat eligible uncertainty, all downloads, discard, error states, chart text alternatives and privacy enforcement. If screenshot capture is available, save only genuine screenshots of synthetic views with exact date/environment—no invented images or trial data. Inspect developer Cloud build/runtime logs only using authorized developer access.

**Gate 5: release decision.** Record actual CI/artifact SHA, exact private URL and genuine QA results in consolidated Notion PM-15. Only after separate privacy/license/science approvals may the owner contemplate a public GitHub PR, public Cloud sharing, package release, site/profile edit or outreach. **A private Cloud app passing tests is not public release authorization.**

The above browser-only steps are contingency documentation, **not chores assigned to the reviewer** nor evidence that the assistant completed deployment. No new host connection, login, browser test, public visibility change, charge or cloud workspace was created here.

## Contingency if Streamlit is unavailable

**BLOCKED.** Do not invent a substitute host, public repository fork, app URL, quota or deployment result. Keep the source private, write any independent docs/verification checks, and revisit deployment only after host permissions, genuine CI and explicit user approval.

## Source dependencies and review gate

- [PM-14 accessibility, invalid input and UNMEASURED profiling](pm14-a11y-errors-performance.md)
- [Release conditions](release-gates.md)
- [Security/license/privacy audit](pm15-security-privacy-audit.md)
- [Browser test script](pm15-browser-smoke.md)
- [Daily honest changelog](pm15-changelog.md)

**PM-15 GO = private source review. DEPLOYMENT / RELEASE = NO-GO.**

## Exact-candidate CI correction — 2026-10-18
The first actual private branch CI [run 39108122761](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/39108122761) installed dependencies successfully on both Python 3.11 and 3.12 but failed 8/317 pytest tests per job. Seven failures were caused by this PM-15 direct pin to Streamlit 1.58.0, whose AppTest interface lacks the `download_button` member used by the committed tests. [Streamlit 1.65.0 official testing API](https://docs.streamlit.io/1.65.0/develop/api-reference/app-testing/st.testing.v1.apptest) documents `AppTest.download_button`; the candidate direct pin and package minimum have therefore been aligned with that test contract. The eighth first-run failure was a case-sensitive deployment-warning assertion, fixed by this emphatic written `DO NOT deploy` warning without changing the policy. These are **candidate corrections**, not PASS claims, until the subsequent exact-commit run proves them. Independent browser QA/host authorization remain absent.
