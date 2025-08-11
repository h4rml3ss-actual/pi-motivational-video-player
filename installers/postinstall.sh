#!/usr/bin/env bash
#
# Post-installation script for VideoWall.
# This script sets up the user configuration directory and copies all necessary files.

set -euo pipefail

# Configuration
readonly CONFIG_DIR="$HOME/.config/videowall"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Error handling
cleanup_on_error() {
    log_error "Installation failed. Cleaning up partial installation..."
    if [[ -d "$CONFIG_DIR" ]]; then
        rm -rf "$CONFIG_DIR"
        log_info "Removed partial installation directory"
    fi
    exit 1
}

trap cleanup_on_error ERR

# Validation functions
validate_source_files() {
    local missing_files=()

    # Check core files
    [[ -f "$PROJECT_ROOT/core/player.lua" ]] || missing_files+=("core/player.lua")
    [[ -d "$PROJECT_ROOT/core/hud/modules" ]] || missing_files+=("core/hud/modules/")
    [[ -d "$PROJECT_ROOT/core/filters" ]] || missing_files+=("core/filters/")
    [[ -d "$PROJECT_ROOT/presets" ]] || missing_files+=("presets/")
    [[ -f "$PROJECT_ROOT/assets/messages/sample.txt" ]] || missing_files+=("assets/messages/sample.txt")

    if [[ ${#missing_files[@]} -gt 0 ]]; then
        log_error "Missing required source files:"
        printf '%s\n' "${missing_files[@]}"
        return 1
    fi

    return 0
}

check_dependencies() {
    local missing_deps=()

    command -v python3 >/dev/null 2>&1 || missing_deps+=("python3")
    command -v mpv >/dev/null 2>&1 || missing_deps+=("mpv")

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_warn "Missing optional dependencies (recommended for full functionality):"
        printf '%s\n' "${missing_deps[@]}"
        log_warn "Please install these dependencies for optimal experience"
    fi
}

# Directory creation functions
create_directory_structure() {
    log_info "Creating directory structure in $CONFIG_DIR"

    local directories=(
        "$CONFIG_DIR"
        "$CONFIG_DIR/hud"
        "$CONFIG_DIR/hud/modules"
        "$CONFIG_DIR/filters"
        "$CONFIG_DIR/filters/presets"
        "$CONFIG_DIR/filters/shaders"
        "$CONFIG_DIR/profiles"
        "$CONFIG_DIR/messages"
    )

    for dir in "${directories[@]}"; do
        if ! mkdir -p "$dir"; then
            log_error "Failed to create directory: $dir"
            return 1
        fi
        chmod 755 "$dir"
    done

    log_info "Directory structure created successfully"
}

# File copying functions
copy_core_files() {
    log_info "Copying core Lua files..."

    # Copy main player script
    if ! cp "$PROJECT_ROOT/core/player.lua" "$CONFIG_DIR/player.lua"; then
        log_error "Failed to copy core/player.lua"
        return 1
    fi
    chmod 644 "$CONFIG_DIR/player.lua"

    # Copy HUD modules
    if ! cp -r "$PROJECT_ROOT/core/hud/modules/"* "$CONFIG_DIR/hud/modules/"; then
        log_error "Failed to copy HUD modules"
        return 1
    fi

    # Set permissions for HUD modules
    find "$CONFIG_DIR/hud/modules" -type f -exec chmod 644 {} \;

    log_info "Core Lua files copied successfully"
}

copy_filter_assets() {
    log_info "Copying filter presets and shaders..."

    # Copy filter presets
    if [[ -d "$PROJECT_ROOT/core/filters/presets" ]]; then
        if ! cp -r "$PROJECT_ROOT/core/filters/presets/"* "$CONFIG_DIR/filters/presets/"; then
            log_error "Failed to copy filter presets"
            return 1
        fi
        find "$CONFIG_DIR/filters/presets" -type f -exec chmod 644 {} \;
    fi

    # Copy shaders
    if [[ -d "$PROJECT_ROOT/core/filters/shaders" ]]; then
        if ! cp -r "$PROJECT_ROOT/core/filters/shaders/"* "$CONFIG_DIR/filters/shaders/"; then
            log_error "Failed to copy filter shaders"
            return 1
        fi
        find "$CONFIG_DIR/filters/shaders" -type f -exec chmod 644 {} \;
    fi

    log_info "Filter assets copied successfully"
}

copy_profile_configurations() {
    log_info "Copying profile configurations..."

    # Copy all preset JSON files to profiles directory
    for preset_file in "$PROJECT_ROOT/presets/"*.json; do
        if [[ -f "$preset_file" ]]; then
            local filename=$(basename "$preset_file")
            if ! cp "$preset_file" "$CONFIG_DIR/profiles/$filename"; then
                log_error "Failed to copy profile: $filename"
                return 1
            fi
            chmod 644 "$CONFIG_DIR/profiles/$filename"
        fi
    done

    log_info "Profile configurations copied successfully"
}

create_message_files() {
    log_info "Creating default message files..."

    # Copy sample message file as default
    if [[ -f "$PROJECT_ROOT/assets/messages/sample.txt" ]]; then
        if ! cp "$PROJECT_ROOT/assets/messages/sample.txt" "$CONFIG_DIR/messages/default.txt"; then
            log_error "Failed to copy sample message file"
            return 1
        fi
        chmod 644 "$CONFIG_DIR/messages/default.txt"
    else
        # Create a basic default message if sample doesn't exist
        cat > "$CONFIG_DIR/messages/default.txt" << 'EOF'
Welcome to VideoWall
CRT Cyberpunk Experience
System Ready
EOF
        chmod 644 "$CONFIG_DIR/messages/default.txt"
    fi

    log_info "Default message files created successfully"
}

# Validation functions
validate_installation() {
    log_info "Validating installation..."

    local validation_errors=()

    # Check core files
    [[ -f "$CONFIG_DIR/player.lua" ]] || validation_errors+=("Missing player.lua")
    [[ -d "$CONFIG_DIR/hud/modules" ]] || validation_errors+=("Missing HUD modules directory")
    [[ -d "$CONFIG_DIR/filters" ]] || validation_errors+=("Missing filters directory")
    [[ -d "$CONFIG_DIR/profiles" ]] || validation_errors+=("Missing profiles directory")
    [[ -f "$CONFIG_DIR/messages/default.txt" ]] || validation_errors+=("Missing default message file")

    # Check that we have at least one profile
    local profile_count=$(find "$CONFIG_DIR/profiles" -name "*.json" -type f | wc -l)
    if [[ $profile_count -eq 0 ]]; then
        validation_errors+=("No profile configurations found")
    fi

    # Check that we have HUD modules
    local hud_count=$(find "$CONFIG_DIR/hud/modules" -name "*.lua" -type f | wc -l)
    if [[ $hud_count -eq 0 ]]; then
        validation_errors+=("No HUD modules found")
    fi

    if [[ ${#validation_errors[@]} -gt 0 ]]; then
        log_error "Installation validation failed:"
        printf '%s\n' "${validation_errors[@]}"
        return 1
    fi

    log_info "Installation validation passed"
    return 0
}

print_installation_summary() {
    log_info "Installation Summary:"
    echo "  Configuration directory: $CONFIG_DIR"
    echo "  Core files: $(find "$CONFIG_DIR" -name "*.lua" -type f | wc -l) Lua files"
    echo "  Profiles: $(find "$CONFIG_DIR/profiles" -name "*.json" -type f | wc -l) configurations"
    echo "  Filter presets: $(find "$CONFIG_DIR/filters/presets" -type f 2>/dev/null | wc -l) presets"
    echo "  Filter shaders: $(find "$CONFIG_DIR/filters/shaders" -type f 2>/dev/null | wc -l) shaders"
    echo "  Message files: $(find "$CONFIG_DIR/messages" -type f | wc -l) files"
}

# Main installation function
main() {
    log_info "Starting VideoWall post-installation setup..."

    # Pre-installation checks
    log_info "Validating source files..."
    validate_source_files

    log_info "Checking dependencies..."
    check_dependencies

    # Check if already installed
    if [[ -d "$CONFIG_DIR" ]]; then
        log_warn "Configuration directory already exists: $CONFIG_DIR"
        read -p "Do you want to overwrite the existing installation? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installation cancelled by user"
            exit 0
        fi
        log_info "Removing existing installation..."
        rm -rf "$CONFIG_DIR"
    fi

    # Perform installation
    create_directory_structure
    copy_core_files
    copy_filter_assets
    copy_profile_configurations
    create_message_files

    # Post-installation validation
    validate_installation

    # Success
    log_info "VideoWall installation completed successfully!"
    print_installation_summary

    log_info "You can now use the VideoWall application with the installed configuration."
    log_info "Configuration files are located in: $CONFIG_DIR"
}

# Run main function
main "$@"
