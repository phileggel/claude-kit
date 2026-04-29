# Web profile — PostgreSQL / Axum recipes — appended to common.just by sync

# Run pending database migrations
# Prerequisites: sqlx must be on $PATH and DATABASE_URL must be set
migrate:
    cd server && sqlx migrate run

# ⚠️  Destructive: drops and recreates the local database
# Prerequisites: DATABASE_URL must point to the local dev database
db-reset:
    cd server && sqlx database reset

# Regenerate SQLx offline query cache (run after schema or query changes)
# Prerequisites: DATABASE_URL must be set to a running database
prepare-sqlx:
    cd server && cargo sqlx prepare
