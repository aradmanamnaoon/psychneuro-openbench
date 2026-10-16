# Rights and licensing decision log

**No project software license has been selected or granted.** The private repository remains all-rights-reserved by default; do not claim it is open source, clone other projects' GPL-licensed implementations, distribute packages, or create a GitHub release without explicit owner approval.

- The generator creates wholly synthetic records and includes no outside human/clinical dataset.
- `rights_basis: synthetic-original` describes the synthetic *data*, not the software licensing terms.
- Any future real behavioral/neuroscience dataset requires a distinct source URL, version, license/permission, ethical/privacy risk review, and usage restrictions recorded on the dataset card before processing.
- License proposals for the code (MIT/BSD-3-Clause/Apache-2.0) need an owner decision before adding a `LICENSE` file; no choice is implied by dependencies.
- Dependencies have their own licenses and must be audited before redistribution. Core code currently uses only Python standard library.
- No contribution solicitation, public release, profile update, or medical claim is authorized by this documentation.

## PM-02 licensing decision preparation — proposed, NOT granted (2026-10-16)

**Recommended future open-source license:** **Apache-2.0**, conditional on the copyright owner's explicit written approval and a final attribution/dependency review. Rationale: permissive academic/industry use, with an express contributor patent-license structure and preservation of applicable notices. [Apache's official guidance](https://apache.org/legal/apply-license.html) and [license text](https://www.apache.org/licenses/LICENSE-2.0.html) explain terms and application. This is a project recommendation, not a legal opinion or permission grant.

| Option | Benefit | Trade-off | Selection status |
| --- | --- | --- | --- |
| Apache-2.0 | Permissive reuse; express patent provisions and notice rules | Longer legal text and attribution/NOTICE obligations to manage | **Preferred for owner consideration** |
| MIT | Short and permissive; easy for learners to understand | Does not contain Apache-2.0's explicit patent grant/termination structure | Alternative for owner |
| BSD-3-Clause | Permissive, familiar to scientific Python community | Different attribution/name-endorsement phrasing; no Apache-style patent provisions | Alternative for owner |

**Before creating a `LICENSE` file, tagging or releasing:** (1) owner chooses the license explicitly; (2) identify code/documentation copyright holders and contributions; (3) check all runtime/developer/deployed dependencies and redistributed assets; (4) ensure required copyright/NOTICE attribution; (5) review whether generated synthetic output will have separately stated data-use terms; (6) verify all [release gates](release-gates.md). No automatic license or public visibility change is authorized, even if engineering tests pass.

**Current enforceable project posture:** private repository, no project `LICENSE` grant made or implied. A recommendation recorded here never replaces an owner's authorization.
