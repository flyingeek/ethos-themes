#!/bin/bash
# Sync themes and README.md to EFC-themes repository
# Usage: ./sync-themes.sh [--dry-run]

set -euo pipefail

DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
    echo "🔍 DRY-RUN MODE (no changes will be made)"
fi

WORKSPACE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="${WORKSPACE_ROOT}/themes"
TARGET="${WORKSPACE_ROOT}/../EFC-themes/lua/themes"

echo "📦 Syncing themes to: $TARGET"
echo ""

# Verify source directory exists
if [[ ! -d "$SOURCE" ]]; then
    echo "❌ Source directory does not exist: $SOURCE"
    exit 1
fi

# Verify target directory exists
if [[ ! -d "$TARGET" ]]; then
    echo "❌ Target directory does not exist: $TARGET"
    echo "   Please ensure ../EFC-themes/lua/themes/ is set up."
    exit 1
fi

# Sync the managed root files explicitly so destination-only infrastructure files are left alone.
echo "→ Syncing themes README.md..."
rsync $DRY_RUN -av \
    --exclude='*.luac' \
    --exclude='.DS_Store' \
    "$SOURCE/README.md" "$TARGET/"

echo "→ Syncing theme directories..."
for theme_dir in "$SOURCE"/theme-*; do
    if [[ ! -d "$theme_dir" ]]; then
        continue
    fi

    echo "  - $(basename "$theme_dir")"
    rsync $DRY_RUN -av --delete \
        --exclude='*.luac' \
        --exclude='.DS_Store' \
        "$theme_dir/" "$TARGET/$(basename "$theme_dir")/"
done

echo ""
if [[ -n "$DRY_RUN" ]]; then
    echo "✓ Dry-run complete. No files were modified."
else
    echo "✓ Sync complete!"
fi
