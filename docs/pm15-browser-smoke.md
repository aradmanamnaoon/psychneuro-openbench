# PM-15 — Browser and mobile smoke-test script (NOT EXECUTED)

**As of 2026-10-17:** No real deployed app URL, screenshot, browser recording, user acceptance outcome or mobile/screen-reader observation exists. This is a reproducible script for a future **explicitly approved PRIVATE** host on the exact PM-15 SHA. It does not authorize deployment or spend.

## Evidence format to record only after genuine execution

For every test: record `case_id`, local timestamp and timezone, assigned private URL, deployed GitHub SHA and host build-log URL, browser/version and operating system, viewport width/zoom, input and expected result, actual observed result, pass/fail/blocked, bug reproduction steps and screenshot URL **only if actually captured**. Remove access tokens, GitHub repo secrets, contact details and any uploaded user records from screenshots. An unavailable screen reader/viewport is **NOT TESTED**, not PASS.

## Test script

| ID | Future manual/private-browser operation | Expected observable outcome | Actual |
| --- | --- | --- | --- |
| B01 | Open private URL signed out/incognito | Authentication required; no preview, results or secrets visible publicly | **NOT RUN** |
| B02 | Sign in as explicitly authorized developer | UI loads with title, clear research/nonclinical warning and source selector | **NOT RUN** |
| B03 | Cold launch at desktop width 1440px | Default source “Original synthetic preview”; no automatically trained model scores | **NOT RUN** |
| B04 | Switch navigation to “Synthetic preview” | Fixed-synthetic preview only; static table of fictional ID, cue/difficulty; no correctness or latency | **NOT RUN** |
| B05 | Set permitted preview seed, cohort and trial controls | Bounded, deterministic preview and synthetic source SHA; no hidden download or model inference | **NOT RUN** |
| B06 | Switch to “Uploaded PM-10 report” without a file | Empty-state message, no charts, metric/CI claims or downloads | **NOT RUN** |
| B07 | Try empty, malformed, duplicate-key, NaN, wrong-version and >2MB JSON via approved synthetic fixtures | Clear rejection, no partial results or exports, no private JSON echoed | **NOT RUN** |
| B08 | Try synthetic-only-valid report copied from an ACTUAL authorized CI artifact | Exact report digest, eligibility and full-report provenance visible; independent CI remains explicitly unverified by UI | **NOT RUN; NO ARTIFACT** |
| B09 | Switch model, metric and repeat display filters | Only originally recorded eligible points; accessible static table matches every plot point; no training/recomputed CI | **NOT RUN** |
| B10 | Change source to “Run bounded synthetic benchmark”; do not submit | No execution, scores or downloads before explicit Run | **NOT RUN** |
| B11 | Submit 1-repeat default fictional scenario, one time | Existing loader/group-split/baseline runs synchronously; no fabricated interval at n<5; status and provenance truthfully displayed | **NOT RUN** |
| B12 | Submit 5-repeat allowed scenario after fresh review of free-tier limits | Legitimate eligible results or transparent ineligible states; nominal CI only for >=5 eligible cohorts; N/A otherwise | **NOT RUN** |
| B13 | Change form inputs after prior submission without clicking Run | Output remains labeled as last SUBMITTED scenario; no accidental rerun or relabeling | **NOT RUN** |
| B14 | Click Discard; then deliberately cause invalid/blocked source | Old results cleared; safe textual error; no previous downloads left exposed | **NOT RUN** |
| B15 | Download full JSON, Markdown and artifact manifest from one actual synthetic run | Only approved full-report fields, original synthetic source rights and exact matching artifact SHA hashes; no raw trial/patient/contact columns | **NOT RUN** |
| B16 | Keyboard-only: Tab/Shift+Tab, arrow controls, Enter/Space to submit, focus/error and download | Logical focus order, visible focus, visible labels, no keyboard trap; statuses understandable without color | **NOT RUN** |
| B17 | Screen reader (NVDA/VoiceOver, record actual name/version) | Chart title/caption plus static numerical table; errors and progress announced; all controls identifiable | **NOT RUN** |
| B18 | 320, 375, 768, 1024 and 1440px; 200% zoom; compare contrast | No clipped critical form, navigation, submit or downloads; measure normal text AA >=4.5:1 and nontext/large AA >=3:1 where applicable | **NOT RUN** |
| B19 | Open same private URL as an uninvited authenticated account | Access denied; no report leak across users/sessions or shared run state | **NOT RUN** |
| B20 | Review Cloud dashboard logs and incident/error states | Logs do not print sensitive input or credentials; resource errors explicitly reported; only authorized admin sees logs | **NOT RUN** |

## Verification gates

- **Source preconditions:** confirm the CI exact SHA and real PM-10–13 report/checksum outputs; private host permissions and one-private-app availability; don't upload human records.
- **Deployment evidence:** real private URL, authenticated and unauthenticated checks, timestamps and browser screenshots **only if genuinely generated**.
- **Scientific:** compare chart points to original exported JSON, verify group-held-out evaluation and ineligible repeat treatment from real logs, do not claim human generalization.
- **Privacy:** no personal input, cross-session leak, unsafe report field or unauthorized invitation.
- **Accessibility:** keyboard, focus, screen-reader chart table, mobile and zoom.
- **Performance:** do not assert launch time/CPU/memory from observations without hosted measurement evidence.
- **External/public:** never make Cloud app public, fork repo publicly, release package or contact third parties absent a separate explicit owner approval.

**Acceptance outcome as of writing: 0/20 tested. All B01–B20 are NOT RUN / BLOCKED BY UNDEPLOYED HOST.** Do not infer a pass from the script's existence.
