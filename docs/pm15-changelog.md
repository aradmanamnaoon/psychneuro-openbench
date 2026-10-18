# PM-15 changelog — private deployment candidate, not a release

**Date: 2026-10-17 · Version: unchanged `0.1.0.dev0` · Overall gate: BLOCKED**

This is an accountable Day-5 engineering change record. No package version was
released, no tag was created, no PR was opened, no GitHub branch was made
public, no hosted app exists and no external success announcement is allowed.

## Added to a private branch

| Change | Why and effect | Evidence status |
| --- | --- | --- |
| [`requirements.txt`](../requirements.txt) | Candidate exact direct pins for Streamlit 1.58.0, Altair 5.5.0, scikit-learn 1.8.0 and local installed source package | Versions exist on PyPI; **NOT INSTALLED/RESOLVED** |
| [`.streamlit/config.toml`](../.streamlit/config.toml) | Proposed Cloud app max upload 2MB, XSRF/CORS enabled, masked errors, no static serving | **STATIC SOURCE ONLY; UNTESTED** |
| [`.gitignore`](../.gitignore) | Prevent future accidental commit of secrets, virtualenv, generated reports, keys and caches | **SOURCE ONLY**, no historical repo-wide secret scan |
| [`tests/test_deployment.py`](../tests/test_deployment.py) | Test pinned direct deps, baseline package/Python, host options, license, rights policy, private release gates and no demo-URL fabrication | **WRITTEN, NOT RUN** |
| [`docs/pm15-host-runbook.md`](pm15-host-runbook.md) | Candidate free Cloud host, one-private-app limit, broad private-repo OAuth scope, no deployment before private CI and owner approval | **PROVIDER DOCS REVIEWED; NO HOST CONNECTED** |
| [`docs/pm15-browser-smoke.md`](pm15-browser-smoke.md) | Twenty exact private browser/mobile/keyboard/privacy/exports smoke scenarios with timestamp/SHA evidence schema | **0/20 EXECUTED** |
| [`docs/pm15-security-privacy-audit.md`](pm15-security-privacy-audit.md) | Source-vs-hosted state for security, licensing, dependencies, package, privacy, rights, cross-session and publication permissions | **AUDIT SOURCE ONLY; MANY P0/P1 BLOCKERS** |
| [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | Add static deployment tests (via pytest) and hosted-only exact direct runtime install + `pip check`, preserve manual-only dispatch | **NO NEW CI RUN / RESULTS** |
| [`README.md`](../README.md) | Keep demo unavailable; link only to true private engineering review artifacts, not invented public URL | **SOURCE REVIEW** |

## Prior implementation preserved

Inherited PM-10 statistical pipeline, PM-11 report/manifest exporter,
PM-12 UI selectors, PM-13 synchronous rights-checked run path, PM-14 tutorial,
friendly errors, accessibility table alternatives and optional
default-OFF CPU/memory profiling. Earlier source was not replaced, and
previous hosted success on old generator commits was NOT attributed to this
PM-15 branch.

## Scientific and operational restrictions

Model results, measured accuracy, performance benchmarks, browser screenshots,
user uptake, privacy audits, private host login and live deployed app address
are all **NOT AVAILABLE** for this exact candidate. Synthetic-only data,
participant-group split and fixed CV-selected model policy must be verified
against real hosted logs before any benchmark use. A successful source-file
write is not a passing test, deploy or release.

The GitHub repo remains PRIVATE. Apache-2.0 and a NOTICE file were present
before PM-15; they license project-authored software, not separately
unapproved human datasets or third-party dependency assets.

The exact parent of the PM-15 branch is
`2cd3f458cdcfba9dc9063bd076a727a0e42f6f21` (PM-14). The final PM-15
head and private commit links are maintained in the consolidated Notion
[PM-15 mission](https://app.notion.com/p/3fa977a963b28149af2bd10610db99fe)
after read-back. Package stays `0.1.0.dev0`.

**Decision: private source-review GO; deployed demo/hosted validation/public
release NO-GO**. PM-16 or any dependent next mission must not be advanced as
“Verified Done” without actual evidence and separate owner authorization.
