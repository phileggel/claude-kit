# Plan — TDD-Oriented Workflow

Introduces contract-first, test-driven development into the Full Feature Workflow (Option A).
Designed from the design conversation of 2026-04-24.

---

## Design Decisions (non-negotiable)

- **Contract is domain-scoped** (`docs/contracts/{domain}.md`) — multiple specs contribute to
  the same file via upsert. Produced by `/contract` skill after spec-reviewer approves.
- **Two gate types**: hard (MUST wait for user — `/smart-commit` only) and soft (MAY review,
  auto-proceed if no criticals).
- **Test-first, not TDD-loop** — `test-writer-*` agents write all stubs for the contract and
  verify red. Implementation is a separate step by the main agent. This is honest about how
  AI agents work: the verification (Bash runs) is the valuable constraint, not a one-at-a-time
  iteration discipline.
- **Minimal implementation** — the implementation step produces only what makes the failing
  tests pass. No anticipation of future rules.
- **Refactor = automated + reviewer per layer** — `just format` (rustfmt + clippy --fix) handles
  automated cleanup. `reviewer-backend` / `reviewer-frontend` run before each layer commit —
  their findings drive manual fixes. This replaces a separate refactor agent.
- **Reviewer split per layer** — `reviewer-backend` runs before the backend commit;
  `reviewer-frontend` before the frontend commit. The cross-cutting `reviewer` runs once at the
  end. This catches architectural issues early, before the other layer is built on top.
- **`just generate-types` compilation fixup** — after type sync, agent fixes TypeScript errors
  from new bindings only (no UI work), then commits. Frontend tests start with clean bindings.
- **Frontend tests = Vitest only** — no Playwright. Mock `@tauri-apps/api/core`. Fast red
  confirmation cycle.
- **Stitch removed entirely** — textual UX Draft in spec is sufficient.

---

## Revised Option A Workflow (after this plan)

```
Phase 1 — Pre-implementation
  1. /spec-writer           → docs/spec/{feature}.md          [soft gate]
  2. spec-reviewer          → validate + contractability       [soft gate — hard if 🔴]
  3. /contract              → docs/contracts/{domain}.md       [soft gate: human approves shape]
  4. contract-reviewer      → validate contract vs spec        [soft gate — hard if 🔴]
  5. feature-planner        → docs/plan/{feature}-plan.md     [auto]

Phase 2 — Backend layer
  5. test-writer-backend    → all stubs from contract          [auto]
                               cargo test → red confirmed
  6. Implement backend      → minimal, make tests pass         [auto]
                               cargo test → green confirmed
  7. just format            → rustfmt + clippy --fix           [auto]
  8. reviewer-backend       → quality review → fix             [auto]
  9. just generate-types    → src/bindings.ts updated          [auto]
  10. Compilation fixup     → TypeScript errors only, no UI   [auto]
  11. just check            → TypeScript clean                 [auto]
  12. /smart-commit         backend layer                      [HARD GATE]

Phase 3 — Frontend layer
  13. test-writer-frontend  → all stubs from contract          [auto]
                               vitest run → red confirmed
                               reads fresh src/bindings.ts
  14. Implement frontend    → minimal, make tests pass         [auto]
                               vitest run → green confirmed
  15. just format           → automated cleanup                [auto]
  16. reviewer-frontend     → quality review → fix             [auto]
  17. /smart-commit         frontend layer                     [HARD GATE]

Phase 4 — Review & Closure
  18. reviewer              → cross-cutting DDD review         [auto]
  19. i18n-checker          → if UI text changed               [conditional]
  20. script-reviewer       → if scripts/hooks modified        [conditional]
  21. spec-checker          → rule coverage + contract check   [auto]
  22. Documentation update                                     [auto]
  23. /smart-commit         docs & tests                       [HARD GATE]
  24. workflow-validator    → final sign-off                   [auto]
```

---

## Implementation Checklist

### Phase A — Prerequisite fix

