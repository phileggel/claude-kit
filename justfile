# Release the kit specifically
kit-release:
    python3 scripts/release-kit.py

# Auto-fix formatting and linting for this kit
format:
    ruff format scripts/
    ruff check --fix scripts/
    shfmt -i 4 -w scripts/ .githooks/
    npx prettier --write "**/*.md" --ignore-path .gitignore
