#!/usr/bin/env bash
set -euo pipefail

# sync.sh — Real sync logic for tauri-claude-kit.
#
# Executed from the cloned kit by the bootstrap (kit/sync-config.sh).
# This script is ephemeral — it runs from $TMP and is cleaned up on exit.
# Never run this script directly.

TMP="${KIT_TMP:?KIT_TMP not set — run via scripts/sync-config.sh}"
VERSION="${1:?VERSION not set}"

trap 'rm -rf "$TMP"' EXIT

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

echo -e "${BLUE}📁 Syncing kit-tools index...${NC}"
mkdir -p "$PROJECT_ROOT/.claude"
cp "$TMP/kit/kit-tools.md" "$PROJECT_ROOT/.claude/"

echo -e "${BLUE}📁 Syncing agents...${NC}"
mkdir -p "$PROJECT_ROOT/.claude/agents"
for agent in "$TMP/kit/agents/"*.md; do
    cp "$agent" "$PROJECT_ROOT/.claude/agents/"
done

echo -e "${BLUE}📁 Syncing skills...${NC}"
for skill_dir in "$TMP/kit/skills/"/*/; do
    skill_name=$(basename "$skill_dir")
    mkdir -p "$PROJECT_ROOT/.claude/skills/$skill_name"
    cp "$skill_dir/SKILL.md" "$PROJECT_ROOT/.claude/skills/$skill_name/"
done

echo -e "${BLUE}📁 Syncing scripts...${NC}"
mkdir -p "$PROJECT_ROOT/scripts"
cp "$TMP/kit/scripts/check.py" "$PROJECT_ROOT/scripts/"
cp "$TMP/kit/scripts/release.py" "$PROJECT_ROOT/scripts/"

echo -e "${BLUE}📁 Syncing .githooks...${NC}"
mkdir -p "$PROJECT_ROOT/.githooks"
cp "$TMP/kit/githooks/commit-msg" "$PROJECT_ROOT/.githooks/"
cp "$TMP/kit/githooks/pre-commit" "$PROJECT_ROOT/.githooks/"
cp "$TMP/kit/githooks/pre-push" "$PROJECT_ROOT/.githooks/"
cp "$TMP/kit/githooks/README.md" "$PROJECT_ROOT/.githooks/"

echo -e "${BLUE}📁 Syncing common justfile...${NC}"
cp "$TMP/kit/common.just" "$PROJECT_ROOT/common.just"

echo "$VERSION" >"$PROJECT_ROOT/.claude-kit-version"

echo -e "${GREEN}✅ Synced tauri-claude-kit@${VERSION}${NC}"
echo -e "${YELLOW}→ Review changes before committing (git diff).${NC}"
