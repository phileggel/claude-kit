# List of TODOs

## kit discovery & version awareness for downstream projects

Make the kit fluid for downstream agents: a sync-managed `.claude/kit-version.md` with version and
delta since last sync, a synced `.claude/kit-tools.md` inventory, and conditionally a `/kit-discover`
skill for `CLAUDE.md` reconciliation. **See `docs/plan-kit-discovery.md` for the full plan** —
phased, scoped, with acceptance criteria.

## add a spec-diff skill to detect when a spec change breaks existing TRIGRAM coverage

A skill that diffs two versions of a spec file (via `git diff`), identifies added/modified/removed TRIGRAM-NNN rules, and outputs a delta report so the developer knows which plan tasks and tests are now stale.

## check-kit.py: lint for end-marker drift in reviewer agents

Add a lint that fails if any review agent's `## Output format` section ends with a natural-conclusion
line outside a code block (e.g. `Review complete: …`, `i18n check: …`, `Result: …`). These end-markers
caused the save-drift bug fixed in commit 909f19b — the model treated the summary line as task
completion and skipped the `## Save report` tool calls. Summary lines now live only inside the saved
compact summary; the lint prevents regression if someone re-introduces the old pattern.

## rename repo to claude-kit (post-web-profile)

Once the web profile ships and the kit is genuinely multi-stack, rename the GitHub repo and project from `tauri-claude-kit` to `claude-kit`. GitHub will redirect old clone URLs. Update `CLAUDE.md`, `kit-readme.md`, and any internal references at that time.

## web profile: resolve "planned" state

`kit/agents/web/` directory doesn't exist but is referenced in 4 places as "planned".
Either: (a) create the directory with a `.gitkeep` so sync infrastructure is tested end-to-end,
or (b) remove all "planned" references until web profile work actually begins (cleaner).
Decide when Muvimu2 exits POC.

## advisor finding

---

Improvement 1 — duplicated git file-discovery preamble across all review agents:
The same 3-command union (git diff HEAD, --cached, porcelain) is copy-pasted in 5+ agents. Extract to
scripts/changed-files.sh so a fix propagates everywhere.
⚠️ Do opportunistically during v3.1.0 when agents are already being edited.

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
