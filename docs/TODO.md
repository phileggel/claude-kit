# List of TODOs

## Active issues

- [x] `check-kit.py`: extend `_check_agent_inventory` and `_check_tool_minimality` to cover `kit/agents/web/*.md` (currently hardcoded to `tauri` only; remove `kit/agents/web` from `PLANNED_PROFILE_DIRS`)
- [x] Generic agents: neutralize Tauri-specific fallback paths in `retro-spec.md`, `feature-planner.md`, `spec-checker.md` (fallbacks reference `src-tauri/`); fix `spec-checker.md:76` `#[tauri::command]` hardcode in contract compliance step
- [x] `spec-diff` skill: replace hardcoded `src-tauri/` grep path with multi-path discovery (add `server/` to search list; update example output paths)

## Improvements

- [x] `web.just`: add `format` recipe (currently missing — `just format` breaks for all web-profile projects)
- [x] `web/check.py`: add `cargo clippy` to `--fast` mode (pre-commit parity with Tauri profile)
- [x] `script-reviewer.md:83`: reword Tauri-specific `SQLX_OFFLINE` rule to be stack-neutral

## Experimental

- [ ] Profile-aware agent templating: shared base + profile-specific overrides to reduce ~70–80% duplication between Tauri and web agents
- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`
- [ ] `reviewer-api` generic agent: web-profile contract-to-code traceability (HTTP route verification, equivalent to Tauri's `#[tauri::command]` check)
