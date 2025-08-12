#!/bin/bash
# Profile switcher for VideoWall

CONFIG_DIR="$HOME/.config/videowall"
PROFILES_DIR="$CONFIG_DIR/profiles"

echo "Available profiles:"
echo "1. Cyberpunk HUD (top, cyan/magenta colors, bright effects)"
echo "2. Pure VHS (bottom, orange/brown colors, vintage effects)"
echo

read -p "Select profile (1-2): " choice

case $choice in
    1)
        cp "$PROFILES_DIR/cyberpunk_hud.json" "$CONFIG_DIR/config.json"
        echo "✓ Switched to Cyberpunk HUD profile"
        ;;
    2)
        cp "$PROFILES_DIR/pure_vhs.json" "$CONFIG_DIR/config.json"
        echo "✓ Switched to Pure VHS profile"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo "Profile switched! Restart videowall to see changes."
echo "Or press 'r' while videowall is running to reload configuration."

