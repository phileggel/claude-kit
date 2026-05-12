# List of TODOs

## v4.6 candidates

_All v4.6 candidates resolved — see commit history. Remaining work is in v4.7._

## v4.7 candidates

- **SDD Workflow A walk — remaining reviewers.** v4.6 walked `test-writer-e2e` and extracted `reviewer-e2e` from `reviewer-frontend`. Workflow A Phase 4 still has four un-walked reviewers:
  - `kit/agents/reviewer-arch.md` — always runs in Phase 4 of A; also in Workflow B
  - `kit/agents/reviewer-sql.md` — if migrations modified
  - `kit/agents/reviewer-infra.md` — 342 lines; needs convention alignment
  - `kit/agents/reviewer-security.md` — convention alignment

  Per file: run `ai-reviewer`, apply structural and density findings, align with sibling pattern (`## Not to be confused with`, `## When to use` / `When NOT to use`, `## Output format`, `## Notes`), `/preflight`. Fold v4.4+v4.5 rule references where they apply.

- **`reviewer-arch` trigger scoping** (post-`reviewer-e2e` split). After v4.6's `reviewer-frontend` → `reviewer-frontend` + `reviewer-e2e` split, `reviewer-arch`'s frontmatter trigger still says "Any `.rs`, `.ts`, or `.tsx` modified" — which includes `e2e/**/*.test.ts`. Decide: should `reviewer-arch` exclude E2E test files? Reasonable answer is yes (E2E scenarios aren't DDD-architecture surfaces), but verify before changing. Small follow-up; fold into the `reviewer-arch` walk above.

- **SDD Workflow B walk — verify reviewer dual-use.** Reviewer agents (`reviewer-arch`, `reviewer-backend`, `reviewer-frontend`, `reviewer-e2e`, `reviewer-sql`, `reviewer-infra`, `reviewer-security`) are used by both Workflow A (Phase 4) and Workflow B (step 5). Workflow B has no `docs/plan/{feature}-plan.md`, no `docs/contracts/{domain}-contract.md`, no `docs/spec/{domain}.md`. Verify each reviewer handles the no-plan / no-contract context gracefully (no hard reads, no halts on absent files). Likely surface mostly verification with small graceful-skip patches.

- **Tools walk.** One-shot setup helpers and maintenance skills — different lens than workflow agents ("is this easy to invoke and complete?"). Targets:
  - `kit/skills/setup-e2e/SKILL.md` — 368 lines, 162-line longest section. Deferred from v4.5 Phase 3.
  - `kit/skills/prune/SKILL.md`, `kit/skills/dep-audit/SKILL.md`, `kit/skills/kit-discover/SKILL.md`, `kit/skills/whats-next/SKILL.md`, `kit/skills/techdebt/SKILL.md`, `kit/skills/visual-proof/SKILL.md`, `kit/skills/start/SKILL.md`, `kit/agents/retro-spec.md`

- **`merge.py` post-merge cleanup of stale remote branch.** v4.6's `merge.py` rewrite deletes the local branch after merge but does not delete the remote tracking branch. When the local branch is "ahead of" its upstream (e.g. later commits never pushed to the feature branch), `git branch -d` refuses. Surface bug hit during v4.6's own release. Fix: before `git branch -d`, run `git push --delete origin <branch>` if the remote branch exists. Restores the "single atomic shortcut" property.

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

## Experimental
