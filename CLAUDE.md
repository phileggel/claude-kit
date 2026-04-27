# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository, which is a shared configuration kit for Tauri 2 / React 19 / Rust projects.

## Simple Technical Workflow

_Use for: Bug fixes, dependency updates, minor maintenance (no new business rules or features)._

1.  **Analysis**: Read relevant documentation and analyze the codebase.
2.  **Direct Plan**: Propose a concise TODO plan with exact file paths in the chat. Ask user to validate.
3.  **Tracking**: Use internal `TaskCreate` / `TaskUpdate` tools to track workflow steps (mark `in_progress` when starting, `completed` when done) for user visibility.
4.  **Implementation**: Execute the code changes.
5.  **Review & Quality**: Run static checks (`python3 scripts/check-kit.py`), write tests, and run `/preflight` before any release.
6.  **Closure**: Ask user if another task is needed before commit, otherwise use **`/smart-commit`** skill.

## Critical Patterns

- **Always use `just`**: Never suggest or execute native commands if a corresponding recipe exists in `justfile`.

- **Never commit without explicit user authorization.** Always use `/smart-commit` and wait for a clear "go" before any `git commit` or `git push` — including hotfixes, release commits, and one-liners. No exceptions.

- **Project Name Neutrality:** Agent files MUST NOT reference a specific project name (e.g., "MyApp").
  - ✅ Correct: "You are a senior code reviewer for a full-stack project."
  - ❌ Wrong: "You are a senior code reviewer for MyApp."
  - _Why it's critical:_ Agents are reusable; embedding project names creates stale references when copied or renamed.

- **Tool Minimality:** Agent `tools:` fields should only list necessary tools. Review-only agents should not have `Edit` or `Write`.
  - ✅ Correct: `tools: Read, Grep, Glob, Bash` for a review agent.
  - ❌ Wrong: `tools: Read, Grep, Glob, Bash, Edit, Write` for a review agent.
  - _Why it's critical:_ Over-privileged agents are slower and pose a security risk.

- **Kit-local tooling only:** When working on this repository, only use tools from `.claude/` (skills, agents) and `scripts/` (check-kit.py, release-kit.py). Never invoke agents or skills from `kit/agents/` or `kit/agents/tauri/` directly — those are downstream artifacts, not kit tooling.
  - ✅ Correct: `/preflight`, `/smart-commit`, `python3 scripts/check-kit.py`
  - ❌ Wrong: running `reviewer`, `spec-checker`, or any `kit/agents/**/*.md` agent on kit files
  - _Why it's critical:_ Kit agents are written for downstream project structure which does not exist in this repository.

```bash
# Declare your profile (once, checked into the project)
echo "tauri" > .claude/kit-profile

# Sync latest tag (auto-detects .claude/kit-profile)
./scripts/sync-config.sh

# Sync a specific tag
./scripts/sync-config.sh v2.0.0

# Override profile for one-off sync
./scripts/sync-config.sh --profile tauri
```

The script self-updates before syncing: if `sync-config.sh` itself changed in the kit, it re-executes the new version automatically. After syncing, review `git diff` before committing.

## Versioning

Use semantic versioning via git tags:

| Bump    | When                                          |
| ------- | --------------------------------------------- |
| `patch` | Bug fix in a script or agent wording          |
| `minor` | New agent/skill, significant improvement      |
| `major` | Breaking change (renamed file, removed agent) |

Run releases via `python3 scripts/release-kit.py` (interactive).

## Git hooks

Hooks in `kit/githooks/` are synced to `.githooks/` in downstream projects and must be activated:

```bash
git config core.hooksPath .githooks
```

- **pre-commit**: runs `python3 scripts/check-kit.py --fast` (lint/format only)
- **commit-msg**: enforces conventional commit format (`type: description`, max 72 chars, no co-author lines, no test results in message)

Valid commit types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `ci`

## Repository layout

```
kit/                        ← everything synced downstream
  sync-config.sh            → scripts/sync-config.sh (bootstrap, copied once)
  agents/                   → .claude/agents/ (generic, always synced)
  agents/tauri/             → .claude/agents/ (tauri profile overlay)
  agents/web/               → .claude/agents/ (web profile — 🚧 planned)
  skills/                   → .claude/skills/ (always synced)
  githooks/                 → .githooks/ (always synced)
  justfile/
    tauri.just              → appended to common.just (tauri profile)
  scripts/
    sync.sh                 ephemeral sync logic (runs from $TMP, never copied)
    tauri/
      check.py              → scripts/check.py (tauri profile)
      release.py            → scripts/release.py (tauri profile)
    web/                    (web profile — 🚧 planned)
  common.just               → common.just (generic recipes + guards)
scripts/                    ← kit-only tooling (not synced)
  check-kit.py              kit quality checker
  release-kit.py            kit release manager
```

## Downstream tools (**CRITICAL** for reference only)

All agents, skills, scripts, git hooks, and justfile recipes provided to downstream projects are inventoried in [`kit/kit-tools.md`](kit/kit-tools.md). Refer to that file for the full list — do not duplicate it here.

## Local tools (kit development only)

These are available in `.claude/` for working on the kit itself. They are **not synced** to downstream projects.

| Type  | Name           | When to use                                                                                           |
| ----- | -------------- | ----------------------------------------------------------------------------------------------------- |
| skill | `preflight`    | Before any release — validates IA readiness, script quality, cross-component coherence (`/preflight`) |
| skill | `smart-commit` | To create a validated conventional commit (`/smart-commit`)                                           |

> `smart-commit` is synced from `kit/skills/smart-commit/` — keep `.claude/skills/smart-commit/SKILL.md` in sync manually when the source changes.
