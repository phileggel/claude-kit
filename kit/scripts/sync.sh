#!/usr/bin/env bash
set -euo pipefail

# sync.sh — Sync logic for claude-kit (Tauri-only).
#
# Executed from the cloned kit by the bootstrap (kit/sync-config.sh).
# This script is ephemeral — it runs from $TMP and is cleaned up on exit.
# Never run this script directly.
#
# Env vars:
#   KIT_TMP        — path to the cloned kit temp directory (required)
#   KIT_SYNC_FORCE — set to "true" to overwrite drifted docs without prompting (-f flag)

TMP="${KIT_TMP:?KIT_TMP not set — run via scripts/sync-config.sh}"
VERSION="${1:?VERSION not set}"
KIT_SYNC_FORCE="${KIT_SYNC_FORCE:-false}"

_sha1() { python3 -c "import hashlib,sys; print(hashlib.sha1(open(sys.argv[1],'rb').read(),usedforsecurity=False).hexdigest())" "$1"; }

trap 'rm -rf "$TMP"' EXIT

# Colors (respect NO_COLOR=1)
if [ -n "${NO_COLOR:-}" ]; then
    YELLOW='' GREEN='' BLUE='' NC=''
else
    YELLOW='\033[0;33m'
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    NC='\033[0m'
fi

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
MANIFEST="$PROJECT_ROOT/.claude/kit-manifest.txt"

# Manifest of every file the sync writes — consumed by `bash scripts/validate-sync.sh`
# (invoked by the /kit-discover skill).
# Paths are relative to PROJECT_ROOT, one per line, sorted at end.
mkdir -p "$PROJECT_ROOT/.claude"
: >"$MANIFEST"

_record() { printf '%s\n' "$1" >>"$MANIFEST"; }

# ── Kit index & readme ────────────────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing kit index and readme...${NC}"
cp "$TMP/kit/kit-tools.md" "$PROJECT_ROOT/.claude/"
_record ".claude/kit-tools.md"
cp "$TMP/kit/kit-readme.md" "$PROJECT_ROOT/.claude/"
_record ".claude/kit-readme.md"

# ── Agents ────────────────────────────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing agents...${NC}"
mkdir -p "$PROJECT_ROOT/.claude/agents"
for agent in "$TMP/kit/agents/"*.md; do
    [ -f "$agent" ] || continue
    name=$(basename "$agent")
    cp "$agent" "$PROJECT_ROOT/.claude/agents/"
    _record ".claude/agents/$name"
done

# ── Skills ────────────────────────────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing skills...${NC}"
for skill_dir in "$TMP/kit/skills/"/*/; do
    [ -d "$skill_dir" ] || continue
    [ -f "$skill_dir/SKILL.md" ] || continue
    skill_name=$(basename "$skill_dir")
    mkdir -p "$PROJECT_ROOT/.claude/skills/$skill_name"
    cp "$skill_dir/SKILL.md" "$PROJECT_ROOT/.claude/skills/$skill_name/"
    _record ".claude/skills/$skill_name/SKILL.md"
done

# ── Git hooks ─────────────────────────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing .githooks...${NC}"
mkdir -p "$PROJECT_ROOT/.githooks"
for hook in commit-msg pre-commit pre-merge-commit pre-push README.md; do
    cp "$TMP/kit/githooks/$hook" "$PROJECT_ROOT/.githooks/"
    _record ".githooks/$hook"
done

# ── common.just (per-recipe override detection) ──────────────────────────────
echo -e "${BLUE}📁 Syncing common justfile...${NC}"

# Collect recipe names defined in any local .just / justfile EXCEPT common.just
# (which we are about to overwrite). Each kit recipe whose name collides with
# a local definition is skipped from the synced common.just so the local one wins.
_local_recipes=""
for _f in "$PROJECT_ROOT"/*.just "$PROJECT_ROOT"/justfile; do
    [ -f "$_f" ] || continue
    [ "$(basename "$_f")" = "common.just" ] && continue
    _local_recipes+=$(grep -hE '^[a-zA-Z_][a-zA-Z0-9_-]*[^:]*:' "$_f" 2>/dev/null | sed -E 's/[ *:].*//')$'\n'
done
_local_recipes=$(printf '%s' "$_local_recipes" | sort -u | sed '/^$/d')

_record "common.just"
if [ -z "$_local_recipes" ]; then
    cp "$TMP/kit/common.just" "$PROJECT_ROOT/common.just"
else
    KIT_COMMON="$TMP/kit/common.just" \
        DEST_COMMON="$PROJECT_ROOT/common.just" \
        LOCAL_RECIPES="$_local_recipes" \
        python3 <<'PY'
import os, re, sys
locals_set = set(os.environ['LOCAL_RECIPES'].split())
src = open(os.environ['KIT_COMMON']).read()
recipe_re = re.compile(
    r'(?:^# [^\n]*\n)*^(?P<name>[a-zA-Z_][a-zA-Z0-9_-]*)[^:\n]*:[^\n]*\n(?:[ \t][^\n]*\n)*',
    re.MULTILINE,
)
skipped = []
def _filter(m):
    if m.group('name') in locals_set:
        skipped.append(m.group('name'))
        return ''
    return m.group(0)
out = recipe_re.sub(_filter, src)
out = re.sub(r'\n{3,}', '\n\n', out)
open(os.environ['DEST_COMMON'], 'w').write(out)
for n in skipped:
    print(f"  \033[1;33m⚠  {n} already defined locally — skipping kit default\033[0m")
PY
fi

