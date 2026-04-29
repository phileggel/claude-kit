# Web profile — PostgreSQL / Axum recipes — appended to common.just by sync

# Backend directory — override here if your layout uses a different name (e.g. "backend")
BACKEND_DIR := "server"

# Run pending database migrations
# Prerequisites: sqlx must be on $PATH and DATABASE_URL must be set
migrate:
    cd {{BACKEND_DIR}} && sqlx migrate run

# ⚠️  Destructive: drops and recreates the local database
# Prerequisites: DATABASE_URL must point to the local dev database
db-reset:
    cd {{BACKEND_DIR}} && sqlx database reset

# Regenerate SQLx offline query cache (run after schema or query changes)
# Prerequisites: DATABASE_URL must be set to a running database
prepare-sqlx:
    cd {{BACKEND_DIR}} && cargo sqlx prepare

# Auto-fix formatting and linting
format:
    @cd {{BACKEND_DIR}} && cargo fmt
    @cd {{BACKEND_DIR}} && cargo clippy --fix --allow-dirty --quiet
    @npm run format:fix
    @npm run format:docs
