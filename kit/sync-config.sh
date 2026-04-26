#!/usr/bin/env bash
set -euo pipefail

# sync-config.sh — Stable bootstrap entry point for tauri-claude-kit.
#
# Copy this file once to scripts/sync-config.sh in your downstream project.
# This file is intentionally minimal — all sync logic lives in kit/scripts/sync.sh.
#
# Usage:
#   ./scripts/sync-config.sh                    # sync latest release tag
#   ./scripts/sync-config.sh v2.0.0             # sync a specific tag
#   ./scripts/sync-config.sh --profile tauri    # explicit profile override
#   ./scripts/sync-config.sh v2.0.0 --profile tauri

REPO="https://github.com/phileggel/tauri-claude-kit"
BLUE='\033[0;34m'
NC='\033[0m'

VERSION=""
PROFILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
    --profile=*)
        PROFILE="${1#*=}"
        shift
        ;;
    --profile)
        PROFILE="${2:-}"
        shift 2
        ;;
    *)
        VERSION="$1"
        shift
        ;;
    esac
done

if [[ -z "$VERSION" ]]; then
    VERSION=$(git ls-remote --tags --sort="v:refname" "$REPO" | tail -n1 | sed 's/.*\///; s/\^{}//')
fi

# Fall back to .claude/kit-profile if --profile not given on the command line
if [[ -z "$PROFILE" ]] && [[ -f ".claude/kit-profile" ]]; then
    PROFILE=$(tr -d '[:space:]' <".claude/kit-profile")
fi

if [[ -z "$PROFILE" ]]; then
    echo "ℹ️  No .claude/kit-profile found — syncing generic agents only"
fi

TMP=$(mktemp -d)
# $TMP is NOT cleaned here — ownership passes to sync.sh via KIT_TMP

echo -e "${BLUE}⬇  Cloning tauri-claude-kit@${VERSION}...${NC}"
git clone --depth 1 --branch "$VERSION" "$REPO" "$TMP" --quiet \
    -c core.autocrlf=false

export KIT_TMP="$TMP"
export PROFILE
exec bash "$TMP/kit/scripts/sync.sh" "$VERSION"
