# List of TODOs

## add a spec-diff skill to detect when a spec change breaks existing TRIGRAM coverage

A skill that diffs two versions of a spec file (via `git diff`), identifies added/modified/removed TRIGRAM-NNN rules, and outputs a delta report so the developer knows which plan tasks and tests are now stale.

## release-kit.py: false positive breaking change detection

`scripts/release-kit.py` checks `"BREAKING CHANGE" in message` on the commit subject line.
A commit like `fix(commit-msg): exempt BREAKING CHANGE footer from body line limit` falsely
triggers a major bump. Fix: only treat `!` bang in title as breaking; drop the subject-line
string check (body footers can't be detected with `--pretty=format:%s` anyway).

## advisor finding

---

Improvement 1 — duplicated git file-discovery preamble across all review agents:
The same 3-command union (git diff HEAD, --cached, porcelain) is copy-pasted in 5+ agents. Extract to
scripts/changed-files.sh so a fix propagates everywhere.
⚠️ Do opportunistically during Phase A (v3.0.0) when all agents are already being edited.
