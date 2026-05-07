---
name: techdebt
description: Produces a normalized tech-debt entry in chat — date-stamped, with auto-filled git context (branch + short commit). The entry is text-only output; the main agent decides whether to append it to `docs/techdebt.md` (the convention), file a GitHub issue, or surface it elsewhere per the downstream CLAUDE.md's policy. Use when a reviewer surfaces a `[DECISION]` critical or pre-existing tech-debt observation worth recording, or when the main agent notices a non-actionable smell during work.
tools: Bash
---

# Skill — `techdebt`

Produces a normalized tech-debt entry. Output-only — the skill never writes to disk.

The kit owns the **format**; the main agent (governed by the downstream `CLAUDE.md`) owns the **destination**. Convention: append to `docs/techdebt.md`, sibling to `docs/todo.md`. Format consistency across projects is the value the skill provides; `whats-next` reads from the conventional location.

---

## Required tools

`Bash` — for current date and git context (branch + short commit hash) auto-fill.

---

## When to use

- A reviewer emits a `[DECISION]` critical the main agent decides not to fix in this branch
- A reviewer's `### ℹ️ Pre-existing tech debt` section flags something worth tracking
- The main agent notices a non-actionable smell during work (cross-cutting issue, brittle pattern) and wants a normalized record

Not for action items the user is committing to today — those belong in `docs/todo.md`. Tech-debt entries are **observations**, not commitments. They describe _what's odd_, not _what to do_.

---

## Execution Steps

### Step 1 — Collect inputs

**Required:**

- `where` — file path with optional line/range (`src/foo.ts:42`, `src-tauri/capabilities/`), or a non-file scope (`across the IPC layer`)
- `obs` — one-line observation: the smell, the surprise, the inconsistency. **Not** the fix
- `found-by` — source: a reviewer name (`reviewer-arch`, `reviewer-security`), `kit-discover`, or `manual`

**Optional:**

- `title` — short title (≤60 chars). Defaults to `obs` truncated at the nearest word boundary
- `severity` — one of 🔴 / 🟡 / 🔵, or a label (`low` / `medium` / `high`). Omit if unknown — do not manufacture

If a required input is missing or empty → ask the user to supply it before proceeding. Do not invent values.

### Step 2 — Auto-fill date and git context

Run each as a separate Bash call:

```bash
date +%Y-%m-%d
```

```bash
git rev-parse --abbrev-ref HEAD 2>/dev/null
```

```bash
git rev-parse --short HEAD 2>/dev/null
```

If not a git repo → the context line reads `(no git context)`. If detached HEAD → use the commit hash only.

### Step 3 — Validate the observation isn't a fix

If `obs` reads like an instruction (`refactor X`, `replace Y with Z`, `extract`, `move`, `delete`, `add`, `fix`, etc.) → ask the user to rephrase as a description of _what's wrong_, not _what to do_. Tech-debt entries lose their value when they prescribe a fix that may turn out to be wrong on closer look — and overlap with `docs/todo.md`.

### Step 4 — Emit the normalized block

Output **as plain markdown text in the chat** (the main agent should be able to copy it verbatim into a file or paste into an issue tracker). Schema:

```
## {YYYY-MM-DD} — {title}
- Found by: {found-by}
- Where: {where}
- Context: branch `{branch}` @ `{short-commit}`
- Severity: {severity}
- Observation: {obs}
```

Omit the `Severity:` line entirely when no severity was provided. Replace the Context value with `(no git context)` when not in a git repo.

After the block, append one short follow-up line:

> Convention: append to `docs/techdebt.md`. The main agent decides the final destination.

Do not write to any file. Do not ask the user where to put it — that's the main agent's call, governed by the downstream `CLAUDE.md`.

---

## Critical Rules

1. **Output-only** — never write, edit, or append to any file. The skill's job is normalization, not persistence. Persistence is the main agent's call.
2. **Observations, not fixes** — the `Observation` field describes what's wrong; it must not say what to do. If the user's `obs` reads like an instruction, ask them to rephrase.
3. **No fabricated context** — if git or any required input is unavailable, say so explicitly (`(no git context)`, prompt for missing input). Never invent values.
4. **No severity by default** — only include the `Severity:` line when the user provides one. Don't invent severity to make the entry look richer.
5. **One entry per invocation** — the skill produces one normalized block. Batches go through repeated invocations or a main-agent loop; this skill stays single-purpose.

---

## Notes

This skill complements the `[DECISION]` reviewer tag (see `kit-readme.md` § "Handling [DECISION] Criticals"). Reviewers flag; the main agent decides; this skill normalizes the persisted record.

`whats-next` reads `docs/techdebt.md` (when present) to surface entries pending triage, but does not score them as work candidates — tech-debt entries are observations, not commitments. Promotion to a real task happens when the main agent or user moves an entry from `docs/techdebt.md` into `docs/todo.md` (or files an issue) with an actionable description.
