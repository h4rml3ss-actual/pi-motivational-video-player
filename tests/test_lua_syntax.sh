#!/usr/bin/env bash
# Integration test: syntax check all Lua modules
set -euo pipefail

echo "Checking Lua syntax..."

# Check core Lua files
for f in \
    core/player.lua \
    core/hud/modules/*.lua \
; do
    if [ -f "$f" ]; then
        luac -p "$f"
    fi
done

# Check any additional Lua files in root directory
for f in *.lua; do
    if [ -f "$f" ]; then
        luac -p "$f"
    fi
done

echo "Lua syntax OK."
