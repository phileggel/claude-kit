#!/usr/bin/env bash
set -euo pipefail

# sync-config.sh — Stable bootstrap entry point for claude-kit.
#
# Copy this file once to scripts/sync-config.sh in your downstream project.
# This file is intentionally minimal — all sync logic lives in kit/scripts/sync.sh.
#
# Usage:
#   ./scripts/sync-config.sh            # sync latest release tag
#   ./scripts/sync-config.sh v4.0.0     # sync a specific tag
#   ./scripts/sync-config.sh -f         # overwrite drifted docs without prompting

REPO="https://github.com/phileggel/claude-kit"
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

VERSION=""
KIT_SYNC_FORCE="false"

while [[ $# -gt 0 ]]; do
    case "$1" in
    --profile=* | --profile)
        echo -e "${YELLOW}⚠  --profile is deprecated and ignored — claude-kit is Tauri-only as of v4.0.0${NC}"
        # Skip the value too if --profile was given as a separate arg
        if [[ "$1" == "--profile" ]] && [[ $# -ge 2 ]]; then shift; fi
        shift
        ;;
    -f | --force)
        KIT_SYNC_FORCE="true"
        shift
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

TMP=$(mktemp -d)
# $TMP is NOT cleaned here — ownership passes to sync.sh via KIT_TMP

echo -e "${BLUE}⬇  Cloning claude-kit@${VERSION}...${NC}"
git clone --depth 1 --branch "$VERSION" "$REPO" "$TMP" --quiet \
    -c core.autocrlf=false

export KIT_TMP="$TMP"
export KIT_SYNC_FORCE
exec bash "$TMP/kit/scripts/sync.sh" "$VERSION"
