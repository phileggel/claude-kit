# Svelte port — pending candidates

Iso-functional port React 19 → Svelte 5 (vanilla + Vite, not SvelteKit). Detailed plan in `/home/phil/.claude/plans/ne-touche-pas-au-witty-sundae.md` (scenario B2: long-lived `svelte-main` branch, fork architecture with `*-svelte.md` suffix files synced via framework-aware strip-suffix logic).

This file lives only on `svelte-main` and its feature branches. It must never be cherry-picked onto `main` (the React lineage).

## svelte-v0.1 candidates — agent and rule forks

- **`kit/docs/frontend-rules-svelte.md`** — fork `kit/docs/frontend-rules.md`. Translate F1, F2, F6–F10, F15, F19, F20, F25 (partially) to Svelte 5 idioms. F19 marked DEPRECATED with pointer. F28 layout uses `ui/modules/` for `.svelte.ts` reactive modules.

- **`kit/docs/test_convention-svelte.md`** — fork `kit/docs/test_convention.md`. Backend section duplicated as-is; frontend section rewritten for Vitest + `@testing-library/svelte` + `flushSync()` patterns, no `renderHook` equivalent.

- **`kit/docs/frontend-visual-proof-svelte.md`** — fork `kit/docs/frontend-visual-proof.md`. Bootstrap via `mount()` from `svelte`. `Preview.svelte` wrapper component. Modal panel example uses `<script lang="ts">` + `$props()` + `{@render children()}`.

- **`kit/agents/reviewer-security-svelte.md`** — fork `kit/agents/reviewer-security.md`. Scan `.svelte` files instead of `.tsx`. Frontend security advice adapted to Svelte's auto-escaping (`{expr}` HTML-escaped, `{@html ...}` is the danger surface).

## svelte-v0.1 candidates — branch-side polish (not forks)

- **Top-level docs on svelte-main** — `CLAUDE.md`, `README.md`, `kit/kit-readme.md`, `kit/kit-tools.md` declare Svelte target (these describe the branch itself, no fork needed).

- **Scripts (additive on svelte-main)** — `kit/scripts/whats-next.py:47` add `.svelte` to `SOURCE_EXTS`; `kit/scripts/check.py:133` label "Frontend Tests" (additive, lossless for React).

## svelte-v0.1 infrastructure (Phase 3.5)

- **`scripts/sync-config.sh`** — framework-aware strip-suffix logic. Reads `.claude/kit.config.json` `"framework": "svelte"` flag. On Svelte sync: prefers `*-svelte.md` over base, strips suffix from filename and `name:` frontmatter.

- **`kit/skills/svelte-update/SKILL.md`** (kit-internal) — orchestrates cherry-pick mirror decisions. Per-commit classification: shared (no action), mirror to `-svelte`, skip with rationale, custom-adapt.
