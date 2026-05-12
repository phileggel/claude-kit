# Release the kit specifically
release *ARGS:
    python3 scripts/release-kit.py {{ARGS}}

# Auto-fix formatting and linting for this kit
format:
    ruff format scripts/ kit/scripts/
    ruff check --fix scripts/ kit/scripts/
    shfmt -i 4 -w kit/scripts/ kit/githooks/ kit/sync-config.sh
    npx prettier --write "**/*.md" --ignore-path .gitignore

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
