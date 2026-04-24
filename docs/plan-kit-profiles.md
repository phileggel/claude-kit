# Plan — Kit Profile Architecture

**Goal**: Transform `tauri-claude-kit` from a single-stack kit into a profile-aware kit
that supports any technology stack from one repo, with zero overhead for projects that use
only the generic layer (e.g. Lua/Factorio mods, Python CLIs, or any stack the kit doesn't
cover with a named profile).

**Status**: Design complete. Implementation deferred.
**Effort**: ~8h for Phases A–E–F (structural, no web content). Phase D (web profile content)
deferred until Muvimu2 exits POC — estimated 5–6h additional when triggered.
**Release target**: v3.0.0 (major — breaking sync script interface + file moves)

---

## Design Decisions

### 1. Organize by resource type, profile as subdirectory

Files are grouped by where they go in downstream projects, not by which profile they belong
to. Profile is always a subdirectory within the resource type folder.

```
kit/agents/         → .claude/agents/
  *.md              base layer (generic, always)
  tauri/*.md        overlay for tauri profile
  web/*.md          overlay for web profile

kit/scripts/        → scripts/
  tauri/*           tauri profile only (no generic base)
  web/*             web profile only

kit/justfile/       → appended to common.just
  tauri.just        tauri profile only
  web.just          web profile only
```

**Why**: each folder has one file type and one destination. Mixing `.md`, `.py`, and `.just`
in one folder creates three different sync rules for one directory — unnecessary complexity.

### 2. Additive sync — never delete local files

The sync script copies kit files into downstream projects but **never deletes** files it
didn't create. A Lumberjack/Lua project may have local `lua-reviewer.md` in `.claude/agents/`
— that file must survive every `just sync-kit` untouched.

Implementation: `cp` only, never `rsync --delete`.

### 3. "No profile" is first-class

A project with no `.claude/kit-profile` (Lua mods, Python tools, any non-kit stack) is
fully supported. It receives all generic process agents and nothing else. It manages its
own quality agents locally. The sync logs "no profile — generic agents only" and exits
cleanly. This is not an error state.

### 4. Incomplete profile — honest failure, not silent partial execution

A profile is **complete** when agents + scripts + justfile are all implemented.
A profile is **planned** (`🚧`) when the structure exists but content is TODO.

- Sync skips missing profile subdirs silently (`if [ -d ... ]` guard)
- `just check` and `just release` fail with a clear, actionable message if no `scripts/check.py`
  or `scripts/release.py` is found — never partial execution
- `kit-tools.md` includes a `Status` column: `✅ complete` or `🚧 planned`
- `check-kit.py` treats `🚧 planned` dirs as known gaps — does not block release

No generic fallback scripts. A partial script that pretends to check a stack it doesn't
understand is worse than an honest "not yet implemented" message.

### 5. Path abstraction for generic agents

Agents that currently hardcode `src-tauri/` or `src/features/` must instead read
`ARCHITECTURE.md` to discover the project's backend/frontend module layout, then verify
paths with Glob. Fallback to common conventions if `ARCHITECTURE.md` is absent (and note it).

This makes generic process agents work for any project layout (`server/`, `client/`,
`backend/`, etc.) without needing a profile variant.

### 6. common.just split

`kit/common.just` keeps only stack-agnostic recipes: `check`, `check-full`, `format`,
`release`, `sync-kit`, `stat`, `clean-branches`.

Stack-specific recipes move to `kit/justfile/{profile}.just`, appended to the downstream
`common.just` during sync. Tauri recipes: `migrate`, `generate-types`, `prepare-sqlx`,
`clean-db`. Web recipes: `migrate`, `db-reset`, `prepare-sqlx`.

`just check` and `just release` in `common.just` gain existence guards:
```bash
if [ ! -f scripts/check.py ]; then
    echo "❌ scripts/check.py not found — profile not synced or not yet implemented."
    echo "   Run: just sync-kit"
    exit 1
fi
```

### 7. Profile declaration

Downstream projects declare their profile in `.claude/kit-profile` (plain text, one line):

```
tauri
```

