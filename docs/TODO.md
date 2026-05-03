# List of TODOs

## ## Bug: tauri reviewer-frontend flags non-command Tauri plugin APIs as gateway violations

**Rule location**: `agents/reviewer-frontend.md`, Part A — Gateway Encapsulation

**Current rule** (lines 44-45):

> No component or hook may call `invoke(...)` or `commands.*` directly — all Tauri command calls
> must go through the feature's `gateway.ts`.
> Flag any direct `invoke` or `commands.*` usage outside a `gateway.ts` file as 🔴 Critical.

**Problem**: The rule is correctly scoped to `invoke`/`commands.*`, but the agent extrapolates it
to cover all `@tauri-apps/plugin-*` imports (e.g. `open()` from `plugin-dialog`, `readFile()` from
`plugin-fs`). This produces false-positive 🔴 Criticals for calls that have no Rust counterpart,
no Specta-generated type, and no reason to be behind a gateway.

**Real-world false positive**: `open()` from `@tauri-apps/plugin-dialog` called inside a hook was
flagged as a gateway violation. The arch reviewer correctly rejected it: the gateway pattern exists
to isolate typed IPC round-trips to Rust commands, not every Tauri plugin API.

**Fix**: Add an explicit carve-out after the critical flag line:

> Tauri plugin APIs that are **not** Rust command invocations (e.g. `open()` from
> `@tauri-apps/plugin-dialog`, `readFile()` from `@tauri-apps/plugin-fs`, `writeFile()`,
> `readTextFile()`) are **not** covered by this rule. They may be called wherever appropriate
> in hooks or components. Only `invoke(...)` and `commands.*` calls require gateway encapsulation.

This keeps the critical rule sharp and prevents the agent from over-extending it to platform-level
OS APIs that carry no domain data and have no testability concern specific to this pattern.

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`

## Kit quality (from kit-advisor 2026-05-01)

- [ ] Reconcile web/tauri release.py asymmetry: web release.py has no quality gate before tagging; add quality suite run, `--version`/`-y` flags, and main-branch guard to match tauri profile — see `kit/scripts/web/release.py`
- [ ] Port RTL integration test step to web test-writer-frontend: added to tauri in commit `f975cb5` but never ported to `kit/agents/web/test-writer-frontend.md`
