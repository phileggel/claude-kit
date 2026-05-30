# List of TODOs

## Candidates

- **Tools walk.** _(v4.17.0 — in progress on `feat/v4.17-candidates`.)_ Audit each one-shot tool skill for invocability: "is this easy to invoke and complete?" — clear trigger with no sibling overlap, documented args (or explicitly none), a deterministic "done" state, no dead-ends, no compound-shell permission-prompt traps. Flag length only where it buries the steps. One commit per skill: analyze → update → review.
  - **Set (7):** `setup-e2e` (368L), `prune` (312L), `visual-proof` (290L), `whats-next` (206L), `kit-discover` (183L), `dep-audit` (154L), `techdebt` (107L).
  - **Excluded:** `start` (workflow selector, reviewed in the SDD pipeline); `retro-spec` (removed this cycle — never used; re-add if it earns a place).

- **Partial-stack audit — agents/skills + dead surface (no-DB Tauri).** Continues the partial-stack work shipped in v4.5 (marker-file detection) and v4.15 (script audit, `--strict` toggle with conditional sqlx expectation). Two axes remain:
  1. **Agents/skills with hard SQLx assumptions** — sweep `kit/agents/*.md` and `kit/skills/*/SKILL.md` for misleading advice (e.g. backend reviewer expecting SQLx idioms, test-writer-backend defaulting to SQLx integration tests, contract skill assuming a DB boundary, dep-audit assuming sqlx in Cargo.toml). For each, decide: gate behind detection, or add an "if your project uses a DB" caveat.
  2. **Dead surface for no-DB projects** — what ships as pure noise? `just prepare-sqlx` recipe in `kit/common.just`, SQLx-specific reviewer rules, SQLx-flavored test-writer templates. Decide per item: ship-and-skip-when-irrelevant, gate at sync time, or split into a separate opt-in module.

## Experimental
