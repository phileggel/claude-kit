# List of TODOs

## v4.5 candidates

_All v4.5 candidates resolved — see commit history. Remaining work is in v4.6._

## v4.6 candidates

- **Framework-aware sync convergence onto `main`.** Port the framework-aware strip-suffix logic from `svelte-main`'s `sync.sh` (+~80 lines) and the framework tag-filter from `sync-config.sh` (+~25 lines) back to `main`. Lossless for React downstream: `.claude/kit.config.json` defaults to `framework: react`, behaviour is unchanged when the flag is absent. Eliminates the highest-friction cherry-pick targets between main and svelte-main. Per memory `project_svelte_script_divergence`: explicitly designated for "the next genuine v4.6.0 feature release, not as a standalone patch". After this lands, the script-divergence table shrinks from 5 to 3 entries.

- **SDD Phase 4 walk: align review & closure agents with v4.3+ conventions.** Phases 1, 2, 3 walked in earlier releases (1 pre-v4.2, 2 in v4.3, 3 in v4.5). Phase 4 is the last remaining SDD phase. Targets:
  - `kit/agents/test-writer-e2e.md` — heaviest unwalked file (302 lines, 246-line longest section, 17 critical rules). Natural fold-in of v4.5's E4 (stable `id` selectors) change.
  - `kit/agents/reviewer-infra.md` — 342 lines; needs convention alignment.
  - `kit/agents/reviewer-security.md` — convention alignment.
  - `kit/skills/setup-e2e/SKILL.md` — deferred from v4.5 Phase 3 (frontend-adjacent). 368 lines, 162-line longest section.

  Per file: run `ai-reviewer` to surface findings, apply fixes (frontmatter discoverability, structural completeness, tool-grant minimality, density trimming, voice consistency), then `/preflight`. Fold the v4.4+v4.5 FE rules (E4, F24, F25, F28) where they apply (especially in `test-writer-e2e` and `setup-e2e`).

  Closes the SDD walk story; maintenance/sanity skills (prune, dep-audit, kit-discover, etc.) stay ad-hoc — not a formal walk batch.

- **Partial-stack audit + `--strict` toggle generalization (no-DB Tauri, etc.).** Generalizes the work shipped in v4.5 for issue #15 (graceful skip on absent stack). v4.5 added marker-file detection (`package.json`, `src-tauri/Cargo.toml`, `src-tauri/.sqlx/`) and per-checker skip-with-summary; this v4.6 candidate completes the partial-stack story across the rest of the kit and adds release-time strictness.

  Three axes to audit (output is a concrete fix list, not the fixes themselves):
  1. **Scripts beyond `check.py`** — sweep all `kit/scripts/*` and any DB-touching agent helper scripts to confirm they all skip-not-fail when `.sqlx/`, `migrations/`, or DB env vars are absent. Catch partial-stack edge cases (`migrations/` exists but `.sqlx/` doesn't, or the reverse).
  2. **Agents/skills with hard SQLx assumptions** — sweep `kit/agents/*.md` and `kit/skills/*/SKILL.md` for misleading advice (e.g. backend reviewer expecting SQLx idioms, test-writer-backend defaulting to SQLx integration tests, contract skill assuming a DB boundary, dep-audit assuming sqlx in Cargo.toml). For each, decide: gate behind detection, or add an "if your project uses a DB" caveat.
  3. **Dead surface for no-DB projects** — what ships as pure noise? `just prepare-sqlx` recipe in `kit/common.just`, SQLx-specific reviewer rules, SQLx-flavored test-writer templates. Decide per item: ship-and-skip-when-irrelevant, gate at sync time, or split into a separate opt-in module.

  **`--strict` toggle** — `check.py` currently treats absent stack as `SKIPPED` (correct for `--fast` / pre-commit). In strict mode (used by `release.py`), absent stack should arguably FAIL: releases shouldn't ship without exercising the full quality gate. But a deliberately no-DB Tauri project should still be releasable. Decide the policy:
  - Option A: `--strict` requires all markers — simple but excludes legitimate no-DB releases.
  - Option B: `--strict` distinguishes core stack (`package.json` + `Cargo.toml` required) from optional stack (`.sqlx/` optional). Allows no-DB releases while still gating "you forgot to scaffold React".
  - Option C: project-level config flag declares which markers are expected. Most flexible, more moving parts.

  v4.5 already left a `TODO(v4.6)` marker in `kit/scripts/check.py` at the stack-markers block. The audit decision lands the policy; implementation is downstream of the decision.

  Categorisation per fix item: graceful-skip / doc-gate / sync-time-exclude / accept-as-noise / strict-required.

## Experimental
