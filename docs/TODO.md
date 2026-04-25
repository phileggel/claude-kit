# List of TODOs

## add a spec-diff skill to detect when a spec change breaks existing TRIGRAM coverage

A skill that diffs two versions of a spec file (via `git diff`), identifies added/modified/removed TRIGRAM-NNN rules, and outputs a delta report so the developer knows which plan tasks and tests are now stale.

## advisor finding

---

Improvement 1 — duplicated git file-discovery preamble across all review agents:
The same 3-command union (git diff HEAD, --cached, porcelain) is copy-pasted in 5+ agents. Extract to
scripts/changed-files.sh so a fix propagates everywhere.
⚠️ Do opportunistically during Phase A (v3.0.0) when all agents are already being edited.
