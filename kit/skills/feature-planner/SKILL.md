---
name: feature-planner
description: Translates a validated spec into an implementation plan (docs/plan/{feature}-plan.md) mapping TRIGRAM-NNN rules to DDD layers and the kit workflow. Use after `spec-reviewer` and `contract-reviewer` approve. Output is gated by `plan-reviewer` before any test-writer runs. Not for spec or contract authoring — use `/spec-writer` or `/contract` instead.
tools: Read, Write, Grep, Glob, AskUserQuestion
model: opus
---

# Skill — `feature-planner`

Invocation: `/feature-planner`

Maps TRIGRAM-NNN rules from a validated spec onto concrete DDD layer tasks, under ADR constraints, producing an executable plan that downstream test-writers and implementers can follow without re-reading the spec.

---

## Required tools

`Read`, `Write`, `Grep`, `Glob`, `AskUserQuestion`. Interactive — Step 6 asks the user how to slice the merge into PRs.

---

## When to use

- **Phase 1 of Workflow A** — after `spec-reviewer` and `contract-reviewer` both green-light their artifacts
- **When the spec has at least one TRIGRAM-NNN rule** — a spec with no rules is incomplete; redirect the user to `/spec-writer` first
- **When introducing a new feature** — produces the first plan for `docs/plan/{feature}-plan.md`

---

## When NOT to use

- **Authoring the spec** — use `/spec-writer`; the plan is derived from a validated spec
- **Authoring the contract** — use `/contract`; the plan consumes the contract
- **Validating the plan** — use the `plan-reviewer` agent
- **Implementing the plan** — use `test-writer-*` agents to write failing tests first; the main agent then implements against them

---

## Critical Rules

1. **Path Verification**: Every file path must be verified with `Glob` before being included — never invent paths.
2. **Synchronization**: Include `just generate-types` as a mandatory step between Backend and Frontend tasks — Specta regenerates `src/bindings.ts` from the Tauri command surface.
3. **No Code Implementation**: Your output is a plan describing _what_ to do and _where_, not the actual code.
4. **Task Tracking**: Ensure the main agent can progressively update the checkboxes in this file during the implementation phase.
5. **Commit Checkpoints**: Every plan must include at least one commit checkpoint per thematic phase (backend, frontend, E2E tests, tests & docs). Each checkpoint provides only a suggested conventional commit title; `/smart-commit` validates, formats, and emits the actual commit.
6. **Minimal implementation**: Implementation tasks must state "implement only what makes failing tests pass — no defensive code, no anticipation of future rules." `test-writer-backend` and `test-writer-frontend` define the scope; the implementation must not exceed it.
7. **Next gate**: After writing the plan, tell the user that `plan-reviewer` is the mandatory next step before any test-writer subagent runs. Do not invoke it yourself; the orchestrating agent runs it.

---

## Execution Steps

### 1. Knowledge Extraction & ADR Analysis

If the feature name or spec path is ambiguous, ask the user via `AskUserQuestion` before reading.

Read the spec doc (e.g., `docs/spec/asset-pricing.md`) and identify:

- All **TRIGRAM-NNN rules** (e.g. REF-010, REF-020, PAY-030), their scope (frontend / backend / both), and descriptions.
- The declared trigram and its registration in `docs/spec-index.md` (mandatory per spec-writer Step 2.5).
- Entities and UI components to be created or modified.
- Cross-context dependencies.
- **CRITICAL**: Read `docs/adr/` to identify technical constraints (e.g., ADR-001 for currency types, ADR-002 for soft-delete) that MUST dictate the implementation details. Record which ADRs apply to this feature — the **Setup** section of the deliverable's TaskList lists them so the implementer re-reads them before coding. Skip silently if `docs/adr/` is absent (new projects may not have any yet).

_If the spec contains no TRIGRAM-NNN rules, report it and ask the user to complete it via `/spec-writer` before proceeding._

### 2. Architectural Contextualization

Read the following to ensure compliance (skip silently if a file is absent). Record which ones were present and which apply to this feature's scope — the **Setup** section of the deliverable's TaskList must list the exact subset the implementer needs to re-read.

- `ARCHITECTURE.md`: Bounded contexts, module layout, data flow, naming conventions.
- `docs/backend-rules.md`: Factory methods, service layer, repository traits. _(BE-relevant)_
- `docs/frontend-rules.md`: Gateway, hook, component patterns, colocated tests. _(FE-relevant)_
- `docs/ddd-reference.md`: DDD glossary + error-flow guidance. _(BE-relevant, especially for new BCs)_
- `docs/error-model.md`: Typed-error contract. _(BE-relevant, especially for command surfaces)_
- `docs/i18n-rules.md`: Translation conventions. _(FE-relevant)_
- `docs/test_convention.md`: Testing conventions (inline `#[cfg(test)]` for Rust, colocated `.test.ts` for the frontend). _(always)_
- `docs/contracts/{domain}-contract.md`: if present, treat as mandatory — its commands anchor the `test-writer-*` tasks in the plan. Derive the domain name from the spec's Context section. Frontend-only or backend-internal-only features have no contract per `/contract`; in that case, proceed without one.

