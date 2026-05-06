# claude-kit

Opinionated Claude-assisted factory for Tauri 2 + Axum / React 19 projects, built around Spec Driven Development.

Provides the agents, skills, scripts, and git hooks that drive the **spec → contract → plan → test-first → verify** workflow. Stack-specific conventions (architecture rules, testing patterns, UI rules) are bundled directly in this repo under `kit/docs/` and synced copy-once to downstream projects.

## Contents

```
kit/
  sync-config.sh   Stable bootstrap entry point (copied once to downstream projects)
  agents/          Claude Code subagent definitions → .claude/agents/
  skills/          Claude Code skill definitions → .claude/skills/
  docs/tauri/      Convention docs → docs/ (copy-once, never overwritten by sync)
  githooks/        Git hooks → .githooks/
  scripts/
    sync.sh        Sync logic (ephemeral, runs from $TMP)
    check.py       Full quality suite (lint, tests, build, SQLx, TSC)
    release.py     Release manager (semver bump, changelog, tag, push)
  common.just      Shared justfile recipes
```

## Setup in a new project

Copy the bootstrap once — it never needs to be updated again:

```bash
# curl
curl -fsSL https://raw.githubusercontent.com/phileggel/claude-kit/main/kit/sync-config.sh \
  -o scripts/sync-config.sh && chmod +x scripts/sync-config.sh

# or wget
wget -qO scripts/sync-config.sh \
  https://raw.githubusercontent.com/phileggel/claude-kit/main/kit/sync-config.sh \
  && chmod +x scripts/sync-config.sh
```

Then run the initial sync:

```bash
./scripts/sync-config.sh
```

## Updating an existing project

```bash
./scripts/sync-config.sh           # latest release
./scripts/sync-config.sh v1.6.0    # specific tag
```

This will:

- Update `.claude/agents/` and `.claude/skills/`
- Update `scripts/check.py` and `scripts/release.py`
- Update `.githooks/`
- Write the version and changelog delta to `.claude/kit-version.md`

> `scripts/sync-config.sh` (the bootstrap) is never overwritten by a sync — it is intentionally stable.

## Migrating from v1.x

The sync architecture changed in v2.0.0: `scripts/sync-config.sh` is now a stable bootstrap that never gets overwritten. Run this one-time command to migrate:

```bash
# curl
curl -fsSL https://raw.githubusercontent.com/phileggel/claude-kit/main/kit/sync-config.sh \
  -o scripts/sync-config.sh && chmod +x scripts/sync-config.sh && ./scripts/sync-config.sh

# or wget
wget -qO scripts/sync-config.sh \
  https://raw.githubusercontent.com/phileggel/claude-kit/main/kit/sync-config.sh \
  && chmod +x scripts/sync-config.sh && ./scripts/sync-config.sh
```

After this, future syncs work as usual with `./scripts/sync-config.sh`.

## Kit development setup

If you're hacking on the kit itself (not just consuming it downstream), `just check` runs the kit's lint suite and expects the following tools on `PATH`:

| Tool         | Purpose                                     | Install (Debian/Ubuntu)                                         |
| ------------ | ------------------------------------------- | --------------------------------------------------------------- |
| `just`       | Task runner                                 | `sudo apt install just`                                         |
| `ruff`       | Python lint + format (mandatory)            | `sudo apt install pipx && pipx ensurepath && pipx install ruff` |
| `shfmt`      | Bash format (mandatory if `.sh`)            | `sudo apt install shfmt`                                        |
| `shellcheck` | Bash lint (optional, recommended)           | `sudo apt install shellcheck`                                   |
| `npx`        | Runs Prettier for Markdown (release-strict) | `sudo apt install nodejs npm`                                   |

After installing pipx-based tools, ensure `~/.local/bin` is on your `PATH` (open a new shell, or `export PATH="$HOME/.local/bin:$PATH"`).

Sanity check: `just check` from the repo root should exit clean.

## Versioning

This repo uses semantic versioning via git tags:

| Bump    | When                                          |
| ------- | --------------------------------------------- |
| `patch` | Bug fix in a script or agent wording          |
| `minor` | New agent/skill, significant improvement      |
| `major` | Breaking change (renamed file, removed agent) |

To release this kit, use `python3 scripts/release-kit.py <major|minor|patch>`.

## Project-specific overrides

Local adaptations (e.g. project-specific rules in an agent) can be kept in the concrete project. They will be overwritten on the next `sync-config.sh` run — keep a note of what to re-apply.

---

## 👤 Author & Architect

**Philippe Eggel**

- **Role:** System Architect & AI Workflow Orchestrator
- **Methodology:** Spec-Driven Development (SDD) & AI-Augmented Engineering
- **GitHub:** [@phileggel](https://github.com/phileggel)

> "The code is a commodity; the specification and the alignment workflow are the real assets."
