# List of TODOs

## Candidates

- **Tools walk.** One-shot setup helpers and maintenance skills — different lens than workflow agents ("is this easy to invoke and complete?"). Targets:
  - `kit/skills/setup-e2e/SKILL.md` — 368 lines, 162-line longest section. Deferred from v4.5 Phase 3.
  - `kit/skills/prune/SKILL.md`, `kit/skills/dep-audit/SKILL.md`, `kit/skills/kit-discover/SKILL.md`, `kit/skills/whats-next/SKILL.md`, `kit/skills/techdebt/SKILL.md`, `kit/skills/visual-proof/SKILL.md`, `kit/skills/start/SKILL.md`, `kit/agents/retro-spec.md`

- **Partial-stack audit — agents/skills + dead surface (no-DB Tauri).** Continues the partial-stack work shipped in v4.5 (marker-file detection) and v4.15 (script audit, `--strict` toggle with conditional sqlx expectation). Two axes remain:
  1. **Agents/skills with hard SQLx assumptions** — sweep `kit/agents/*.md` and `kit/skills/*/SKILL.md` for misleading advice (e.g. backend reviewer expecting SQLx idioms, test-writer-backend defaulting to SQLx integration tests, contract skill assuming a DB boundary, dep-audit assuming sqlx in Cargo.toml). For each, decide: gate behind detection, or add an "if your project uses a DB" caveat.
  2. **Dead surface for no-DB projects** — what ships as pure noise? `just prepare-sqlx` recipe in `kit/common.just`, SQLx-specific reviewer rules, SQLx-flavored test-writer templates. Decide per item: ship-and-skip-when-irrelevant, gate at sync time, or split into a separate opt-in module.

- **Collapse `branch-files.sh` + `changed-files.sh` into `branch.sh files` subcommand.** _(v4.17.0 candidate — in progress on `feat/branch-sh-files`.)_ v4.7.3 introduced `branch.sh {base|diff|log}` to absorb compound shell from reviewer prompts (issue #37). Fold both file-listing scripts into a `files` subcommand and delete the originals (net −2 scripts). Hard cutover — every caller lives inside the kit and downstream re-syncs `scripts/` wholesale, so no deprecation shims. Plan:
  - **Design.** `branch.sh files` = old `branch-files.sh` (branch-diff ∪ staged ∪ unstaged ∪ untracked, with the 6 named filters `--rust|--frontend|--arch|--e2e|--migrations|--security`). Add `--uncommitted-only` to drop the branch-diff line (= old `changed-files.sh`). Filters and `--uncommitted-only` compose; bare `files` matches old `branch-files.sh` 1:1.
  - **Extend** `kit/scripts/branch.sh` with the `files)` case + arg parser; delete `branch-files.sh` / `changed-files.sh` (kit + mirrored `scripts/`).
  - **Migrate 11 callers** (`branch-files.sh [--x]` → `branch.sh files [--x]`): 10 reviewer/spec-checker agents + `visual-proof` skill.
  - **Manifests/inventory:** drop the two rows from `scripts/mirror-local.sh`; update `kit/kit-tools.md`; fold any `Bash(bash scripts/branch-files.sh *)` allowlist hint into the existing `branch.sh *` prefix.
  - **Verify:** `grep -rn "branch-files\|changed-files"` returns only history; reviewers (`script-reviewer`, `ai-reviewer`, `doc-reviewer`) + `/review-triage`; `just format` → `check.py`.

## Experimental
