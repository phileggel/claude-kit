---
name: preflight
description: Pre-release validator for kit artifacts. Checks downstream-readiness of agents/skills (no kit-centric language, correct paths), script quality, and cross-component coherence. Use before releasing kit updates to downstream projects.
tools: Read, Grep, Glob, Bash
---

# Skill — `preflight`

Validates that all kit artifacts are production-ready for downstream projects before a release.

> **Deterministic checks live in `python3 scripts/check-kit.py`** — kit-centric language,
> agent inventory coverage, sync→kit-tools.md coverage, and tool-minimality are enforced there
> on every commit. Run it first; if it passes, focus this skill on the semantic checks below
> that only a reader can judge: tone, ambiguous references, terminology drift, and
> cross-component coherence.

---

## Execution Steps

### 0. Run deterministic checks first

```
python3 scripts/check-kit.py
```

If it fails, fix those issues before continuing — they are blocking and unambiguous.

### 1. Identify downstream artifacts to validate

Collect all downstream files changed since the last release tag — this is the full set that will ship:

1. Run `git describe --tags --abbrev=0` to get the last release tag (e.g. `v3.7.0`).
2. Run `git diff --name-only <last-tag>..HEAD` to get every file committed since that tag.
3. Also collect any working-tree changes not yet committed (for edits made right before the release):
   - `git diff --name-only HEAD` — unstaged changes
   - `git diff --cached --name-only` — staged changes
   - `git status --porcelain | grep "^?" | awk '{print $2}'` — untracked new files
4. Union and deduplicate all sources.

If `git describe` finds no tags, fall back to `git diff --name-only HEAD` (first release in the repo).

Filter the combined (deduplicated) list to keep only downstream artifacts — files that will be synced to downstream projects:

**IA artifacts** (synced to `.claude/`, `.claude/agents/`, and `.claude/skills/`):

- `kit/agents/*.md` — generic agents
- `kit/agents/*/*.md` — profile agent overlays (e.g. `kit/agents/tauri/`)
- `kit/skills/*/*.md` — skills
- `kit/kit-tools.md`, `kit/kit-readme.md` — discovery files synced to `.claude/`

**Script artifacts** (synced to `scripts/`, `.githooks/`, project root):

- `kit/scripts/sync.sh` — sync logic
- `kit/scripts/*/*.py` — profile-specific scripts (e.g. `kit/scripts/tauri/check.py`)
- `kit/githooks/*`
- `kit/common.just` — generic justfile recipes
- `kit/justfile/*.just` — profile-specific justfile recipes (appended to `common.just` downstream)

If no modified files match — output `ℹ️ No modified kit artifacts — nothing to validate.` and stop.

Validate **only the matched files**. Skip unmodified files entirely.

---

### 2. Validate IA downstream context

For each agent/skill file, check:

#### A — Language & Context

> Kit-centric paths and phrases are caught by `check-kit.py` (Step 0). Focus here on:

- 🔴 **Wrong downstream paths** — references to paths that don't exist downstream (e.g. assumes a directory not present in the project layout)
- 🟡 **Ambiguous "this" references** — unclear if referring to the agent itself, the kit, or the downstream project

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
- 🟡 **Terminology drift** — inconsistent use of terms (e.g., "TRIGRAM-NNN" vs "rule identifier")
- 🟡 **Severity label missing** — a rule in an agent has no 🔴/🟡/🔵 label

#### E — Bash Command Ergonomics (skills only)

Claude Code's permission system does **not** auto-allow compound shell constructs, even when the first token is on the auto-allow list. Scan every fenced `bash`/`sh` code block in skill files for:

- 🔴 **Compound operators** — `&&`, `||`, or `;` chaining two or more commands → split into separate Bash calls
- 🔴 **Shell loops** — `for … do … done` or `while … do … done` → replace with `Glob` + `Read`/`Grep` or in-context logic
- 🔴 **Pipelines delegating to non-trivial commands** — `cmd | awk …`, `cmd | sed …`, `cmd | while read …` → use dedicated tools or a simple `grep` call instead

These constructs cause a permission prompt on every invocation, breaking the no-friction intent of skills. The fix is always one of: (a) split into multiple simple Bash calls, or (b) replace with `Glob`/`Read`/`Grep` tool calls.

---

### 3. Validate script quality

For each file in `kit/scripts/` (including profile subdirs like `kit/scripts/tauri/`) and `kit/githooks/`:

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

> Inventory coverage (every agent listed in kit-tools.md, every synced root file documented)
> is enforced by `check-kit.py` (Step 0). Focus here on:

- 🔴 Agent references a script that won't be synced downstream
- 🔴 Agent A references agent B that isn't in `kit/agents/` or `kit/agents/<profile>/`
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

1. **`check-kit.py` is the deterministic gate** — it enforces kit-centric language, agent inventory, sync→kit-tools.md coverage, and tool-minimality. Do not duplicate those checks here.
2. **All cross-references verified** — if agent A mentions agent B or script X, both must exist and be synced
3. **Script safety non-negotiable** — `set -euo pipefail`, shebang, quoted variables; no exceptions
4. **Run before every release** — this skill is the gate before `python3 scripts/release-kit.py`
