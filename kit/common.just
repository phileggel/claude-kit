# Common recipes — synced from kit to downstream projects via sync-config.sh

sync-kit:
    ./scripts/sync-config.sh

# Run fast quality check (lint/format only, no tests)
check:
    @[ -f scripts/check.py ] || { echo "❌ scripts/check.py not found — run: just sync-kit"; exit 1; }
    python3 scripts/check.py --fast

# Run full quality check (tests + build + lint)
check-full:
    @[ -f scripts/check.py ] || { echo "❌ scripts/check.py not found — run: just sync-kit"; exit 1; }
    python3 scripts/check.py

# Release new version (interactive)
release *ARGS:
    @[ -f scripts/release.py ] || { echo "❌ scripts/release.py not found — run: just sync-kit"; exit 1; }
    python3 scripts/release.py {{ARGS}}

# ⚠️  Destructive: removes stale remote-tracking branches
clean-branches:
    git fetch --prune
    git branch -vv | grep ': gone]' | awk '{print $1}' | xargs git branch -D || true

stat:
    cloc . --vcs=git

# Fast-forward current branch into main (no merge commit), then delete the branch
merge:
    #!/usr/bin/env bash
    set -euo pipefail
    branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$branch" = "main" ]; then echo "❌ Already on main — nothing to merge."; exit 1; fi
    git checkout main
    git merge --ff-only "$branch"
    git branch -d "$branch"
    echo "✅ $branch fast-forwarded into main and deleted."
