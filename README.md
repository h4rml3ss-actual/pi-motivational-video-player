# CRT Cyberpunk Video Wall

A Raspberry Pi application to display video clips with dynamic overlay text and retro visual effects on a CRT via HDMI→VGA.

## Prerequisites

- Raspberry Pi 4 (4–8 GB RAM) running Raspberry Pi OS (64‑bit Bookworm)
- Active HDMI→VGA adapter and CRT monitor
- USB keyboard for hotkeys

### System Dependencies

Install required system packages:

```bash
sudo apt update
sudo apt install -y \
  mpv ffmpeg libass9 fontconfig fonts-dejavu \
  python3 python3-pip python3-venv \
  jq coreutils procps iproute2 net-tools \
  wiringpi lm-sensors mesa-utils
```

### Python Environment Setup

Create and activate a Python virtual environment:

```bash
# Create virtual environment
python3 -m venv ~/.venvs/videowall

# Activate virtual environment
source ~/.venvs/videowall/bin/activate

# Upgrade pip and install required packages
pip install --upgrade pip
pip install -r requirements.txt

# Install additional system monitoring packages
pip install psutil netifaces textual
```

**Note:** Remember to activate the virtual environment (`source ~/.venvs/videowall/bin/activate`) before running VideoWall commands.

## Installation

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/videowall.git
cd videowall

# Run the post-installation script
./installers/postinstall.sh
```

### Manual Installation Steps

If you prefer to understand each step or need to troubleshoot:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/videowall.git
   cd videowall
   ```

2. **Run the post-installation script:**
   ```bash
   ./installers/postinstall.sh
   ```

   This script will:
   - Create the configuration directory at `~/.config/videowall/`
   - Copy all Lua modules and HUD components
   - Copy filter presets and shaders
   - Set up default profile configurations
   - Create sample message files
   - Set appropriate file permissions

3. **Verify installation:**
   ```bash
   # Check that configuration directory exists
   ls -la ~/.config/videowall/

   # Verify core files are present
   ls ~/.config/videowall/player.lua
   ls ~/.config/videowall/hud/modules/
   ls ~/.config/videowall/profiles/
   ```

## Usage

### Select a profile
```bash
bin/videowall-launcher
```

### Start playback

```bash
# Play videos from profile-defined directories
bin/videowall

# Or override video directories on the command line
bin/videowall --dirs /path/to/videos /other/videos
```

All configuration and profiles live under `~/.config/videowall`. Playback parameters are validated against the JSON schema in `docs/config-schema.json`.

## Development Setup

### Pre-commit Hooks

This project uses pre-commit hooks to maintain code quality. To set up the development environment:

1. **Install pre-commit:**
   ```bash
   # Activate your virtual environment first
   source ~/.venvs/videowall/bin/activate

   # Install pre-commit
   pip install pre-commit
   ```

2. **Install the git hook scripts:**
   ```bash
   pre-commit install
   ```

3. **Run hooks on all files (optional):**
   ```bash
   pre-commit run --all-files
   ```

### Code Quality Checks

The pre-commit configuration includes:

- **Lua Syntax Check**: Validates all `.lua` files using the existing `test_lua_syntax.sh` script
- **Python Code Formatting**: Formats Python code using Black
- **Python Linting**: Checks Python code style using flake8
- **JSON Schema Validation**: Validates profile configurations against the schema
- **General Quality**: Trims whitespace, fixes file endings, checks YAML/JSON syntax

### Manual Code Quality Checks

You can run individual quality checks manually:

```bash
# Check Lua syntax
./tests/test_lua_syntax.sh

# Format Python code
black .

# Lint Python code
flake8 --max-line-length=88 --extend-ignore=E203

# Validate JSON configurations
python -c "import json, jsonschema; schema=json.load(open('docs/config-schema.json')); [jsonschema.validate(json.load(open(f'presets/{f}')), schema) for f in ['cyberpunk_hud.json', 'pure_vhs.json']]"
```

## Testing

### Running All Tests

```bash
# Activate virtual environment
source ~/.venvs/videowall/bin/activate

# Run all tests with pytest
python -m pytest tests/ -v

# Or use the test runner script
python3 tests/run_tests.py
```

