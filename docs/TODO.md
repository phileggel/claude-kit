# List of TODOs

## New features

- [ ] `/create-pr` skill: standalone skill that checks you're on a feature branch, pushes if needed, generates PR title + description from branch commits and plan doc, then calls `gh pr create` with user confirmation before push

## Cleanup

- [ ] Remove `spec-diff` skill — no identified use case; remove `kit/skills/spec-diff/`, its entry in `kit/kit-tools.md`, and any references in agent descriptions

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`
- [ ] `reviewer-api` generic agent: web-profile contract-to-code traceability (HTTP route verification, equivalent to Tauri's `#[tauri::command]` check)
- [ ] `test-writer-frontend`: analyse and define a component integration test step (RTL, mocking gateway not invoke) to cover component→gateway wiring — needs design before implementation: where to colocate (next to component? separate `*.integration.test.tsx`?), what the selection constraint is (not every gateway test needs an RTL equivalent — what's the right trigger? stateful components only? commands with side effects?), how many tests per component max, and whether this belongs as a step in the existing agent or a separate agent
