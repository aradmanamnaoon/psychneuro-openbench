"""Generate a reproducible CycloneDX v1.5 Python environment inventory.

This is a package inventory, NOT a vulnerability scan, licensing audit, or
cryptographically locked dependency resolution. Run only in the test runtime
whose dependencies you want to attest, and archive it with that exact SHA.
"""
from __future__ import annotations

import importlib.metadata
import json
import platform
import re
from urllib.parse import quote


def normalized(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def main() -> None:
    packages: dict[str, dict[str, str]] = {}
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name")
        if not name:
            continue
        canon = normalized(name)
        version = distribution.version
        packages[f"{canon}@{version}"] = {
            "type": "library",
            "name": canon,
            "version": version,
            "purl": "pkg:pypi/" + quote(canon) + "@" + quote(version),
        }
    document = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": "psychneuro-openbench-private-w04",
                "version": "0.4.3",
            },
            "properties": [
                {"name": "w04:evidence", "value": "installed-python-packages-only"},
                {"name": "w04:python", "value": platform.python_version()},
                {"name": "w04:security-scan", "value": "NOT_PERFORMED"},
            ],
        },
        "components": [packages[k] for k in sorted(packages)],
    }
    print(json.dumps(document, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
