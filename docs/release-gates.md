# Research-software release criteria

**Repository visibility:** Public source repository. **Packaged research-software release:** Not yet certified.

Publishing source code on GitHub is distinct from publishing a stable software release or authorizing deployment. This document records the checks required before offering the integrated platform as a supported research tool. Earlier internal planning discussions treated the repository as private; that is historical context, not its current visibility.

## Release acceptance checklist

- [ ] **Complete research workflow.** Validate a lawful/synthetic dataset, apply participant-group-safe splits and training-only preprocessing, compare transparent baselines, and export a reproducible run record.
- [ ] **Exact-revision verification.** Execute tests, linting, typing, packaging and realistic integration checks on the proposed release SHA, with reproducible logs. Passing runs on a different revision do not certify the candidate.
- [ ] **Scientific methodology.** Audit feature availability, split definitions, undefined metrics, uncertainty treatment, baseline comparisons and differences between synthetic and empirical claims.
- [ ] **Privacy and security.** Review permitted data sources, confidentiality, authentication, source validation, service isolation, input parsing and report rendering. No unapproved clinical or participant data.
- [ ] **Licensing.** Verify package dependencies, bundled assets, generated-data permissions and applicable third-party dataset rights independently of the project's Apache-2.0 code license.
- [ ] **Usability.** Validate onboarding, installation, examples, documentation, browser/accessibility routes and failure messages across supported environments.
- [ ] **Maintainer release review.** Confirm user benefit, maintainability, scope, outstanding issues and accurately described limitations before tagging or promoting a release.

## Available engineering evidence

- The default branch includes synthetic generators, schema/rights validation and focused regressions.
- A previous [Python 3.11 PM-04 verification run](https://github.com/aradmanamnaoon/psychneuro-openbench/actions/runs/38874446677) completed with 80 passing tests, Ruff and strict mypy for the source revision checked in that run.
- Additional grouped-evaluation, provenance and service integrations are under separate draft review. Their existence does not imply complete release-candidate acceptance.

## Usage boundaries

This project is **nonclinical**. Test data is invented unless and until a future source has an independently documented lawful processing and reuse basis. No performance figure from fictional datasets should be represented as observed human behavioral accuracy.

The release checklist must be met before presenting the entire integrated system as production-ready, independently validated or clinically appropriate. No automatic merge, package publication or external deployment is authorized by documentation or partial passing tests.

See the [README](../README.md), [scientific scope](spec-v0.md) and [dataset licensing policy](license-policy.md).
