#!/bin/bash
# Test different video effects with mpv

echo "Testing VideoWall visual effects..."
echo

VIDEO_FILE="$HOME/media/videos/*.mp4"

echo "1. Testing normal video (no effects):"
echo "mpv --no-config --fs $VIDEO_FILE"
echo

echo "2. Testing cyberpunk-glitch effect:"
echo "mpv --no-config --fs --vf='eq=brightness=0.5:contrast=2.5:saturation=3.0:gamma=0.6,hue=h=30:s=1.5,noise=alls=40:allf=t' $VIDEO_FILE"
echo

echo "3. Testing vhs-glitch effect:"
echo "mpv --no-config --fs --vf='eq=brightness=0.1:contrast=1.3:saturation=0.4:gamma=1.2,hue=h=-20:s=0.7,noise=alls=30:allf=t' $VIDEO_FILE"
echo

echo "4. Testing cyberpunk-glow (subtle):"
echo "mpv --no-config --fs --vf='eq=brightness=0.4:contrast=2.0:saturation=2.5:gamma=0.7,hue=h=15:s=1.3' $VIDEO_FILE"
echo

read -p "Which test would you like to run? (1-4): " choice

case $choice in
    1)
        mpv --no-config --fs ~/media/videos/*.mp4
        ;;
    2)
        mpv --no-config --fs --vf='eq=brightness=0.5:contrast=2.5:saturation=3.0:gamma=0.6,hue=h=30:s=1.5,noise=alls=40:allf=t' ~/media/videos/*.mp4
        ;;
    3)
        mpv --no-config --fs --vf='eq=brightness=0.1:contrast=1.3:saturation=0.4:gamma=1.2,hue=h=-20:s=0.7,noise=alls=30:allf=t' ~/media/videos/*.mp4
        ;;
    4)
        mpv --no-config --fs --vf='eq=brightness=0.4:contrast=2.0:saturation=2.5:gamma=0.7,hue=h=15:s=1.3' ~/media/videos/*.mp4
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
