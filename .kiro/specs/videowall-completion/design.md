# Design Document

## Overview

The VideoWall completion design focuses on implementing the remaining infrastructure components needed to make the CRT Cyberpunk Video Wall project production-ready. The design addresses installation automation, code quality tooling, and integration testing while maintaining the existing modular architecture.

The project follows a clean separation of concerns with:
- Core Lua modules for mpv integration (player, HUD modules)
- Python executables for configuration management and launching
- JSON-based configuration with schema validation
- Modular filter and shader system
- Profile-based preset management

## Architecture

### Installation System Architecture

The installation system uses a shell-based approach that integrates with the existing directory structure:

```
~/.config/videowall/
├── config.json (active configuration)
├── profiles/ (available profiles)
├── player.lua (copied from core/)
├── hud/modules/ (copied from core/hud/modules/)
├── filters/ (copied from core/filters/)
└── messages/ (message files)
```

The postinstall.sh script acts as the bridge between the source repository structure and the user's configuration directory, ensuring all components are properly positioned for mpv and the Python launchers to find them.

### Code Quality Architecture

The code quality system leverages existing tools and patterns:
- Pre-commit hooks for automated validation
- Existing Lua syntax checking via luac
- Python linting with standard tools (flake8, black)
- JSON schema validation for configuration files
- Integration with the existing test structure

### Integration Testing Architecture

The integration testing approach builds on the existing test framework:
- Lua syntax validation (already implemented)
- Python module testing with pytest
- Configuration schema validation
- End-to-end profile loading tests

## Components and Interfaces

### PostInstall Script Component

**Interface:**
- Input: Source repository structure
- Output: Configured ~/.config/videowall/ directory
- Dependencies: bash, standard Unix utilities

**Responsibilities:**
- Create directory structure in user config
- Copy Lua modules with proper permissions
- Copy filter presets and shaders
- Create default profiles from presets
- Generate sample message files
- Validate copied files

### Pre-commit Hook Component

**Interface:**
- Input: Git staged files
- Output: Pass/fail validation results
- Dependencies: pre-commit, luac, python linters

**Responsibilities:**
- Validate Lua syntax using existing test_lua_syntax.sh
- Check Python code style and syntax
- Validate JSON configuration files against schema
- Prevent commits with quality issues

### Configuration Integration Component

**Interface:**
- Input: Profile JSON files, schema definitions
- Output: Validated runtime configurations
- Dependencies: jsonschema, existing Python modules

**Responsibilities:**
- Ensure profile configurations are valid
- Test configuration loading in both executables
- Validate schema compliance across all presets

## Data Models

### Installation Manifest

The postinstall script operates on a logical manifest of files to copy:

```bash
# Source -> Destination mappings
CORE_FILES=(
    "core/player.lua:player.lua"
    "core/hud/modules:hud/modules"
    "core/filters:filters"
)

PRESET_FILES=(
    "presets/*.json:profiles/"
)

ASSET_FILES=(
    "assets/messages/sample.txt:messages/default.txt"
)
```

### Code Quality Configuration

Pre-commit configuration follows standard patterns:

```yaml
repos:
  - repo: local
    hooks:
      - id: lua-syntax
        name: Lua Syntax Check
        entry: tests/test_lua_syntax.sh
        language: system
        files: \.lua$

      - id: python-lint
        name: Python Linting
        entry: flake8
        language: python
        files: \.py$

      - id: json-validate
        name: JSON Schema Validation
        entry: python -m jsonschema
        language: python
        files: \.(json)$
```

## Error Handling

### Installation Error Handling

The postinstall script implements robust error handling:

1. **Directory Creation Failures**: Check permissions and provide clear error messages
2. **File Copy Failures**: Validate source files exist before copying
3. **Permission Issues**: Set appropriate permissions and handle permission errors
4. **Missing Dependencies**: Check for required tools (mpv, python3) before proceeding

### Code Quality Error Handling

Pre-commit hooks provide clear feedback:

1. **Syntax Errors**: Display exact line numbers and error descriptions
2. **Style Violations**: Show specific violations with fix suggestions
3. **Schema Violations**: Display validation errors with context
4. **Tool Missing**: Provide installation instructions for missing linters

### Integration Error Handling

Integration tests handle various failure modes:

1. **Configuration Loading**: Test invalid JSON and schema violations
2. **Module Loading**: Verify Lua modules can be loaded by mpv
3. **Profile Switching**: Test profile loading and validation
4. **Missing Files**: Handle missing assets gracefully

## Testing Strategy

### Unit Testing

- **Python Modules**: Use pytest for configuration validation, argument parsing, and profile management
- **Lua Modules**: Extend existing syntax checking to include basic functionality tests
- **JSON Schemas**: Validate all preset files against the schema

### Integration Testing

- **Installation Process**: Test postinstall.sh in isolated environments
- **Configuration Loading**: Test both videowall and videowall-launcher with various profiles
- **mpv Integration**: Verify Lua scripts load correctly with mpv
- **Filter Application**: Test that video filters and shaders apply correctly

### End-to-End Testing

- **Profile Workflow**: Test complete profile selection and video playback workflow
- **Message System**: Verify message overlay functionality works with different configurations
- **HUD Modules**: Test that all HUD modules display correct information
- **Error Recovery**: Test behavior with invalid configurations and missing files

### Continuous Integration

The CI pipeline should:

1. Run all unit tests
2. Execute integration tests in a Pi-like environment
3. Validate all configuration files
4. Check code quality standards
5. Test installation process in clean environment

This testing strategy ensures reliability across different Pi configurations and user setups while maintaining the project's modular architecture.