### 3. Path Verification

Verify every path the plan will reference exists, using `Glob` or `Grep`. If `ARCHITECTURE.md` (read in Step 2) named specific roots, validate them; otherwise fall back to common roots (`src/`, `server/src/`, `src-tauri/src/` for backend; `src/features/`, `client/src/` for frontend) and note the assumption in the plan.

### 4. Mapping & Dependency Graph

For each TRIGRAM-NNN rule, identify concrete tasks:

- Determine if it requires a creation or a modification.
- Map which layer(s) are affected.
- **ADR Application**: Explicitly mention ADR constraints in the tasks (e.g., "Implement amount using i64 as per ADR-001").
- Define dependencies (e.g., Backend logic -> `just generate-types` -> Frontend gateway).
- **Commit phases**: identify thematic boundaries where a `/smart-commit` is appropriate. Suggest a conventional commit title for each (e.g., `feat(asset): implement pricing backend`).
- **Schema changes**: identify rules that imply a database schema change (new entity, new field, new status column, new FK). For each, note the expected migration filename (`{timestamp}_create_{table}.sql` or `{timestamp}_add_{column}_to_{table}.sql`) and infer the columns from the domain rules. Flag that `just prepare-sqlx` must be run after migrating.

### 5. Modified-function coverage

For each rule scoped to `frontend` or `frontend + backend` that **modifies an existing function** (not a new file/creation):

- Mark the rule `[unit-test-needed]` in the Rules Coverage table.
- Collect the affected functions as a `modified_functions` list `[<file>:<function>]` (e.g. `[useEditFoo.ts:recomputeUnitPrice]`), attached to the `test-writer-frontend` checkpoint in the Workflow TaskList so the test-writer receives it alongside the contract.

Example trigger: rule REF-040 says _"when discount changes, recompute `unit_price`"_ — this modifies `useEditRefund.ts:applyDiscount`, so REF-040 gets `[unit-test-needed]` and `useEditRefund.ts:applyDiscount` joins the `modified_functions` list. These rules have no contract entry and would otherwise receive no test coverage.

### 6. PR Plan

From the tasks identified in Step 4, estimate the change size per layer. Heuristic: count target file paths from Step 4's Mapping, then multiply by ~30 LOC per new file (less for modifications to existing files). The estimate is advisory — it pre-selects the recommended slicing but the user picks. Then ask via `AskUserQuestion`:

- **1 PR** — single merge covering all layers. Recommended for small or tightly-coupled features (rename, contract reshape, migration that demands both layers in lockstep).
- **2 PRs** — backend (spec + migration + Rust + bindings) merges first; frontend + E2E + closure follow on a branch rebased off `main` after the BE PR merges.
- **3 PRs** — backend; then frontend (gateway / hooks / components / i18n); then E2E + ARCHITECTURE/todo/spec-checker closure. Each PR branches off the prior one once merged.

Pre-select based on the estimate: if **either layer exceeds ~20 files OR ~500 LOC**, recommend 2 PRs (or 3 if E2E adds significant volume); otherwise recommend 1 PR. The estimate is advisory — the user picks; coupling judgment trumps the threshold.

Surface the estimate explicitly in the question (e.g. "BE: ~14 files / ~380 LOC; FE: ~9 files / ~210 LOC"). Capture the answer verbatim in the deliverable's **PR Plan** section.

---

## Output format

You MUST generate and **WRITE** `docs/plan/{feature}-plan.md` with the following sections:

### 1. Workflow TaskList (Derived from CLAUDE.md)

A synthetic checklist for mandatory quality and process steps, grouped by phase. Skip an entire phase if its top-level condition does not apply.

**Setup** _(planner fills in exact paths per this feature — Steps 1 + 2 produce the lists)_

- [ ] 📖 Read spec: `docs/spec/{feature}.md`
- [ ] 📖 Read contract: `docs/contracts/{domain}-contract.md` — _omit if frontend-only or backend-internal-only (no contract)_
- [ ] 📖 Read constraining ADRs: list per this feature (e.g. `docs/adr/001-currency-types.md`) — _omit if none apply_
- [ ] 📖 Read conventions: `ARCHITECTURE.md` + per-scope subset (e.g. `docs/backend-rules.md`, `docs/error-model.md`, `docs/ddd-reference.md` for BE; `docs/frontend-rules.md`, `docs/i18n-rules.md` for FE; `docs/test_convention.md` always)

