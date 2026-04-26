#!/usr/bin/env bash
set -euo pipefail

# sync.sh — Profile-aware sync logic for tauri-claude-kit.
#
# Executed from the cloned kit by the bootstrap (kit/sync-config.sh).
# This script is ephemeral — it runs from $TMP and is cleaned up on exit.
# Never run this script directly.
#
# Env vars:
#   KIT_TMP  — path to the cloned kit temp directory (required)
#   PROFILE  — profile name (optional, e.g. "tauri"); empty = generic only

TMP="${KIT_TMP:?KIT_TMP not set — run via scripts/sync-config.sh}"
VERSION="${1:?VERSION not set}"

trap 'rm -rf "$TMP"' EXIT

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# ── Kit index & readme ────────────────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing kit index and readme...${NC}"
mkdir -p "$PROJECT_ROOT/.claude"
cp "$TMP/kit/kit-tools.md" "$PROJECT_ROOT/.claude/"
cp "$TMP/kit/kit-readme.md" "$PROJECT_ROOT/.claude/"

# ── Generic agents (always) ───────────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing generic agents...${NC}"
mkdir -p "$PROJECT_ROOT/.claude/agents"
for agent in "$TMP/kit/agents/"*.md; do
    [ -f "$agent" ] || continue
    cp "$agent" "$PROJECT_ROOT/.claude/agents/"
done

# ── Profile agents (overlay, additive) ───────────────────────────────────────
if [ -n "${PROFILE:-}" ] && [ -d "$TMP/kit/agents/$PROFILE" ]; then
    echo -e "${BLUE}📁 Syncing ${PROFILE} profile agents...${NC}"
    for agent in "$TMP/kit/agents/$PROFILE/"*.md; do
        [ -f "$agent" ] || continue
        cp "$agent" "$PROJECT_ROOT/.claude/agents/"
    done
fi

# ── Skills (always) ───────────────────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing skills...${NC}"
for skill_dir in "$TMP/kit/skills/"/*/; do
    skill_name=$(basename "$skill_dir")
    mkdir -p "$PROJECT_ROOT/.claude/skills/$skill_name"
    cp "$skill_dir/SKILL.md" "$PROJECT_ROOT/.claude/skills/$skill_name/"
done

# ── Git hooks (always) ────────────────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing .githooks...${NC}"
mkdir -p "$PROJECT_ROOT/.githooks"
cp "$TMP/kit/githooks/commit-msg" "$PROJECT_ROOT/.githooks/"
cp "$TMP/kit/githooks/pre-commit" "$PROJECT_ROOT/.githooks/"
cp "$TMP/kit/githooks/pre-push" "$PROJECT_ROOT/.githooks/"
cp "$TMP/kit/githooks/README.md" "$PROJECT_ROOT/.githooks/"

# ── Generic common.just (always) ──────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing common justfile...${NC}"
cp "$TMP/kit/common.just" "$PROJECT_ROOT/common.just"

# ── Profile scripts (skip if dir absent or contains only .gitkeep) ────────────
if [ -n "${PROFILE:-}" ] && [ -d "$TMP/kit/scripts/$PROFILE" ]; then
    HAS_SCRIPTS=false
    for f in "$TMP/kit/scripts/$PROFILE/"*; do
        [ -f "$f" ] || continue
        [ "$(basename "$f")" = ".gitkeep" ] && continue
        HAS_SCRIPTS=true
        break
    done
    if [ "$HAS_SCRIPTS" = true ]; then
        echo -e "${BLUE}📁 Syncing ${PROFILE} profile scripts...${NC}"
        mkdir -p "$PROJECT_ROOT/scripts"
        for f in "$TMP/kit/scripts/$PROFILE/"*; do
            [ -f "$f" ] || continue
            [ "$(basename "$f")" = ".gitkeep" ] && continue
            cp "$f" "$PROJECT_ROOT/scripts/"
        done
    fi
fi

# ── Profile justfile recipes (append) ─────────────────────────────────────────
if [ -n "${PROFILE:-}" ] && [ -f "$TMP/kit/justfile/$PROFILE.just" ]; then
    echo -e "${BLUE}📁 Appending ${PROFILE} justfile recipes...${NC}"
    printf '\n' >>"$PROJECT_ROOT/common.just"
    cat "$TMP/kit/justfile/$PROFILE.just" >>"$PROJECT_ROOT/common.just"
fi

# ── Version stamp & summary ───────────────────────────────────────────────────
echo "$VERSION" >"$PROJECT_ROOT/.claude-kit-version"

if [ -n "${PROFILE:-}" ]; then
    echo -e "${GREEN}✅ Synced tauri-claude-kit@${VERSION} — generic agents + profile: ${PROFILE}${NC}"
else
    echo -e "${GREEN}✅ Synced tauri-claude-kit@${VERSION} — generic agents only${NC}"
fi
echo -e "${YELLOW}→ Review changes before committing (git diff).${NC}"
