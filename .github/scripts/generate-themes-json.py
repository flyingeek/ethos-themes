#!/usr/bin/env python3

"""Generate themes.json with folder names and download URLs.

Output JSON maps folder_name -> download_url for each theme.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 4:
        print(
            "Usage: generate-themes-json.py <output_dir> <tag> <repo_owner> <repo_name>",
            file=sys.stderr,
        )
        print("  output_dir: directory to write themes.json", file=sys.stderr)
        print("  tag: release tag (e.g., release/1.0.0)", file=sys.stderr)
        print("  repo_owner: GitHub repo owner (e.g., flyingeek)", file=sys.stderr)
        print("  repo_name: GitHub repo name (e.g., ethos-themes)", file=sys.stderr)
        return 1

    output_dir = Path(sys.argv[1])
    tag = sys.argv[2]
    repo_owner = sys.argv[3]
    repo_name = sys.argv[4]

    # Find all manifests
    repo_root = Path(__file__).resolve().parents[2]
    manifests = sorted(repo_root.glob("themes/theme-*/ethos_lua_manifest.json"))

    if not manifests:
        print(
            "No theme manifests found under themes/theme-*/ethos_lua_manifest.json",
            file=sys.stderr,
        )
        return 1

    # Build themes object
    themes: dict[str, dict[str, str]] = {}
    for manifest_path in manifests:
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                manifest = json.load(f)

            folder_name = manifest.get("folder")
            if not folder_name:
                print(f"Warning: {manifest_path} missing 'folder' key, skipping", file=sys.stderr)
                continue

            version = manifest.get("version", "unknown")
            download_url = f"https://github.com/{repo_owner}/{repo_name}/releases/download/{tag}/{folder_name}.zip"
            themes[folder_name] = {
                "download": download_url,
                "version": version,
            }
        except Exception as exc:
            print(f"Error processing {manifest_path}: {exc}", file=sys.stderr)
            return 1

    if not themes:
        print("No themes were processed", file=sys.stderr)
        return 1

    # Write themes.json
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "themes.json"

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(themes, f, indent=2, sort_keys=True)

    print(f"✓ Generated {output_file} with {len(themes)} themes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