- [ ] **A1** — `kit/common.just`: add `generate-types` recipe
  - Command varies per project Specta setup — must be noted as project-configurable
  - Suggested default: `cargo tauri build --no-bundle` (triggers Specta export) or a dedicated
    `specta export` call if the project exposes one
  - Cross-reference: existing TODO.md bug ("missing generate-types recipe")

---

### Phase B — Stitch removal from spec-writer

- [ ] **B1** — `kit/skills/spec-writer/SKILL.md`
  - Frontmatter `description`: remove "or Stitch mockup" — keep "optional UX draft"
  - Frontmatter `tools`: remove `mcp__stitch__generate_screen_from_text`,
    `mcp__stitch__list_screens`, `mcp__stitch__get_screen`
  - Step 1 glob exclusion: remove `stitch/` from the pattern
  - Step 7: remove entirely (was "UX visual draft (optional) via Stitch")
  - Step 8: remove Stitch branch — simplify final question to
    "Validate, refine, write the ADR, or generate the implementation plan?"
  - Critical Rules: remove rule 10 (Stitch project ID) and rule 12 (.stitch HTML files)
  - Notes section: remove the Stitch MCP setup paragraph
  - Renumber Critical Rules after removal

---

### Phase C — New skill: `/contract`

- [ ] **C1** — Create `kit/skills/contract/SKILL.md`

  **Frontmatter**

  ```
  name: contract
  description: Derives or updates an IPC contract (docs/contracts/{domain}.md) from a validated
    feature spec. Upsert-aware — adds commands to an existing domain contract without overwriting.
    Run after spec-reviewer approves, before feature-planner.
  tools: Read, Glob, Write, Edit, AskUserQuestion
  ```

  **Behavior**
  1. Ask for spec path if not provided; read `docs/spec/{feature}.md`
  2. Extract domain name from the spec's Context section, or ask the user
  3. Check if `docs/contracts/{domain}.md` exists:
     - If yes → show current content, propose additions/modifications as a diff;
       ask user to approve before writing
     - If no → derive full contract from spec, show to user, ask to approve before creating
  4. Write or patch the file on approval
  5. Append changelog entry: `- {date} — Added by {spec-name}: {command list}`

  **Contract file format**

  ```markdown
  # Contract — {Domain}

  > Domain: {domain}
  > Last updated by: {spec-name}

  ## Commands

  | Command | Args | Return | Errors |
  | ------- | ---- | ------ | ------ |

  ## Shared Types

  \`\`\`rust
  // Rust structs — mirrored to TypeScript via Specta
  \`\`\`

  ## Events

  | Event | Payload |
  | ----- | ------- |

  ## Changelog

  - {date} — Added by {spec-name}: {command list}
  ```

  **Rules**
  - Never silently overwrite existing commands — always diff and confirm with user
  - Frontend-only features: create a minimal contract with "no new commands" note for traceability
  - Types use Rust naming conventions (`snake_case` fields, `PascalCase` structs)
  - Errors must be exhaustive — every failure path that surfaces to the frontend must appear

---

### Phase D — New agent: `contract-reviewer`

