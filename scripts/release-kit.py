#!/usr/bin/env python3
"""
Release script for tauri-claude-kit.
- Automatically detects version bump based on commits (feat/fix/breaking)
- Updates CHANGELOG.md
- Commits and pushes to origin
"""

import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

# ANSI colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'

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
                ['git', 'describe', '--tags', '--abbrev=0'],
                cwd=self.repo_root, text=True
            ).strip()
        except subprocess.CalledProcessError:
            return "v0.0.0"

    def parse_commit(self, message: str) -> dict:
        match = re.match(r'^(feat|fix|docs|chore|refactor|test|ci)(\(.+\))?(!)?: (.+)$', message, re.DOTALL)
        if not match:
            return {'type': 'other', 'breaking': 'BREAKING CHANGE' in message}
        
        commit_type, _, bang, _ = match.groups()
        return {'type': commit_type, 'breaking': bang == '!' or 'BREAKING CHANGE' in message}

    def analyze_commits(self):
        tag_range = f'{self.current_version}..HEAD'
        log = subprocess.check_output(['git', 'log', tag_range, '--pretty=format:%s%n%b%x00'], cwd=self.repo_root, text=True)
        entries = [e.strip() for e in log.split('\x00') if e.strip()]
        
        for entry in entries:
            commit = self.parse_commit(entry)
            if commit['breaking']: self.breaking_changes += 1
            elif commit['type'] == 'feat': self.features += 1
            elif commit['type'] == 'fix': self.fixes += 1

    def calculate_new_version(self) -> str:
        major, minor, patch = map(int, self.current_version.lstrip('v').split('.'))
        if self.breaking_changes > 0: major += 1; minor = patch = 0
        elif self.features > 0: minor += 1; patch = 0
        else: patch += 1
        return f"v{major}.{minor}.{patch}"

    def update_changelog(self, new_version: str):
        print(f"{BLUE}Updating CHANGELOG.md...{NC}")
        changelog = self.repo_root / 'CHANGELOG.md'
        today = datetime.now().strftime('%Y-%m-%d')
        new_entry = f"## [{new_version}] - {today}\n- Release {new_version}\n\n"
        
        content = new_entry
        if changelog.exists(): content += changelog.read_text(encoding='utf-8')
        changelog.write_text(content, encoding='utf-8')

    def run(self):
        self.analyze_commits()
        new_version = self.calculate_new_version()
        
        print(f"{BLUE}Current: {self.current_version} | Suggested: {new_version}{NC}")
        confirm = input(f"{YELLOW}Release {new_version}? (y/n): {NC}")
        if confirm.lower() != 'y':
            print("Release aborted.")
            return

        self.update_changelog(new_version)
        
        subprocess.run(['git', 'add', 'CHANGELOG.md'], check=True)
        subprocess.run(['git', 'commit', '-m', f'chore: release {new_version}'], check=True)
        subprocess.run(['git', 'tag', new_version], check=True)
        
        print(f"{GREEN}Successfully tagged {new_version}{NC}")
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        subprocess.run(['git', 'push', 'origin', new_version], check=True)

if __name__ == "__main__":
    ReleaseManager().run()
