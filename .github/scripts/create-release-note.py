#!/usr/bin/env python3

"""Generate a markdown list of theme names and versions.

Scans all files matching: themes/theme-*/ethos_lua_manifest.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_theme_entry(manifest_path: Path) -> tuple[str, str]:
	"""Return (theme_name, theme_version) for a manifest file."""
	with manifest_path.open("r", encoding="utf-8") as manifest_file:
		data = json.load(manifest_file)

	theme_name = str(data.get("name") or manifest_path.parent.name)
	theme_version = str(data.get("version") or "unknown")
	return theme_name, theme_version


def main() -> int:
	repo_root = Path(__file__).resolve().parents[2]
	manifests = sorted(repo_root.glob("themes/theme-*/ethos_lua_manifest.json"))

	if not manifests:
		print("No theme manifests found under themes/theme-*/ethos_lua_manifest.json", file=sys.stderr)
		return 1

	entries: list[tuple[str, str]] = []

	for manifest_path in manifests:
		try:
			entries.append(load_theme_entry(manifest_path))
		except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
			print(f"Failed to parse {manifest_path}: {exc}", file=sys.stderr)
			return 1

	entries.sort(key=lambda item: item[0].lower())

	print("# Themes")
	print()
	for name, version in entries:
		print(f"- {name}: `{version}`")

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