# ── Scripts ───────────────────────────────────────────────────────────────────
echo -e "${BLUE}📁 Syncing scripts...${NC}"
mkdir -p "$PROJECT_ROOT/scripts"
for f in "$TMP/kit/scripts/"*.sh; do
    [ -f "$f" ] || continue
    base="$(basename "$f")"
    # sync.sh is kit-internal — never copy it to downstream
    [ "$base" = "sync.sh" ] && continue
    cp "$f" "$PROJECT_ROOT/scripts/$base"
    chmod +x "$PROJECT_ROOT/scripts/$base"
    _record "scripts/$base"
done
for f in "$TMP/kit/scripts/"*.py; do
    [ -f "$f" ] || continue
    base="$(basename "$f")"
    cp "$f" "$PROJECT_ROOT/scripts/"
    _record "scripts/$base"
done

# Hint about the previous quirk where sync.sh was copied to downstream
if [ -f "$PROJECT_ROOT/scripts/sync.sh" ]; then
    echo -e "${BLUE}ℹ scripts/sync.sh is kit-internal (no longer copied). Safe to delete.${NC}"
fi

# ── Docs (overwrite if unchanged; prompt on local drift; -f to force) ─────────
echo -e "${BLUE}📁 Syncing docs...${NC}"
mkdir -p "$PROJECT_ROOT/docs"
for doc in "$TMP/kit/docs/"*.md; do
    [ -f "$doc" ] || continue
    doc_name=$(basename "$doc")
    dest="$PROJECT_ROOT/docs/$doc_name"
    if [ ! -f "$dest" ]; then
        cp "$doc" "$dest"
        echo -e "  → docs/$doc_name (new)"
    elif [ "$(_sha1 "$doc")" = "$(_sha1 "$dest")" ]; then
        : # identical — silent, no drift
    elif [ "$KIT_SYNC_FORCE" = "true" ]; then
        cp "$doc" "$dest"
        echo -e "  ↑ docs/$doc_name (overwritten — local differed from kit)"
    elif [ -e /dev/tty ] && [ -r /dev/tty ]; then
        printf "  ⚠  docs/%s differs from kit. Overwrite? [y/N] " "$doc_name"
        read -r _answer </dev/tty || _answer="n"
        if [[ "$_answer" =~ ^[Yy] ]]; then
            cp "$doc" "$dest"
            echo -e "  ↑ docs/$doc_name (overwritten)"
        else
            echo -e "  ↩ docs/$doc_name (skipped — local copy kept)"
        fi
    else
        echo -e "  ↩ docs/$doc_name (skipped — non-interactive; pass -f to overwrite)"
    fi
done

# ── Vestigial profile file warning ────────────────────────────────────────────
if [ -f "$PROJECT_ROOT/.claude/kit-profile" ]; then
    echo -e "${BLUE}ℹ .claude/kit-profile is vestigial (kit is now Tauri-only). Safe to delete.${NC}"
fi

# ── Version stamp & changelog delta ───────────────────────────────────────────
PREV_VERSION=""
if [ -f "$PROJECT_ROOT/.claude/kit-version.md" ]; then
    PREV_VERSION=$(grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' "$PROJECT_ROOT/.claude/kit-version.md" | head -n1 || true)
fi
if [ -z "$PREV_VERSION" ] && [ -f "$PROJECT_ROOT/.claude-kit-version" ]; then
    PREV_VERSION=$(tr -d '[:space:]' <"$PROJECT_ROOT/.claude-kit-version")
fi

TODAY=$(date +%Y-%m-%d)

if [ -z "$PREV_VERSION" ]; then
    DELTA_BODY="_Initial install._"
elif [ "$PREV_VERSION" = "$VERSION" ]; then
    DELTA_BODY="_No changes since previous sync._"
else
    DELTA=$(
        python3 - "$TMP/CHANGELOG.md" "$PREV_VERSION" "$VERSION" <<'_PY_DELTA_EOF'
import re, sys
path, prev, curr = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    text = open(path, encoding='utf-8').read()
except FileNotFoundError:
    sys.exit(0)
header = re.compile(r'^## \[(v\d+\.\d+\.\d+)\].*$', re.MULTILINE)
matches = list(header.finditer(text))
collecting, out = False, []
for i, m in enumerate(matches):
    version = m.group(1)
    if not collecting:
        if version == curr:
            collecting = True
        else:
            continue
    if version == prev:
        break
    start = m.end()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    bullets = re.findall(r'^- (.+)$', text[start:end], re.MULTILINE)
    summary = '; '.join(bullets) if bullets else '(no changes recorded)'
    out.append(f"- {version}: {summary}")
print('\n'.join(out))
_PY_DELTA_EOF
    )
    if [ -n "$DELTA" ]; then
        DELTA_BODY="## Changes since ${PREV_VERSION} (your previous sync)

${DELTA}"
    else
        DELTA_BODY="_No changelog entries between ${PREV_VERSION} and ${VERSION}._"
    fi
fi

cat >"$PROJECT_ROOT/.claude/kit-version.md" <<EOF
# Kit version

claude-kit **${VERSION}** — synced ${TODAY}

${DELTA_BODY}
EOF
_record ".claude/kit-version.md"

# Sort manifest for deterministic diffs
sort -u -o "$MANIFEST" "$MANIFEST"

# Remove legacy version file — superseded by .claude/kit-version.md
rm -f "$PROJECT_ROOT/.claude-kit-version"

echo -e "${GREEN}✅ Synced claude-kit@${VERSION}${NC}"
echo -e "${BLUE}→ Review changes before committing (git diff).${NC}"
if [ -n "$PREV_VERSION" ] && [ "$PREV_VERSION" != "$VERSION" ]; then
    echo -e "${BLUE}→ Run /kit-discover to reconcile CLAUDE.md with the new kit surface.${NC}"
fi