`just sync-kit` → `sync-config.sh` reads this automatically and passes `--profile` to
`sync.sh`. Absent file = generic agents only. `--profile` flag on `sync-config.sh` overrides
the file for one-off syncs.

### 8. Web profile is 🚧 planned at v3.0.0

The directory structure ships at v3.0.0 with `.gitkeep` placeholders. Content (7 agents,
2 scripts, 1 justfile) is written as Phase D when Muvimu2 exits POC — so agents are
validated against a real codebase before shipping.

### 9. Repo rename (deferred open question)

`tauri-claude-kit` is a misleading name for a multi-profile kit. `claude-kit` is the right
long-term name but breaks all downstream sync URLs. Do not block v3.0.0 on this.

---

## Target Directory Structure

```
kit/
  agents/                     → .claude/agents/ (additive cp, always)
    contract-reviewer.md      ← generic (minor: remove "Tauri 2" from prompt)
    feature-planner.md        ← updated: reads paths from ARCHITECTURE.md
    i18n-checker.md           ← generic (unchanged)
    retro-spec.md             ← updated: reads paths from ARCHITECTURE.md
    script-reviewer.md        ← updated: remove Tauri version-bump rule
    spec-checker.md           ← updated: reads paths from ARCHITECTURE.md
    spec-reviewer.md          ← updated: "IPC contract" → "domain contract"
    workflow-validator.md     ← generic (unchanged)
    tauri/                    → .claude/agents/ (overlay, tauri profile only)
      maintainer.md           ← moved from kit/agents/ (no content change)
      reviewer.md             ← moved
      reviewer-backend.md     ← moved
      reviewer-frontend.md    ← moved
      reviewer-sql.md         ← moved
      test-writer-backend.md  ← moved
      test-writer-frontend.md ← moved
    web/                      → .claude/agents/ (overlay, web profile only) [🚧 planned]
      .gitkeep
  skills/                     → .claude/skills/ (always, no profile variants)
    adr-manager/              ← generic (unchanged)
    contract/                 ← updated: "IPC contract" → "domain contract"
    dep-audit/                ← updated: discover Cargo.toml from ARCHITECTURE.md
    smart-commit/             ← generic (unchanged)
    spec-writer/              ← updated: retro mode reads paths from ARCHITECTURE.md
  scripts/                    → scripts/ (profile only — no generic base scripts)
    tauri/                    → scripts/ (tauri profile only)
      check.py                ← moved from kit/scripts/ (no content change)
      release.py              ← moved from kit/scripts/ (no content change)
    web/                      → scripts/ (web profile only) [🚧 planned]
      .gitkeep
  justfile/                   → appended to downstream common.just (profile only)
    tauri.just                ← extracted from kit/common.just
    web.just                  [🚧 planned]
  githooks/                   → .githooks/ (always, unchanged)
  sync-config.sh              ← updated: reads .claude/kit-profile, passes --profile
  common.just                 ← updated: generic recipes only + guards on check/release
  kit-tools.md                ← updated: profile-aware inventory with Status column
  kit-readme.md               ← updated: add Profiles section
scripts/                      (kit-only, never synced downstream)
  check-kit.py                ← updated: validate new structure, treat 🚧 as known gaps
  release-kit.py              ← unchanged
```

### Sync rule (identical pattern for every resource type)

```
Step  Source                          Destination          Condition
----  ──────────────────────────────  ───────────────────  ─────────────────────────────
1     kit/agents/*.md                 .claude/agents/      always
2     kit/agents/$PROFILE/*.md        .claude/agents/      if $PROFILE set AND dir exists
3     kit/skills/                     .claude/skills/      always
4     kit/githooks/                   .githooks/           always
5     kit/common.just                 common.just          always
6     kit/scripts/$PROFILE/*          scripts/             if $PROFILE set AND dir exists
7     kit/justfile/$PROFILE.just      >> common.just       if $PROFILE set AND file exists
```

All steps use `cp` — never delete, never overwrite files that were not put there by the kit.

### What moves / what changes

