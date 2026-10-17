#!/usr/bin/env bash
# Copies the vsd-feature-lifecycle skills into Codex (${CODEX_HOME:-~/.codex}/skills).
# The skills use paths relative to their own folders, so they copy verbatim.
# Usage: install-codex.sh [PLUGIN_DIR]  (default: the newest installed copy). Re-run after updates.
set -euo pipefail
PLUGIN_DIR="${1:-}"
if [ -z "$PLUGIN_DIR" ]; then
  PLUGIN_DIR="$(ls -d "$HOME"/.claude/plugins/cache/verosoft-design/vsd-feature-lifecycle/* 2>/dev/null | sort -V | tail -1)"
fi
if [ -z "$PLUGIN_DIR" ] || [ ! -d "$PLUGIN_DIR/skills" ]; then
  echo "vsd-feature-lifecycle not found; pass the plugin folder" >&2
  exit 1
fi
DEST="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$DEST"
count=0
for skill in "$PLUGIN_DIR"/skills/*/; do
  name="$(basename "$skill")"
  rm -rf "${DEST:?}/$name"
  cp -R "$skill" "$DEST/$name"
  count=$((count + 1))
done
echo "installed $count skills from $PLUGIN_DIR into $DEST"
