#!/usr/bin/env python3
"""Quality checker for Axum + React/TypeScript projects (web profile).

Fast mode (--fast): format-check + lint only.
Full mode (default): fast checks + build + tests.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
SERVER = next(
    (ROOT / d for d in ["server", "backend"] if (ROOT / d).is_dir()), ROOT / "server"
)
CLIENT = next(
    (ROOT / d for d in ["client", "frontend"] if (ROOT / d).is_dir()), ROOT / "client"
)

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
NC = "\033[0m"


def run_cmd(cmd, cwd=None, env=None):
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr


def check(label, cmd, cwd=None, env=None):
    start = time.monotonic()
    passed, output = run_cmd(cmd, cwd=cwd, env=env)
    duration = time.monotonic() - start
    symbol = f"{GREEN}PASS{NC}" if passed else f"{RED}FAIL{NC}"
    print(f"  {label:<30} {symbol}  ({duration:.1f}s)")
    return label, passed, duration, output


def main():
    parser = argparse.ArgumentParser(
        description="Quality checks for Axum + React project"
    )
    parser.add_argument(
        "--fast", action="store_true", help="Lint/format only, skip build and tests"
    )
    args = parser.parse_args()

    mode = "FAST" if args.fast else "FULL"
    print(f"{BOLD}{BLUE}=== Quality Check [{mode}] ==={NC}\n")

    results = []

    # ── Backend: Rust ────────────────────────────────────────────────────────
    print(f"{YELLOW}Backend (Rust){NC}")
    results.append(check("cargo fmt --check", ["cargo", "fmt", "--check"], cwd=SERVER))
    results.append(
        check("cargo clippy", ["cargo", "clippy", "--", "-D", "warnings"], cwd=SERVER)
    )

    if not args.fast:
        sqlx_env = {**os.environ, "SQLX_OFFLINE": "true"}
        results.append(
            check("cargo build", ["cargo", "build"], cwd=SERVER, env=sqlx_env)
        )
        results.append(check("cargo test", ["cargo", "test"], cwd=SERVER, env=sqlx_env))

    # ── Frontend: TypeScript / React ─────────────────────────────────────────
    print(f"\n{YELLOW}Frontend (TypeScript){NC}")
    results.append(check("eslint", ["npx", "eslint", "."], cwd=CLIENT))
    results.append(check("tsc --noEmit", ["npx", "tsc", "--noEmit"], cwd=CLIENT))

    if not args.fast:
        results.append(check("vitest run", ["npx", "vitest", "run"], cwd=CLIENT))
        results.append(check("vite build", ["npx", "vite", "build"], cwd=CLIENT))

    # ── Summary ──────────────────────────────────────────────────────────────
    failures = [r for r in results if not r[1]]
    total = len(results)
    passed = total - len(failures)

    print(f"\n{BOLD}{'─' * 44}{NC}")
    print(f"  {passed}/{total} checks passed")

    if failures:
        print(f"\n{RED}Failed checks:{NC}")
        for label, _, _, output in failures:
            print(f"\n  [{label}]")
            tail = output.strip().splitlines()[-20:]
            for line in tail:
                print(f"    {line}")
        print(f"\n{RED}❌ {len(failures)} check(s) failed.{NC}")
        sys.exit(1)

    print(f"{GREEN}✅ All checks passed.{NC}")
    sys.exit(0)


if __name__ == "__main__":
    main()
