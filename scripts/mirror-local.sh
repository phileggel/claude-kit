#!/usr/bin/env bash
set -euo pipefail

# mirror-local.sh — Mirror kit artifacts into the local kit repo so they are
# active during kit development. Run via: just mirror-local
#
# Mirrors:
#   kit/skills/{skill}/SKILL.md  → .claude/skills/{skill}/SKILL.md
#   kit/githooks/{hook}          → .githooks/{hook}  (executable, README excluded)

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# Skills
SKILLS=(smart-commit whats-next create-pr)

for skill in "${SKILLS[@]}"; do
    src="$PROJECT_ROOT/kit/skills/$skill/SKILL.md"
    dst_dir="$PROJECT_ROOT/.claude/skills/$skill"

    if [ ! -f "$src" ]; then
        echo "⚠  Skipping skill $skill — source not found"
        continue
    fi

    mkdir -p "$dst_dir"
    cp "$src" "$dst_dir/SKILL.md"
    echo "✅ Mirrored skill: $skill"
done

# Git hooks (exclude README.md)
mkdir -p "$PROJECT_ROOT/.githooks"
for src in "$PROJECT_ROOT/kit/githooks/"*; do
    filename="$(basename "$src")"
    [ "$filename" = "README.md" ] && continue

    cp "$src" "$PROJECT_ROOT/.githooks/$filename"
    chmod +x "$PROJECT_ROOT/.githooks/$filename"
    echo "✅ Mirrored hook:  $filename"
done

# Generic scripts (mirrors what sync.sh copies to downstream projects)
# Excludes sync.sh — that is ephemeral kit infrastructure, not a project helper.
mkdir -p "$PROJECT_ROOT/scripts"
for src in "$PROJECT_ROOT/kit/scripts/"*.sh; do
    filename="$(basename "$src")"
    [ "$filename" = "sync.sh" ] && continue

    cp "$src" "$PROJECT_ROOT/scripts/$filename"
    chmod +x "$PROJECT_ROOT/scripts/$filename"
    echo "✅ Mirrored script: $filename"
done

# Remind user to activate hooks if not already done
HOOKS_PATH="$(git -C "$PROJECT_ROOT" config core.hooksPath 2>/dev/null || true)"
if [ "$HOOKS_PATH" != ".githooks" ]; then
    echo ""
    echo "⚠  Hooks not yet active. Run once:"
    echo "   git config core.hooksPath .githooks"
fi
