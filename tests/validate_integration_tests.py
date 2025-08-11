#!/usr/bin/env python3
"""
Simple validation script to test basic functionality of integration tests.
"""
import os
import sys
import tempfile
import subprocess


def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("Testing basic integration test functionality...")

    # Test 1: File existence checks
    project_root = os.path.dirname(os.path.dirname(__file__))

    # Check core files exist
    core_files = [
        "core/player.lua",
        "core/hud/modules/clock.lua",
        "core/hud/modules/cpu.lua",
    ]

    for file_path in core_files:
        full_path = os.path.join(project_root, file_path)
        assert os.path.exists(full_path), f"Core file missing: {file_path}"
        print(f"✓ Found {file_path}")

    # Test 2: Lua syntax validation
    print("\nTesting Lua syntax validation...")
    try:
        for file_path in core_files:
            full_path = os.path.join(project_root, file_path)
            result = subprocess.run(
                ["luac", "-p", full_path], capture_output=True, text=True, timeout=10
            )
            assert (
                result.returncode == 0
            ), f"Lua syntax error in {file_path}: {result.stderr}"
            print(f"✓ {file_path} syntax OK")
    except FileNotFoundError:
        print("⚠ luac not available, skipping Lua syntax tests")

    # Test 3: Basic HUD module loading
    print("\nTesting HUD module loading...")
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy a HUD module
        clock_src = os.path.join(project_root, "core/hud/modules/clock.lua")
        clock_dst = os.path.join(temp_dir, "clock.lua")

        with open(clock_src, "r") as src, open(clock_dst, "w") as dst:
            dst.write(src.read())

        # Create test script
        test_script = os.path.join(temp_dir, "test.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
package.path = package.path .. ";{temp_dir}/?.lua"
local clock = require('clock')
assert(clock, "Failed to load clock module")
assert(type(clock.get) == "function", "clock module missing get() function")
local result = clock.get()
assert(type(result) == "string", "clock.get() should return string")
assert(#result > 0, "clock.get() should return non-empty string")
print("Clock module test passed: " .. result)
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=10
            )
            assert result.returncode == 0, f"HUD module test failed: {result.stderr}"
            assert "Clock module test passed" in result.stdout
            print("✓ HUD module loading test passed")
        except FileNotFoundError:
            print("⚠ lua interpreter not available, skipping HUD module tests")

    # Test 4: Filter preset validation
    print("\nTesting filter preset validation...")
    presets_dir = os.path.join(project_root, "core/filters/presets")
    if os.path.exists(presets_dir):
        preset_files = [f for f in os.listdir(presets_dir) if f.endswith(".conf")]
        for preset_file in preset_files:
            preset_path = os.path.join(presets_dir, preset_file)
            assert os.path.isfile(preset_path), f"Preset file not found: {preset_file}"
            assert os.access(
                preset_path, os.R_OK
            ), f"Preset file not readable: {preset_file}"
            print(f"✓ {preset_file} accessible")
    else:
        print("⚠ Filter presets directory not found")

    # Test 5: Message file parsing
    print("\nTesting message file parsing...")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test message 1\n# Comment\nTest message 2\n\n   Test message 3   \n")
        f.flush()

        # Test parsing logic
        messages = []
        with open(f.name, "r") as msg_file:
            for line in msg_file:
                msg = line.strip()
                if msg and not msg.startswith("#"):
                    messages.append(msg)

        expected = ["Test message 1", "Test message 2", "Test message 3"]
        assert messages == expected, f"Message parsing failed: {messages} != {expected}"
        print("✓ Message file parsing test passed")

        os.unlink(f.name)

    print("\n✅ All basic integration test functionality validated!")
    return True


if __name__ == "__main__":
    try:
        test_basic_functionality()
        print("\n🎉 Integration tests are ready to run!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
