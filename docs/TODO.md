# List of TODOs

## add a spec-diff skill to detect when a spec change breaks existing TRIGRAM coverage

A skill that diffs two versions of a spec file (via `git diff`), identifies added/modified/removed TRIGRAM-NNN rules, and outputs a delta report so the developer knows which plan tasks and tests are now stale.

## just format is too verbose.

## advisor finding

---

Active issue (fix now):
kit/scripts/release.py lines 385–401 have French log strings. The kit's own reviewer would flag this. Easy fix.

---

Improvement 1 — commit-msg hook vs BREAKING CHANGE:
The 5-line body limit rejects valid feat!: commits with a BREAKING CHANGE: footer. Either exempt BREAKING CHANGE:
lines from the count, or raise the limit to 8–10. smart-commit hardcodes the same 5-line rule — both need updating
together.

Improvement 2 — missing generate-types recipe in common.just:
feature-planner mandates just generate-types between backend and frontend, but the recipe doesn't exist in
common.just. First time someone follows a plan literally, it crashes.

Improvement 3 — duplicated git file-discovery preamble across all review agents:
The same 3-command union (git diff HEAD, --cached, porcelain) is copy-pasted in 5+ agents. Extract to
scripts/changed-files.sh so a fix propagates everywhere.