| File | Action | Content change |
|---|---|---|
| `kit/agents/reviewer*.md` (7 files) | Move → `kit/agents/tauri/` | None |
| `kit/scripts/check.py` | Move → `kit/scripts/tauri/check.py` | None |
| `kit/scripts/release.py` | Move → `kit/scripts/tauri/release.py` | None |
| `kit/common.just` (Tauri recipes) | Extract → `kit/justfile/tauri.just` | Split |
| `kit/common.just` (generic + guards) | Update in place | Add guards |
| `kit/agents/feature-planner.md` | Update in place | Remove hardcoded paths |
| `kit/agents/retro-spec.md` | Update in place | Remove hardcoded paths |
| `kit/agents/spec-checker.md` | Update in place | Remove hardcoded paths |
| `kit/agents/spec-reviewer.md` | Update in place | "IPC" language |
| `kit/agents/contract-reviewer.md` | Update in place | "Tauri 2" language |
| `kit/agents/script-reviewer.md` | Update in place | Remove Tauri version rule |
| `kit/skills/contract/SKILL.md` | Update in place | "IPC" → "domain" throughout |
| `kit/skills/spec-writer/SKILL.md` | Update in place | Retro mode paths |
| `kit/skills/dep-audit/SKILL.md` | Update in place | Cargo.toml discovery |
| `kit/sync-config.sh` | Update in place | Profile detection + --profile flag |
| `kit/scripts/sync.sh` | Rewrite | Profile-aware, additive-only |
| `scripts/check-kit.py` | Update in place | New structure + 🚧 handling |
| `kit/kit-tools.md` | Update in place | Profile tables + Status column |
| `kit/kit-readme.md` | Update in place | Profiles section |
| `CLAUDE.md` | Update in place | Sync examples + kit-profile note |

---

## Implementation Phases

### Phase A — Genericize agents and skills (~2h)

Edit existing files to remove hardcoded Tauri paths and stack language. No new files.

**1. `kit/agents/feature-planner.md`**
- Step 3 (Codebase Verification): replace `src-tauri/src/context/{domain}/`,
  `src/features/`, `specta_builder.rs` with: "Read `ARCHITECTURE.md` to discover the
  backend and frontend module layout; verify paths with Glob before referencing them."
- Step 4 mapping: replace `src-tauri/src/use_cases/` with: "the project's cross-context
  module as defined in `ARCHITECTURE.md`"
- Workflow TaskList: replace "`maintainer` if `capabilities/*.json` or `tauri.conf.json`
  modified" with "`maintainer` if project config files modified (see `ARCHITECTURE.md`)"
- Critical Rule 8: same — replace hardcoded path with ARCHITECTURE.md reference

**2. `kit/agents/retro-spec.md`**
- Replace all `src-tauri/src/context/{domain}/` and `src/features/{domain}/` references
  with ARCHITECTURE.md-derived paths
- Update description to remove "src-tauri" mention

**3. `kit/agents/spec-checker.md`**
- Step 3 (backend check): replace `src-tauri/src/` with ARCHITECTURE.md-derived backend path
- Step 4 (frontend check): replace `src/features/` with ARCHITECTURE.md-derived frontend path
- Step 5 (contract): replace `src-tauri/` and `src/features/{domain}/gateway.ts` with
  ARCHITECTURE.md-derived paths

**4. `kit/agents/spec-reviewer.md`**
- Section G, closing line: "IPC contract" → "domain contract"
- Final summary: "Ready for /contract: yes — 0 critical findings (incl. contractability)."
  Remove "IPC" from any descriptive text

**5. `kit/agents/contract-reviewer.md`**
- System prompt first line: "IPC contract for a Tauri 2 / React 19 / Rust project" →
  "domain contract for a Rust / React project"

**6. `kit/agents/script-reviewer.md`**
- Find and remove the rule about version bumps requiring sync of `package.json`,
  `src-tauri/Cargo.toml`, and `src-tauri/tauri.conf.json` — that belongs in
  the Tauri `maintainer.md`, not a generic script reviewer

**7. `kit/skills/contract/SKILL.md`**
- Replace every occurrence of "IPC contract" with "domain contract"
- Update title/description to remove Tauri-specific framing
- Contract file format and Commands table are already generic — no change needed there

