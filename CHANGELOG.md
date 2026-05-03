# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v3.16.0] - 2026-05-03

### Added

- scope review findings to diff lines only

### Fixed

- carve out Tauri plugin APIs from gateway rule

## [v3.15.0] - 2026-05-02

### Added

- cover modified-function blind spot in test-writer

## [v3.14.0] - 2026-05-02

### Added

- improve wdio template with port constants and DB isolation

### Fixed

- suppress E2E output noise via logLevel and RUST_LOG

## [v3.13.0] - 2026-05-02

### Added

- enforce DDD aggregate scope checks

## [v3.12.1] - 2026-05-02

### Fixed

- resolve ARCHITECTURE.md path inconsistency

## [v3.12.0] - 2026-05-02

### Added

- enforce backend boundary and uniqueness
- survey roadmap.md as source f

### Fixed

- correct contract step numbering and add Bash to start
- reposition test-writer-e2e as green verifier in quality phase
- add vitest and SQLX_OFFLINE to check.py full mode
- enforce branch creation and add E2E step
- mirror generic scripts in mirror-local.sh

## [v3.11.0] - 2026-05-01

### Added

- add E2E testing layer (agent, skill, doc template)
- extract REPORT_PATH boilerplate into report-path.sh
- add RTL integration test step to test-writer-frontend

### Fixed

- remove compound operators and locale hardcoding in E2E files
- remove mkdir from whats-next and guard settings.json in check

## [v3.10.0] - 2026-04-30

### Added

- add merge recipe to common.just

## [v3.9.1] - 2026-04-30

## [v3.9.0] - 2026-04-30

### Added

- add mirror-local script and pre-merge-commit hook
- add create-pr skill and remove spec-diff and workflow-validator
- enforce branch workflow and fix reviewer file scope

### Fixed

- use --no-verify on release commits to bypass main hook
- sync pre-merge-commit hook and replace awk in create-pr
- dynamic base branch in create-pr, Tauri-only on generate-types
- add utf-8 encoding to remaining open() call
- add utf-8 encoding to open() calls in sync.sh and prune shipped TODOs

## [v3.8.0] - 2026-04-29

### Added

- add integration test step to test-writer-backend

### Fixed

- scope artifact scan to changes since last release tag
- address preflight warnings in generic agents
- add clippy to web fast mode and neutralize SQLX_OFFLINE rule
- add missing format recipe to web.just
- make spec-diff code search profile-neutral
- neutralize Tauri-specific paths in generic agents
- extend check-kit agent coverage to all profile dirs
- remove hardcoded server/ paths in web profile

## [v3.7.0] - 2026-04-29

### Added

- add web profile for Axum + React 19 + PostgreSQL projects

### Fixed

- replace compound Bash constructs with separate tool calls in agents and skills

## [v3.6.0] - 2026-04-28

### Added

- add prune skill for project-wide KISS audit

## [v3.5.0] - 2026-04-27

### Added

- add kit-discover skill for CLAUDE.md reconciliation

## [v3.4.0] - 2026-04-27

### Added

- add whats-next skill for session-start triage
- add spec-diff skill for revisit-time drift detection
- add output-format end-marker lint to check-kit.py

### Fixed

- drop already-done contract steps from feature plan

## [v3.3.0] - 2026-04-27

### Added

- add language and sync-coverage lints to check-kit.py
- write kit-version.md with changelog delta on sync

## [v3.2.0] - 2026-04-26

### Added

- add tool-minimality lint and fix smart-commit quality gate

### Fixed

- front-load report path to prevent reviewer save drift

## [v3.1.2] - 2026-04-26

### Fixed

- skip colliding profile recipes, warn on conflict

## [v3.1.1] - 2026-04-26

### Fixed

- auto-detect kit-profile in sync.sh for old bootstraps

## [v3.1.0] - 2026-04-26

### Added

- replace full-report save with compact summary

## [v3.0.1] - 2026-04-26

### Added

- add save-report section to 7 review agents

## [v3.0.0] - 2026-04-26

### Added

- rewrite sync scripts for profile-aware additive sync (Phase C)
- restructure kit into profile-aware layout (Phase B)

## [v2.13.0] - 2026-04-26

### Added

- genericize paths and language for multi-profile support

## [v2.12.1] - 2026-04-26

### Fixed

- detect breaking changes via ! bang only

## [v2.12.0] - 2026-04-26

### Added

- use {domain}-contract.md filename for contracts
- save reviewer reports to tmp/ after each run
- write real test bodies in TDD test-writer agents

## [v2.11.0] - 2026-04-25

### Added

- add workflow selector skill

### Fixed

- exempt BREAKING CHANGE footer from body line limit
- translate French log strings to English

## [v2.10.0] - 2026-04-24

### Added

- add contract-first TDD workflow