- [ ] **D1** — Create `kit/agents/contract-reviewer.md`

  **Frontmatter**

  ```
  name: contract-reviewer
  description: Reviews a domain contract (docs/contracts/{domain}.md) against its source spec
    for coverage, consistency, and technical correctness. Blocks progression to feature-planner
    on critical findings. Run after /contract produces or updates the contract file.
  tools: Read, Grep, Glob
  model: claude-sonnet-4-6
  ```

  **Behavior**
  1. Ask for contract path if not provided (e.g. `docs/contracts/user.md`)
  2. Ask for (or infer from changelog) the source spec path
  3. Read both files; read `docs/adr/` if present for type constraints

  **Checks**

  #### A — Coverage (spec → contract)
  - 🔴 A `backend` or `frontend + backend` scoped rule in the spec has no corresponding command
    in the contract
  - 🟡 A state-transition rule implies an event but no event row exists in the contract

  #### B — Traceability (contract → spec)
  - 🔴 A command in the contract cannot be traced to any spec rule — no business justification

  #### C — Error exhaustiveness
  - 🔴 A command that performs a mutation (create/update/delete) has no error variants
  - 🔴 An error case explicitly described in a spec rule is absent from the command's Errors column
  - 🟡 A command has only generic errors (e.g. `DbError` only) when the spec describes
    domain-specific failure conditions

  #### D — Type correctness
  - 🔴 A return type is too vague (`String`, `Value`, `Json`) when the spec's Entity Definition
    implies a struct — Specta cannot generate a useful TypeScript type from this
  - 🔴 A type referenced in Args or Return is not defined in the Shared Types section
  - 🟡 A struct field type contradicts an active ADR (e.g. `f64` for amounts when ADR mandates `i64`)

  #### E — Naming conventions
  - 🟡 A command name is not `snake_case`
  - 🟡 A type name is not `PascalCase`

  #### F — Infallible commands
  - 🟡 A command has no error variants and no comment justifying why it cannot fail

  **Output format** (mirrors spec-reviewer)

  ```
  ## contract — {domain}

  ### A — Coverage
  🔴 ...
  ### B — Traceability
  ✅ None.
  ...

  Review complete: N critical, N warning(s).
  Ready for feature-planner: yes — 0 critical findings. /
  no — blocked by N critical finding(s).
  ```

  **Rules**
  - Read-only — never edit the contract or spec
  - Report against command names and spec rule IDs, not line numbers
  - Every 🔴 finding blocks progression to `feature-planner`

---

### Phase E — New agent: `test-writer-backend`

- [ ] **D1** — Create `kit/agents/test-writer-backend.md`

  **Frontmatter**

  ```
  name: test-writer-backend
  description: Writes failing Rust test stubs for every command and behavior defined in the
    domain contract (docs/contracts/{domain}.md). Verifies cargo test exits non-zero (red)
    before finishing. Does not implement — implementation is a separate step.
    Run after /contract is approved, before backend implementation.
  tools: Read, Grep, Glob, Write, Edit, Bash
  model: claude-sonnet-4-6
  ```

  **Behavior**
  1. Ask for domain if not provided; read `docs/contracts/{domain}.md`
  2. Read `docs/backend-rules.md` and `docs/testing.md` if present
  3. Locate `src-tauri/src/context/{domain}/api.rs` (or equivalent command file)
  4. For each command in the contract, write one `#[tokio::test]` per behavior:
     - happy path (returns expected type)
     - one test per error variant listed in the contract
  5. Place stubs in an inline `#[cfg(test)]` module in the command file
  6. Run `cargo test {domain}` via Bash; confirm non-zero exit (red)
  7. Report: list of stubs written, cargo test output confirming red

  **Stub format**

  ```rust
  #[cfg(test)]
  mod tests {
      use super::*;

      // CNT-010 — get_user: happy path
      #[tokio::test]
      async fn test_get_user_returns_user() {
          todo!("implement")
      }

      // CNT-010 — get_user: not found
      #[tokio::test]
      async fn test_get_user_not_found() {
          todo!("implement")
      }
  }
  ```

  **Rules**
  - Write all stubs for the full contract in one pass — no partial output
  - One stub per behavior (happy path + each error variant), not one stub per command
  - Annotate each stub with the contract command and behavior in a comment
  - `todo!("implement")` body only — no implementation, no helper code
  - If a `#[cfg(test)]` module already exists, append — never duplicate the module declaration
  - Must confirm non-zero cargo test exit before finishing

---

### Phase F — New agent: `test-writer-frontend`

