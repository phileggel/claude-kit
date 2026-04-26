# List of TODOs

## add a spec-diff skill to detect when a spec change breaks existing TRIGRAM coverage

A skill that diffs two versions of a spec file (via `git diff`), identifies added/modified/removed TRIGRAM-NNN rules, and outputs a delta report so the developer knows which plan tasks and tests are now stale.

## common.just: format recipe is Tauri-specific in a generic file

The `format` recipe in `kit/common.just` hardcodes `cargo fmt`, `cargo clippy`, and `npm run` —
Tauri-specific commands in a recipe that ships to all profiles. Fix: move `format` to
`kit/justfile/tauri.just` and replace with a no-op stub (or remove) from `common.just`.
Do alongside Phase D (v3.1.0) when tauri.just is already being touched.

## rename repo to claude-kit (post-web-profile)

Once the web profile ships and the kit is genuinely multi-stack, rename the GitHub repo and project from `tauri-claude-kit` to `claude-kit`. GitHub will redirect old clone URLs. Update `CLAUDE.md`, `kit-readme.md`, and any internal references at that time.

## advisor finding

---

Improvement 1 — duplicated git file-discovery preamble across all review agents:
The same 3-command union (git diff HEAD, --cached, porcelain) is copy-pasted in 5+ agents. Extract to
scripts/changed-files.sh so a fix propagates everywhere.
⚠️ Do opportunistically during v3.1.0 when agents are already being edited.
