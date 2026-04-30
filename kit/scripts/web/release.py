#!/usr/bin/env python3
"""Release manager for Axum + React projects (web profile).

Discovers backend Cargo.toml (server/Cargo.toml, backend/Cargo.toml, or Cargo.toml)
and frontend package.json (client/package.json, frontend/package.json, or package.json).
Infers semver bump from conventional commits, updates both version files and
CHANGELOG.md, then commits, tags, and pushes.

Usage:
  python3 scripts/release.py              # auto-detect bump type
  python3 scripts/release.py patch        # force patch bump
  python3 scripts/release.py minor        # force minor bump
  python3 scripts/release.py major        # force major bump
  python3 scripts/release.py --dry-run    # preview without changes
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent


def _find(candidates):
    for p in candidates:
        path = ROOT / p
        if path.exists():
            return path
    return ROOT / candidates[0]


CARGO_TOML = _find(["server/Cargo.toml", "backend/Cargo.toml", "Cargo.toml"])
PKG_JSON = _find(["client/package.json", "frontend/package.json", "package.json"])
CHANGELOG = ROOT / "CHANGELOG.md"

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
NC = "\033[0m"


def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"{RED}Command failed: {' '.join(cmd)}{NC}")
        print(result.stdout + result.stderr)
        sys.exit(1)
    return result.stdout.strip()


# ── Version I/O ──────────────────────────────────────────────────────────────


def cargo_read():
    text = CARGO_TOML.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        print(f"{RED}Could not find version in {CARGO_TOML}{NC}")
        sys.exit(1)
    return m.group(1)


def cargo_write(old_ver, new_ver):
    text = CARGO_TOML.read_text(encoding="utf-8")
    # Replace only the first occurrence (package table, not dependency versions)
    CARGO_TOML.write_text(
        text.replace(f'version = "{old_ver}"', f'version = "{new_ver}"', 1),
        encoding="utf-8",
    )


def pkg_read():
    return json.loads(PKG_JSON.read_text(encoding="utf-8"))["version"]


def pkg_write(new_ver):
    data = json.loads(PKG_JSON.read_text(encoding="utf-8"))
    data["version"] = new_ver
    PKG_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# ── Semver helpers ────────────────────────────────────────────────────────────


def bump(version, bump_type):
    major, minor, patch = map(int, version.split("."))
    if bump_type == "major":
        return f"{major + 1}.0.0"
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def commits_since_last_tag():
    last_tag = run(["git", "describe", "--tags", "--abbrev=0"], cwd=ROOT, check=False)
    if last_tag:
        log = run(["git", "log", f"{last_tag}..HEAD", "--pretty=format:%s"], cwd=ROOT)
    else:
        log = run(["git", "log", "--pretty=format:%s"], cwd=ROOT)
    return [c for c in log.splitlines() if c]


def infer_bump(commits):
    if any("BREAKING CHANGE" in c or "!:" in c for c in commits):
        return "major"
    if any(c.startswith("feat") for c in commits):
        return "minor"
    return "patch"


# ── CHANGELOG ────────────────────────────────────────────────────────────────


def update_changelog(new_ver, commits):
    today = date.today().isoformat()
    sections = {"feat": [], "fix": [], "other": []}
    for c in commits:
        if c.startswith("feat"):
            sections["feat"].append(c)
        elif c.startswith("fix"):
            sections["fix"].append(c)
        else:
            sections["other"].append(c)

    entry = f"## [{new_ver}] - {today}\n\n"
    if sections["feat"]:
        entry += "### Features\n" + "".join(f"- {c}\n" for c in sections["feat"]) + "\n"
    if sections["fix"]:
        entry += "### Bug Fixes\n" + "".join(f"- {c}\n" for c in sections["fix"]) + "\n"
    if sections["other"]:
        entry += "### Other\n" + "".join(f"- {c}\n" for c in sections["other"]) + "\n"

    if CHANGELOG.exists():
        existing = CHANGELOG.read_text(encoding="utf-8")
        if existing.startswith("# "):
            cut = existing.index("\n") + 1
            CHANGELOG.write_text(
                existing[:cut] + "\n" + entry + existing[cut:], encoding="utf-8"
            )
        else:
            CHANGELOG.write_text(entry + existing, encoding="utf-8")
    else:
        CHANGELOG.write_text("# Changelog\n\n" + entry, encoding="utf-8")


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Release manager for Axum + React project"
    )
    parser.add_argument(
        "bump_type",
        nargs="?",
        choices=["patch", "minor", "major"],
        help="Override auto-detected bump type",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without making any changes"
    )
    args = parser.parse_args()

    current_ver = cargo_read()
    pkg_ver = pkg_read()

    print(f"{BOLD}{BLUE}=== Release Manager ==={NC}\n")
    print(f"  {CARGO_TOML.relative_to(ROOT)}: {current_ver}  (source of truth)")
    print(f"  {PKG_JSON.relative_to(ROOT)}: {pkg_ver}")
    if pkg_ver != current_ver:
        print(
            f"  {YELLOW}⚠  versions are out of sync — package.json will be updated{NC}"
        )

    commits = commits_since_last_tag()
    if not commits:
        print(f"\n{YELLOW}No commits since last tag. Nothing to release.{NC}")
        sys.exit(0)

    bump_type = args.bump_type or infer_bump(commits)
    new_ver = bump(current_ver, bump_type)

    print(f"\n  Commits since last tag : {len(commits)}")
    print(f"  Inferred bump type     : {bump_type}")
    print(f"  {current_ver} → {BOLD}{new_ver}{NC}")

    if args.dry_run:
        print(f"\n{YELLOW}[dry-run] Would release v{new_ver} — no changes made.{NC}")
        return

    try:
        answer = input(f"\nRelease v{new_ver}? [y/N] ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)
    if answer != "y":
        print("Aborted.")
        sys.exit(0)

    print(f"\n{BLUE}Updating version files...{NC}")
    cargo_write(current_ver, new_ver)
    pkg_write(new_ver)
    print(f"  ✓ {CARGO_TOML.relative_to(ROOT)} → {new_ver}")
    print(f"  ✓ {PKG_JSON.relative_to(ROOT)} → {new_ver}")

    print(f"\n{BLUE}Updating CHANGELOG.md...{NC}")
    update_changelog(new_ver, commits)
    print("  ✓ CHANGELOG.md")

    print(f"\n{BLUE}Committing...{NC}")
    run(
        [
            "git",
            "add",
            str(CARGO_TOML.relative_to(ROOT)),
            str(PKG_JSON.relative_to(ROOT)),
            str(CHANGELOG.relative_to(ROOT)),
        ],
        cwd=ROOT,
    )
    run(["git", "commit", "--no-verify", "-m", f"chore: release v{new_ver}"], cwd=ROOT)
    print(f"  ✓ chore: release v{new_ver}")

    print(f"\n{BLUE}Tagging...{NC}")
    run(["git", "tag", f"v{new_ver}"], cwd=ROOT)
    print(f"  ✓ v{new_ver}")

    print(f"\n{BLUE}Pushing...{NC}")
    run(["git", "push"], cwd=ROOT)
    run(["git", "push", "--tags"], cwd=ROOT)
    print("  ✓ pushed branch + tag")

    print(f"\n{GREEN}✅ Released v{new_ver}{NC}")


if __name__ == "__main__":
    main()
