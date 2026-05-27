# Svelte Mirror Log

Audit trail for `/svelte-update` decisions on every cherry-pick from `main` into `svelte-main`. Each entry records: what was mirrored, what was skipped (with reason), and what was flagged for custom treatment.

This file lives on `svelte-main` only — never cherry-picked back to `main`.

---

## svelte-v0.9.0+4.14.0 → svelte-v0.10.0+4.15.0

Baseline: `+4.14.0`. New baseline: `+4.15.0`. v4.15 substance is **kit hardening + reviewer hygiene** — gh#68 (markdown drift detection in `--fast`), `check.py` `--strict` toggle for release-time enforcement (sqlx conditional on `migrations/`), helper extract (`_frontend_npm_check_step`), partial-stack `npm` guards in `common.just`, gh#67 partial (Prong 2 humility rule across 5 reviewers), TODO trim. Cherry-picked `76ca394..c0de943` (6 commits, dropped `chore: release v4.15.0` per usual).

### Mirrored to `-svelte` variants

- `kit/agents/reviewer-frontend-svelte.md` — applied humility rule (gh#67) verbatim. Framework-neutral wording (about version/idiom/tool claims, not framework-specific). Added as Critical Rule #9 after Scope-drift guard, matching the React fork's placement.
- `kit/agents/reviewer-security-svelte.md` — same humility rule, added as Critical Rule #11 after Scope-drift guard. Identical wording across both -svelte forks (and the 5 React reviewers on `main`).

### Shared (cherry-pick applies as-is)

- `kit/agents/reviewer-arch.md`, `kit/agents/reviewer-backend.md`, `kit/agents/reviewer-infra.md` — humility rule cherry-picked into React canonicals; no Svelte fork exists for these so they ARE the svelte-main version.
- `kit/scripts/check.py` — md drift + helper extract + `--strict` + `expected_when`. Auto-merged cleanly with the existing svelte divergence (`"React Tests"` → `"Frontend Tests"` rename preserved by git's 3-way merge).
- `kit/scripts/release.py` — `strict_mode=True` wiring on the `QualityChecker` call; framework-neutral.
- `kit/common.just` — `npm run format:fix` / `format:docs` guards on `package.json` presence; framework-neutral.
- `scripts/check.py` — kit-local; promoted prettier markdown check from full-only to also run in `--fast` mode.
- `docs/TODO.md` — partial-stack entry trim; framework-neutral.

### Skipped (React-specific)

None this cycle.

### Custom

None this cycle.

---

## svelte-v0.8.0+4.13.0 → svelte-v0.9.0+4.14.0

Baseline: `+4.13.0`. New baseline: `+4.14.0`. v4.14 substance is **FE rules + workflow polish** — gh#62 (TaskCreate now Step 5 in `/start`), gh#63 (F28 Store kinds: BE/FE shared cache → `infra/cache/`, FE-persisted settings → `infra/settings/`), gh#64 (reviewer-frontend F26 cross-feature store detector). Also a new deterministic `check.py` lint preventing future gh#62-class drift. Cherry-picked `c441e86..700a71a` (4 commits, dropped the `chore: release v4.14.0` commit on the usual conflict).

### Mirrored to `-svelte` variants

- `kit/docs/frontend-rules-svelte.md` — applied F28 Store kinds + F26 promotion target + infra/ exclusion tightening + F0 tree update with Svelte filenames. Translations: `Zustand singleton` → `Svelte store singleton (writable / Svelte 5 runes)`; `useCacheStore.ts` → `cacheStore.svelte.ts`; `useSettingsStore.ts` → `settingsStore.svelte.ts`. Architectural concept (3 store kinds, 3 homes, cross-feature reads via gateway) is framework-neutral and applies identically.
- `kit/agents/reviewer-frontend-svelte.md` — applied F26 promotion-target update + F28 widget-local wording verbatim. Translated the F26 cross-feature store-import detector: React's `useXStore` symbol-shape regex doesn't apply to Svelte (no naming convention), so switched to a path-based detector — `grep -rE 'import\s+\{[^}]*\}\s+from\s+"@/features/[^/"]+/store(\.svelte)?"'`. Same path-scope rule and remediation message.

### Shared (cherry-pick applies as-is)

- `kit/skills/start/SKILL.md` — TaskCreate Step 5 + imperative blockquotes; framework-neutral workflow.
- `scripts/check.py` — new `_check_skills_with_checklists_seed_tasks` lint; kit-only (not synced).
- React canonicals (`kit/agents/reviewer-frontend.md`, `kit/docs/frontend-rules.md`) — cherry-pick lands their React-form updates; the Svelte forks above carry the Svelte-form mirror.

### Skipped (React-specific)

- _None._ Every v4.14 concept transfers; only wording needed translation.

### Custom (manual treatment)

- _None._

---

## svelte-v0.7.0+4.12.0 → svelte-v0.8.0+4.13.0

Baseline: `+4.12.0`. New baseline: `+4.13.0`. v4.13 substance is **kit reliability**: `sync-config.sh` flag-parsing rework (`-y`/`-h`, fail-loud on unknown), `whats-next.py` per-stream `kit_update` detection (closes gh#59 — the false `behind: true` on Svelte projects this branch is most affected by), stale-bootstrap detector + recovery recipe, and a release/merge/sync script hardening pass. All 5 commits are framework-neutral; cherry-pick `821ff3d..620cb27` applies as-is.

### Mirrored to `-svelte` variants

- _None._ No agent or doc with a `-svelte` fork was touched on main during the cycle. The 4 forked agents (`reviewer-frontend-svelte`, `reviewer-security-svelte`, `test-writer-e2e-svelte`, `test-writer-frontend-svelte`) and 4 forked docs (`e2e-rules-svelte`, `frontend-rules-svelte`, `frontend-visual-proof-svelte`, `test_convention-svelte`) all stay unchanged.

### Shared (cherry-pick applies as-is)

- Agent wording: `kit/agents/{reviewer-e2e,reviewer-infra,spec-reviewer}.md` — framework-neutral wording polish (Rule 8 X-for-Y example; Step 7 defers to `## Scope`; Category C transport-vocab swap + Category G CR6 duplicate trim).
- Scripts: `kit/scripts/{merge.py,release.py,sync.sh,validate-sync.sh}` — release/merge/sync hardening pass (CLI validation, recovery messages, atomic-rename manifest + kit-version.md, python3 preflight).
- Bootstrap: `kit/sync-config.sh` — `-y`/`-h` flag rework + unknown-flag fail-loud.
- Discovery: `kit/kit-readme.md`, `kit/skills/kit-discover/SKILL.md`, `kit/skills/whats-next/SKILL.md` — stale-bootstrap recovery recipe + recipe pointer; whats-next skill body documents per-stream cache.
- Local mirrors: `scripts/validate-sync.sh`, `scripts/whats-next.py` — auto-applied by cherry-pick.

### Spot-check after cherry-pick

- `kit/scripts/whats-next.py` and `scripts/whats-next.py`: divergent only at `SOURCE_EXTS` (svelte-main adds `".svelte"`). v4.13's gh#59 fix replaces `_kit_tag_cache_file()` + `_latest_kit_tag()` (identical in both lineages pre-v4.13), so cherry-pick should leave the `.svelte` extension intact. Confirm before tagging.

### Skipped (React-specific)

- _None._ Every v4.13 change is framework-neutral.

### Custom (manual treatment)

- _None._

---

## svelte-v0.6.1+4.11.1 → svelte-v0.7.0+4.12.0

Baseline: `+4.11.1`. New baseline: `+4.12.0`. Cherry-picked all 5 v4.12 commits individually (`e215dc8..a28e5ab`). One merge conflict resolved on `kit/kit-tools.md` Scripts table — svelte-main has the `list-fe-test-targets.py` row (Svelte-specific helper) absent on main; main added a `plan-context.py` row. Resolution: keep both, wider column padding from svelte-main. v4.12 substance is the new `/feature-planner` skill (agent→skill migration + helper script) and Workflow A/B tightening — framework-neutral.

### Mirrored to `-svelte` variants

- `kit/agents/reviewer-security-svelte.md` — dropped the Workflow B compatible footer to match main's drop in `bea07fc` (v4.12 docs B commit). Framework-neutral footer; the v4.11.1 cycle had added it, now removed everywhere.
- `kit/agents/test-writer-frontend-svelte.md` — `feature-planner` → `/feature-planner` reference update (one line at the `modified_functions` paragraph). Mirrors main's same change from the agent→skill migration.

### Skipped (no fork — change flows through cherry-pick as-is)

- `kit/agents/{adr-reviewer,contract-reviewer,plan-reviewer,reviewer-arch,reviewer-infra,reviewer-sql,spec-reviewer}.md` — no svelte fork; cherry-pick applied directly. All carry `feature-planner` → `/feature-planner` reference updates from the migration.
- `kit/skills/{contract,spec-writer,start}/SKILL.md` — no svelte fork; cherry-pick applied. `start/SKILL.md` carries the full Workflow A/B tightening (parallel reviewer batches, per-layer reviewer placement, format-late, spec-checker HARD GATE, closure collapse, Phase 1 reviewer parallelization).
- `kit/kit-readme.md`, `kit/kit-tools.md` — discovery docs; applied as-is (kit-tools conflict resolved per above).
- `kit/scripts/plan-context.py` (NEW) — framework-neutral deterministic data collector; downstream-only (not mirrored to .claude/). Works on any spec regardless of frontend framework.
- `kit/skills/feature-planner/SKILL.md` (NEW) — framework-neutral skill body; references generic spec/contract/ADR/conventions. No React idiom.
- `kit/agents/feature-planner.md` (DELETED) — old agent file removed by the migration; no svelte fork to deal with.
- `scripts/check.py` — kit-internal tooling; never synced downstream.
- `.claude/skills/preflight/SKILL.md`, `docs/TODO.md` — kit-local files; not part of the release artifact set.

### Custom (flagged for manual treatment)

(None this cycle — all forks accepted the same wording as their React counterparts since the v4.12 changes are framework-neutral discipline / authoring infrastructure.)

---

## svelte-v0.6.0+4.11.0 → svelte-v0.6.1+4.11.1

Baseline: `+4.11.0`. New baseline: `+4.11.1`. Cherry-picked all 3 v4.11.1 commits individually (`cfa68f1..311362e`) — clean apply on all; `kit/kit-readme.md` and `kit/scripts/whats-next.py` auto-merged against pre-existing svelte-main divergences without conflict.

### Mirrored to `-svelte` variants

- `kit/agents/reviewer-frontend-svelte.md` Step 1 → `bash scripts/branch-files.sh --frontend` (same filter name as React lineage; underlying regex is Svelte-flavored on svelte-main per `branch-files.sh` divergence).
- `kit/agents/reviewer-security-svelte.md` Step 1 → `bash scripts/branch-files.sh --security` (same shape).

### Divergence introduced

- `kit/scripts/branch-files.sh` — `--frontend`/`--arch`/`--security` regex on svelte-main replaces `tsx` with `svelte` (3 single-line diffs). Lets the Svelte `-svelte` reviewers use the same filter names as React reviewers post-sync (the `-svelte` suffix is stripped during sync, so downstream Svelte projects see one `reviewer-frontend` calling `--frontend` against a Svelte-aware script). Adds branch-files.sh to the previously-3 diverging scripts; total now 4.

### Skipped (no fork — change flows through cherry-pick as-is)

- `kit/agents/{reviewer-arch,reviewer-backend,reviewer-e2e,reviewer-sql}.md` @ cfa68f1 — no svelte fork; cherry-pick applied directly. Their `--rust`/`--arch`/`--e2e`/`--migrations` filter calls work without per-lineage adaptation because their regexes either match the same files (`--rust`, `--migrations`) or the `--arch` regex is itself Svelte-aware on svelte-main.
- `kit/kit-readme.md` @ e9e592e — Write(.review/\*\*) allowlist suggestion is framework-neutral.
- `kit/scripts/whats-next.py` @ 311362e — `_latest_kit_tag` endpoint swap auto-merged against the pre-existing `.svelte` SOURCE_EXTS divergence (disjoint regions).

### Custom (flagged for manual treatment)

(None this cycle — all forks accepted the same filter-name swap as their React counterparts since branch-files.sh on svelte-main makes the regex Svelte-aware.)

---

## svelte-v0.5.0+4.10.0 → svelte-v0.6.0+4.11.0

Baseline: `+4.10.0`. New baseline: `+4.11.0`. Cherry-picked all 8 v4.11 substance commits individually (`6019c63..060c973`) — clean apply on all, no conflicts. v4.11's centerpiece is the new `/review-triage` skill + `.review/` persistence layer; framework-neutral discipline (sub-agent → main-agent boundary exists identically in Svelte projects).

### Mirrored to `-svelte` variants

- `kit/agents/reviewer-frontend-svelte.md` — mirrored Save report section + Write tool grant + reframed Critical Rule 1, identical wording to React counterpart (commits 51cb6a0 + 060c973). The Save protocol bridges the sub-agent boundary; framework-agnostic.
- `kit/agents/reviewer-security-svelte.md` — same pattern as reviewer-frontend-svelte. Same rationale.
- `kit/agents/test-writer-frontend-svelte.md` — mirrored Critical Rule 12 (abstraction discipline) + new halt template "test requires unplanned abstraction" (commit 6019c63). The failure mode (inventing dead-code helpers) applies identically to Svelte test-writers; the case-study example `presentAssetCrudError` would just become `presentUserError.svelte.ts` on this side.

### Skipped (no fork — change flows through cherry-pick as-is)

- `kit/agents/{reviewer-arch,reviewer-backend,reviewer-e2e,reviewer-infra,reviewer-sql,feature-planner,test-writer-backend}.md` — no svelte fork; cherry-pick applied directly.
- `kit/scripts/review-path.sh`, `kit/scripts/list-fresh-reviews.sh` — new helpers; framework-neutral; applied as-is.
- `kit/skills/review-triage/SKILL.md` (new) + `kit/skills/start/SKILL.md` — new skill body and template tweaks are framework-neutral.
- `kit/kit-readme.md`, `kit/kit-tools.md` — discovery docs; applied as-is.
- `.claude/agents/{ai,doc,script}-reviewer.md` + `.claude/skills/review-triage/SKILL.md` + `scripts/{review-path,list-fresh-reviews}.sh` + `scripts/mirror-local.sh` + `.gitignore` — kit-internal mirror; framework-neutral.

### Custom (flagged for manual treatment)

(None this cycle — all forks accepted the same wording as their React counterparts since the v4.11 additions are pure discipline / persistence infrastructure with no framework idiom in the wording.)

---

## svelte-v0.4.0+4.9.0 → svelte-v0.5.0+4.10.0

Baseline: `+4.9.0`. New baseline: `+4.10.0`. Cherry-picked all 7 v4.10 substance commits individually (`aa65dca..4e281ab`) — first cycle under the new rebase-merge convention, so main now ships each fix/feat as its own commit instead of a single squash; per-commit granularity carries to the svelte lineage too.

### Auto-merged during cherry-pick (no manual resolution)

- `kit/scripts/whats-next.py` @ c892df1 + 082e1bd — svelte-main has a pre-existing divergent version (per the v4.6.0 framework-aware convergence); the v4.10 additions (`collect_kit_update()`, plain-bullet TODO regex) auto-merged cleanly because they touched disjoint regions.
- `kit/scripts/check.py` @ 8f201f9 — same story; the `_pad_visible` / `_WIDE_CHARS` additions sit at module top, away from svelte-main's divergent metric-label section.

### Mirrored to `-svelte` variant

- `kit/docs/frontend-rules.md` @ 083736d — gh#46 F0 split mirrored to `frontend-rules-svelte.md`. `App.svelte` + `Router.svelte` moved out of `shell/` to `src/` root; `shell/` reduced to layout chrome only (`AppShell.svelte`); F28 `shell/` REJECTS list rewritten to match. Also took the opportunity to fix a pre-existing F23 wiring-points reference that named `router.ts` instead of `Router.svelte` — drift wasn't introduced by this commit, but the F0 mirror made it actively contradictory, so closed the loop in the same commit (caught by doc-reviewer).

### Skipped (no fork — change flows through cherry-pick as-is)

- `kit/docs/error-model.md`, `kit/docs/ddd-reference.md`, `kit/docs/backend-rules.md` @ aa65dca — gh#45 fix is backend/Rust + Specta-derived FE bindings. Framework-neutral; no -svelte fork.
- `kit/agents/reviewer-backend.md` @ aa65dca — error-handling lane wording update. Backend-only.
- `kit/skills/whats-next/SKILL.md` @ 3438e59 + c892df1 — Recap + kit-update sections added to a shared skill. No fork.
- `kit/scripts/whats-next.py` + `kit/scripts/check.py` — see "Auto-merged" above.
- `docs/TODO.md` @ 4e281ab — kit-internal TODO restructure (flattening `## v4.X candidates` sections). Cherry-picked cleanly into svelte-main's own TODO file; the version-tag drop applies to either lineage.

### Custom (flagged for manual treatment)

(None this cycle — the F23 stale-router fix that doc-reviewer caught was folded into the F0 mirror commit rather than deferred, since it's a 1-line change made actively contradictory by F0.)

---

## svelte-v0.1.1+4.5.2 → svelte-v0.2.0+4.7.2

Baseline: `+4.5.2`. New baseline: `+4.7.2`. Cherry-picked 9 substance commits (release commits skipped — svelte-main owns its own release lineage).

### Mirrored to `-svelte` variant

- `kit/agents/reviewer-frontend.md` @ c1b12e3 — reviewer-e2e lane split applied verbatim to `reviewer-frontend-svelte.md`. Scope tightened to `src/`, E-rules / `e2e/` references moved to `reviewer-e2e`'s lane. Framework-neutral; no Svelte-specific substitutions needed beyond what was already there.
- `kit/agents/reviewer-security.md` @ f016b07 — v4.7 template alignment (When-to-use / Process steps / Critical Rules / Notes / false-positive list / cross-layer findings) applied to `reviewer-security-svelte.md`. All structural changes mirrored; XSS examples kept Svelte-specific (`{@html}` instead of `dangerouslySetInnerHTML`); `.tsx` swapped for `.svelte` throughout; output-format examples updated to use `$state` instead of `React state`. Added `{@html sanitizedMarkdown}` to false-positive list as the Svelte equivalent of "documented-sanitizer-in-scope".
- `kit/agents/test-writer-e2e.md` @ c6ce3f1 — scenario-writer pivot (pick critical-path commands / write scenarios / halt for missing helpers / sibling-pattern sections) applied to `test-writer-e2e-svelte.md`. The `setReactInputValue()` helper and its references dropped throughout (Svelte 5 `bind:value` + `$state` synchronous DOM update means native `setValue()` works); template uses `await (await $("#id")).setValue(value)` directly. Added Notes section explaining why no React-style input workaround is needed.

### Skipped (React-specific, no Svelte mirror needed)

(None — all React-side changes on forked files this cycle had framework-neutral structure or were translatable.)

### Custom (flagged for manual treatment)

- `kit/scripts/check.py` — internal metric key `react_tests` is inconsistent with the user-facing label `"Frontend Tests"` (svelte-main's framework-neutral wording, in place since the v4.6.0 a517098 convergence). Rename `react_tests` → `frontend_tests` across all 5 sites (lines 84, 284, 297, 357, 363) on svelte-main only. Cosmetic — does not affect functionality. Defer to a svelte-only follow-up branch; not part of this migration PR.

### Shared (no `-svelte` variant — cherry-pick applied as-is)

23 files: kit-tools, kit-readme, scripts, hooks, common.just, skills (create-pr / start), CI workflow, plus the new `kit/agents/reviewer-e2e.md` (framework-agnostic WebDriver scenario reviewer — no fork needed).

---

## svelte-v0.2.0+4.7.2 → svelte-v0.2.1+4.7.3

Baseline: `+4.7.2`. New baseline: `+4.7.3`. Cherry-picked the single substance commit from main (`d337eb5`, PR #38) — closes GH #37.

### Mirrored to `-svelte` variant

- `kit/agents/reviewer-frontend.md` @ d337eb5 — Step 3 compound-shell wrapper applied verbatim to `reviewer-frontend-svelte.md`. Framework-neutral.
- `kit/agents/reviewer-security.md` @ d337eb5 — Step 3 compound-shell wrapper applied verbatim to `reviewer-security-svelte.md`. Framework-neutral.

### Skipped (React-specific, no Svelte mirror needed)

(None — the entire #37 fix is framework-neutral plumbing.)

### Custom (flagged for manual treatment)

(None this cycle.)

### Shared (no `-svelte` variant — cherry-pick applied as-is)

Everything else: `branch.sh` (new), `branch-files.sh` (sources `branch.sh base`), `scripts/check.py` lint rule, the 7 main-side reviewer patches, `test-writer-backend.md`, `create-pr/SKILL.md`, `kit-tools.md`, `kit-readme.md`, `docs/TODO.md`.

---

## svelte-v0.2.0+4.7.3 → svelte-v0.2.1+4.7.4

Baseline: `+4.7.3`. New baseline: `+4.7.4`. Cherry-picked one main commit (`0f3a0a2`, PR #40) — convention-doc compound-shell follow-up to #37.

### Mirrored to `-svelte` variant

- `kit/docs/test_convention.md` @ 0f3a0a2 — one-line example `cd src-tauri && cargo test` → `cargo test --manifest-path src-tauri/Cargo.toml`. Mirrored verbatim to `test_convention-svelte.md`. Framework-neutral.

### Skipped (React-specific, no Svelte mirror needed)

(None.)

### Custom (flagged for manual treatment)

(None.)

### Shared (no `-svelte` variant — cherry-pick applied as-is)

`kit/docs/test_convention.md` (React-side; coexists with the Svelte fork in this branch).

---

## svelte-v0.3.0+4.8.0 → svelte-v0.4.0+4.9.0

Baseline: `+4.8.0`. New baseline: `+4.9.0`. Cherry-picked the single squash commit `bd45f68` (PR #43) — v4.9 docs alignment.

### Conflicts resolved during cherry-pick

(None — clean cherry-pick.)

### Mirrored to `-svelte` variant

- `kit/docs/frontend-rules.md` @ bd45f68 — full F0 introduction + F28 restructure mirrored to `frontend-rules-svelte.md`: F0 tree adapted to Svelte (`.svelte` components, `.svelte.ts` reactive modules, `snackbarStore.svelte.ts`, `ui/modules/` instead of `ui/hooks/`, `Router.svelte`, `main.ts` Svelte 5 entry, `infra/i18n/`). F1 trimmed to one-sentence cite of F0. F24↔E4 reverse cross-link + F18→visual-proof reference added. Banner dropped.
- `kit/docs/e2e-rules.md` @ bd45f68 — banner dropped, `docs/` prefix removed from peer-file refs, E4↔F24 reverse cross-link added to `e2e-rules-svelte.md`. Verbatim mirror.
- `kit/docs/test_convention.md` @ bd45f68 — snackbar mock path moved from `@/infra/snackbar` to `@/ui/components/snackbar/snackbarStore.svelte` (matching the Svelte F0 widget colocation). Tier 4 row + body section added pointing at `e2e-rules-svelte.md` (B36 ephemeral DB).
- `kit/docs/frontend-visual-proof.md` @ bd45f68 — banner dropped (replaced with F18 reverse-link callout), config defaults + example imports updated to F0 paths (`src/styles/index.css`, `src/infra/i18n/index.ts`, `import { setupI18n } from "../infra/i18n"`).
- `kit/agents/reviewer-frontend.md` @ bd45f68 — single F28→F0 citation fix mirrored to `reviewer-frontend-svelte.md` ("F0 layout uses `src/ui/modules/`" — the Svelte path).
- `kit/agents/test-writer-frontend.md` @ bd45f68 — 4 F28→F0 citations mirrored to `test-writer-frontend-svelte.md` (read-list gloss, "anywhere in src/" placement, vitest target prose, colocation rule).

### Skipped (no fork — change flows through cherry-pick as-is)

- `kit/docs/backend-rules.md`, `kit/docs/ddd-reference.md`, `kit/docs/error-model.md`, `kit/docs/i18n-rules.md` — backend/neutral layering and convention. No fork.
- `kit/skills/visual-proof/SKILL.md` — i18n glob + config defaults updated to F0 paths. Skill body is framework-neutral (works for both React and Svelte projects via the per-project config).
- `scripts/branch.sh` (NEW), `scripts/mirror-local.sh` — kit-internal infra. Shared.
- `.claude/agents/doc-reviewer.md` — new Category F (40-char table cell). Kit-internal reviewer. Shared.

### Custom (flagged for manual treatment)

(None this cycle — all mirrors clean.)

---

## svelte-v0.2.1+4.7.4 → svelte-v0.3.0+4.8.0

Baseline: `+4.7.4`. New baseline: `+4.8.0`. Cherry-picked the single squash commit `c3a695d` (PR #42) — closes GH #15, #22, #23, #25, #27, #28, #29, #32, #35, #41.

### Conflicts resolved during cherry-pick

- `kit/kit-readme.md` — kept Svelte "frontend-rules" wording from svelte-main; added the new `error-model.md` row from main. Convention-doc count is now 8 (matches main).
- `kit/scripts/check.py` — kept svelte-main's `"Frontend Tests"` label (framework-neutral, per a517098 convergence); genericized the gh#27 comment from "scaffolded React stack" to "scaffolded frontend stack"; applied main's `SKIP_FRONTEND_ABSENT` constant and `--passWithNoTests` flag.

### Mirrored to `-svelte` variant

- `kit/agents/reviewer-frontend.md` @ c3a695d — added the v4.8-new `## Scope` section (diff-scoped default + opt-in `release-sweep` literal trigger) and Critical Rule 8 (Scope-drift guard with cap-overflow guidance) to `reviewer-frontend-svelte.md`. Framework-neutral — the neighbour examples ("presenter for a component change, the hook for a gateway change") apply equally to Svelte (`.svelte` presentational + `.svelte.ts` modules). Verbatim mirror.
- `kit/agents/reviewer-security.md` @ c3a695d — added the v4.8-new `## Scope` section, the `## When to use` "Skip for" clause (return-type / rename / helper-split refactors with no security delta), the `## Cross-layer findings` intro paragraph (default-mode-vs-release-sweep), and Critical Rule 10 (Scope-drift guard with cap-overflow guidance) to `reviewer-security-svelte.md`. All framework-neutral. Verbatim mirror.

### Skipped (no fork — change flows through cherry-pick as-is)

- `kit/docs/error-model.md` (NEW) — backend-only contract (Rust types + Tauri command boundary). FE handling section narrows on `code` discriminator via Specta-derived bindings; no framework-specific idiom. No `-svelte` fork needed; ships verbatim.
- `kit/docs/backend-rules.md`, `kit/docs/ddd-reference.md` — backend layering / error-model framing. Framework-neutral; no fork.
- `kit/agents/reviewer-backend.md`, `kit/agents/reviewer-arch.md`, `kit/agents/reviewer-infra.md`, `kit/agents/reviewer-sql.md`, `kit/agents/reviewer-e2e.md`, `kit/agents/spec-reviewer.md` — no `-svelte` fork; cherry-pick applies as-is.
- `kit/skills/spec-writer/SKILL.md` — gh#41 Rule 7 expansion. Spec writing is framework-neutral (UL + behavior); no fork.
- All other touched files (kit-tools, kit-readme handled in conflicts, common.just, scripts, hooks, top-level `docs/TODO.md`, `CLAUDE.md`, `scripts/branch-files.sh`, `scripts/mirror-local.sh`) — shared.

### Custom (flagged for manual treatment)

(None this cycle — both fork-bearing agents had clean verbatim mirrors.)

---

## Architectural note — when to fork vs share

A new agent or doc should get a `-svelte` fork **only** when its substance is framework-specific (idioms, syntax, helper code). `reviewer-e2e` reviews WebDriver scenarios at the test-code level (selectors, async correctness, no-mock discipline) — these are framework-agnostic, so no fork.

When a forked file's `main` side changes and the change is purely structural / framework-neutral, the mirror is verbatim. When it carries framework-specific code (React hooks, `{@html}`, `setReactInputValue`), the mirror needs targeted substitution. The skill makes this decision visible per commit; this log records the result.
