# List of TODOs

## v4.7 candidates

- **SDD Workflow B walk — verify reviewer dual-use.** Reviewer agents (`reviewer-arch`, `reviewer-backend`, `reviewer-frontend`, `reviewer-e2e`, `reviewer-sql`, `reviewer-infra`, `reviewer-security`) are used by both Workflow A (Phase 4) and Workflow B (step 5). Workflow B has no `docs/plan/{feature}-plan.md`, no `docs/contracts/{domain}-contract.md`, no `docs/spec/{domain}.md`. Verify each reviewer handles the no-plan / no-contract context gracefully (no hard reads, no halts on absent files). Likely surface mostly verification with small graceful-skip patches.

- **Tools walk.** One-shot setup helpers and maintenance skills — different lens than workflow agents ("is this easy to invoke and complete?"). Targets:
  - `kit/skills/setup-e2e/SKILL.md` — 368 lines, 162-line longest section. Deferred from v4.5 Phase 3.
  - `kit/skills/prune/SKILL.md`, `kit/skills/dep-audit/SKILL.md`, `kit/skills/kit-discover/SKILL.md`, `kit/skills/whats-next/SKILL.md`, `kit/skills/techdebt/SKILL.md`, `kit/skills/visual-proof/SKILL.md`, `kit/skills/start/SKILL.md`, `kit/agents/retro-spec.md`

