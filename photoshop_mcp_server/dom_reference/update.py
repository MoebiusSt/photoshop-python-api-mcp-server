"""Refresh the bundled api.json files from indesignjs.de.

manifest.json lists every target with a contentHash (api.json without its "generated" field) and the
sha256 of every file; only targets whose contentHash changed are downloaded.

Usage:
    python -m photoshop_mcp_server.dom_reference.update [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request

from photoshop_mcp_server.dom_reference.reference import API_BASE_URL, DATA_DIR, SOURCES

HASHES_FILE = DATA_DIR / "content_hashes.json"


def _get(url: str, timeout: int = 120) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "photoshop-mcp-server"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def main(argv: list[str] | None = None) -> int:
    """Download api.json files whose upstream contentHash changed into DATA_DIR."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="Only report changes, do not write files")
    args = parser.parse_args(argv)

    manifest = json.loads(_get(f"{API_BASE_URL}/manifest.json", timeout=30))
    targets = {t["slug"]: t for t in manifest.get("targets", [])}
    local = json.loads(HASHES_FILE.read_text(encoding="utf-8")) if HASHES_FILE.exists() else {}

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    changed = 0
    for source, target in SOURCES.items():
        entry = targets.get(target)
        if entry is None:
            print(f"{source:<11} missing in manifest.json, skipped")
            continue
        same = local.get(target) == entry["contentHash"]
        print(f"{source:<11} {entry['version']}: {'unchanged' if same else 'changed'}")
        if same or args.check:
            continue
        payload = _get(f"{API_BASE_URL}/{target}/api.json")
        expected = next((f["sha256"] for f in entry.get("files", []) if f["path"] == f"{target}/api.json"), None)
        actual = "sha256:" + hashlib.sha256(payload).hexdigest()
        if expected and expected != actual:
            print(f"{source:<11} sha256 mismatch ({actual} != {expected}), skipped")
            continue
        path = DATA_DIR / f"{target}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_bytes(payload)
        os.replace(tmp, path)
        local[target] = entry["contentHash"]
        changed += 1
    if changed:
        HASHES_FILE.write_text(json.dumps(local, indent=2) + "\n", encoding="utf-8")
        print("Restart the Photoshop MCP server to load the new files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