**8. `kit/skills/spec-writer/SKILL.md`**
- Step 3 (retro mode): replace `src-tauri/src/context/`, `src/features/`,
  `specta_builder.rs` with: "Read `ARCHITECTURE.md` to discover backend and frontend
  module layout, then Grep for related entities in the backend module"
- Step 7 next steps: "IPC contract" → "domain contract"

**9. `kit/skills/dep-audit/SKILL.md`**
- Step 2 (Cargo audit): replace `src-tauri/Cargo.toml` hardcode with: "Locate `Cargo.toml`
  by reading `ARCHITECTURE.md` or by searching for `Cargo.toml` in the project root and
  one level of subdirectories; skip Cargo checks if not found"

### Phase B — Restructure repository (~1.5h)

Move files and create new directory structure. No content changes in moved files.

1. Create directories:
   ```bash
   mkdir -p kit/agents/tauri kit/agents/web
   mkdir -p kit/scripts/tauri kit/scripts/web
   mkdir -p kit/justfile
   ```

2. Move Tauri quality agents (git mv to preserve history):
   ```bash
   git mv kit/agents/reviewer.md          kit/agents/tauri/
   git mv kit/agents/reviewer-backend.md  kit/agents/tauri/
   git mv kit/agents/reviewer-frontend.md kit/agents/tauri/
   git mv kit/agents/reviewer-sql.md      kit/agents/tauri/
   git mv kit/agents/test-writer-backend.md  kit/agents/tauri/
   git mv kit/agents/test-writer-frontend.md kit/agents/tauri/
   git mv kit/agents/maintainer.md        kit/agents/tauri/
   ```

3. Move scripts (git mv):
   ```bash
   git mv kit/scripts/check.py   kit/scripts/tauri/check.py
   git mv kit/scripts/release.py kit/scripts/tauri/release.py
   ```

4. Split `kit/common.just`:
   - Extract these recipes into new `kit/justfile/tauri.just`:
     `migrate`, `generate-types`, `prepare-sqlx`, `clean-db`
   - Keep in `kit/common.just`: `check`, `check-full`, `format`, `release`,
     `sync-kit`, `stat`, `clean-branches`
   - Add existence guards to `check`, `check-full`, and `release` recipes (see Design
     Decision §6 for the bash guard pattern)

5. Add placeholders for planned web profile:
   ```bash
   touch kit/agents/web/.gitkeep
   touch kit/scripts/web/.gitkeep
   # kit/justfile/web.just — do NOT create yet (Phase D)
   ```

6. Update `kit/kit-tools.md`:
   - Add a preamble section explaining profiles and how to declare `.claude/kit-profile`
   - Add `Status` column to all tables: `✅ complete` for tauri profile, `🚧 planned` for web
   - Reorganize "Code Review Agents" table to show tauri profile agents separately
   - Add new "Profiles" section listing available profiles and their status

### Phase C — Update sync scripts (~1.5h)

**1. `kit/scripts/sync.sh`** — rewrite for profile-aware, additive-only sync

The script runs inside a temp dir cloned from the kit tag (called by `sync-config.sh`).
Receives `PROFILE` env var (empty string if no profile).

Sync sequence — identical pattern for each resource type:
```bash
# 1. Generic agents (always)
cp kit/agents/*.md "$TARGET/.claude/agents/"

# 2. Profile agents (overlay, skip if dir absent)
if [ -n "$PROFILE" ] && [ -d "kit/agents/$PROFILE" ]; then
    cp kit/agents/"$PROFILE"/*.md "$TARGET/.claude/agents/" 2>/dev/null || true
fi

# 3. Skills (always)
cp -r kit/skills/. "$TARGET/.claude/skills/"

# 4. Git hooks (always)
cp kit/githooks/. "$TARGET/.githooks/"

# 5. Generic common.just (always)
cp kit/common.just "$TARGET/common.just"

# 6. Profile scripts (skip if dir absent or empty)
if [ -n "$PROFILE" ] && [ -d "kit/scripts/$PROFILE" ] && \
   [ -n "$(ls kit/scripts/$PROFILE/ 2>/dev/null)" ]; then
    cp kit/scripts/"$PROFILE"/* "$TARGET/scripts/"
fi

# 7. Profile justfile recipes (append, skip if file absent)
if [ -n "$PROFILE" ] && [ -f "kit/justfile/$PROFILE.just" ]; then
    echo "" >> "$TARGET/common.just"
    cat kit/justfile/"$PROFILE.just" >> "$TARGET/common.just"
fi
```

