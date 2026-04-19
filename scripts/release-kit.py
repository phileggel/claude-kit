#!/usr/bin/env python3
"""
Release script for tauri-claude-kit.
- Automatically detects version bump based on commits (feat/fix/breaking)
- Updates CHANGELOG.md
- Commits and pushes to origin
"""

import subprocess
import re
from datetime import datetime
from pathlib import Path

# ANSI colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
NC = "\033[0m"


class ReleaseManager:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.current_version = self.get_latest_tag()
        self.commits = []
        self.breaking_changes = 0
        self.features = 0
        self.fixes = 0

    def get_latest_tag(self) -> str:
        try:
            return subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=self.repo_root,
                text=True,
            ).strip()
        except subprocess.CalledProcessError:
            return "v0.0.0"

    def parse_commit(self, message: str) -> dict:
        match = re.match(
            r"^(feat|fix|docs|chore|refactor|test|ci)(\(.+\))?(!)?: (.+)$",
            message,
        )
        if not match:
            return {
                "type": "other",
                "description": message,
                "breaking": "BREAKING CHANGE" in message,
            }

        commit_type, _, bang, description = match.groups()
        return {
            "type": commit_type,
            "description": description,
            "breaking": bang == "!" or "BREAKING CHANGE" in message,
        }

    def analyze_commits(self):
        tag_range = f"{self.current_version}..HEAD"
        log = subprocess.check_output(
            ["git", "log", tag_range, "--pretty=format:%s%x00"],
            cwd=self.repo_root,
            text=True,
        )
        entries = [e.strip() for e in log.split("\x00") if e.strip()]

        for entry in entries:
            commit = self.parse_commit(entry)
            self.commits.append(commit)
            if commit["breaking"]:
                self.breaking_changes += 1
            elif commit["type"] == "feat":
                self.features += 1
            elif commit["type"] == "fix":
                self.fixes += 1

    def calculate_new_version(self) -> str:
        major, minor, patch = map(int, self.current_version.lstrip("v").split("."))
        if self.breaking_changes > 0:
            major += 1
            minor = patch = 0
        elif self.features > 0:
            minor += 1
            patch = 0
        else:
            patch += 1
        return f"v{major}.{minor}.{patch}"

    def update_changelog(self, new_version: str):
        print(f"{BLUE}Updating CHANGELOG.md...{NC}")
        changelog = self.repo_root / "CHANGELOG.md"
        today = datetime.now().strftime("%Y-%m-%d")

        new_entry = f"## [{new_version}] - {today}\n"

        if self.features > 0:
            new_entry += "\n### Added\n"
            for commit in self.commits:
                if commit["type"] == "feat":
                    new_entry += f"- {commit['description']}\n"

        if self.fixes > 0:
            new_entry += "\n### Fixed\n"
            for commit in self.commits:
                if commit["type"] == "fix":
                    new_entry += f"- {commit['description']}\n"

        new_entry += "\n"

        if changelog.exists():
            content = changelog.read_text(encoding="utf-8")
            # Look for the first existing version header
            match = re.search(r"(## \[v\d+\.\d+\.\d+\])", content)
            if match:
                idx = match.start()
                content = content[:idx] + new_entry + content[idx:]
            else:
                # If no version header found, append after intro
                if "# Changelog" in content:
                    content = content.replace(
                        "# Changelog", "# Changelog\n\n" + new_entry.strip()
                    )
                else:
                    content = "# Changelog\n\n" + new_entry + content
        else:
            content = "# Changelog\n\n" + new_entry

        changelog.write_text(content, encoding="utf-8")

    def quality_check(self) -> bool:
        """Run check-kit.py to validate code quality before release."""
        print(f"{BLUE}Running quality checks...{NC}")
        result = subprocess.run(
            ["python3", "scripts/check-kit.py"],
            cwd=self.repo_root,
        )
        if result.returncode != 0:
            print(f"{RED}✗ Quality check failed — fix issues before releasing.{NC}")
            return False
        print(f"{GREEN}✓ Quality check passed{NC}")
        return True

    def format_files(self) -> bool:
        """Run 'just format' to ensure CHANGELOG and code are clean."""
        print(f"{BLUE}Formatting files...{NC}")
        try:
            subprocess.run(
                ["just", "format"],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"{GREEN}✓ Files formatted{NC}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"{RED}⚠ Formatting failed: {e}{NC}")
            return False

    def run(self, yes: bool = False, force_version: str = ""):
        # Strict quality check — files must already be well-formatted before release
        print(f"{BLUE}Running strict quality check (release mode)...{NC}")
        result = subprocess.run(
            ["python3", "scripts/check-kit.py", "--strict"],
            cwd=self.repo_root,
        )
        if result.returncode != 0:
            print(f"{RED}✗ Quality check failed — run 'just format' to fix issues.{NC}")
            return

        self.analyze_commits()
        new_version = force_version if force_version else self.calculate_new_version()

        print(f"{BLUE}Current: {self.current_version} | Suggested: {new_version}{NC}")
        if not yes:
            confirm = input(f"{YELLOW}Release {new_version}? (y/n): {NC}")
            if confirm.lower() != "y":
                print("Release aborted.")
                return

        self.update_changelog(new_version)

        if not self.format_files():
            print(f"{RED}Release cancelled due to formatting error.{NC}")
            return

        subprocess.run(["git", "add", "CHANGELOG.md"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"chore: release {new_version}"], check=True
        )
        subprocess.run(["git", "tag", new_version], check=True)

        print(f"{GREEN}Successfully tagged {new_version}{NC}")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        subprocess.run(["git", "push", "origin", new_version], check=True)


if __name__ == "__main__":
    import sys

    _yes = "-y" in sys.argv or "--yes" in sys.argv
    _version = next((a for a in sys.argv[1:] if a.startswith("v")), "")
    ReleaseManager().run(yes=_yes, force_version=_version)
