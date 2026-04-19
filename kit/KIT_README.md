# Agents & Skills Reference

This file documents all agents and skills available in your project.

**Location**: `.claude/KIT_README.md` (read-only reference)

**Note**: Your project may have additional agents/skills in `.claude/agents/` and `.claude/skills/`. See your project's local `.claude/` documentation for project-specific agents.

---

## Kit Agents

All kit agents are designed for Tauri 2 / React 19 / Rust projects using DDD architecture.

| Agent                  | Purpose                                                                                          | When to Use                                  | Input                                               |
| ---------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------- | --------------------------------------------------- |
| **reviewer**           | Code review: DDD, backend/frontend rules, general quality                                        | After code is written, before commit         | File path or code snippet                           |
| **spec-reviewer**      | Spec quality gate: rule atomicity, scope coverage, DDD alignment, UX completeness                | After spec-writer produces a draft           | Spec path (e.g., `docs/spec/refund.md`)             |
| **spec-checker**       | Verify all business rules (TRIGRAM-NNN) are implemented & tested                                 | After implementation, before release         | Spec path                                           |
| **feature-planner**    | Translate validated specs into detailed implementation plans                                     | After spec-reviewer approves spec            | Spec path → generates `docs/plan/{feature}-plan.md` |
| **reviewer-frontend**  | React/TS quality + UX/M3 design compliance, UX completeness (empty/loading/error/success states) | After UI components are built                | Modified `.ts` / `.tsx` files                       |
| **maintainer**         | GitHub Actions workflows, config files, pre-release checks                                       | When CI/CD or config files change            | Modified workflow or config file                    |
| **script-reviewer**    | Internal quality of scripts and hooks (robustness, security, portability)                        | When `.githooks/` or `scripts/` are modified | Modified script file                                |
| **i18n-checker**       | Hardcoded strings, missing/unused translation keys                                               | When UI text changes                         | Modified component files                            |
| **workflow-validator** | Validates all required workflow steps were done before commit                                    | Pre-commit validation                        | None (run as final check)                           |

---

## Kit Skills

### `smart-commit`

Create conventional commits with strict validation, tests, linters, and confirmation.

- **Validates**: Tests pass, linters pass, commit message conventions, no sensitive files
- **Output**: Committed changes with conventional message

### `dep-audit`

npm + Cargo dependency audit (outdated versions, CVEs) before releases.

- **Validates**: All dependencies up-to-date, no security warnings
- **Output**: Audit report with actionable fixes

### `adr-manager`

Create/update Architecture Decision Records in `docs/adr/`.

- **Creates**: ADR files with standard format (title, context, decision, consequences)
- **Output**: `docs/adr/ADR-NNN-{title}.md`

### `spec-writer`

Interactive spec creation for new features.

- **Interviews**: User via 3 rounds max (feature name, trigram, business need, domain)
- **Creates**: `docs/spec/{feature}.md` with TRIGRAM-NNN rules
- **Also manages**: `docs/spec-index.md` registry (created in Step 2.5)
- **Output**: Feature spec + updated trigram registry

---

## Standard Workflow (Kit-provided)

```
1. Feature Idea
   ↓ (run spec-writer)
2. Spec Draft (docs/spec/{feature}.md)
   ↓ (pass to spec-reviewer)
3. Spec Validated ✅
   ↓ (run feature-planner)
4. Implementation Plan (docs/plan/{feature}-plan.md)
   ↓ (implement features, write tests, update docs)
5. Implementation Complete
   ↓ (run spec-checker to verify all rules implemented)
6. Spec Compliance Verified ✅
   ↓ (run code linting, tests, code review)
7. Code Quality ✅
   ↓ (run smart-commit)
8. Committed to main
```

---

## Spec Rule Numbering System (Project Standard)

Your project uses **TRIGRAM-NNN** format for spec rules (example: `REF-010, PAY-020, INV-030`):

- **TRIGRAM** = 3-letter identifier unique per project (e.g., REF for Refund, PAY for Payment)
- **NNN** = 3-digit number, organized by topic:
  - 010–019: Eligibility & initiation
  - 020–029: Creation
  - 030–039: Updates & status changes
  - 040–049: Deletion
  - 050–059: Extensions & future

**Immutability**: Once assigned, a rule number never changes. If a rule is removed, its number stays vacant.

**Registry**: All trigrams are registered in `docs/spec-index.md` (created by spec-writer).

---

## Standard Project Artifacts

| File                     | Location             | Purpose                                  |
| ------------------------ | -------------------- | ---------------------------------------- |
| `kit/agents/*.md`        | `.claude/agents/`    | Agent definitions                        |
| `kit/skills/*/SKILL.md`  | `.claude/skills/*/`  | Skill definitions                        |
| `kit/common.just`        | `common.just`        | Shared justfile recipes                  |
| `kit/scripts/check.py`   | `scripts/check.py`   | Quality checker                          |
| `kit/scripts/release.py` | `scripts/release.py` | Release manager                          |
| `kit/githooks/*`         | `.githooks/`         | Git hooks (pre-commit, commit-msg, etc.) |

---

## Using Agents in Your Project

### Basic Usage

**In VS Code Copilot Chat**, trigger agents with:

```
/run-agent spec-writer      # Create a new spec
/run-agent spec-reviewer    # Review a spec before implementation
/run-agent feature-planner  # Build implementation plan
```

**Or invoke directly**:

```bash
cd .claude/agents
# Each agent's instructions are built into the `.md` file
```

### Customizing/Extending

Your project can:

- ✅ Add **local agents** in `.claude/agents/{your-agent}.md` (project-specific reviewers, validators, etc.)
- ✅ Add **local skills** in `.claude/skills/{your-skill}/SKILL.md`
- ❌ Do NOT modify kit agents/skills (they're overwritten on next sync)

If you need to extend a kit agent's behavior:

1. Create a new local agent that **uses** the kit agent
2. Add project-context or domain-specific validation
3. Document in your project's local `.claude/` README

---

## Handling `[DECISION]` Criticals

Some reviewer Criticals are tagged `[DECISION]`. These indicate that the correct fix requires an architectural choice — not a mechanical code change — and cannot be resolved without domain or team input.

**Recommended rule for your project's `CLAUDE.md`:**

> **Reviewer `[DECISION]` criticals must not be fixed unilaterally.** When a reviewer flags a Critical with `[DECISION]`, stop and present the finding to the user before writing any code. The reviewer's guidance describes the direction, not the final answer — the architectural boundary must be agreed upon first.

**Why this matters:** a cross-boundary import can be "fixed" in several structurally valid ways (new use-case, shared port, merged context). Choosing the wrong one silently encodes an architectural assumption that is hard to undo. The `[DECISION]` tag is the reviewer's signal that human judgment is required.

---

## Before Major Project Releases

Verify that all agents, skills, and scripts are working correctly with your project:

- Run agents on sample specs/code to validate output
- Execute scripts to confirm they work in your environment
- Check that spec-index.md is up-to-date

For more information on managing these artifacts, see your project's local `.claude/` documentation.

---

## Troubleshooting

**Agent not found?**

- Check if agent file exists: `ls -la .claude/agents/`
- Run `./scripts/sync-config.sh` to re-sync kit files

**Agent gives wrong output?**

- Verify your spec/code is in the right path (e.g., `docs/spec/{feature}.md` not `docs/{feature}.md`)
- Check that required files exist (e.g., `ARCHITECTURE.md`, `docs/adr/`)

**Trigram collision?**

- Check `docs/spec-index.md` for registered trigrams
- Use different 3-letter prefix for new feature specs
