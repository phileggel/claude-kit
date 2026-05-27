# List of TODOs

## Candidates

- **Tools walk.** One-shot setup helpers and maintenance skills — different lens than workflow agents ("is this easy to invoke and complete?"). Targets:
  - `kit/skills/setup-e2e/SKILL.md` — 368 lines, 162-line longest section. Deferred from v4.5 Phase 3.
  - `kit/skills/prune/SKILL.md`, `kit/skills/dep-audit/SKILL.md`, `kit/skills/kit-discover/SKILL.md`, `kit/skills/whats-next/SKILL.md`, `kit/skills/techdebt/SKILL.md`, `kit/skills/visual-proof/SKILL.md`, `kit/skills/start/SKILL.md`, `kit/agents/retro-spec.md`

- **Partial-stack audit — agents/skills + dead surface (no-DB Tauri).** Continues the partial-stack work shipped in v4.5 (marker-file detection) and v4.15 (script audit, `--strict` toggle with conditional sqlx expectation). Two axes remain:
  1. **Agents/skills with hard SQLx assumptions** — sweep `kit/agents/*.md` and `kit/skills/*/SKILL.md` for misleading advice (e.g. backend reviewer expecting SQLx idioms, test-writer-backend defaulting to SQLx integration tests, contract skill assuming a DB boundary, dep-audit assuming sqlx in Cargo.toml). For each, decide: gate behind detection, or add an "if your project uses a DB" caveat.
  2. **Dead surface for no-DB projects** — what ships as pure noise? `just prepare-sqlx` recipe in `kit/common.just`, SQLx-specific reviewer rules, SQLx-flavored test-writer templates. Decide per item: ship-and-skip-when-irrelevant, gate at sync time, or split into a separate opt-in module.

- **Collapse `branch-files.sh` + `changed-files.sh` into `branch.sh files` subcommand.** v4.7.3 introduced `branch.sh {base|diff|log}` to absorb compound shell from reviewer prompts (issue #37). `branch-files.sh` and `changed-files.sh` differ by exactly one line (whether the committed branch diff is included) — natural candidates to fold in as `branch.sh files` and `branch.sh files --uncommitted-only`. Net −2 scripts. Breaking change for downstream callers (agents naming the scripts directly) — handle as a coordinated rename + sync cycle, not piecemeal.

## Experimental