Log at end:
- With profile: `✅ Synced generic agents + profile: $PROFILE`
- Without profile: `ℹ️  Synced generic agents only (no .claude/kit-profile found)`

**2. `kit/sync-config.sh`** — add profile detection

Before invoking `sync.sh`, detect profile:
```bash
PROFILE=""
# --profile flag overrides file
for arg in "$@"; do
    case $arg in
        --profile=*) PROFILE="${arg#*=}" ;;
        --profile)   shift; PROFILE="$1" ;;
    esac
done
# Fall back to .claude/kit-profile file
if [ -z "$PROFILE" ] && [ -f ".claude/kit-profile" ]; then
    PROFILE=$(cat .claude/kit-profile | tr -d '[:space:]')
fi
export PROFILE
```

If no profile found: print `ℹ️  No .claude/kit-profile found — syncing generic agents only`
(not a warning, not an error — first-class state).

### Phase D — Create web profile content (~5–6h) ⚠️ DEFERRED

**Trigger**: start this phase when Muvimu2 (Axum + React + PostgreSQL project at
`/home/phil/projects/Muvimu2/`) exits POC phase. Writing agents without a real codebase
to validate them against produces agents that miss real patterns.

**D.1 — `kit/agents/web/` (7 agent files)**

Each adapted from its Tauri counterpart. Key differences per agent:

- **`reviewer.md`**: "Axum + React + PostgreSQL"; REST data flow; paths from ARCHITECTURE.md
- **`reviewer-backend.md`**: Axum extractors, `axum::response`, tower middleware, no `unwrap()`
  in handlers, `thiserror`/`anyhow`, inline `#[cfg(test)]` with `axum-test`
- **`reviewer-frontend.md`**: no `invoke()`, no M3 tokens, `fetch`/`axios` only through
  gateway, same UX completeness rules (empty/loading/error/success)
- **`reviewer-sql.md`**: PostgreSQL — `BIGSERIAL` PKs, `TEXT`/`TIMESTAMPTZ`/`NUMERIC` types,
  `RETURNING` clause, FK indexes, `BEGIN`/`COMMIT`, no SQLite affinity rules
- **`test-writer-backend.md`**: `sqlx::PgPool` test setup, `axum-test` or `reqwest` HTTP
  assertions, `#[tokio::test]`, stub: `todo!("implement")`, confirm red via `cargo test`
- **`test-writer-frontend.md`**: Vitest + `vi.fn()` fetch mock or MSW, no `@tauri-apps/api/core`,
  colocate `gateway.test.ts`, stub: `expect(true).toBe(false)`, confirm red via `npx vitest run`
- **`maintainer.md`**: Dockerfile + docker-compose correctness, `.env.example` completeness,
  nginx/Caddy port alignment, CI build/test/deploy steps, `Cargo.toml`+`package.json` version sync

**D.2 — `kit/scripts/web/` (2 Python scripts)**

- **`check.py`**: Rust dir `server/` (read from ARCHITECTURE.md, default `server/`); no SQLx
  offline mode; no SQLx prepare check; same npm/TSC checks; remove `sqlx` metric
- **`release.py`**: version files = `package.json` + `server/Cargo.toml` only; stage those +
  `server/Cargo.lock` + `CHANGELOG.md`; all semver/changelog/tag logic identical to Tauri version

**D.3 — `kit/justfile/web.just`**

```just
# Web profile — PostgreSQL / Axum recipes
migrate:
    cd server && sqlx migrate run

db-reset:
    cd server && sqlx database reset

prepare-sqlx:
    cd server && cargo sqlx prepare
```

After Phase D: run preflight, `/smart-commit`, release v3.1.0 (minor).

