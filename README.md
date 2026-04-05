# tauri-claude-kit

Shared Claude Code configuration for Tauri 2 / React 19 / Rust projects.

## Contents

```
agents/          Claude Code subagent definitions (.claude/agents/)
skills/          Claude Code skill definitions (.claude/skills/)
scripts/
  check.py       Full quality suite (lint, tests, build, SQLx, TSC)
  release.py     Release manager (semver bump, changelog, tag, push)
.githooks/
  commit-msg     Conventional commit validation
  pre-commit     Fast quality check before commit
  pre-push       Full quality check before push
```

## Setup in a new project

```bash
# 1. Copy the sync script into your project
curl -o scripts/sync-config.sh \
  https://raw.githubusercontent.com/your-username/tauri-claude-kit/main/scripts/sync-config.sh
chmod +x scripts/sync-config.sh

# 2. Run initial sync
./scripts/sync-config.sh v1.0.0
```

## Updating an existing project

```bash
./scripts/sync-config.sh v1.1.0
```

This will:
- Update `.claude/agents/` and `.claude/skills/`
- Update `scripts/check.py` and `scripts/release.py`
- Update `.githooks/`
- Write the version to `.claude-kit-version`

## Versioning

This repo uses semantic versioning via git tags:

| Bump | When |
|------|------|
| `patch` | Bug fix in a script or agent wording |
| `minor` | New agent/skill, significant improvement |
| `major` | Breaking change (renamed file, removed agent) |

## Project-specific overrides

Local adaptations (e.g. project-specific rules in an agent) can be kept in the concrete project. They will be overwritten on the next `sync-config.sh` run — keep a note of what to re-apply.
