# List of TODOs

## v4.1.0 candidates

- [ ] Refactor `whats-next` skill: move deterministic data collection (TODO files, inline grep, plan/spec parsing, git state, `gh issue/pr list`, roadmap) into `scripts/whats-next.py`; skill keeps only the judgment layer (verify-not-done, score, pick suggested action, save report). Reduces tool-call round-trips, makes the script reusable for dashboards/CI.

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`