### Fixed

- remove Stitch integration

## [v2.9.0] - 2026-04-19

### Added

- restructure kit docs into tools index and readme

## [v2.8.0] - 2026-04-19

### Added

- add [DECISION] tag for architectural criticals

## [v2.7.0] - 2026-04-19

### Added

- add migration stub detection and checklist step

## [v2.6.0] - 2026-04-19

### Added

- extend maintainer to capabilities, bump reviewer-backend model

### Fixed

- align rule format with spec-writer canonical format

## [v2.5.0] - 2026-04-19

### Added

- add retro-spec, fix TSC detection, resolve validator circular dep
- add kit-advisor kit-local agent
- add thematic commit checkpoints

### Fixed

- address preflight warnings before release
- strip commit body from changelog entries
- print step name before each check runs

## [v2.4.0] - 2026-04-15

### Added

- add model tiering and merge ux-reviewer into reviewer-frontend
  Assign Haiku/Sonnet/Opus per agent complexity; merge ux-reviewer into reviewer-frontend to reduce agent invocations per .tsx change

### Fixed

- remove stale ux-reviewer references after merge
  Update kit-tools.md, KIT_README.md, feature-planner and workflow-validator to drop ux-reviewer and reflect its merge into reviewer-frontend

## [v2.3.0] - 2026-04-13

### Added

- refactor reviewers, add preflight skill, improve downstream agents
- add kit-tools index synced to downstream .claude/
  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
- add layered reviewer agents and sql reviewer
- Split reviewer.md into DDD-only; extract Rust rules to reviewer-backend, TS rules to reviewer-frontend
- Add reviewer-sql for SQL migration audits (atomicity, affinity, PKs, FK indexes)
- Update workflow-validator triggers for the three new agents
- Sync smart-commit skill char-count UX improvement to local .claude copy

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

### Fixed

- correct downstream agent inconsistencies
- i18n-checker: clarify --cached already covers staged-new files
- workflow-validator: docs/spec/_-plan.md → docs/plan/_-plan.md
- feature-planner: add English rule for docs/todo.md entries
- smart-commit: pre-populate suggested title with char count in step 5

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

## [v2.2.1] - 2026-04-11

### Fixed

- use proper check in hook

## [v2.2.0] - 2026-04-11

### Added

- add strict mode for releases, enforce format before release
- Add --strict flag to check-kit.py for release checks
- Strict mode: fails if prettier not installed (required for releases)
- Strict mode: fails if any format check fails (files must be pre-formatted)
- Update release-kit.py to call check-kit.py --strict before release
- Enforce workflow: format check → release (not: release → auto-format)
- Users must run 'just format' beforehand to fix formatting

### Fixed

- correct check-kit format issue
- ensure proper crlf format
- correct script name in pre-commit hook from check.py to check-kit.py

## [v2.1.0] - 2026-04-11

### Added

- implement TRIGRAMME-NNN spec numbering system
- spec-writer: Add Step 2.5 to create/register mandatory docs/spec-index.md
- spec-reviewer: Validate TRIGRAMME-NNN format and trigram registration
- spec-checker: Extract and report TRIGRAMME-NNN rules from implementations
- feature-planner: Map TRIGRAMME-NNN rules to implementation plans in docs/plan/
- Align all downstream paths (docs/spec/, docs/plan/, docs/spec-index.md)
- Fix grammar and unicode rendering issues
- All agents/skills ready for downstream project sync

### Fixed

- remove kit-only references, add downstream validator & KIT_README
- Remove sync.sh from kit documentation (kit-only, ephemeral)
- Fix command reference: sync-kit → sync-config.sh
- Add KIT_README.md as navigational reference for downstream projects
- Add downstream-validator agent for artifact validation
- Add .gitignore to exclude Python cache files
- All downstream-destined artifacts now pass validation

## [v2.0.2] - 2026-04-10

### Fixed

- add missing script-reviewer step to feature workflow

## [v2.0.1] - 2026-04-09

## [v2.0.0] - 2026-04-08

### Added

- add --version flag to force a specific version

## [v1.6.1] - 2026-04-08

### Fixed

- add migration shim at scripts/ for pre-v1.6.0 downstream projects

## [v1.6.0] - 2026-04-07

### Added

- add stat info shortcut with cloc

### Fixed

- remove project names, add doc fallbacks, clean workflow-validator scope

## [v1.5.0] - 2026-04-05

### Added

- add a changelog title properly

## [v1.4.0] - 2026-04-05

### Added

- improve kit-release script

## [v1.3.3] - 2026-04-05

### Fixed

- correct kit-release issue

## [v1.3.2] - 2026-04-05

- Release v1.3.2

## [v1.3.1] - 2026-04-05

- Release v1.3.1

## [v1.3.0] - 2026-04-05

- Release v1.3.0
