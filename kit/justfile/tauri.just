# Tauri profile recipes — appended to common.just by sync

# Run pending database migrations
# Prerequisites: sqlx must be on $PATH and DATABASE_URL must be set
migrate:
    cd src-tauri && sqlx migrate run

# Regenerate Specta TypeScript bindings (run after adding or changing Tauri commands)
# The exact command depends on your Specta export setup — override in your local justfile if needed
generate-types:
    cd src-tauri && cargo test export_bindings

# Regenerate SQLx offline query cache (run after schema or query changes)
prepare-sqlx:
    cd src-tauri && DATABASE_URL="sqlite:.local/dev_check.sqlite" cargo sqlx prepare -- --tests

# Auto-fix formatting and linting
format:
    @cd src-tauri && cargo fmt
    @cd src-tauri && cargo clippy --fix --allow-dirty --quiet
    @npm run format:fix
    @npm run format:docs

# ⚠️  Destructive: deletes local database and recreates schema
clean-db:
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf src-tauri/.local/*
    cd src-tauri && sqlx database setup
