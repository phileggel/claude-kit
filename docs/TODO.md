# List of TODOs

## Active issues

- [ ] `kit/scripts/sync.sh`: inline Python heredoc (line ~225) uses `open(path)` without `encoding='utf-8'` — non-blocking but should be fixed for correctness

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`
- [ ] `reviewer-api` generic agent: web-profile contract-to-code traceability (HTTP route verification, equivalent to Tauri's `#[tauri::command]` check)
