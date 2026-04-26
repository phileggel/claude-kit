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

# Profile subdirs treated as known gaps — not errors when empty or .gitkeep only
PLANNED_PROFILE_DIRS = [
    "kit/agents/web",
    "kit/scripts/web",
]


class KitChecker:
    def __init__(
        self, fast_mode: bool = False, strict_mode: bool = False, verbose: bool = False
    ):
        self.fast_mode = fast_mode
        self.strict_mode = strict_mode
        self.verbose = verbose
        self.results: dict[str, Optional[bool]] = {}
        self.suite_failed = False
        self.failures: dict[str, str] = {}

    def _vprint(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

    def _header(self, title: str) -> None:
        self._vprint(f"\n{BLUE}🚀 {title}{NC}")
        self._vprint(f"{BLUE}{'═' * 59}{NC}")

    def _step(self, name: str, cmd: list[str]) -> bool:
        print(f"  {name}...", flush=True)
        self._vprint(f"\n{BLUE}▶ {name}...{NC}")
        if self.verbose:
            result = subprocess.run(cmd, cwd=REPO_ROOT)
            output = ""
        else:
            result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
            output = (result.stdout + result.stderr).strip()
        ok = result.returncode == 0
        if ok:
            self._vprint(f"{GREEN}✓ {name}: Passed{NC}")
        else:
            self._vprint(f"{RED}✗ {name}: Failed (exit {result.returncode}){NC}")
            self.suite_failed = True
            if output:
                self.failures[name] = output
        self.results[name] = ok
        return ok

    def _tool_exists(self, tool: str) -> bool:
        return shutil.which(tool) is not None

    def run(self) -> bool:
        self._header("Kit Quality Check")

        self._step("Ruff lint", ["ruff", "check"] + PYTHON_DIRS)

        if not self.fast_mode:
            self._step("Ruff format", ["ruff", "format", "--check"] + PYTHON_DIRS)

        bash_files = self._collect_bash_files()
        if bash_files:
            self._step("shfmt", ["shfmt", "-d", "-i", "4"] + bash_files)
        else:
            self._vprint(f"{YELLOW}⚠ shfmt: no Bash files found, skipping.{NC}")

        if self._tool_exists("shellcheck"):
            if bash_files:
                self._step("shellcheck", ["shellcheck"] + bash_files)
        else:
            self._vprint(f"{YELLOW}ℹ shellcheck not installed, skipping.{NC}")

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
                self._vprint(f"{YELLOW}ℹ npx not installed, skipping Prettier.{NC}")

        self._check_agent_inventory()

        self._report()
        return not self.suite_failed

    def _check_agent_inventory(self) -> bool:
        """Verify every agent in kit/agents/ and kit/agents/tauri/ is listed in kit-tools.md."""
        tools_path = REPO_ROOT / "kit" / "kit-tools.md"
        if not tools_path.exists():
            return True
        tools_content = tools_path.read_text(encoding="utf-8")

        missing: list[str] = []
        for pattern in ["kit/agents/*.md", "kit/agents/tauri/*.md"]:
            for agent_path in sorted((REPO_ROOT).glob(pattern)):
                agent_name = agent_path.stem
                if f"`{agent_name}`" not in tools_content:
                    missing.append(f"{agent_path.relative_to(REPO_ROOT)}")

        if missing:
            print("  Agent inventory...")
            for m in missing:
                print(f"    ✗ {m} not listed in kit/kit-tools.md")
            self.suite_failed = True
            self.results["Agent inventory"] = False
            return False

        self.results["Agent inventory"] = True
        return True

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
        print(f"\n{BLUE}🚀 Quality Report{NC}")
        print(f"| {'Check':<25} | {'Status':<10} |")
        print(f"|{'-' * 27}|{'-' * 12}|")
        for name, ok in self.results.items():
            status = f"{GREEN}✅ Pass{NC}" if ok else f"{RED}❌ Fail{NC}"
            print(f"| {name:<25} | {status:<20} |")
        if self.suite_failed:
            print(f"\n{RED}❌ SUITE FAILED{NC}")
            if self.failures:
                print(f"\n{BLUE}— Failure details —{NC}")
                for step, output in self.failures.items():
                    print(f"\n{RED}▶ {step}{NC}")
                    print(output)
        else:
            print(f"\n{GREEN}✨ ALL CHECKS PASSED{NC}\n")


if __name__ == "__main__":
    fast = "--fast" in sys.argv
    strict = "--strict" in sys.argv
    verbose = "--verbose" in sys.argv
    if not KitChecker(fast_mode=fast, strict_mode=strict, verbose=verbose).run():
        sys.exit(1)