- **Partial-stack audit + `--strict` toggle generalization (no-DB Tauri, etc.).** Generalizes the work shipped in v4.5 for issue #15 (graceful skip on absent stack). v4.5 added marker-file detection (`package.json`, `src-tauri/Cargo.toml`, `src-tauri/.sqlx/`) and per-checker skip-with-summary; this candidate completes the partial-stack story across the rest of the kit and adds release-time strictness.

  Three axes to audit (output is a concrete fix list, not the fixes themselves):
  1. **Scripts beyond `check.py`** — sweep all `kit/scripts/*` and any DB-touching agent helper scripts to confirm they all skip-not-fail when `.sqlx/`, `migrations/`, or DB env vars are absent. Catch partial-stack edge cases (`migrations/` exists but `.sqlx/` doesn't, or the reverse).
  2. **Agents/skills with hard SQLx assumptions** — sweep `kit/agents/*.md` and `kit/skills/*/SKILL.md` for misleading advice (e.g. backend reviewer expecting SQLx idioms, test-writer-backend defaulting to SQLx integration tests, contract skill assuming a DB boundary, dep-audit assuming sqlx in Cargo.toml). For each, decide: gate behind detection, or add an "if your project uses a DB" caveat.
  3. **Dead surface for no-DB projects** — what ships as pure noise? `just prepare-sqlx` recipe in `kit/common.just`, SQLx-specific reviewer rules, SQLx-flavored test-writer templates. Decide per item: ship-and-skip-when-irrelevant, gate at sync time, or split into a separate opt-in module.

  **`--strict` toggle** — `check.py` currently treats absent stack as `SKIPPED` (correct for `--fast` / pre-commit). In strict mode (used by `release.py`), absent stack should arguably FAIL: releases shouldn't ship without exercising the full quality gate. But a deliberately no-DB Tauri project should still be releasable. Decide the policy:
  - Option A: `--strict` requires all markers — simple but excludes legitimate no-DB releases.
  - Option B: `--strict` distinguishes core stack (`package.json` + `Cargo.toml` required) from optional stack (`.sqlx/` optional). Allows no-DB releases while still gating "you forgot to scaffold React".
  - Option C: project-level config flag declares which markers are expected. Most flexible, more moving parts.

  Closes GH #15 + #27 as side-effects. Categorisation per fix item: graceful-skip / doc-gate / sync-time-exclude / accept-as-noise / strict-required.

- **`reviewer-backend` convention audit.** Surfaced during the reviewer-arch/sql/infra/security walk on `feat/v4.7-candidates`. `reviewer-backend.md` (198 lines, untouched in v4.6) likely shares the structural gaps the four sibling walks fixed: missing `## Not to be confused with`, `## When to use` / `When NOT to use`, `## Critical Rules`, `## Notes`; possibly stale base-resolution if Step 3 doesn't use the `BASE=$(git merge-base ...)` fallback chain. Run `ai-reviewer` once, apply must-fix + structural alignment, `/preflight`. Single-file scope.

- **Stable rule numbering for DDD + SQL conventions.** v4.4 introduced rule-number stability for `frontend-rules.md` (F-NN) and `backend-rules.md` (B-NN). Two gaps surface: (1) `docs/ddd-reference.md` is a concept glossary without numbered rules — `reviewer-arch` cites zero rule numbers in its DDD block, breaking the v4.4 pattern; (2) SQL conventions inside `backend-rules.md` aren't separately numbered (no SQL-NN scheme), so `reviewer-sql` findings can't cite a stable id. Decide per-doc: introduce numbered rules (D-NN, SQL-NN), accept the asymmetry as "DDD/SQL conventions are external/established, not project style rules", or hybrid (number SQL, leave DDD). Output is a documented decision + (if number) the renumbered doc and reviewer citations.

- **Collapse `branch-files.sh` + `changed-files.sh` into `branch.sh files` subcommand.** v4.7.3 introduced `branch.sh {base|diff|log}` to absorb compound shell from reviewer prompts (issue #37). `branch-files.sh` and `changed-files.sh` differ by exactly one line (whether the committed branch diff is included) — natural candidates to fold in as `branch.sh files` and `branch.sh files --uncommitted-only`. Net −2 scripts. Breaking change for downstream callers (agents naming the scripts directly) — handle as a coordinated rename + sync cycle, not piecemeal.

- **`release.py` deferred refactors.** Script-reviewer surfaced 13 pre-existing items on `feat/v4.7-candidates`; the cheap ones (atomic push, UTC datetime, `--no-verify` waiver, `MAIN_BRANCH` constant, `cargo metadata` recovery) landed inline. Remaining (refactor-tax, not bugs):
  1. `run()` is 84 lines and 8 responsibilities — split into `_resolve_version()` / `_apply_changes()` / `_finalize()`.
  2. `preview` + `dry_run` are two booleans where a `Mode = {REAL, DRY_RUN, PREVIEW}` enum + argparse mutex group belongs.
  3. `Optional[str]` / `List[dict]` imports — migrate to PEP 604 (`str | None`, `list[dict]`).

- **`check.py` deferred polish.** Cheap items (subprocess timeouts, missing-tool diagnostic, `check_sqlx` `check=False`) landed inline. Remaining:
  1. `Optional[Path]` / `List[str]` imports — migrate to PEP 604.
  2. Magic strings repeated (`"src-tauri/Cargo.toml absent"` × 4, `"package.json absent"` × 6) — extract constants.
  3. Stack-marker paths hard-coded to `src-tauri/` layout — should be discoverable for frontend-only projects.
  4. Emoji column width: `_pad_visible` pads by Python `len()` which counts the ⏩/✅/❌ as 1 char but terminals render them as 2 columns; the table is off by 1 column on emoji rows. Either depend on `wcwidth` or hardcode emoji width compensation.

- **`merge.py` force-push divergence pre-flight.** Surfaced as out-of-scope by script-reviewer on the v4.7 fix. Today: if `origin/<branch>` has commits not in local (someone force-pushed while user wasn't pulling), Step 2's local rebase discards them and Step 5 deletes them from origin without warning. By-design for local-only feature branches, footgun for shared ones. Add Pre-flight 5: `git fetch origin <branch>` + ahead/behind check; refuse if `origin/<branch>` has commits not in local.

- **`common.just` partial-stack guards.** `cd src-tauri &&` recipes (`migrate`, `generate-types`, `prepare-sqlx`, `clean-db`, `format`) lack the `[ -d src-tauri ]` guard that script-backed recipes use — non-Tauri downstream projects get a bare `cd: src-tauri: No such file or directory`. Single-line guard per recipe.

## Experimental
