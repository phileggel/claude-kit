# Plan — Kit Discovery & Version Awareness

**Goal**: make the kit "fluid" for downstream projects — the downstream agent should know which
kit version is installed, what changed since the last sync, and what the kit ships across all
surfaces (`.claude/`, `scripts/`, `.githooks/`, `justfile`). Today, only `.claude/agents/` and
`.claude/skills/` are auto-discovered by the model; other surfaces are invisible.

**Status**: Design agreed. Implementation pending.
**Effort**: ~2h for Phases 1+2. Phase 3 conditional, scope separately if triggered.
**Release target**: minor bump (additive, no breaking change).

---

## Context

Captured 2026-04-26. The downstream `CLAUDE.md` is user-owned and must NOT be rewritten by sync —
it can only be referenced. Auto-loading happens for: `CLAUDE.md` (full), agent/skill _names and
descriptions_ (not bodies), nothing else under `.claude/`. Other files are read on demand when
the model knows where to look.

This plan adds two passive files that sync keeps current, and conditionally a skill that
actively reconciles drift between `CLAUDE.md` and kit content.

---

## Phase 1 — `.claude/kit-version.md` (sync-managed)

**Goal**: a small, always-current file the agent reads on demand to know version + recent changes.

**Format**:

```markdown
# Kit version

claude-kit **v3.1.3** — synced 2026-04-27

## Changes since v3.1.2 (your previous sync)

- v3.1.3: <release commit subject or tag annotation>
- v3.1.2: smart-commit uses just check; tool-minimality lint added
```

**Implementation in `kit/scripts/sync.sh`**:

1. Read previous version from existing `.claude/kit-version.md` (parse the `**v…**` line). If file
   absent → first install, omit "Changes since" section, write "Initial install" instead.
2. After copying kit files, walk `git tag --sort=-creatordate` between previous and new version.
   For each tag, take the first line of the release commit (`git log -1 --format=%s <tag>`).
3. Write `.claude/kit-version.md` with the format above.

**Files touched**: `kit/scripts/sync.sh` only.

**Acceptance**:

- After `just sync-kit`, `.claude/kit-version.md` exists with the current version and a delta list.
- Subsequent syncs update it correctly (delta is "since last installed", not "since v0").
- First-install path works (no previous file to read).

---

## Phase 2 — sync `kit/kit-tools.md` → `.claude/kit-tools.md`

**Goal**: the existing inventory file lands in downstream so the agent can read it on demand.

**Implementation**:

1. Add `kit/kit-tools.md` → `.claude/kit-tools.md` to the sync set in `kit/scripts/sync.sh`.
2. Verbatim copy. No transformation.
3. Run `/preflight` against `kit/kit-tools.md` — if it flags kit-centric language (e.g. "kit/agents/"),
   rewrite those sections to reference downstream paths (`.claude/agents/`).

**Files touched**: `kit/scripts/sync.sh`, possibly `kit/kit-tools.md`.

**Acceptance**:

- After `just sync-kit`, `.claude/kit-tools.md` exists in downstream and matches `kit/kit-tools.md`.
- `/preflight` on `kit/kit-tools.md` passes with no kit-centric language warnings.

---

## Phase 3 — `/kit-discover` skill (conditional)

**Trigger to build**: ship Phases 1+2 first. Build this only if downstream `CLAUDE.md` is observed
contradicting kit content (e.g., describes a workflow the kit replaced). If sync stays surgical
and `CLAUDE.md` aligns naturally, skip this phase.

**Shape if built**:

- Skill at `kit/skills/kit-discover/SKILL.md`
- Reads: `.claude/kit-tools.md`, `.claude/kit-version.md`, existing `CLAUDE.md`, listing of
  `scripts/`, `.githooks/`, `justfile` recipes
- Cross-references for **drift** (CLAUDE.md describes a workflow now changed by the kit), **gaps**
  (kit ships an agent CLAUDE.md doesn't reference), **redundancies** (CLAUDE.md duplicates kit-owned
  content)
- Outputs a proposed `CLAUDE.md` patch — user reviews, accepts, or skips. Skill never auto-applies.
- `sync.sh` prints "Run /kit-discover to reconcile" at the end of each sync (especially when the
  delta in kit-version.md spans a major version)

**Files touched**: new skill directory, `sync.sh` footer message, possibly a tag-annotation
convention for marking releases as "breaking" so sync knows when to elevate the prompt.

**Acceptance**: scope when phase is triggered.

---

## Open decisions (for tomorrow)

- Skill name if Phase 3 fires: `/kit-discover`, `/kit-onboard`, `/kit-merge`, `/kit-reconcile`. Pick one.
- `kit-version.md` delta format: tag subjects only (cheap, current) vs full changelog excerpts.
  Recommend: tag subjects.
- Should `sync.sh` overwrite `.claude/kit-version.md` unconditionally, or merge if user has annotated
  it locally? Recommend: overwrite unconditionally — it's a kit-managed file, not user content.

---

## Out of scope

- Modifying `CLAUDE.md` automatically. Sync stays passive there.
- Hooking into Claude Code's SessionStart. Too invasive; the model already discovers agents/skills
  via the system list.
- Auto-applying `/kit-discover`'s suggested patch. Always human-gated.

---

## Notes for the executing agent

- Today's session restructured 11 reviewer agents (commit `909f19b`) — unrelated to this plan.
- Today shipped `just check` smart-commit fix and tool-minimality lint (commit `ddf42ae`).
- Current kit version: latest tag in `git tag` (v3.1.2 at time of writing).
- Read `kit/scripts/sync.sh` first to understand the existing sync flow before adding writes.
- Use `Write` (not `Edit`) for `kit-version.md` since each sync overwrites it fully.
