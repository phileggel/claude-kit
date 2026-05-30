# Project Conventions

_Kit-internal authoring standard. Not synced downstream._

## Style Guide

- **Quotes**: Always use double quotes (`"`) for strings in Python and TypeScript/JavaScript.
- **Python**: Follow PEP 8 style, enforced by `ruff`.
- **Bash/Shell**: Indentation of 4 spaces, enforced by `shfmt`.
- **Markdown**: Enforced by `prettier`.

---

## Agent & Skill Design

The gold standard for authoring kit agents (`kit/agents/*.md`) and skills
(`kit/skills/*/SKILL.md`). Grounded in the Claude Code [sub-agents docs](https://code.claude.com/docs/en/sub-agents),
the [skills-vs-subagents decision rule](https://claude.com/blog/skills-explained),
and tool-grant minimality — not a kit-specific invention. Three mechanisms keep
artifacts on-standard, each at a different moment:

- **This doc** — the normative spec you read _before_ authoring or editing.
- **`.claude/agents/ai-reviewer.md`** — judgment-layer review at _author time_
  (discoverability, voice, structural completeness; the A–J rubric references this doc).
- **`scripts/check.py`** — deterministic enforcement on _every commit_ (required
  sections, tool minimality, compound-shell, heading presence).

### Choosing the artifact type

Before writing a skill or agent, confirm it is the right shape. The kit authors
six types; pick by what the work _is_:

- **Script** (`kit/scripts/*.{py,sh,mjs}`) — deterministic work: file
  collection, regex extraction, counting, parsing, format checks. The model does
  these slowly and inconsistently; a script does them once and a skill consumes
  the structured output. Decisive test: _could a unit test assert the output?_ →
  script. Kit example: `whats-next.py` collects the backlog; the `/whats-next`
  skill applies judgment to its JSON.
- **Skill** (`kit/skills/*/SKILL.md`) — a user-invoked (or model-invoked)
  procedure that runs **in the current context**: a checklist, a multi-step
  workflow, a formatter. Reach for one when you keep pasting the same
  instructions, or a CLAUDE.md section has grown from a _fact_ into a _procedure_.
- **Subagent** (`kit/agents/*.md`) — a focused worker that runs in a **fresh,
  isolated context** and returns only a summary: a quality gate, a researcher, a
  reviewer. Use when the work would flood the main context, or needs a restricted
  tool grant / different model.
- **Git hook** (`kit/githooks/*`) — enforcement that must fire on a git event
  (pre-commit lint, commit-msg format), not on demand.
- **Justfile recipe** (`kit/common.just`) — a stable command entry point a human
  or agent runs by name (`just check`); thin orchestration over scripts.
- **Convention doc** (`kit/docs/*.md`) — durable rules an agent reads at run time
  (DDD, error model, frontend rules), synced copy-once downstream.

The decision rule for the two judgment artifacts (Anthropic's): _"If the work is
small and stays in front of you, that's a skill. If the work is big and runs in a
side process, that's a subagent."_ When a skill's step describes deterministic
collection/extraction/counting, split it: script does the work, skill consumes
the output (name the inputs and the output shape — "extract to a script" without
a contract is half a decision).

### Skill vs slash command

These are the **same artifact** since the 2026 merge: a file at
`.claude/commands/foo.md` and a skill at `.claude/skills/foo/SKILL.md` both
create `/foo`. `.claude/commands/` is the **legacy single-file format**; the
kit standardises on the **skill directory format** (`SKILL.md`) — it supports
supporting files, invocation-control frontmatter, and model auto-invocation that
plain command files do not. Do not add `.claude/commands/` files.

### Other Claude Code artifact types (reference)

The kit does not author these, but they exist in the platform. Know them so you
don't reinvent one as a skill:

| Type          | Location                                | Purpose                                                                |
| ------------- | --------------------------------------- | ---------------------------------------------------------------------- |
| Slash command | `.claude/commands/*.md`                 | Legacy single-file form of a skill — merged into skills; prefer skills |
| Hook          | `.claude/settings.json` `hooks`         | Event-driven automation (pre-tool, post-edit) — fires without a prompt |
| Output style  | `settings.json`                         | Reshape Claude Code for non-software-engineering uses                  |
| MCP server    | `.claude/mcp.json` / `settings.json`    | External tool/data integrations via Model Context Protocol             |
| Plugin        | `.claude-plugin/` + marketplace         | Distribution container bundling skills, agents, hooks, MCP             |
| Workflow      | `.claude/workflows/*`                   | Deterministic multi-subagent orchestration scripts                     |
| Settings      | `settings.json` / `settings.local.json` | Permissions, env, model config                                         |
| Memory        | `CLAUDE.md`                             | Persistent project facts/instructions loaded every session             |

There is **no standalone "prompt" file type** — system-prompt content lives in
`CLAUDE.md`, a hook, or a subagent/skill body, not a separate artifact.

### Skill vs subagent

Anthropic's decision rule: _"If the work is small and stays in front of you,
that's a skill. If the work is big and runs in a side process, that's a
subagent."_ A user-invoked workflow primer or formatter → **skill**. A
multi-step quality gate other agents call with a fresh context → **subagent**.

### Frontmatter (both)

- `name` — kebab-case, matches the directory/file name.
- `description` — the **routing surface**: Claude picks the artifact from this
  alone (fuzzy-matched, not documentation). Name the concrete artifacts it
  operates on and a trigger (`Use when X` / `after Y produces Z`). It must
  discriminate from siblings (swap-test: if the name were a sibling's, would the
  description still fit? If yes, sharpen it). Write in **third person** — it is
  injected into the system prompt, and a mixed point of view degrades discovery.
  Claude tends to **undertrigger**, so state the trigger assertively (`Use
proactively after…`) rather than tentatively. Skill descriptions cap at **1024
  characters** (hard platform limit); lead with the discriminating signal. No
  marketing verbs (`powerful`, `comprehensive`).
- `tools` — minimal. Omitting the field inherits every tool, so always set it
  for a constrained artifact. A review-only agent has no `Edit`/`Write` (use the
  `tools` allowlist, or `disallowedTools` as a denylist). Over-grant is flagged
  by the v2.1.98+ security classifiers and by `check.py`.
- `model` — defaults to `inherit`. Declare it for non-trivial artifacts:
  judgment-heavy → `opus`, mechanical → `sonnet`/`haiku`.

### Canonical section skeleton — skills

In this order (omit a section only when it genuinely does not apply):

1. `## Required tools` — when the `tools:` field is non-trivial
2. `## When to use`
3. `## When NOT to use` — name the negative case and redirect to the right sibling
4. `## Output format` — when the skill produces output
5. `## Execution Steps`
6. `## Critical Rules`
7. `## Notes` — optional; the author-side _why_

`## When to use` and `## Output format` are **enforced** by `check.py`.

Keep the SKILL.md body **under 500 lines** (every loaded line is a recurring
token cost). When it must grow past that, use **progressive disclosure**: keep
SKILL.md as the lean entry point and split detail into sibling files the skill
links to, loaded only when needed — rather than one monolithic file. `check.py`
emits a density signal at 300 lines as an earlier nudge.

### Canonical section skeleton — agents

- Role declaration in the opening (`You are… / Your job is…`)
- `## Process` or `## Execution Steps` — a numbered playbook, not prose
- `## Output format` — with a concrete example **and** an empty-result marker
- `## Critical Rules`
- A scope-boundary section when the role overlaps a sibling (e.g.
  `reviewer-arch` vs `reviewer-backend`)

### Heading & step style

- **Title Case** for all `##`/`###` headings (`## Execution Steps`, not
  `## Execution steps`).
- **Steps**: `### Step N — Title`, imperative voice (`Read the file`, not
  `The agent should read…`). One numbering style per file; `### Step N —` is
  canonical for new and edited work.

### Output discipline

- Lead with a one-line headline/verdict; never bury the conclusion.
- Show the literal shape with a concrete example.
- Specify an explicit empty-result marker (`✅ None.`, `ℹ️ No X to review.`) —
  silence is unparseable for an AI consumer.
- Use the `🔴`/`🟡`/`🔵` severity scheme consistently.

### Bash ergonomics (skills)

The permission allowlist matches by literal prefix. Inside a skill's own
`bash` blocks, avoid compound operators (`&&`, `||`, `;`), loops, and
discovery pipelines (`find … | grep …`) — each prompts on every invocation.
Split into separate calls or use `Glob`/`Grep`/`Read`. Single redirects
(`2>/dev/null`) and genuine process/data shell (a `lsof | xargs kill`, an
`awk`/`jq` data parse with no tool equivalent) are fine — document the latter.

### Project neutrality

Agent and skill files MUST NOT reference a specific project name — they are
reusable across every downstream project.

### Known drift backlog

`check.py`'s `GRANDFATHER` set lists skills that predate the section standard
and are exempted from the `check.py` gate. It is a shrinking TODO, not a
permanent allowance: bring a grandfathered skill up to standard when you next
touch it, then remove it from the set. Do not add new entries.
