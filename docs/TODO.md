# List of TODOs

## Candidates

- **Partial-stack audit — agents/skills + dead surface (no-DB Tauri).** Continues the partial-stack work shipped in v4.5 (marker-file detection) and v4.15 (script audit, `--strict` toggle with conditional sqlx expectation). Two axes remain:
  1. **Agents/skills with hard SQLx assumptions** — sweep `kit/agents/*.md` and `kit/skills/*/SKILL.md` for misleading advice (e.g. backend reviewer expecting SQLx idioms, test-writer-backend defaulting to SQLx integration tests, contract skill assuming a DB boundary, dep-audit assuming sqlx in Cargo.toml). For each, decide: gate behind detection, or add an "if your project uses a DB" caveat.
  2. **Dead surface for no-DB projects** — what ships as pure noise? `just prepare-sqlx` recipe in `kit/common.just`, SQLx-specific reviewer rules, SQLx-flavored test-writer templates. Decide per item: ship-and-skip-when-irrelevant, gate at sync time, or split into a separate opt-in module.

## Experimental