- [ ] **E1** — Create `kit/agents/test-writer-frontend.md`

  **Frontmatter**

  ```
  name: test-writer-frontend
  description: Writes failing Vitest stubs for every command and behavior defined in the domain
    contract (docs/contracts/{domain}.md). Reads src/bindings.ts for actual generated types.
    Verifies vitest run exits non-zero (red) before finishing. Does not implement.
    Run after the backend commit (bindings are fresh), before frontend implementation.
  tools: Read, Grep, Glob, Write, Edit, Bash
  model: claude-sonnet-4-6
  ```

  **Behavior**
  1. Ask for domain if not provided; read `docs/contracts/{domain}.md`
  2. Read `src/bindings.ts` — reference actual generated TypeScript types, never inferred ones
  3. Read `docs/frontend-rules.md` and `docs/testing.md` if present
  4. Locate or create `src/features/{domain}/gateway.test.ts` (colocated with `gateway.ts`)
  5. For each command in the contract, write one `it()` per behavior (happy path + each error)
  6. Run `vitest run src/features/{domain}/` via Bash; confirm non-zero exit (red)
  7. Report: list of stubs written, vitest output confirming red

  **Stub format**

  ```typescript
  import { vi, it, expect, describe } from "vitest";
  import { invoke } from "@tauri-apps/api/core";

  vi.mock("@tauri-apps/api/core", () => ({ invoke: vi.fn() }));

  describe("{domain} gateway", () => {
    // CNT-010 — get_user: happy path
    it("getUser returns user data", async () => {
      expect(true).toBe(false); // red — implement in gateway.ts
    });

    // CNT-010 — get_user: not found
    it("getUser handles NotFound error", async () => {
      expect(true).toBe(false); // red — implement in gateway.ts
    });
  });
  ```

  **Rules**
  - Read `src/bindings.ts` before writing — stubs must reference actual generated types
  - Write all stubs in one pass — no partial output
  - `expect(true).toBe(false)` body only — no gateway implementation
  - Mock `@tauri-apps/api/core` at file top — never import Tauri runtime types in tests
  - Colocate test file next to `gateway.ts` — never create a `__tests__/` directory
  - If a test file already exists, append inside the existing `describe` block
  - Must confirm non-zero vitest exit before finishing

---

### Phase G — Modify: `spec-reviewer`

- [ ] **F1** — Add check **G — Contractability** (new section after F — Open Questions)

  ```markdown
  #### G — Contractability

  - 🔴 Backend rules are present but `## Entity Definition` section is missing — payload
    types cannot be derived for the contract
  - 🔴 A backend rule describes a mutation (create/update/delete) but no error cases are
    described — contract error variants cannot be derived
  - 🟡 A backend rule's return type cannot be inferred from the spec (entity shape too vague)
  - 🟡 A state-transition rule implies an event but no event name is given
  ```

- [ ] **F2** — Update the closing verdict line:
  - Before: `Ready for feature-planner: yes — 0 critical findings.`
  - After: `Ready for /contract: yes — 0 critical findings (incl. contractability).`

---

### Phase H — Modify: `feature-planner`

- [ ] **G1** — Step 2 (Architectural Contextualization): add read of `docs/contracts/{domain}.md`
  - If present: mandatory input — commands anchor the test-writer tasks in the plan
  - If absent: proceed without it (frontend-only or simple feature)

- [ ] **G2** — Workflow TaskList: replace current backend/frontend/tests block

  ```markdown
  - [ ] 📄 Contract (`/contract` — human approves shape) — if backend rules present
  - [ ] 🔍 Contract review (`contract-reviewer` → fix issues) — if backend rules present
  - [ ] ✍️ Backend test stubs (`test-writer-backend` — all stubs written, red confirmed)
  - [ ] 🏗️ Backend implementation (minimal — make failing tests pass, green confirmed)
  - [ ] 🧹 `just format` (rustfmt + clippy --fix)
  - [ ] 🔍 Backend review (`reviewer-backend` → fix issues)
  - [ ] 🔗 Type synchronization (`just generate-types`)
  - [ ] 🔧 Compilation fixup (TypeScript errors from new bindings only — no UI work)
  - [ ] ✅ `just check` — TypeScript clean
  - [ ] 💾 Commit: backend layer (hard gate: `/smart-commit`)
  - [ ] ✍️ Frontend test stubs (`test-writer-frontend` — all stubs written, red confirmed)
  - [ ] 💻 Frontend implementation (minimal — make failing tests pass, green confirmed)
  - [ ] 🧹 `just format`
  - [ ] 🔍 Frontend review (`reviewer-frontend` → fix issues)
  - [ ] 💾 Commit: frontend layer (hard gate: `/smart-commit`)
  - [ ] 🔍 Cross-cutting review (`reviewer` always + `reviewer-sql` if migrations modified)
  - [ ] 🌐 i18n review (`i18n-checker` — if UI text changed)
  - [ ] 🔧 Script review (`script-reviewer` — if scripts/hooks modified)
  - [ ] 🔧 Maintainer (`maintainer` — if capabilities/\*.json or tauri.conf.json modified)
  - [ ] 📚 Documentation update (`ARCHITECTURE.md` + `docs/todo.md`)
  - [ ] ✅ Spec check (`spec-checker`)
  - [ ] 💾 Commit: tests & docs (hard gate: `/smart-commit`)
  ```

- [ ] **G3** — Critical Rules: add rule about test-writer agents and minimal implementation
  - "The plan must not add implementation tasks for commands already covered by
    `test-writer-backend` stubs. The implementation task is: make the failing tests pass with
    minimal code — no extras."

---

### Phase I — Modify: `spec-checker`

- [ ] **H1** — Add **Step 5 — Contract compliance** after current Step 4

  ```markdown
  ### Step 5 — Contract compliance

  If `docs/contracts/{domain}.md` exists for this feature's domain:

  For each command in the contract:

  - Backend: verify a `#[tauri::command]` with that name exists in `src-tauri/`
  - Frontend: verify a gateway call to that command exists in `src/features/{domain}/gateway.ts`
  - Tests: verify at least one `#[tokio::test]` (backend) and one `it()` (frontend) references it

  Output per command:
  \`\`\`
  get_user ✅ backend + ✅ frontend + ✅ tested
  update_user ✅ backend + ✅ frontend + ⚠️ no test
  delete_user ❌ no backend implementation
  \`\`\`
  ```

