# Release the kit specifically
release *ARGS:
    python3 scripts/release-kit.py {{ARGS}}

# Auto-fix formatting and linting for this kit
format:
    ruff format scripts/ kit/scripts/
    ruff check --fix scripts/ kit/scripts/
    shfmt -i 4 -w kit/scripts/ kit/githooks/ kit/sync-config.sh
    npx --yes @biomejs/biome check --write --line-width=100 kit/scripts/
    npx prettier --write "**/*.md" --ignore-path .gitignore

# Lint kit-shipped scripts against tool defaults — catches files that would
# fail downstream linters at first sync. biome (recommended + lineWidth=100),
# ruff (kit-default selection), shellcheck (default). No project config; CLI
# flags only — the kit is not a Node/Python project, only ships scripts.
lint-scripts:
    #!/usr/bin/env bash
    set -euo pipefail
    fail=0
    mjs=$(find kit/scripts -maxdepth 1 -type f \( -name '*.mjs' -o -name '*.js' \) | sort)
    py=$(find kit/scripts -maxdepth 1 -type f -name '*.py' | sort)
    # Include kit/sync-config.sh — the bootstrap script ships once to downstream
    # as scripts/sync-config.sh but lives outside kit/scripts/.
    sh=$( { find kit/scripts -maxdepth 1 -type f -name '*.sh'; echo kit/sync-config.sh; } | sort)
    if [ -n "$mjs" ]; then
        echo "▶ biome check (lineWidth=100): $(echo "$mjs" | wc -l) file(s)"
        # shellcheck disable=SC2086  # word-splitting intentional for the file list
        npx --yes @biomejs/biome check --line-width=100 $mjs || fail=1
    fi
    if [ -n "$py" ]; then
        echo "▶ ruff check + format --check: $(echo "$py" | wc -l) file(s)"
        # shellcheck disable=SC2086
        ruff check $py || fail=1
        # shellcheck disable=SC2086
        ruff format --check $py || fail=1
    fi
    if [ -n "$sh" ]; then
        echo "▶ shellcheck: $(echo "$sh" | wc -l) file(s)"
        # shellcheck disable=SC2086
        shellcheck $sh || fail=1
    fi
    exit "$fail"

stat:
    cloc . --vcs=git

# Run kit quality checks
check:
    python3 scripts/check.py

# Mirror kit skills and hooks to .claude/skills/ and .githooks/ for local kit development
mirror-local:
    bash scripts/mirror-local.sh

# Auto-rebase + FF-merge current branch into main, push, then delete the branch.
# Soft failure on conflict: aborts the rebase and leaves the branch unchanged.
merge:
    python3 kit/scripts/merge.py

# Auto-rebase + FF-merge current branch into svelte-main, push, then delete the branch.
merge-svelte:
    python3 kit/scripts/merge.py --target svelte-main
