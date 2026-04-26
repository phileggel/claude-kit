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