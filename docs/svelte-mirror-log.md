# Svelte Mirror Log

Audit trail for `/svelte-update` decisions on every cherry-pick from `main` into `svelte-main`. Each entry records: what was mirrored, what was skipped (with reason), and what was flagged for custom treatment.

This file lives on `svelte-main` only — never cherry-picked back to `main`.

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

## Architectural note — when to fork vs share

A new agent or doc should get a `-svelte` fork **only** when its substance is framework-specific (idioms, syntax, helper code). `reviewer-e2e` reviews WebDriver scenarios at the test-code level (selectors, async correctness, no-mock discipline) — these are framework-agnostic, so no fork.

When a forked file's `main` side changes and the change is purely structural / framework-neutral, the mirror is verbatim. When it carries framework-specific code (React hooks, `{@html}`, `setReactInputValue`), the mirror needs targeted substitution. The skill makes this decision visible per commit; this log records the result.
