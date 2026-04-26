# List of TODOs

## add a spec-diff skill to detect when a spec change breaks existing TRIGRAM coverage

A skill that diffs two versions of a spec file (via `git diff`), identifies added/modified/removed TRIGRAM-NNN rules, and outputs a delta report so the developer knows which plan tasks and tests are now stale.

## common.just: format recipe is Tauri-specific in a generic file

The `format` recipe in `kit/common.just` hardcodes `cargo fmt`, `cargo clippy`, and `npm run` —
Tauri-specific commands in a recipe that ships to all profiles. Fix: move `format` to
`kit/justfile/tauri.just` and replace with a no-op stub (or remove) from `common.just`.
Do alongside Phase D (v3.1.0) when tauri.just is already being touched.

## rename repo to claude-kit (post-web-profile)

Once the web profile ships and the kit is genuinely multi-stack, rename the GitHub repo and project from `tauri-claude-kit` to `claude-kit`. GitHub will redirect old clone URLs. Update `CLAUDE.md`, `kit-readme.md`, and any internal references at that time.

## check-kit.py: tool-minimality lint for review agents

Add a check that reads each agent's frontmatter `tools:` field and enforces:

- Review/checker/validator agents must not have `Edit` (unconditional)
- `Write` is allowed only if the agent has a `## Save report` section (saves to `tmp/` only)
- `test-writer-*` agents must have `Edit` and `Write`

Agents can't invoke skills mid-run, so `Write` must stay in review agents for save-report.
The lint makes the constraint explicit and catches future tool-list mistakes at release time.

## smart-commit: use `just check` instead of hardcoded `scripts/check.py`

The `/smart-commit` skill hardcodes `python3 scripts/check.py` as its quality gate. For generic-only
projects (no profile), `scripts/check.py` doesn't exist. Fix: use `just check` instead — the recipe
already guards on file existence and shows a clear error message if check.py is absent.

## release.py (downstream tauri): remove --no-verify from git push

`kit/scripts/tauri/release.py` uses `--no-verify` on `git push`, bypassing the pre-push hook.
Contradicts CLAUDE.md's "never skip hooks" rule. Fix: remove `--no-verify` and let the hook run.
If the pre-push hook is too slow for releases, add a `--skip-push-hook` flag with explicit opt-in.

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
