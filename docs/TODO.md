# List of TODOs

## Active issues

- [ ] `kit/scripts/sync.sh`: inline Python heredoc (line ~225) uses `open(path)` without `encoding='utf-8'` — non-blocking but should be fixed for correctness

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`
- [ ] `reviewer-api` generic agent: web-profile contract-to-code traceability (HTTP route verification, equivalent to Tauri's `#[tauri::command]` check)
- [ ] `test-writer-frontend`: analyse and define a component integration test step (RTL, mocking gateway not invoke) to cover component→gateway wiring — needs design before implementation: where to colocate (next to component? separate `*.integration.test.tsx`?), what the selection constraint is (not every gateway test needs an RTL equivalent — what's the right trigger? stateful components only? commands with side effects?), how many tests per component max, and whether this belongs as a step in the existing agent or a separate agent
