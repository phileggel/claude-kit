# List of TODOs

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`
- [ ] `reviewer-api` generic agent: web-profile contract-to-code traceability (HTTP route verification, equivalent to Tauri's `#[tauri::command]` check)
- [ ] E2E Tauri tests: design a `test-writer-e2e` agent using Tauri WebDriver + Playwright against the full running app (real IPC, no mocking) — separate concern from RTL component tests, covers the full command→UI and UI→command stack
