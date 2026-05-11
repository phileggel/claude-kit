# Svelte branch — operating manual

This document is shipped only on `svelte-main` and its derivatives. It explains how downstream projects interact with the Svelte fork of the kit, and how the React lineage on `main` continues unchanged.

---

## 1. The framework flag

The Svelte branch's `sync.sh` reads `.claude/kit.config.json` at the downstream project root:

```json
{
  "framework": "svelte"
}
```

Recognised values: `"react"` (default) and `"svelte"`.

**Behaviour:**

- `"react"` (or file absent) — only base files are synced. `*-svelte.md` variants are skipped entirely.
- `"svelte"` — `*-svelte.md` files take precedence over their base counterparts: at copy time the `-svelte` suffix is stripped from both the filename and the frontmatter `name:` field, so downstream sees one canonical agent/doc per role (e.g. `reviewer-frontend.md` with Svelte content).

Cross-references between agents are unaffected because every consumer sees the canonical (suffix-stripped) names.

---

## 2. Kick-start a new Svelte project

Bootstrap from a fresh Tauri 2 + Svelte template (`create-tauri-app`, choose the Svelte preset), then:

```bash
# 1. Declare the framework BEFORE the first sync.
mkdir -p .claude
cat > .claude/kit.config.json <<'JSON'
{ "framework": "svelte" }
JSON

# 2. Bootstrap the kit from a Svelte tag.
#    The first sync MUST pass the tag explicitly because the local
#    sync-config.sh is not yet framework-aware. After this run, the bootstrap
#    self-updates and subsequent syncs can omit the version.
curl -fsSL https://raw.githubusercontent.com/phileggel/claude-kit/svelte-main/sync-config.sh \
  | bash -s -- svelte-v0.1.0+4.5.1
```

After the sync:

- `.claude/agents/` contains `reviewer-frontend`, `test-writer-frontend`, `test-writer-e2e`, `reviewer-security` — all sourced from their `-svelte` variants but exposed under canonical names.
- `docs/` contains `frontend-rules.md`, `e2e-rules.md`, `test_convention.md`, `frontend-visual-proof.md` — sourced from `-svelte` variants.
- All shared assets (backend agents, scripts, hooks, common.just) are identical to a React install.

Verify with `bash scripts/validate-sync.sh` and run `/kit-discover` to seed your project's `CLAUDE.md`.

---

## 3. Migrating an existing React project to Svelte

This is a one-off operation for projects with a real Svelte rewrite in progress (e.g. **SpaceTycoon**). The kit-side change is purely the sync; the application-level rewrite (components, dependencies, build config) is out of scope here.

```bash
# 1. Set the framework flag.
mkdir -p .claude
echo '{ "framework": "svelte" }' > .claude/kit.config.json

# 2. Re-run sync from a Svelte tag, with -f to refresh convention docs.
./scripts/sync-config.sh svelte-v0.1.1+4.5.2 -f
```

**Why `-f` matters here.** `.claude/agents/` and `.claude/skills/` are always overwritten by the sync (the kit owns them). `docs/` is copy-once: on a regular sync the kit only writes a doc when the destination is missing, identical, or you explicitly approve a y/N prompt. On a framework switch, the React versions of `frontend-rules.md`, `test_convention.md`, `e2e-rules.md`, and `frontend-visual-proof.md` already exist on disk from your previous React sync — and they differ from the Svelte versions the kit now ships. Without `-f`:

- With a TTY: you get a y/N prompt for each drifted doc — workable but tedious.
- Without a TTY (some `just`-wrappers, multiplexers, CI): the prompts are silently skipped and your `docs/` stays React-flavored. The agents will then audit Svelte code against React conventions, producing confusing reports.

`-f` skips both prompt and skip path: the sync overwrites every drifted doc unconditionally. Use it exactly once, at framework-switch time. Subsequent syncs in the same framework return to the safe copy-once default.

After the sync, existing project files (your components, your contracts, your tests) are untouched — only kit-owned files change. Review `git diff` before committing. The application migration (Svelte components, dependencies, build config) is project-specific and not framed by the kit.

---

## 4. Recurring sync workflow for established Svelte projects

Once a project has `.claude/kit.config.json` set to `{"framework":"svelte"}` and has been synced at least once from a Svelte tag, the bootstrap auto-selects the latest matching tag. **Subsequent syncs need no version argument**:

```bash
./scripts/sync-config.sh
```

The bootstrap reads the framework flag and filters `git ls-remote --tags` to `svelte-v*` only — React tags are never selected for a Svelte project, and vice versa.

To pin a specific Svelte version (e.g. for reproducible builds or rollback), pass it explicitly:

```bash
./scripts/sync-config.sh svelte-v0.2.0+4.6.0
```

The version suffix `+4.6.0` declares which `main` (React) baseline the Svelte tag was cut against. Downstream projects do not need to act on this — it is provenance metadata for the kit maintainer's cherry-pick discipline (see the `/svelte-update` skill in the kit, kit-internal).

Listing available Svelte tags:

```bash
git ls-remote --tags https://github.com/phileggel/claude-kit.git | grep svelte-v
```

---

## 5. React projects continue unchanged

The React lineage on `main` is untouched by anything in this document.

- Existing React downstream projects (no `.claude/kit.config.json`, or `{"framework": "react"}`) continue to sync from `vX.Y.Z` tags on `main` exactly as before.
- The `sync.sh` on `main` does not read the framework flag (the flag is a Svelte-branch addition); React projects effectively see the legacy behaviour.
- If a React project sets `framework: "svelte"` in its config but syncs from a React tag, the flag is silently ignored — the older `sync.sh` does not know about it. No corruption, just no-op.

In short: nothing migrates by accident. The framework flag is opt-in and only active when paired with a Svelte tag sync.

---

## Compatibility matrix

| Downstream config             | Sync tag      | Result                                                        |
| ----------------------------- | ------------- | ------------------------------------------------------------- |
| absent or `{framework:react}` | `vX.Y.Z`      | React kit (legacy, unchanged)                                 |
| absent or `{framework:react}` | `svelte-vX+Y` | React kit even though tag is Svelte — base files only         |
| `{framework:svelte}`          | `vX.Y.Z`      | React kit (flag has no effect — old sync.sh ignores it)       |
| `{framework:svelte}`          | `svelte-vX+Y` | **Svelte kit** — `-svelte` variants override, suffix stripped |

The last row is the only configuration that produces a Svelte install. The flag and the tag must match.
