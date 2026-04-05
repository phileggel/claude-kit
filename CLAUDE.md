# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository, which is a shared configuration kit for Tauri 2 / React 19 / Rust projects.

## Simple Technical Workflow

_Use for: Bug fixes, dependency updates, minor maintenance (no new business rules or features)._

1.  **Analysis**: Read relevant documentation and analyze the codebase.
2.  **Direct Plan**: Propose a concise TODO plan with exact file paths in the chat. Ask user to validate.
3.  **Tracking**: Use internal `TaskCreate` / `TaskUpdate` tools to track workflow steps (mark `in_progress` when starting, `completed` when done) for user visibility.
4.  **Implementation**: Execute the code changes.
5.  **Review & Quality**: Run static checks (`python3 scripts/check.py`), write tests, and run the relevant subagents (`reviewer`, `script-reviewer`, etc.) just like in Phase 3 of the Full Workflow.
6.  **Closure**: Ask user if another task is needed before commit, otherwise use **`/smart-commit`** skill.

## Critical Patterns

- **Project Name Neutrality:** Agent files MUST NOT reference a specific project name (e.g., "PortfolioManager").
  - ✅ Correct: "You are a senior code reviewer for a Tauri 2 / React 19 / Rust project."
  - ❌ Wrong: "You are a senior code reviewer for PortfolioManager."
  - _Why it's critical:_ Agents are reusable; embedding project names creates stale references when copied or renamed.

- **Tool Minimality:** Agent `tools:` fields should only list necessary tools. Review-only agents should not have `Edit` or `Write`.
  - ✅ Correct: `tools: Read, Grep, Glob, Bash` for a review agent.
  - ❌ Wrong: `tools: Read, Grep, Glob, Bash, Edit, Write` for a review agent.
  - _Why it's critical:_ Over-privileged agents are slower and pose a security risk.

```bash
# Sync latest main
./scripts/sync-config.sh

# Sync a specific tag
./scripts/sync-config.sh v1.2.0
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

Hooks in `.githooks/` must be activated in downstream projects:

```bash
git config core.hooksPath .githooks
```

- **pre-commit**: runs `python3 scripts/check.py --fast` (lint/format only)
- **commit-msg**: enforces conventional commit format (`type: description`, max 72 chars, no co-author lines, no test results in message)

Valid commit types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`

## Agents

Defined in `agents/*.md`, synced to `.claude/agents/` in downstream projects:

| Agent                | Purpose                                                               |
| -------------------- | --------------------------------------------------------------------- |
| `reviewer`           | Code review: DDD, backend/frontend rules, general quality             |
| `ux-reviewer`        | M3 design compliance, UX completeness (empty/loading/error states)    |
| `maintainer`         | GitHub Actions workflows, config files, pre-release checks            |
| `script-reviewer`    | Internal quality of `scripts/` and `.githooks/` files                 |
| `spec-reviewer`      | Spec quality gate before implementation                               |
| `spec-checker`       | Verifies all spec business rules (R1, R2…) are implemented and tested |
| `feature-planner`    | Translates spec to implementation plan with exact file paths          |
| `ia-reviewer`        | Meta-reviewer for agent/skill/CLAUDE.md correctness                   |
| `i18n-checker`       | Hardcoded strings, missing/unused translation keys                    |
| `workflow-validator` | Validates all required workflow steps were done before commit         |

## Skills

Defined in `skills/*/SKILL.md`, synced to `.claude/skills/` in downstream projects:

| Skill          | Purpose                                                                  |
| -------------- | ------------------------------------------------------------------------ |
| `smart-commit` | Conventional commit with strict validation, tests, linters, confirmation |
| `dep-audit`    | npm + Cargo dependency audit (outdated versions, CVEs) before releases   |
| `adr-manager`  | Create/update Architecture Decision Records in `docs/adr/`               |
| `spec-writer`  | Interactive spec creation (also available as a skill)                    |

## common.just

Shared justfile recipes intended to be imported into downstream project justfiles. Key recipes:

- `just check` — fast quality check (lint/format only)
- `just check-full` — full quality check including tests and build
- `just format` — auto-fix formatting (Rust + frontend)
- `just migrate` — run pending SQLx migrations
- `just prepare-sqlx` — regenerate SQLx offline query cache after schema/query changes
- `just release` — interactive release manager
- `just sync-kit version=<tag>` — sync this kit into the project
- `just clean-db` — **destructive**: deletes local DB and recreates schema
- `just clean-branches` — **destructive**: removes stale remote-tracking branches
