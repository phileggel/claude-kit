---
name: start
description: Select the right workflow for the current task and output an actionable working context for the session. Optional scope argument (fix, chore, test, feature, refactor) pre-selects a workflow; user can always switch.
tools: AskUserQuestion
---

# Skill — `start`

Invocation: `/start [fix|chore|test|feature|refactor]`

---

## Step 1 — Determine workflow suggestion from scope

| Scope      | Suggestion                |
| ---------- | ------------------------- |
| `feature`  | A — Full Feature Workflow |
| `refactor` | ask — could go either way |
| `fix`      | B — Simple Workflow       |
| `chore`    | B — Simple Workflow       |
| `test`     | B — Simple Workflow       |
| (none)     | ask                       |

## Step 2 — Ask the user

Use **AskUserQuestion** to collect two things in one call:

**Q1 — Task description**: "What needs to be done?" (one sentence, free text)

**Q2 — Workflow**: show both options; pre-select the suggested one (mark as Recommended if a suggestion exists):

- `A — Full workflow` — new feature, business logic, contract changes, significant refactor
- `B — Simple workflow` — bug fix, chore, tests, maintenance, no new business rules

## Step 3 — Check branch before outputting context

Before outputting anything, run `git branch --show-current` to check the current branch.

- If on `main`: use **AskUserQuestion** to ask for a branch name, then run `git checkout -b {branch}`. Do not proceed until the branch is created.
- If already on a feature branch: proceed.

## Step 4 — Output working context

Output the block below immediately after the branch check. This block is the main agent's session context — it drives the rest of the work.

---

Replace `{task}` with the user's description and `{type}` with the scope argument or "unspecified".

---

### If Workflow A:

```
## Working Context

**Task**: {task}
**Type**: {type}
**Workflow**: A — Full Feature Workflow

### Phase 1 — Spec & Contract & Plan
- [ ] `/spec-writer` → `docs/spec/{domain}.md`
- [ ] `spec-reviewer` → validate spec quality [soft gate — hard if 🔴]
- [ ] `/contract` → `docs/contracts/{domain}-contract.md` [human approves shape]
- [ ] `contract-reviewer` → validate contract vs spec [soft gate — hard if 🔴]
- [ ] `feature-planner` → `docs/plan/{feature}-plan.md`

### Phase 2 — Backend
- [ ] `test-writer-backend` → Rust stubs from contract, confirm red
- [ ] Implement backend (make tests green)
- [ ] `just format`
- [ ] `reviewer-backend` → fix issues
- [ ] `just generate-types` → updates `src/bindings.ts` _(Tauri only)_
- [ ] `/smart-commit`: backend layer [HARD GATE]

### Phase 3 — Frontend
- [ ] `test-writer-frontend` → Vitest stubs from contract, confirm red
- [ ] Implement frontend (make tests green)
- [ ] `just format`
- [ ] `reviewer-frontend` → fix issues (Parts A + B + C)
- [ ] `test-writer-e2e` → E2E stubs from contract, confirm red _(Tauri only — run `/setup-e2e` first if not done)_
- [ ] Make E2E tests green (fix selector gaps per `docs/e2e-rules.md`)
- [ ] `/smart-commit`: frontend + E2E layer [HARD GATE]

### Phase 4 — Review & Closure
- [ ] `reviewer-arch` (always) + `reviewer-sql` (if migrations) + `reviewer-infra` (if any config, script, hook, or workflow file changed)
- [ ] `i18n-checker` (if UI text changed)
- [ ] Update `ARCHITECTURE.md` + `docs/todo.md`
- [ ] `spec-checker` → all rules and contract commands covered
- [ ] `/smart-commit`: tests & docs [HARD GATE]
- [ ] `/create-pr` → push branch and open PR (or merge directly: `git checkout main && git merge --no-ff feat/{name}`)
```

---

### If Workflow B:

```
## Working Context

**Task**: {task}
**Type**: {type}
**Workflow**: B — Simple Technical Workflow

### Steps
- [ ] Analyze: read relevant docs and code
- [ ] Propose plan in chat → wait for user validation
- [ ] Implement changes
- [ ] `just check` (or `just check-full` if tests needed)
- [ ] Run relevant reviewers (`reviewer-arch`, `reviewer-infra`, etc.) as needed
- [ ] Ask user if another task is needed
- [ ] `/smart-commit` [HARD GATE]
- [ ] `/create-pr` → push branch and open PR (or merge directly: `git checkout main && git merge --no-ff fix/{name}`)
```
