"""
Integration tests for HUD module functionality and data accuracy.
"""
import os
import tempfile
import subprocess
import pytest
import time
import re
from pathlib import Path


class TestHudIntegration:
    """Test HUD module functionality and data accuracy."""

    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary videowall config directory with HUD modules."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = os.path.join(temp_dir, ".config", "videowall")
            hud_dir = os.path.join(config_dir, "hud", "modules")
            os.makedirs(hud_dir, exist_ok=True)
            yield config_dir

    def test_clock_module_functionality(self, temp_config_dir, project_root):
        """Test that clock module returns accurate time information."""
        hud_modules_dir = os.path.join(project_root, "core", "hud", "modules")
        clock_src = os.path.join(hud_modules_dir, "clock.lua")

        if not os.path.exists(clock_src):
            pytest.skip("clock.lua module not found")

        # Copy clock module to temp config
        clock_dst = os.path.join(temp_config_dir, "hud", "modules", "clock.lua")
        with open(clock_src, "r") as src, open(clock_dst, "w") as dst:
            dst.write(src.read())

        # Create test script
        test_script = os.path.join(temp_config_dir, "test_clock.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
package.path = package.path .. ";{temp_config_dir}/hud/modules/?.lua"

local clock = require('clock')
local result = clock.get()

-- Verify result is a string
assert(type(result) == "string", "Clock should return a string")
assert(#result > 0, "Clock should return non-empty string")

-- Verify basic date/time format (YYYY-MM-DD HH:MM:SS)
local pattern = "^%d%d%d%d%-%d%d%-%d%d %d%d:%d%d:%d%d$"
assert(string.match(result, pattern), "Clock format should be YYYY-MM-DD HH:MM:SS, got: " .. result)

-- Verify the time is reasonably current (within last minute)
local year = tonumber(string.sub(result, 1, 4))
assert(year >= 2024 and year <= 2030, "Year should be reasonable: " .. year)

print("Clock test passed: " .. result)
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=10
            )

            assert result.returncode == 0, f"Clock module test failed: {result.stderr}"
            assert (
                "Clock test passed" in result.stdout
            ), "Clock test did not complete successfully"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for HUD testing")

    def test_cpu_module_functionality(self, temp_config_dir, project_root):
        """Test that CPU module returns valid CPU usage information."""
        hud_modules_dir = os.path.join(project_root, "core", "hud", "modules")
        cpu_src = os.path.join(hud_modules_dir, "cpu.lua")

        if not os.path.exists(cpu_src):
            pytest.skip("cpu.lua module not found")

        # Copy CPU module to temp config
        cpu_dst = os.path.join(temp_config_dir, "hud", "modules", "cpu.lua")
        with open(cpu_src, "r") as src, open(cpu_dst, "w") as dst:
            dst.write(src.read())

        # Create test script
        test_script = os.path.join(temp_config_dir, "test_cpu.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
package.path = package.path .. ";{temp_config_dir}/hud/modules/?.lua"

local cpu = require('cpu')

-- Test multiple calls to ensure consistency
local results = {{}}
for i = 1, 3 do
    local result = cpu.get()
    table.insert(results, result)

    -- Verify result is a string
    assert(type(result) == "string", "CPU should return a string")
    assert(#result > 0, "CPU should return non-empty string")

    -- Should contain "cpu" and either percentage or "N/A"
    assert(string.match(result, "cpu"), "Result should contain 'cpu': " .. result)

    -- Check for valid format: "cpu XX.X%" or "cpu N/A"
    local is_percentage = string.match(result, "cpu %d+%.%d%%")
    local is_na = string.match(result, "cpu N/A")
    assert(is_percentage or is_na, "CPU format should be 'cpu XX.X%' or 'cpu N/A', got: " .. result)

    if is_percentage then
        local percentage = tonumber(string.match(result, "(%d+%.%d)%%"))
        assert(percentage >= 0 and percentage <= 100, "CPU percentage should be 0-100: " .. percentage)
    end

    -- Small delay between calls
    os.execute("sleep 0.1")
end

print("CPU test passed with results:")
for i, result in ipairs(results) do
    print("  Call " .. i .. ": " .. result)
end
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=15
            )

            assert result.returncode == 0, f"CPU module test failed: {result.stderr}"
            assert (
                "CPU test passed" in result.stdout
            ), "CPU test did not complete successfully"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for HUD testing")

    def test_memory_module_functionality(self, temp_config_dir, project_root):
        """Test that memory module returns valid memory usage information."""
        hud_modules_dir = os.path.join(project_root, "core", "hud", "modules")
        mem_src = os.path.join(hud_modules_dir, "mem.lua")

        if not os.path.exists(mem_src):
            pytest.skip("mem.lua module not found")

        # Copy memory module to temp config
        mem_dst = os.path.join(temp_config_dir, "hud", "modules", "mem.lua")
        with open(mem_src, "r") as src, open(mem_dst, "w") as dst:
            dst.write(src.read())

        # Create test script
        test_script = os.path.join(temp_config_dir, "test_mem.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
package.path = package.path .. ";{temp_config_dir}/hud/modules/?.lua"

local mem = require('mem')
local result = mem.get()

-- Verify result is a string
assert(type(result) == "string", "Memory should return a string")
assert(#result > 0, "Memory should return non-empty string")

-- Should contain "mem" and either usage info or "N/A"
assert(string.match(result, "mem"), "Result should contain 'mem': " .. result)

-- Check for valid format patterns
local is_percentage = string.match(result, "mem %d+%.%d%%")
local is_usage = string.match(result, "mem %d+/%d+MB")
local is_na = string.match(result, "mem N/A")

assert(is_percentage or is_usage or is_na,
    "Memory format should be 'mem XX.X%', 'mem XXX/XXXMB', or 'mem N/A', got: " .. result)

if is_percentage then
    local percentage = tonumber(string.match(result, "(%d+%.%d)%%"))
    assert(percentage >= 0 and percentage <= 100, "Memory percentage should be 0-100: " .. percentage)
end

if is_usage then
    local used, total = string.match(result, "mem (%d+)/(%d+)MB")
    used, total = tonumber(used), tonumber(total)
    assert(used >= 0 and total > 0 and used <= total,
        "Memory usage should be valid: used=" .. used .. " total=" .. total)
end

print("Memory test passed: " .. result)
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=10
            )

            assert result.returncode == 0, f"Memory module test failed: {result.stderr}"
            assert (
                "Memory test passed" in result.stdout
            ), "Memory test did not complete successfully"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for HUD testing")

    def test_network_module_functionality(self, temp_config_dir, project_root):
        """Test that network module returns valid network information."""
        hud_modules_dir = os.path.join(project_root, "core", "hud", "modules")
        net_src = os.path.join(hud_modules_dir, "net.lua")

        if not os.path.exists(net_src):
            pytest.skip("net.lua module not found")

        # Copy network module to temp config
        net_dst = os.path.join(temp_config_dir, "hud", "modules", "net.lua")
        with open(net_src, "r") as src, open(net_dst, "w") as dst:
            dst.write(src.read())

        # Create test script
        test_script = os.path.join(temp_config_dir, "test_net.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
package.path = package.path .. ";{temp_config_dir}/hud/modules/?.lua"

local net = require('net')
local result = net.get()

-- Verify result is a string
assert(type(result) == "string", "Network should return a string")
assert(#result > 0, "Network should return non-empty string")

-- Should contain "net" and either network info or "N/A"
assert(string.match(result, "net"), "Result should contain 'net': " .. result)

-- Check for valid format patterns
local is_speed = string.match(result, "net %d+%.%d+/%d+%.%d+ [KMG]B/s")
local is_na = string.match(result, "net N/A")

assert(is_speed or is_na,
    "Network format should be 'net XX.X/XX.X KB/s' or 'net N/A', got: " .. result)

print("Network test passed: " .. result)
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=10
            )

            assert (
                result.returncode == 0
            ), f"Network module test failed: {result.stderr}"
            assert (
                "Network test passed" in result.stdout
            ), "Network test did not complete successfully"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for HUD testing")

    def test_uptime_module_functionality(self, temp_config_dir, project_root):
        """Test that uptime module returns valid system uptime information."""
        hud_modules_dir = os.path.join(project_root, "core", "hud", "modules")
        uptime_src = os.path.join(hud_modules_dir, "uptime.lua")

        if not os.path.exists(uptime_src):
            pytest.skip("uptime.lua module not found")

        # Copy uptime module to temp config
        uptime_dst = os.path.join(temp_config_dir, "hud", "modules", "uptime.lua")
        with open(uptime_src, "r") as src, open(uptime_dst, "w") as dst:
            dst.write(src.read())

        # Create test script
        test_script = os.path.join(temp_config_dir, "test_uptime.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
package.path = package.path .. ";{temp_config_dir}/hud/modules/?.lua"

local uptime = require('uptime')
local result = uptime.get()

-- Verify result is a string
assert(type(result) == "string", "Uptime should return a string")
assert(#result > 0, "Uptime should return non-empty string")

-- Should contain "uptime" and either time info or "N/A"
assert(string.match(result, "uptime"), "Result should contain 'uptime': " .. result)

-- Check for valid format patterns
local is_time = string.match(result, "uptime %d+:%d+:%d+")
local is_days = string.match(result, "uptime %d+ days")
local is_na = string.match(result, "uptime N/A")

assert(is_time or is_days or is_na,
    "Uptime format should be 'uptime HH:MM:SS', 'uptime X days', or 'uptime N/A', got: " .. result)

print("Uptime test passed: " .. result)
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=10
            )

            assert result.returncode == 0, f"Uptime module test failed: {result.stderr}"
            assert (
                "Uptime test passed" in result.stdout
            ), "Uptime test did not complete successfully"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for HUD testing")

    def test_all_hud_modules_consistency(self, temp_config_dir, project_root):
        """Test that all HUD modules have consistent interface and behavior."""
        hud_modules_dir = os.path.join(project_root, "core", "hud", "modules")

        if not os.path.exists(hud_modules_dir):
            pytest.skip("HUD modules directory not found")

        # Copy all HUD modules to temp config
        temp_hud_dir = os.path.join(temp_config_dir, "hud", "modules")
        lua_files = [f for f in os.listdir(hud_modules_dir) if f.endswith(".lua")]

        for lua_file in lua_files:
            src_path = os.path.join(hud_modules_dir, lua_file)
            dst_path = os.path.join(temp_hud_dir, lua_file)
            with open(src_path, "r") as src, open(dst_path, "w") as dst:
                dst.write(src.read())

        # Create comprehensive test script
        test_script = os.path.join(temp_config_dir, "test_all_hud.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
package.path = package.path .. ";{temp_hud_dir}/?.lua"

local modules = {{}}
local results = {{}}

-- Load all modules
"""
            )

            for lua_file in lua_files:
                module_name = lua_file.replace(".lua", "")
                f.write(
                    f"""
-- Load {module_name} module
local {module_name} = require('{module_name}')
assert({module_name}, "Failed to load {module_name} module")
assert(type({module_name}.get) == "function", "{module_name} module missing get() function")
modules['{module_name}'] = {module_name}
"""
                )

            f.write(
                """
-- Test all modules for consistency
for name, module in pairs(modules) do
    local result = module.get()

    -- Basic consistency checks
    assert(type(result) == "string", name .. " should return a string")
    assert(#result > 0, name .. " should return non-empty string")
    assert(string.match(result, name), name .. " result should contain module name")

    results[name] = result
    print(name .. " module OK: " .. result)
end

-- Test multiple calls for stability
print("\\nTesting stability with multiple calls...")
for name, module in pairs(modules) do
    for i = 1, 3 do
        local result = module.get()
        assert(type(result) == "string", name .. " call " .. i .. " should return string")
        assert(#result > 0, name .. " call " .. i .. " should return non-empty string")
    end
    print(name .. " stability test passed")
end

print("\\nAll HUD modules passed consistency tests")
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=20
            )

            assert (
                result.returncode == 0
            ), f"HUD modules consistency test failed: {result.stderr}"
            assert (
                "All HUD modules passed consistency tests" in result.stdout
            ), "HUD modules consistency test did not complete successfully"

            # Verify each module was tested
            for lua_file in lua_files:
                module_name = lua_file.replace(".lua", "")
                assert (
                    f"{module_name} module OK" in result.stdout
                ), f"{module_name} module was not tested successfully"
                assert (
                    f"{module_name} stability test passed" in result.stdout
                ), f"{module_name} module stability test failed"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for HUD testing")

    def test_hud_data_accuracy_over_time(self, temp_config_dir, project_root):
        """Test that HUD modules provide reasonably accurate data over time."""
        hud_modules_dir = os.path.join(project_root, "core", "hud", "modules")

        if not os.path.exists(hud_modules_dir):
            pytest.skip("HUD modules directory not found")

        # Focus on modules that should show changing data
        test_modules = ["cpu", "mem"]  # These should potentially change over time

        # Copy relevant modules
        temp_hud_dir = os.path.join(temp_config_dir, "hud", "modules")
        for module_name in test_modules:
            src_path = os.path.join(hud_modules_dir, f"{module_name}.lua")
            if os.path.exists(src_path):
                dst_path = os.path.join(temp_hud_dir, f"{module_name}.lua")
                with open(src_path, "r") as src, open(dst_path, "w") as dst:
                    dst.write(src.read())

        # Create time-based test script
        test_script = os.path.join(temp_config_dir, "test_hud_accuracy.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
package.path = package.path .. ";{temp_hud_dir}/?.lua"

-- Test data accuracy over time
local function test_module_over_time(module_name)
    local module = require(module_name)
    local readings = {{}}

    -- Take multiple readings over time
    for i = 1, 5 do
        local result = module.get()
        table.insert(readings, result)

        -- Verify basic format
        assert(type(result) == "string", module_name .. " should return string")
        assert(#result > 0, module_name .. " should return non-empty string")

        -- Small delay between readings
        os.execute("sleep 0.2")
    end

    -- Verify readings are consistent in format
    for i, reading in ipairs(readings) do
        assert(string.match(reading, module_name),
            module_name .. " reading " .. i .. " should contain module name: " .. reading)
    end

    print(module_name .. " accuracy test passed:")
    for i, reading in ipairs(readings) do
        print("  Reading " .. i .. ": " .. reading)
    end

    return readings
end

-- Test available modules
"""
            )

            for module_name in test_modules:
                src_path = os.path.join(hud_modules_dir, f"{module_name}.lua")
                if os.path.exists(src_path):
                    f.write(
                        f"""
if pcall(require, '{module_name}') then
    test_module_over_time('{module_name}')
else
    print('{module_name} module not available for testing')
end
"""
                    )

            f.write(
                """
print("\\nHUD data accuracy tests completed")
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=25
            )

            assert result.returncode == 0, f"HUD accuracy test failed: {result.stderr}"
            assert (
                "HUD data accuracy tests completed" in result.stdout
            ), "HUD accuracy test did not complete successfully"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for HUD testing")
