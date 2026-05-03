# List of TODOs

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`

## Kit quality (from kit-advisor 2026-05-01)

- [ ] Reconcile web/tauri release.py asymmetry: web release.py has no quality gate before tagging; add quality suite run, `--version`/`-y` flags, and main-branch guard to match tauri profile — see `kit/scripts/web/release.py`
- [ ] Port RTL integration test step to web test-writer-frontend: added to tauri in commit `f975cb5` but never ported to `kit/agents/web/test-writer-frontend.md`