**Backend phase** _(skip if no backend rules)_

- [ ] 🗄️ Database Migration (`just migrate` + `just prepare-sqlx`) — if schema changes required
- [ ] ✍️ Backend test stubs (`test-writer-backend` — all stubs written, red confirmed)
- [ ] 🏗️ Backend Implementation (minimal — make failing tests pass, green confirmed)
- [ ] 🔍 Backend Review (`reviewer-backend` + `reviewer-arch` + `reviewer-sql` if migrations — all in parallel → `/review-triage` → apply Follow-ups)
- [ ] 🔗 Type Synchronization (`just generate-types`)
- [ ] 🔧 Run `npx tsc --noEmit` → fix TS errors from new bindings only (no UI work)
- [ ] 🧹 `just format` (rustfmt + clippy --fix)
- [ ] 💾 Commit: backend layer via `/smart-commit` (suggested title from plan)
- [ ] 🔀 `/create-pr` — if the PR Plan slices BE into its own PR; otherwise continue. After merge, branch the next phase off updated `main`.

**Frontend phase** _(skip if no frontend rules)_

- [ ] ✍️ Frontend test stubs (`test-writer-frontend` — all stubs written, red confirmed; pass `modified_functions` list if any `[unit-test-needed]` rules are present)
- [ ] 💻 Frontend Implementation (minimal — make failing tests pass, green confirmed)
- [ ] 📸 Visual proof (`/visual-proof` — capture final state; stage screenshots before commit) — if .tsx/.css changed
- [ ] 🔍 Frontend Review (`reviewer-frontend` → `/review-triage` → apply Follow-ups)
- [ ] 🧹 `just format`
- [ ] 💾 Commit: frontend layer via `/smart-commit` (suggested title from plan)
- [ ] 🔀 `/create-pr` — if the PR Plan slices FE into its own PR; otherwise continue. After merge, branch the next phase off updated `main`.

**Closure** _(always)_

- [ ] ✍️ E2E scenarios (`test-writer-e2e` — produces pyramid-friendly scenarios; run `/setup-e2e` first if not done) — if E2E coverage applies
- [ ] ▶️ Run E2E suite (`npm run test:e2e` → green confirmed; main agent triages any failure) — if E2E coverage applies
- [ ] 🔍 Cross-cutting Review (`reviewer-e2e` if E2E test files modified + `reviewer-infra` if config/script/hook/workflow files changed + `reviewer-security` if Tauri command/capability/sensitive file modified — all in parallel → `/review-triage` → apply Follow-ups)
- [ ] 📚 Documentation Update (`docs/todo.md` — close shipped entries; `ARCHITECTURE.md` only if a new module/path or layer pattern was introduced)
- [ ] ✅ Spec check (`spec-checker`) [HARD GATE — halt on any uncovered rule or command]
- [ ] 🧹 `just format`
- [ ] 💾 Commit: closure via `/smart-commit` (suggested title from plan)
- [ ] 🔀 `/create-pr` — final PR per the PR Plan (or merge directly: `git checkout main && git merge --no-ff feat/{name}`)

### 2. Detailed Implementation Plan

A granular breakdown by architectural layer:

- **Migrations** (if any): List each migration file with its suggested filename, inferred columns, and a reminder to run `just migrate` then `just prepare-sqlx` before writing backend code. Omit this section if no schema changes are required.
- **Backend**: Exact file paths, struct names, factory methods (follow project conventions from `docs/backend-rules.md`), service methods, and command handlers.
- **Frontend**: Exact file paths, gateway methods, custom hooks, and frontend components.
- **Rules Coverage**: see table below.

#### Rules Coverage

A table mapping every TRIGRAM-NNN rule to its corresponding implementation task. Example rows:

| Rule    | Layer    | Task                                | Notes                |
| ------- | -------- | ----------------------------------- | -------------------- |
| REF-010 | backend  | `RefundService::record_overpayment` | ADR-001 (i64)        |
| REF-040 | frontend | `useEditRefund.ts:applyDiscount`    | `[unit-test-needed]` |

### 3. PR Plan

Captures the answer from Step 6. Format:

- **Strategy**: `1 PR` | `2 PRs` | `3 PRs`
- **Estimate**: per-layer file count and LOC used to pre-select.
- **PR list** — for each planned PR:
  - **Title** (conventional commit format, e.g. `feat(asset): pricing backend`)
  - **Scope**: which layer(s) and which Workflow TaskList checkpoints terminate it
  - **Dependency**: what must be merged first (e.g. "rebase off main after PR #1 merges")
  - **Branch suffix** (suggestion): `feat/{name}-be`, `feat/{name}-fe`, `feat/{name}-e2e` for multi-PR strategies; `feat/{name}` for single-PR

`/start` reads this section to decide where to emit `/create-pr` checkpoints in the working context.
