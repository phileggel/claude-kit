# List of TODOs

## v4.1.0 candidates

- [ ] Refactor `whats-next` skill: move deterministic data collection (TODO files, inline grep, plan/spec parsing, git state, `gh issue/pr list`, roadmap) into `scripts/whats-next.py`; skill keeps only the judgment layer (verify-not-done, score, pick suggested action, save report). Reduces tool-call round-trips, makes the script reusable for dashboards/CI.
- [ ] Rename `adr-manager` skill → `adr-writer` and add a paired `adr-reviewer` agent in `kit/agents/`, matching the writer/reviewer split already used by `spec-writer` ↔ `spec-reviewer`, `contract` ↔ `contract-reviewer`, and `feature-planner` ↔ `plan-reviewer`. Touch points: rename `kit/skills/adr-manager/` → `kit/skills/adr-writer/`, update frontmatter `name:` and headings in `SKILL.md`, update references in `kit/kit-readme.md`, `kit/kit-tools.md`, `kit/skills/spec-writer/SKILL.md`, and `.claude/skills/preflight/SKILL.md`; then add the new `adr-reviewer` agent and list it in `kit/kit-tools.md`.

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`
