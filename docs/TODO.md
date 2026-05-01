# List of TODOs

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`

## Kit quality (from kit-advisor 2026-05-01)

- [ ] Reconcile web/tauri release.py asymmetry: web release.py has no quality gate before tagging; add quality suite run, `--version`/`-y` flags, and main-branch guard to match tauri profile — see `kit/scripts/web/release.py`
- [ ] Web check.py missing vitest step and SQLX_OFFLINE guard: add `npx vitest run` in full mode and `SQLX_OFFLINE=true` to cargo test env — see `kit/scripts/web/check.py` vs tauri equivalent
- [ ] Port RTL integration test step to web test-writer-frontend: added to tauri in commit `f975cb5` but never ported to `kit/agents/web/test-writer-frontend.md`
- [ ] Resolve Write tool on review-only agents: all reviewer agents carry Write solely for report saving, contradicting the Tool Minimality rule in CLAUDE.md — either amend the rule or extract saving to a post-agent hook