### Phase E — Update kit documentation (~2h)

**1. `kit/kit-tools.md`**
- Add preamble: "Profiles — declare your stack in `.claude/kit-profile`. Absent = generic only."
- All tables: add `Status` column (`✅` / `🚧 planned`)
- Code Review Agents table: show generic agents separately from profile agents
- Add profile summary table:
  | Profile | Agents | Scripts | Justfile | Status |
  |---------|--------|---------|----------|--------|
  | `tauri` | 7 | check.py, release.py | tauri.just | ✅ complete |
  | `web`   | 7 | check.py, release.py | web.just   | 🚧 planned |
  | (none)  | 0 | — | — | ✅ first-class |

**2. `kit/kit-readme.md`**
- Add `## Profiles` section explaining the two-tier architecture, how to declare a profile,
  what "no profile" means, how to add a custom profile

**3. `CLAUDE.md`**
- Update sync command example: `./scripts/sync-config.sh --profile tauri`
- Add: "Declare profile: `echo 'tauri' > .claude/kit-profile`"
- Update repository layout comment to reflect new `kit/agents/tauri/`, `kit/scripts/tauri/`,
  `kit/justfile/` structure

**4. `scripts/check-kit.py`**
- Update paths: `kit/agents/*.md` now includes `kit/agents/tauri/*.md` and `kit/agents/web/`
- `kit/agents/web/.gitkeep` and `kit/scripts/web/.gitkeep` → treat as `🚧 planned`, not error
- Cross-reference check: agents in `kit/agents/tauri/` must appear in `kit-tools.md` with
  `✅` status; agents in `kit/agents/web/` (if any) must have `🚧` status
- Preflight agent (`/preflight`) covers `kit/agents/tauri/` automatically — no change needed
  there, but verify its glob patterns pick up subdirs

### Phase F — Preflight + Release (~1h)

```bash
python3 scripts/check-kit.py       # must pass
/preflight                         # validate all modified downstream files
/smart-commit                      # conventional commit
python3 scripts/release-kit.py     # v3.0.0 (major)
```

**v3.0.0 is breaking for downstream projects** — existing Tauri projects must migrate:

```bash
# In each downstream Tauri project:
echo "tauri" > .claude/kit-profile
./scripts/sync-config.sh --profile tauri
git add .claude/kit-profile .claude/agents/ scripts/ common.just
git commit -m "chore: adopt kit v3 tauri profile"
```

No behavior change after migration — same agents, same scripts, same justfile recipes.

---

## Effort Summary

| Phase | What | Effort | When |
|---|---|---|---|
| A | Genericize 9 agents/skills (path abstraction, remove "IPC"/"Tauri" language) | ~2h | v3.0.0 |
| B | Restructure repo (move 9 files, split common.just, create dirs) | ~1.5h | v3.0.0 |
| C | Sync script rewrite (profile-aware, additive-only) + sync-config.sh | ~1.5h | v3.0.0 |
| E | Docs + check-kit.py (kit-tools, kit-readme, CLAUDE.md, check-kit.py) | ~2h | v3.0.0 |
| F | Preflight + v3.0.0 release | ~1h | v3.0.0 |
| D | Web profile content (7 agents + 2 scripts + justfile) | ~5–6h | v3.1.0, post-Muvimu2 POC |

**Total to ship v3.0.0: ~8h across 2 sessions.**

Session 1 suggestion: Phases A + B
Session 2 suggestion: Phases C + E + F

---

## Open Questions (non-blocking)

- [ ] **Repo rename**: `tauri-claude-kit` → `claude-kit` — correct long-term name but breaks
  all downstream sync URLs. Decide separately, don't block v3.0.0.
- [ ] **`workflow-validator.md`**: references `tauri.conf.json` as a `maintainer` trigger —
  small Tauri-specific leak in a generic agent. Fix in Phase A or leave for v3.1.0.
- [ ] **web.just path convention**: `server/` is Muvimu2's convention, not universal for web
  projects. Phase D agents should read from `ARCHITECTURE.md`, not hardcode `server/`.
  Note this when writing Phase D.
