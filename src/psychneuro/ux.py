"""PM-14 privacy-preserving, accessible copy for invalid/blocked UI inputs.

Never show raw uploaded JSON, exception repr, paths, people or model traces.
These messages are user-actionable without misrepresenting scientific status.
"""
from __future__ import annotations


def explain_upload_failure(exc: ValueError) -> str:
    """Constrain user-facing upload errors to known, safe remediation text."""
    reason = str(exc).lower()
    if "2 mb" in reason or "empty" in reason:
        return (
            "The report is empty or larger than 2 MB. Select the original "
            "PM-10 report.json from an authorized synthetic-only run."
        )
    if any(x in reason for x in ("utf-8", "duplicate json", "nonfinite json")):
        return (
            "The JSON file is malformed or contains invalid numbers or repeated "
            "fields. Re-export the original PM-10 report.json; do not edit scores."
        )
    if any(x in reason for x in (
        "non-synthetic", "rights", "source policy", "independence unit",
        "unsafe for export", "unexpected exportable", "unknown report",
    )):
        return (
            "This file is not an approved original-synthetic PM-10 report. "
            "Do not upload participant, medical, private or external datasets."
        )
    if any(x in reason for x in ("sha-256", "checksum", "digest")):
        return (
            "The report integrity check failed. Use the original unmodified "
            "synthetic report.json and verify its GitHub Actions artifact hash."
        )
    if any(x in reason for x in (
        "version", "protocol", "repeats", "seed", "model", "summary",
        "ineligible", "eligibility", "invalid", "missing", "unsupported",
        "slice", "interpretation", "metric", "unsafe reason",
    )):
        return (
            "The file does not match the expected PM-10 synthetic benchmark "
            "format or predeclared evaluation policy. Generate a fresh report "
            "using the locked project pipeline."
        )
    return (
        "The report could not be safely checked. Only an unmodified original "
        "PM-10 synthetic report.json is supported; no chart or export was created."
    )


def explain_scenario_failure(exc: ValueError) -> str:
    """No raw run exceptions, filesystem paths or partial scores in browser."""
    reason = str(exc).lower()
    if "registry" in reason:
        return (
            "The approved synthetic dataset registry is not available or is unsafe. "
            "No run was completed. A reviewer must restore the rights-gated "
            "repository registry before the demo can execute."
        )
    if any(x in reason for x in ("choices", "trial budget", "settings")):
        return (
            "The scenario is outside approved synthetic bounds. Select the "
            "provided seed, fictional cohort size and repeat options."
        )
    if "baseline" in reason or "versioned" in reason:
        return (
            "The frozen research protocol cannot be validated. No results were "
            "saved; the repository configuration needs review."
        )
    return (
        "The synthetic benchmark did not complete. No scores or downloads "
        "were saved from this attempt. Review the private hosted test logs "
        "before trying another permitted scenario."
    )
