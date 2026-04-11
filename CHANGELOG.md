# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
