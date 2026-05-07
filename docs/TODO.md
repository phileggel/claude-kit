# List of TODOs

## Pending release

- [ ] Cut **v4.0.0** — 3 unpushed commits on `main` since v3.21.0 (1 breaking via `BREAKING CHANGE:` footer, plus `refactor` and `docs`). Validated by `/preflight`; `release-kit` dry-run confirms `v4.0.0` bump. Run `just release -y` when ready.

## v4.1.0 candidates

- [ ] Refactor `whats-next` skill: move deterministic data collection (TODO files, inline grep, plan/spec parsing, git state, `gh issue/pr list`, roadmap) into `scripts/whats-next.py`; skill keeps only the judgment layer (verify-not-done, score, pick suggested action, save report). Reduces tool-call round-trips, makes the script reusable for dashboards/CI.
- [ ] Improve DDD doc with error-handling guidance: extend `kit/docs/ddd-reference.md` (or add a sibling `kit/docs/ddd-errors.md`) covering the three error categories (domain / application / infrastructure), scoping rule, travel rule, flow toward the UI, principles, application-boundary contract, and an illustrative Rust shape. Draft already written to `docs/draft-ddd-errors.md` — review, decide on placement (extend vs sibling), then move into `kit/docs/` and update `kit/kit-tools.md` Convention Docs table accordingly.
- [ ] Rename `adr-manager` skill → `adr-writer` and add a paired `adr-reviewer` agent in `kit/agents/`, matching the writer/reviewer split already used by `spec-writer` ↔ `spec-reviewer`, `contract` ↔ `contract-reviewer`, and `feature-planner` ↔ `plan-reviewer`. Touch points: rename `kit/skills/adr-manager/` → `kit/skills/adr-writer/`, update frontmatter `name:` and headings in `SKILL.md`, update references in `kit/kit-readme.md`, `kit/kit-tools.md`, `kit/skills/spec-writer/SKILL.md`, and `.claude/skills/preflight/SKILL.md`; then add the new `adr-reviewer` agent and list it in `kit/kit-tools.md`.

## Experimental

- [ ] Post-sync validator: `validate-sync.sh` that verifies all expected agents/scripts/hooks landed after `just sync-kit`
