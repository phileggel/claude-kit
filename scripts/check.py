#!/usr/bin/env python3
"""Kit quality checker — validates Python, Bash, and Markdown files in this repo."""

import re
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
        self._check_tool_minimality()
        self._check_kit_centric_language()
        self._check_sync_coverage()
        self._check_output_format_end_markers()
        self._check_no_settings_json_in_scripts()

        self._report()
        return not self.suite_failed

    def _agent_patterns(self) -> list[str]:
        """Return glob patterns covering all agent files."""
        return ["kit/agents/*.md"]

    def _check_agent_inventory(self) -> bool:
        """Verify every agent in kit/agents/ is listed in kit-tools.md."""
        tools_path = REPO_ROOT / "kit" / "kit-tools.md"
        if not tools_path.exists():
            return True
        tools_content = tools_path.read_text(encoding="utf-8")

        missing: list[str] = []
        for pattern in self._agent_patterns():
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

    def _check_tool_minimality(self) -> bool:
        """Enforce tool-minimality rules for review and test-writer agents."""
        REVIEW_PATTERNS = ["reviewer", "checker", "validator"]
        TEST_WRITER_PATTERN = "test-writer"

        failures: list[str] = []

        for pattern in self._agent_patterns():
            for agent_path in sorted((REPO_ROOT).glob(pattern)):
                stem = agent_path.stem.lower()
                content = agent_path.read_text(encoding="utf-8")

                tools: list[str] = []
                for line in content.splitlines():
                    if line.startswith("tools:"):
                        tools = [
                            t.strip() for t in line.replace("tools:", "").split(",")
                        ]
                        break

                rel = str(agent_path.relative_to(REPO_ROOT))
                is_review = any(pat in stem for pat in REVIEW_PATTERNS)
                is_test_writer = TEST_WRITER_PATTERN in stem

                if is_review:
                    if "Edit" in tools:
                        failures.append(
                            f"{rel}: review agent must not have Edit in tools"
                        )
                    if "Write" in tools and "## Save report" not in content:
                        failures.append(
                            f"{rel}: review agent has Write but no '## Save report' section"
                        )

                if is_test_writer:
                    if "Edit" not in tools:
                        failures.append(
                            f"{rel}: test-writer agent must have Edit in tools"
                        )
                    if "Write" not in tools:
                        failures.append(
                            f"{rel}: test-writer agent must have Write in tools"
                        )

        if failures:
            print("  Tool minimality...")
            for f in failures:
                print(f"    ✗ {f}")
            self.suite_failed = True
            self.results["Tool minimality"] = False
            return False

        self.results["Tool minimality"] = True
        return True

    def _check_kit_centric_language(self) -> bool:
        """Flag kit-centric paths or phrases inside agent/skill bodies (downstream-destined)."""
        path_pat = re.compile(r"kit/(agents|skills|scripts|justfile|githooks)/")
        phrase_pat = re.compile(
            r"\b(this kit|in this kit|synced to downstream)\b", re.IGNORECASE
        )

        targets: list[Path] = []
        for pattern in ["kit/agents/**/*.md", "kit/skills/**/SKILL.md"]:
            targets.extend(sorted(REPO_ROOT.glob(pattern)))

        failures: list[str] = []
        for path in targets:
            rel = str(path.relative_to(REPO_ROOT))
            for lineno, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1
            ):
                for m in path_pat.finditer(line):
                    failures.append(f"{rel}:{lineno}: kit-centric path '{m.group(0)}'")
                for m in phrase_pat.finditer(line):
                    failures.append(
                        f"{rel}:{lineno}: kit-centric phrase '{m.group(0)}'"
                    )

        if failures:
            print("  Kit-centric language...")
            for f in failures:
                print(f"    ✗ {f}")
            self.suite_failed = True
            self.results["Kit-centric language"] = False
            return False

        self.results["Kit-centric language"] = True
        return True

    def _check_sync_coverage(self) -> bool:
        """Verify every file sync.sh writes to .claude/ root is documented in kit-tools.md."""
        sync_path = REPO_ROOT / "kit" / "scripts" / "sync.sh"
        tools_path = REPO_ROOT / "kit" / "kit-tools.md"
        if not sync_path.exists() or not tools_path.exists():
            return True

        cp_pat = re.compile(
            r'^\s*cp\s+"\$TMP/kit/([^"]+)"\s+"\$PROJECT_ROOT/\.claude/"\s*$'
        )
        redirect_pat = re.compile(r'>\s*"\$PROJECT_ROOT/\.claude/([^/"]+)"')

        synced_files: set[str] = set()
        for line in sync_path.read_text(encoding="utf-8").splitlines():
            m = cp_pat.match(line)
            if m:
                synced_files.add(Path(m.group(1)).name)
            for m in redirect_pat.finditer(line):
                synced_files.add(m.group(1))

        tools_content = tools_path.read_text(encoding="utf-8")
        missing = sorted(f for f in synced_files if f"`{f}`" not in tools_content)

        if missing:
            print("  Sync coverage...")
            for f in missing:
                print(
                    f"    ✗ {f} written to .claude/ by sync.sh but not listed in kit/kit-tools.md"
                )
            self.suite_failed = True
            self.results["Sync coverage"] = False
            return False

        self.results["Sync coverage"] = True
        return True

    def _check_output_format_end_markers(self) -> bool:
        """Flag natural-conclusion lines in '## Output format' sections.

        Regression guard for commit 909f19b: a summary line outside a code
        block at the end of `## Output format` (e.g. `i18n check: N critical…`)
        is read by the model as task completion, causing the `## Save report`
        Write call to be skipped. Summary text must live inside the saved
        compact summary's code block, not as standalone prose.
        """
        suspect = re.compile(
            r"^\s*("
            r"final summary|review complete|result|score|verdict"
            r"|[a-z0-9-]+(?: [a-z0-9-]+)? (?:check|coverage|review)"
            r")\s*:\s+\S",
            re.IGNORECASE,
        )

        failures: list[str] = []
        for agent_path in sorted(REPO_ROOT.glob("kit/agents/**/*.md")):
            lines = agent_path.read_text(encoding="utf-8").splitlines()
            in_section = False
            in_fence = False
            rel = str(agent_path.relative_to(REPO_ROOT))
            for lineno, line in enumerate(lines, 1):
                if line.startswith("## "):
                    if line.strip() == "## Output format":
                        in_section = True
                        in_fence = False
                        continue
                    if in_section and not in_fence:
                        in_section = False
                if not in_section:
                    continue
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                if suspect.match(line):
                    failures.append(f"{rel}:{lineno}: end-marker '{line.strip()}'")

        if failures:
            print("  Output format end-markers...")
            for f in failures:
                print(f"    ✗ {f}")
            self.suite_failed = True
            self.results["Output format end-markers"] = False
            return False

        self.results["Output format end-markers"] = True
        return True

    def _check_no_settings_json_in_scripts(self) -> bool:
        """Flag any kit script that references settings.json — it must stay user-managed."""
        failures: list[str] = []
        for d in BASH_DIRS + ["kit/scripts"]:
            p = REPO_ROOT / d
            if not p.exists():
                continue
            for f in sorted(p.rglob("*")):
                if not f.is_file():
                    continue
                try:
                    text = f.read_text(encoding="utf-8")
                except OSError:
                    continue
                for lineno, line in enumerate(text.splitlines(), 1):
                    if "settings.json" in line:
                        rel = str(f.relative_to(REPO_ROOT))
                        failures.append(f"{rel}:{lineno}: references settings.json")

        if failures:
            print("  No settings.json in scripts...")
            for f in failures:
                print(f"    ✗ {f}")
            self.suite_failed = True
            self.results["No settings.json in scripts"] = False
            return False

        self.results["No settings.json in scripts"] = True
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
