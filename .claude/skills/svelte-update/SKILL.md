---
name: svelte-update
description: Reviews main→svelte-main cherry-pick drift and surfaces mirror decisions for forked `*-svelte.md` files. For each main commit since the last svelte tag, classifies the touched files as shared (auto-applied), mirror-needed (the -svelte variant should be updated to match), or skip (React-specific change with no Svelte equivalent). Kit-internal — used by the kit maintainer during the React→Svelte transition. Use after cherry-picking from main, or before tagging the next `svelte-vX.Y.Z+M.N.P`.
tools: Read, Grep, Glob, Bash
---

# Skill — `svelte-update`

Tracks the contract between the React lineage on `main` and the Svelte fork files on `svelte-main`. When `main` evolves, its rule files, agents, and docs may need to be mirrored into their `*-svelte.md` counterparts — but not always. This skill enumerates the candidates and lets the maintainer decide per file.

> **Branch model recap.** `svelte-main` cherry-picks from `main`. Files without a `-svelte` variant flow through unchanged. Files with a `-svelte` variant (e.g. `frontend-rules.md` ↔ `frontend-rules-svelte.md`) require a per-commit decision: is the change framework-neutral (mirror), React-specific (skip), or partially relevant (custom)?

---

## Execution Steps

### 1. Determine the baseline

Find the last `svelte-vX.Y.Z+M.N.P` tag — its `+M.N.P` suffix names the `main` version it tracked:

```bash
git describe --tags --match 'svelte-v*' --abbrev=0
```

Extract the `+M.N.P` portion. If no svelte tag exists yet, fall back to the kit's last regular tag (the first svelte release will track everything since then).

If the user passed a baseline explicitly (`/svelte-update v4.5.1` or `/svelte-update svelte-v0.2.0+4.6.0`), use that instead.

### 2. List main-side changes since baseline

```bash
git diff --name-only v{M.N.P}..main -- kit/ scripts/ CLAUDE.md README.md
```

Filter to the surfaces this skill cares about:

- `kit/agents/*.md` — agent definitions
- `kit/docs/*.md` — convention docs
- `kit/skills/**/SKILL.md` — skill bodies
- `kit/kit-tools.md`, `kit/kit-readme.md` — discovery
- Anything else (scripts, hooks, common.just) — shared by default

### 3. Classify each changed file

For each path:

- **A. Shared (no `-svelte` variant exists)** — the cherry-pick will apply it as-is. No mirror decision needed. Note for the maintainer to spot-check the result.
- **B. Forked (`{name}-svelte.md` exists in `kit/agents/` or `kit/docs/`)** — needs a mirror decision (see Step 4).
- **C. New file** — does it need a Svelte variant? Ask the user.

### 4. For each Forked file, surface the diff

Show:

```
{path} (main change since v{M.N.P})

@@ Main diff @@
{git diff v{M.N.P}..main -- {path}}

@@ Current Svelte variant @@
{first 30 lines of the -svelte.md file, or the section impacted by the diff}
```

Ask the user one of:

- **Mirror** — apply an equivalent change to `{name}-svelte.md`. The skill proposes an edit; user accepts/edits.
- **Skip** — the change is React-specific (e.g. tightened `useMemo` rule wording). No Svelte mirror needed. Record rationale.
- **Custom** — flag for manual treatment later; do not auto-edit.

### 5. Log decisions

Append to `docs/svelte-mirror-log.md` (create if absent) under a header for the current sync:

```markdown
## svelte-v{NEXT}+{BASELINE} → svelte-v{NEXT}+{NEW_BASELINE}

- `{path}` @ {commit-sha} — {mirrored|skipped: {reason}|custom: pending}
```

The log is kit-local discipline — it lives on `svelte-main` only, never cherry-picked to `main`.

### 6. Final report

```
## svelte-update — baseline v{M.N.P} → main HEAD

Files touched on main: N
- N_shared shared (cherry-pick applies as-is — spot-check recommended on: …)
- N_mirrored mirrored to -svelte variant
- N_skipped React-specific (rationale logged)
- N_custom flagged for manual treatment

Pending custom items:
- {path} — {reason}

Next: cherry-pick the main commits (`git cherry-pick {baseline}..main`) and tag `svelte-v{NEXT}+{NEW_BASELINE}`.
```

---

## Critical Rules

1. **Read-only on `main`** — never modify `main` from this skill. All edits target files on `svelte-main`.
2. **One decision per file** — do not batch multiple main commits into one diff if they touched the same file separately; the maintainer needs each change in context.
3. **Trust the user's judgment** — propose a recommendation but never apply edits without explicit confirmation. The diff inspection is the load-bearing step.
4. **Never auto-mirror** — even when a change looks "obviously framework-neutral", surface it as a recommendation. Hidden coupling between rule wording and framework idioms is the failure mode this skill exists to prevent.
5. **Log every skip with a reason** — `docs/svelte-mirror-log.md` is the audit trail for "why didn't we mirror this?"; an unrecorded skip becomes invisible technical debt.

---

## Notes

This skill is the **discipline layer** for B2 (long-lived `svelte-main` branch) architecture. Without it, cherry-pick conflicts are absorbed silently and mirror gaps accumulate. With it, every main commit gets an explicit decision on the Svelte side: mirror, skip, or custom.

The skill is intentionally judgment-heavy. v0.1 surfaces diffs and records decisions; it does not auto-generate Svelte translations. AI-assisted mirror proposals are a v0.2 candidate once the maintainer has observed enough cycles to know which transformations are safe to automate.

If `svelte-main` is eventually merged back into `main` (Svelte becomes the kit's sole frontend target), this skill is deleted along with the `*-svelte.md` files — its purpose is bound to the transition period.
