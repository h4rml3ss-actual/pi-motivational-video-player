#!/bin/bash
# VideoWall troubleshooting script

echo "=== VideoWall Troubleshooting ==="
echo

# Check if postinstall was run
echo "1. Checking installation..."
if [[ -f ~/.config/videowall/player.lua ]]; then
    echo "✓ player.lua found"
    # Check if it's the correct version (should not contain expand_path)
    if grep -q "expand_path" ~/.config/videowall/player.lua; then
        echo "✗ player.lua contains old expand_path function - need to re-run postinstall.sh"
    else
        echo "✓ player.lua appears to be correct version"
    fi
else
    echo "✗ player.lua not found - need to run postinstall.sh"
fi

if [[ -d ~/.config/videowall/profiles ]]; then
    profile_count=$(ls ~/.config/videowall/profiles/*.json 2>/dev/null | wc -l)
    echo "✓ Found $profile_count profile(s)"
else
    echo "✗ No profiles directory found"
fi

echo

# Check dependencies
echo "2. Checking dependencies..."
command -v python3 >/dev/null && echo "✓ python3 found" || echo "✗ python3 missing"
command -v mpv >/dev/null && echo "✓ mpv found" || echo "✗ mpv missing"

# Check Python modules
echo "3. Checking Python modules..."
python3 -c "import jsonschema" 2>/dev/null && echo "✓ jsonschema available" || echo "✗ jsonschema missing - run: pip install jsonschema"

echo

# Check video system
echo "4. Checking video system..."
echo "Display service status:"
tvservice -s 2>/dev/null || echo "tvservice not available"

echo "Available video outputs for mpv:"
mpv --vo=help 2>/dev/null | head -10

echo

# Check video files
echo "5. Checking video files..."
if [[ -d ~/media/videos ]]; then
    video_count=$(find ~/media/videos -name "*.mp4" | wc -l)
    echo "✓ Found $video_count video files in ~/media/videos"
else
    echo "✗ ~/media/videos directory not found"
fi

echo

# Test basic mpv functionality
echo "6. Testing basic mpv functionality..."
echo "Testing mpv with null video output (audio only)..."
timeout 5s mpv --no-video --vo=null ~/media/videos/*.mp4 2>/dev/null && echo "✓ mpv can play audio" || echo "✗ mpv has issues"

echo
echo "=== Troubleshooting Complete ==="
echo
echo "Common fixes:"
echo "1. Run: ./installers/postinstall.sh"
echo "2. Install missing dependencies: pip install jsonschema"
echo "3. Create mpv config: mkdir -p ~/.config/mpv && cp mpv-config-template.conf ~/.config/mpv/mpv.conf"
echo "4. Test mpv directly: mpv --vo=drm --fs ~/media/videos/*.mp4"
