# VideoWall Integration Tests

This directory contains comprehensive integration tests for the VideoWall project, covering all major components and their interactions.

## Test Files

### Core Integration Tests

1. **`test_mpv_integration.py`** - Tests Lua module loading with mpv
   - Validates that player.lua loads correctly in mpv
   - Tests HUD module syntax and loading
   - Verifies module interfaces and functionality

2. **`test_filter_integration.py`** - Tests video filter and shader application
   - Validates filter preset configurations
   - Tests GLSL shader syntax and references
   - Verifies mpv can parse and apply filters
   - Tests profile-filter integration

3. **`test_hud_integration.py`** - Tests HUD module functionality and data accuracy
   - Tests individual HUD modules (clock, cpu, mem, net, uptime)
   - Validates data accuracy and format consistency
   - Tests module stability over time
   - Verifies consistent interfaces across modules

4. **`test_message_integration.py`** - Tests message overlay system functionality
   - Tests message file loading and parsing
   - Validates message overlay with mpv
   - Tests configuration options and error handling
   - Tests message reload and random selection functionality

### Supporting Files

- **`validate_integration_tests.py`** - Basic validation script to verify test environment
- **`README_INTEGRATION_TESTS.md`** - This documentation file

## Dependencies

### Required for Full Testing
- **Python 3.x** - For running pytest and test scripts
- **pytest** - Python testing framework (install with `pip install pytest`)
- **lua** - Lua interpreter for HUD module testing
- **luac** - Lua compiler for syntax validation
- **mpv** - Media player for integration testing

### Optional Dependencies
- **jsonschema** - For configuration validation (install with `pip install jsonschema`)

## Running Tests

### Run All Integration Tests
```bash
# With pytest (recommended)
python -m pytest tests/test_*_integration.py -v

# Or run individual test files
python -m pytest tests/test_mpv_integration.py -v
python -m pytest tests/test_filter_integration.py -v
python -m pytest tests/test_hud_integration.py -v
python -m pytest tests/test_message_integration.py -v
```

### Validate Test Environment
```bash
python3 tests/validate_integration_tests.py
```

### Run Existing Test Suite
```bash
python3 tests/run_tests.py
```

## Test Coverage

### Requirements Coverage
These integration tests cover the following requirements from the VideoWall completion spec:

- **Requirement 4.1**: Lua modules properly integrated with mpv player
- **Requirement 4.2**: Video filters and shaders apply correctly
- **Requirement 4.3**: HUD modules display accurate system information
- **Requirement 4.5**: Message overlay system displays text correctly over video content

### Component Coverage

#### mpv Integration (`test_mpv_integration.py`)
- ✅ mpv availability and version checking
- ✅ player.lua syntax validation and loading
- ✅ HUD module syntax validation
- ✅ Module loading and interface verification

#### Filter System (`test_filter_integration.py`)
- ✅ Filter preset file existence and readability
- ✅ GLSL shader file validation
- ✅ Filter preset syntax validation
- ✅ Shader reference validation in presets
- ✅ mpv filter parsing and application
- ✅ Profile-filter integration validation

#### HUD System (`test_hud_integration.py`)
- ✅ Individual module functionality testing
  - Clock module (time format and accuracy)
  - CPU module (usage percentage validation)
  - Memory module (usage statistics)
  - Network module (throughput monitoring)
  - Uptime module (system uptime display)
- ✅ Module interface consistency
- ✅ Data accuracy validation
- ✅ Stability testing over time

#### Message System (`test_message_integration.py`)
- ✅ Message file loading and parsing
- ✅ Comment and whitespace handling
- ✅ mpv integration with message overlay
- ✅ Configuration option validation
- ✅ Error handling (missing files, etc.)
- ✅ Message reload functionality
- ✅ Random selection algorithm
- ✅ Profile integration
- ✅ Performance testing with large message files

## Test Design Principles

### Isolation
- Each test file focuses on a specific component
- Tests use temporary directories to avoid side effects
- External dependencies are checked and skipped if unavailable

### Robustness
- Tests handle missing dependencies gracefully
- Timeout protection for external process calls
- Clear error messages and assertions

### Realism
- Tests use actual project files and configurations
- Integration with real mpv player when available
- Validation against actual system resources (/proc files)

### Performance
- Tests include performance validation
- Timeout limits prevent hanging tests
- Efficient test data generation

## Troubleshooting

### Common Issues

1. **"mpv not available"** - Install mpv media player
   ```bash
   # macOS
   brew install mpv

   # Ubuntu/Debian
   sudo apt install mpv
   ```

2. **"lua interpreter not available"** - Install Lua
   ```bash
   # macOS
   brew install lua

   # Ubuntu/Debian
   sudo apt install lua5.4
   ```

3. **"pytest not found"** - Install pytest
   ```bash
   pip install pytest jsonschema
   ```

4. **Permission errors** - Ensure test files are readable
   ```bash
   chmod +r tests/*.py
   chmod +r core/**/*.lua
   ```

### Test Skipping
Tests are designed to skip gracefully when dependencies are unavailable:
- Missing mpv → mpv integration tests skipped
- Missing lua → HUD module tests skipped
- Missing pytest → fallback to basic Python testing

### Debug Mode
Run tests with verbose output for debugging:
```bash
python -m pytest tests/test_mpv_integration.py -v -s
```

## Contributing

When adding new integration tests:

1. Follow the existing test structure and naming conventions
2. Include proper dependency checking and graceful skipping
3. Add timeout protection for external processes
4. Update this README with new test coverage
5. Ensure tests are isolated and don't affect each other
6. Include both positive and negative test cases
7. Test error handling and edge cases

## Test Results Interpretation

### Success Indicators
- All assertions pass
- No timeout errors
- Expected output messages appear
- Performance benchmarks met

### Common Warnings
- "skipping" messages indicate missing optional dependencies
- Timeout warnings may indicate system load issues
- "N/A" results from HUD modules indicate system resource unavailability

### Failure Investigation
1. Check dependency availability
2. Verify file permissions and paths
3. Review system resource availability
4. Check for conflicting processes
5. Validate configuration file syntax
