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
        self._check_start_template_references()
        self._check_skill_conventions()
        self._check_workflow_gate_drift()

        self._print_artifact_metrics()

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

    def _check_workflow_gate_drift(self) -> bool:
        """Verify workflow gates stay in sync between start and feature-planner.

        Both `start`'s Workflow A template and `feature-planner`'s emitted
        Workflow TaskList list the gates (agents and slash commands) the main
        agent must execute during implementation. If they drift, the main
        agent runs different sequences depending on which artifact it follows.

        Compares Phase 2/3/4 of start's Workflow A (after plan-reviewer
        green-lights) against feature-planner's Workflow TaskList. Phase 1
        gates are excluded — they run before the plan is written and are
        irrelevant to the post-plan implementation TaskList.
        """
        start_path = REPO_ROOT / "kit" / "skills" / "start" / "SKILL.md"
        planner_path = REPO_ROOT / "kit" / "agents" / "feature-planner.md"
        if not start_path.exists() or not planner_path.exists():
            return True

        slash_pat = re.compile(r"`/([a-z][a-z0-9-]*)`")
        agent_pat = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`")

        def extract_gates(lines: list[str]) -> set[str]:
            gates: set[str] = set()
            for line in lines:
                for m in slash_pat.finditer(line):
                    gates.add(f"/{m.group(1)}")
                for m in agent_pat.finditer(line):
                    name = m.group(1)
                    if "/" in name or "." in name:
                        continue
                    gates.add(name)
            return gates

        start_lines = start_path.read_text(encoding="utf-8").splitlines()
        in_workflow_a = False
        in_fence = False
        in_phase_2plus = False
        start_gate_lines: list[str] = []
        for line in start_lines:
            if line.strip() == "### If Workflow A:":
                in_workflow_a = True
                continue
            if not in_workflow_a:
                continue
            if line.lstrip().startswith("```"):
                if in_fence:
                    break
                in_fence = True
                continue
            if not in_fence:
                continue
            if (
                line.startswith("### Phase 2")
                or line.startswith("### Phase 3")
                or line.startswith("### Phase 4")
            ):
                in_phase_2plus = True
                continue
            if in_phase_2plus:
                start_gate_lines.append(line)

        start_gates = extract_gates(start_gate_lines)

        planner_lines = planner_path.read_text(encoding="utf-8").splitlines()
        in_tasklist = False
        planner_gate_lines: list[str] = []
        for line in planner_lines:
            if line.startswith("### 1. Workflow TaskList"):
                in_tasklist = True
                continue
            if in_tasklist and line.startswith("### "):
                in_tasklist = False
                continue
            if in_tasklist:
                planner_gate_lines.append(line)

        planner_gates = extract_gates(planner_gate_lines)

        failures: list[str] = []
        for gate in sorted(start_gates - planner_gates):
            failures.append(
                f"start's Workflow A Phase 2/3/4 mentions `{gate}` but feature-planner's TaskList doesn't"
            )
        for gate in sorted(planner_gates - start_gates):
            failures.append(
                f"feature-planner's TaskList mentions `{gate}` but start's Workflow A Phase 2/3/4 doesn't"
            )

        if failures:
            print("  Workflow gate drift...")
            for f in failures:
                print(f"    ✗ {f}")
            self.suite_failed = True
            self.results["Workflow gate drift"] = False
            return False

        self.results["Workflow gate drift"] = True
        return True

    def _print_artifact_metrics(self) -> None:
        """Surface size/density metrics for agents and skills (informational only).

        Bloat in agent/skill files costs model context, dilutes attention on
        long instructions, and lets quiet inconsistencies accumulate. Lists
        artifacts that exceed soft thresholds on three mechanical signals:
        file length, longest section, Critical Rules entry count. Does not
        fail the suite; `ai-reviewer` interprets whether a flagged artifact
        is genuinely bloated or appropriately complex.
        """
        LINE_THRESHOLD = 300
        SECTION_THRESHOLD = 60
        RULES_THRESHOLD = 12

        targets: list[Path] = []
        targets.extend(sorted((REPO_ROOT / "kit" / "agents").glob("*.md")))
        targets.extend(sorted((REPO_ROOT / "kit" / "skills").glob("*/SKILL.md")))

        rules_item_pat = re.compile(r"^\d+\.\s")
        flagged: list[str] = []

        for path in targets:
            rel = str(path.relative_to(REPO_ROOT))
            lines = path.read_text(encoding="utf-8").splitlines()
            line_count = len(lines)

            sections: list[tuple[str, int]] = []
            rules_count = 0
            in_fence = False
            in_rules = False
            for i, line in enumerate(lines):
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                if line.startswith("## "):
                    heading = line[3:].strip()
                    sections.append((heading, i))
                    in_rules = heading == "Critical Rules"
                    continue
                if in_rules and rules_item_pat.match(line):
                    rules_count += 1

            longest_len = 0
            longest_heading = ""
            for idx, (heading, start) in enumerate(sections):
                end = sections[idx + 1][1] if idx + 1 < len(sections) else len(lines)
                length = end - start
                if length > longest_len:
                    longest_len = length
                    longest_heading = heading

            flags: list[str] = []
            if line_count >= LINE_THRESHOLD:
                flags.append(f"{line_count} lines")
            if longest_len >= SECTION_THRESHOLD:
                flags.append(
                    f"longest section '{longest_heading}' is {longest_len} lines"
                )
            if rules_count >= RULES_THRESHOLD:
                flags.append(f"{rules_count} critical rules")

            if flags:
                flagged.append(f"  {rel}: {'; '.join(flags)}")

        if flagged:
            print(
                f"\n{YELLOW}ℹ Density signals (ai-reviewer territory; not blocking):{NC}"
            )
            for entry in flagged:
                print(f"{YELLOW}{entry}{NC}")

    def _check_skill_conventions(self) -> bool:
        """Verify every kit/skills/*/SKILL.md has the required convention sections.

        Required sections: `## When to use` and `## Output format`. These document
        the trigger and the produced output, and are load-bearing for downstream
        routing and consumption.

        Skills in `GRANDFATHER` are exempted as a known TODO — the kit
        standardised on the skill-section triplet during the v4.2 cycle, and
        these older skills predate it. Do NOT add new entries to the
        grandfather list — fix the skill instead. The list should shrink to
        empty over time as skills are brought up to convention.
        """
        GRANDFATHER = {
            "adr-writer",
            "create-pr",
            "dep-audit",
            "setup-e2e",
            "smart-commit",
            "techdebt",
            "visual-proof",
        }
        REQUIRED_SECTIONS = ["## When to use", "## Output format"]

        failures: list[str] = []
        for skill_path in sorted((REPO_ROOT / "kit" / "skills").glob("*/SKILL.md")):
            skill_name = skill_path.parent.name
            if skill_name in GRANDFATHER:
                continue
            content = skill_path.read_text(encoding="utf-8")
            rel = str(skill_path.relative_to(REPO_ROOT))
            for section in REQUIRED_SECTIONS:
                pattern = rf"^{re.escape(section)}\s*$"
                if not re.search(pattern, content, re.MULTILINE):
                    failures.append(f"{rel}: missing '{section}' section")

        if failures:
            print("  Skill conventions...")
            for f in failures:
                print(f"    ✗ {f}")
            self.suite_failed = True
            self.results["Skill conventions"] = False
            return False

        self.results["Skill conventions"] = True
        return True

    def _check_start_template_references(self) -> bool:
        """Verify every agent/skill reference in start/SKILL.md fenced templates exists.

        The start skill emits Workflow A/B templates that name specific agents and
        slash commands. If those names drift (rename, removal), the template
        silently lies. This check parses every fenced block in the file and
        confirms each `/skill-name` and kebab-case `agent-name` reference resolves
        to an actual kit artifact.
        """
        start_path = REPO_ROOT / "kit" / "skills" / "start" / "SKILL.md"
        if not start_path.exists():
            return True

        valid_agents = {p.stem for p in (REPO_ROOT / "kit" / "agents").glob("*.md")}
        valid_skills = {
            p.parent.name for p in (REPO_ROOT / "kit" / "skills").glob("*/SKILL.md")
        }

        slash_pat = re.compile(r"`/([a-z][a-z0-9-]*)`")
        agent_pat = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`")

        failures: list[str] = []
        in_fence = False
        for lineno, line in enumerate(
            start_path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence:
                continue
            for m in slash_pat.finditer(line):
                name = m.group(1)
                if name not in valid_skills:
                    failures.append(
                        f"kit/skills/start/SKILL.md:{lineno}: '/{name}' not found in kit/skills/"
                    )
            for m in agent_pat.finditer(line):
                name = m.group(1)
                if name not in valid_agents and name not in valid_skills:
                    failures.append(
                        f"kit/skills/start/SKILL.md:{lineno}: '`{name}`' not found in kit/agents/ or kit/skills/"
                    )

        if failures:
            print("  Start template references...")
            for f in failures:
                print(f"    ✗ {f}")
            self.suite_failed = True
            self.results["Start template references"] = False
            return False

        self.results["Start template references"] = True
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
