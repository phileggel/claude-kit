---
name: preflight
description: Pre-release validator for kit artifacts. Checks downstream-readiness of agents/skills (no kit-centric language, correct paths), script quality, and cross-component coherence. Use before releasing kit updates to downstream projects.
tools: Read, Grep, Glob, Bash
---

# Skill — `preflight`

Validates that all kit artifacts are production-ready for downstream projects before a release.

---

## Execution Steps

### 1. Identify downstream artifacts to validate

Collect all modified downstream files by unioning these three commands:

- `git diff --name-only HEAD` — unstaged changes vs HEAD
- `git diff --cached --name-only` — staged changes vs HEAD
- `git status --porcelain | grep "^?" | awk '{print $2}'` — untracked new files

Filter the combined (deduplicated) list to keep only downstream artifacts — files that will be synced to downstream projects:

**IA artifacts** (synced to `.claude/agents/` and `.claude/skills/`):

- `kit/agents/*.md`
- `kit/skills/*/*.md`
- `kit/kit-tools.md`

**Script artifacts** (synced to `scripts/`, `.githooks/`, project root):

- `kit/scripts/check.py`, `kit/scripts/release.py`
- `kit/scripts/sync.sh`
- `kit/githooks/*`
- `kit/common.just`

If no modified files match — output `ℹ️ No modified kit artifacts — nothing to validate.` and stop.

Validate **only the matched files**. Skip unmodified files entirely.

---

### 2. Validate IA downstream context

For each agent/skill file, check:

#### A — Language & Context

- 🔴 **Kit-centric language** — phrases like `kit/agents/`, `this kit`, `synced to downstream`; correct form is `your project's`, `in this skill`
- 🔴 **Upstream-only paths** — references to `kit/` directories that don't exist in downstream projects
- 🔴 **Wrong downstream paths** — should reference `docs/`, `scripts/`, `.claude/` not `kit/`
- 🟡 **Ambiguous "this" references** — unclear if referring to the agent itself or the downstream project

#### B — Downstream Instructions

- 🔴 **Tool not listed in frontmatter** — agent uses a tool not declared in its `tools:` field
- 🔴 **Instructions assume kit layout** — should work identically when synced to `.claude/agents/{name}.md`
- 🟡 **Path not relative to downstream root** — paths must resolve from downstream project root

#### C — Workflow Alignment

- 🔴 **Broken cross-reference** — agent A references agent B that isn't synced downstream
- 🔴 **Script reference incorrect** — agent mentions a script that won't exist in downstream `scripts/`
- 🟡 **Outdated agent reference** — link to an agent that no longer exists or was renamed

#### D — Internal Consistency

- 🟡 **Path inconsistency** — different steps use different paths for the same resource
- 🟡 **Terminology drift** — inconsistent use of terms (e.g., "TRIGRAMME-NNN" vs "rule identifier")
- 🟡 **Severity label missing** — a rule in an agent has no 🔴/🟡/🔵 label

---

### 3. Validate script quality

For each file in `kit/scripts/` and `kit/githooks/`:

#### Bash scripts / git hooks

- 🔴 Missing `#!/usr/bin/env bash` shebang
- 🔴 Missing `set -euo pipefail`
- 🔴 Unquoted variables (`$var` instead of `"$var"`)
- 🔴 Command injection risk (user input in `eval` or unescaped substitution)
- 🟡 Non-portable patterns (`grep -P`, `sed -i` without `.bak`, GNU-only flags)
- 🟡 Temp files not cleaned up with `trap ... EXIT`

#### Python scripts

- 🔴 Missing `#!/usr/bin/env python3` shebang
- 🔴 Bare `except:` — must catch specific exceptions
- 🔴 `subprocess` calls without `check=True` or return-code validation
- 🟡 String concatenation for file paths — use `pathlib.Path`
- 🟡 `open()` without `encoding='utf-8'`

---

### 4. Cross-component coherence

Cross-references are checked against the **full kit** (not just modified files) — a modified agent may reference an existing unmodified file, which is valid.

- 🔴 Agent references a script that won't be synced downstream
- 🔴 Agent A references agent B that isn't in `kit/agents/`
- 🔴 Agent in `kit/agents/` missing from `kit/kit-tools.md` (only check staged agents)
- 🟡 `kit/kit-tools.md` trigger or description diverges from agent frontmatter

---

### 5. Output

```
## Preflight Report

### IA Artifacts
#### kit/agents/example.md
- 🔴 Line 12: kit-centric path "kit/docs/" → use "docs/"

### Scripts
#### kit/scripts/sync.sh
✅ No issues found.

### Cross-Component
✅ All agent cross-references valid.
✅ kit-tools.md complete.

---
Preflight complete: N critical, N warnings.
Ready for release: yes / no (if critical > 0).
```

---

## Critical Rules

1. **Zero kit-centric language** in downstream-destined files — any `kit/` path reference in an agent or skill body is a 🔴 blocker
2. **All cross-references verified** — if agent A mentions agent B or script X, both must exist and be synced
3. **Script safety non-negotiable** — `set -euo pipefail`, shebang, quoted variables; no exceptions
4. **Run before every release** — this skill is the gate before `python3 scripts/release-kit.py`
