#!/usr/bin/env python3
"""Kit quality checker — validates Python, Bash, and Markdown files in this repo."""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

BLUE = "\033[0;34m"
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
NC = "\033[0m"

REPO_ROOT = Path(__file__).parent.parent

PYTHON_DIRS = ["scripts", "kit/scripts"]
BASH_DIRS = ["kit/scripts", "kit/githooks"]


class KitChecker:
    def __init__(self, fast_mode: bool = False, strict_mode: bool = False):
        self.fast_mode = fast_mode
        self.strict_mode = (
            strict_mode  # For releases: all checks must pass, no auto-skip
        )
        self.results: dict[str, Optional[bool]] = {}
        self.suite_failed = False

    def _header(self, title: str) -> None:
        print(f"\n{BLUE}🚀 {title}{NC}")
        print(f"{BLUE}{'═' * 59}{NC}")

    def _step(self, name: str, cmd: list[str]) -> bool:
        print(f"\n{BLUE}▶ {name}...{NC}")
        result = subprocess.run(cmd, cwd=REPO_ROOT)
        ok = result.returncode == 0
        if ok:
            print(f"{GREEN}✓ {name}: Passed{NC}")
        else:
            print(f"{RED}✗ {name}: Failed (exit {result.returncode}){NC}")
            self.suite_failed = True
        self.results[name] = ok
        return ok

    def _tool_exists(self, tool: str) -> bool:
        return shutil.which(tool) is not None

    def run(self) -> bool:
        self._header("Kit Quality Check")

        # Python — ruff lint
        self._step(
            "Ruff lint",
            ["ruff", "check"] + PYTHON_DIRS,
        )

        # Python — ruff format check
        # In strict mode (releases): always check format. In fast mode: skip.
        if not self.fast_mode:
            self._step(
                "Ruff format",
                ["ruff", "format", "--check"] + PYTHON_DIRS,
            )

        # Bash — shfmt format check
        bash_files = self._collect_bash_files()
        if bash_files:
            self._step("shfmt", ["shfmt", "-d", "-i", "4"] + bash_files)
        else:
            print(f"{YELLOW}⚠ shfmt: no Bash files found, skipping.{NC}")

        # Bash — shellcheck (optional, skip if not installed)
        if self._tool_exists("shellcheck"):
            if bash_files:
                self._step("shellcheck", ["shellcheck"] + bash_files)
        else:
            print(f"{YELLOW}ℹ shellcheck not installed, skipping.{NC}")

        # Markdown — prettier check
        # In strict mode (releases): fail if prettier not available. Otherwise: skip safely.
        if not self.fast_mode:
            if self._tool_exists("npx"):
                self._step(
                    "Prettier (markdown)",
                    [
                        "npx",
                        "prettier",
                        "--check",
                        "**/*.md",
                        "--ignore-path",
                        ".gitignore",
                    ],
                )
            elif self.strict_mode:
                print(
                    f"{RED}✗ Prettier not installed — required for release checks.{NC}"
                )
                print("  Install with: npm install -g prettier")
                self.results["Prettier (markdown)"] = False
                self.suite_failed = True
            else:
                print(f"{YELLOW}ℹ npx not installed, skipping Prettier.{NC}")

        self._report()
        return not self.suite_failed

    def _collect_bash_files(self) -> list[str]:
        files: list[str] = []
        for d in BASH_DIRS:
            p = REPO_ROOT / d
            if not p.exists():
                continue
            for f in p.iterdir():
                if f.is_file() and (f.suffix == ".sh" or self._is_bash(f)):
                    files.append(str(f.relative_to(REPO_ROOT)))
        return files

    def _is_bash(self, path: Path) -> bool:
        try:
            first = path.read_text(encoding="utf-8").splitlines()[0]
            return "bash" in first
        except (OSError, IndexError):
            return False

    def _report(self) -> None:
        self._header("Final Quality Report")
        print(f"| {'Check':<25} | {'Status':<10} |")
        print(f"|{'-' * 27}|{'-' * 12}|")
        for name, ok in self.results.items():
            status = f"{GREEN}✅ Pass{NC}" if ok else f"{RED}❌ Fail{NC}"
            print(f"| {name:<25} | {status:<20} |")
        if self.suite_failed:
            print(f"\n{RED}❌ SUITE FAILED — check logs above{NC}\n")
        else:
            print(f"\n{GREEN}✨ ALL CHECKS PASSED{NC}\n")


if __name__ == "__main__":
    fast = "--fast" in sys.argv
    strict = "--strict" in sys.argv
    if not KitChecker(fast_mode=fast, strict_mode=strict).run():
        sys.exit(1)
