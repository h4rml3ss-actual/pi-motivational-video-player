#!/usr/bin/env bash
# Integration test: syntax check all Lua modules
set -euo pipefail

echo "Checking Lua syntax..."
for f in \
    core/player.lua \
    core/hud/modules/*.lua \
; do
    luac -p "$f"
done
echo "Lua syntax OK."
