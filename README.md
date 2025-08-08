# CRT Cyberpunk Video Wall

A Raspberry Pi application to display video clips with dynamic overlay text and retro visual effects on a CRT via HDMI→VGA.

## Prerequisites

- Raspberry Pi 4 (4–8 GB RAM) running Raspberry Pi OS (64‑bit Bookworm)
- Active HDMI→VGA adapter and CRT monitor
- USB keyboard for hotkeys

### System packages
```bash
sudo apt update
sudo apt install -y \
  mpv ffmpeg libass9 fontconfig fonts-dejavu \
  python3 python3-pip python3-venv \
  jq coreutils procps iproute2 net-tools \
  wiringpi lm-sensors mesa-utils
```

### Python packages
```bash
python3 -m venv ~/.venvs/videowall
source ~/.venvs/videowall/bin/activate
pip install --upgrade pip
pip install psutil netifaces textual jsonschema pytest
```

## Installation

```bash
git clone https://github.com/yourusername/videowall.git
cd videowall
# Copy mpv Lua script and assets to config directory
./installers/postinstall.sh
```

## Usage

### Select a profile
```bash
bin/videowall-launcher
```

### Start playback
```bash
bin/videowall
```

All configuration and profiles live under `~/.config/videowall`.  Playback parameters are validated against the JSON schema in `docs/config-schema.json`.

## Documentation

See detailed design and feature specifications in [docs/specs.md](docs/specs.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
