# List of TODOs

## add a spec-diff skill to detect when a spec change breaks existing TRIGRAM coverage

A skill that diffs two versions of a spec file (via `git diff`), identifies added/modified/removed TRIGRAM-NNN rules, and outputs a delta report so the developer knows which plan tasks and tests are now stale.

## rename repo to claude-kit (post-web-profile)

Once the web profile ships and the kit is genuinely multi-stack, rename the GitHub repo and project from `tauri-claude-kit` to `claude-kit`. GitHub will redirect old clone URLs. Update `CLAUDE.md`, `kit-readme.md`, and any internal references at that time.

## advisor finding

---

Improvement 2 — `/review-pipeline` skill (experimental):
A skill that reads git diff, determines which Phase 4 reviewers are triggered (same logic as
workflow-validator step 3), runs each as a subagent, and outputs a unified pass/fail summary.
Reduces Phase 4 from 5-7 manual invocations to one. Risk: context window limits on large diffs.

---

Improvement 3 — downstream drift detector (experimental):
At sync time, store checksums of synced files in `.claude-kit-checksums`. A `--drift` flag on the
downstream check script compares current files against stored checksums and warns on accidental edits.
Prevents kit-managed files from being silently overwritten on the next sync.

---

Improvement 4 — contract-as-code YAML sidecar (experimental):
`/contract` skill emits both `{domain}-contract.md` (human-readable) and `{domain}-contract.yaml`
(machine-readable). Agents read YAML for reliable type extraction instead of parsing markdown tables.
Enables future tooling: auto-generated gateway stubs, Rust command signatures, OpenAPI-like docs.
