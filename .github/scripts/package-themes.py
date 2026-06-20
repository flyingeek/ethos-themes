#!/usr/bin/env python3

"""Package themes into zip artifacts.

For each theme manifest, creates a zip file containing:
- ethos_lua_manifest.json (always included)
- All files matched by the manifest's files section (globbed)

Zip entries are flattened to the root (no parent directory nesting).
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


def validate_tag(tag: str) -> bool:
    """Validate tag format: release/x.X.X or release/x.X.X-suffix."""
    if not tag.startswith("release/"):
        return False
    version_part = tag[8:]  # remove "release/" prefix
    # Allow x.X.X or x.X.X-rc1, etc.
    parts = version_part.split(".")
    return len(parts) >= 2 and all(p and (p[0].isdigit() or p[0].isalpha()) for p in parts)


def glob_files(base_dir: Path, patterns: list[str]) -> list[Path]:
    """Glob files matching patterns within base_dir. Return absolute paths."""
    result = []
    for pattern in patterns:
        matches = list(base_dir.glob(pattern))
        if not matches:
            raise ValueError(f"Pattern '{pattern}' in {base_dir} matched no files")
        result.extend(matches)
    return result


def package_theme(manifest_path: Path, output_dir: Path) -> tuple[str, int]:
    """Package a single theme into a zip.

    Returns: (zip_filename, file_count)
    Raises: Exception on validation failure.
    """
    theme_dir = manifest_path.parent

    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    folder_name = manifest.get("folder")
    if not folder_name:
        raise ValueError(f"{manifest_path}: missing 'folder' key")

    files_patterns = manifest.get("files", [])
    if not isinstance(files_patterns, list):
        raise ValueError(f"{manifest_path}: 'files' must be a list")

    # Collect files: always include manifest, then match patterns
    files_to_add: dict[str, Path] = {}  # arcname -> source_path

    # Always add the manifest
    files_to_add["ethos_lua_manifest.json"] = manifest_path

    # Glob and add pattern matches
    if files_patterns:
        globbed = glob_files(theme_dir, files_patterns)
        for file_path in globbed:
            arcname = file_path.name  # Flatten: use only filename
            if arcname in files_to_add:
                raise ValueError(
                    f"Duplicate flattened name '{arcname}' from patterns in {manifest_path}"
                )
            files_to_add[arcname] = file_path

    # Create zip
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{folder_name}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, source_path in sorted(files_to_add.items()):
            zf.write(source_path, arcname=arcname)

    return zip_path.name, len(files_to_add)


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: package-themes.py <output_dir> [tag]",
            file=sys.stderr,
        )
        print("  output_dir: directory to write .zip files", file=sys.stderr)
        print("  tag: optional release tag to validate (release/x.X.X)", file=sys.stderr)
        return 1

    output_dir = Path(sys.argv[1])
    tag = sys.argv[2] if len(sys.argv) > 2 else None

    # Validate tag if provided
    if tag and not validate_tag(tag):
        print(f"Invalid tag format: '{tag}' (expected release/x.X.X)", file=sys.stderr)
        return 1

    # Find all manifests
    repo_root = Path(__file__).resolve().parents[2]
    manifests = sorted(repo_root.glob("themes/theme-*/ethos_lua_manifest.json"))

    if not manifests:
        print(
            "No theme manifests found under themes/theme-*/ethos_lua_manifest.json",
            file=sys.stderr,
        )
        return 1

    # Package each theme
    packaged = []
    for manifest_path in manifests:
        try:
            zip_name, file_count = package_theme(manifest_path, output_dir)
            packaged.append((zip_name, file_count))
            print(f"✓ {zip_name} ({file_count} files)")
        except Exception as exc:
            print(f"✗ {manifest_path}: {exc}", file=sys.stderr)
            return 1

    if not packaged:
        print("No zip files were created", file=sys.stderr)
        return 1

    print(f"\nCreated {len(packaged)} theme zip(s) in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