- [ ] **H2** — Update final summary to include contract coverage count

---

### Phase J — Modify: `workflow-validator`

- [ ] **J1** — Step 3 conditional triggers: add
  - `docs/contracts/{domain}.md` present for this feature →
    Contract review, Backend test stubs, and Frontend test stubs steps required

---

### Phase K — Update docs

- [ ] **K1** — `kit/kit-readme.md`: rewrite Option A phases to match new workflow + gate taxonomy
- [ ] **K2** — `kit/kit-tools.md`:
  - Skills table: add `/contract` row
  - Spec & Planning Agents table: add `contract-reviewer`, `test-writer-backend`, `test-writer-frontend`

---

### Phase L — Quality & release

- [ ] **K1** — Run `python3 scripts/check-kit.py` — fix all issues
- [ ] **K2** — Run `/preflight` — validate all new and modified artifacts
- [ ] **K3** — `/smart-commit` per logical group: Stitch removal / new tools / modified agents / docs
- [ ] **K4** — `python3 scripts/release-kit.py` — minor bump (new agents + skill)

---

## File map

| Action | File                                 |
| ------ | ------------------------------------ |
| Modify | `kit/skills/spec-writer/SKILL.md`    |
| Create | `kit/skills/contract/SKILL.md`       |
| Create | `kit/agents/contract-reviewer.md`    |
| Create | `kit/agents/test-writer-backend.md`  |
| Create | `kit/agents/test-writer-frontend.md` |
| Modify | `kit/agents/spec-reviewer.md`        |
| Modify | `kit/agents/feature-planner.md`      |
| Modify | `kit/agents/spec-checker.md`         |
| Modify | `kit/agents/workflow-validator.md`   |
| Modify | `kit/kit-readme.md`                  |
| Modify | `kit/kit-tools.md`                   |
| Modify | `kit/common.just`                    |

---

## Implementation order

```
A (prerequisite fix)
→ B (Stitch removal)
→ C (contract skill)
→ D (contract-reviewer)          ← depends on C (reviews the contract format C produces)
→ E + F in parallel (test-writer-backend, test-writer-frontend)
→ G + H + I + J in parallel (spec-reviewer, feature-planner, spec-checker, workflow-validator)
→ K (docs)
→ L (quality + release)
```

C must precede D (contract-reviewer validates what /contract produces).
D must precede H (feature-planner Workflow TaskList references contract-reviewer step).
E and F are independent of each other but both depend on C (reference contract format).
G, I, J are independent of each other.