### Running Specific Test Categories

```bash
# Run integration tests only
python -m pytest tests/test_*_integration.py -v

# Run individual test files
python -m pytest tests/test_mpv_integration.py -v
python -m pytest tests/test_filter_integration.py -v
python -m pytest tests/test_hud_integration.py -v
python -m pytest tests/test_message_integration.py -v
```

### Test Environment Validation

```bash
# Validate that your system has the required dependencies for testing
python3 tests/validate_integration_tests.py
```

### Test Coverage

The test suite covers:

- **Configuration Loading**: Validates JSON schema compliance and profile loading
- **Lua Integration**: Tests mpv integration and Lua module loading
- **Filter System**: Validates video filters and shader application
- **HUD Modules**: Tests system information display accuracy
- **Message System**: Tests text overlay functionality
- **Installation Process**: Validates the post-installation setup

## Troubleshooting

### Common Installation Issues

#### Permission Errors
```bash
# If you get permission errors during installation:
chmod +x ./installers/postinstall.sh

# If configuration directory has wrong permissions:
chmod -R 755 ~/.config/videowall/
find ~/.config/videowall/ -type f -exec chmod 644 {} \;
```

#### Missing Dependencies
```bash
# If mpv is not found:
sudo apt install mpv

# If Python virtual environment issues:
sudo apt install python3-venv python3-pip

# If Python modules are missing:
source ~/.venvs/videowall/bin/activate
pip install -r requirements.txt
pip install psutil netifaces textual

# If Lua syntax checking fails:
sudo apt install lua5.4
```

#### Configuration Issues
```bash
# If profiles are not loading:
# Check JSON syntax
python -m json.tool ~/.config/videowall/profiles/cyberpunk_hud.json

# Validate against schema
python -c "import json, jsonschema; jsonschema.validate(json.load(open('~/.config/videowall/profiles/cyberpunk_hud.json')), json.load(open('docs/config-schema.json')))"

# If video directory doesn't exist:
mkdir -p ~/media/videos
# Add some sample video files to test
```

### Common Runtime Issues

#### Video Playback Problems
- **No video output**: Check HDMI→VGA adapter connection and CRT monitor power
- **Audio issues**: Verify audio output settings in mpv configuration
- **Performance issues**: Ensure sufficient RAM (4GB minimum) and check CPU usage

#### HUD Display Issues
- **Missing system info**: Verify that system monitoring tools are installed (`lm-sensors`, `net-tools`)
- **Incorrect data**: Check that `/proc` filesystem is accessible and readable

#### Filter/Shader Problems
- **Filters not applying**: Verify GPU acceleration is available (`mesa-utils`)
- **Shader compilation errors**: Check GLSL shader syntax in `core/filters/shaders/`

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Run with debug output
MPV_VERBOSE=1 bin/videowall --dirs /path/to/videos

# Check mpv logs
tail -f ~/.config/mpv/mpv.log
```

### Getting Help

1. **Check the logs**: Look for error messages in terminal output
2. **Validate installation**: Run `./installers/postinstall.sh` again
3. **Test components**: Use the integration tests to isolate issues
4. **Check dependencies**: Ensure all system packages are installed
5. **Verify permissions**: Ensure configuration files are readable

### Performance Optimization

#### For Raspberry Pi 4
```bash
# Increase GPU memory split
sudo raspi-config
# Advanced Options → Memory Split → 128 or 256

# Enable GPU acceleration
echo 'gpu_mem=128' | sudo tee -a /boot/config.txt

# Optimize for video playback
echo 'dtoverlay=vc4-kms-v3d' | sudo tee -a /boot/config.txt
```

#### For High-Resolution Videos
- Use lower resolution source videos (720p recommended for CRT)
- Reduce filter complexity in profile configurations
- Monitor CPU/GPU usage during playback

## Documentation

See detailed design and feature specifications in [docs/specs.md](docs/specs.md).

For comprehensive integration test documentation, see [tests/README_INTEGRATION_TESTS.md](tests/README_INTEGRATION_TESTS.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
