"""Machine-readable installed Python package inventory (not vulnerability scan)."""
import importlib.metadata as m
import json
import sys

if __name__ == "__main__":
    packages = sorted(
        ({"name": d.metadata["Name"], "version": d.version}
         for d in m.distributions() if d.metadata.get("Name")),
        key=lambda x: (x["name"].lower(), x["version"]),
    )
    print(json.dumps({"version": "w04-inventory-1", "python": sys.version.split()[0],
                      "packages": packages, "security_scan": "not performed"}, indent=2))
