"""
Integration tests for mpv Lua module loading and functionality.
"""
import os
import tempfile
import subprocess
import pytest


class TestMpvLuaIntegration:
    """Test Lua module loading with mpv."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary videowall config directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.makedirs(config_dir, exist_ok=True)
            yield config_dir

    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return os.path.dirname(os.path.dirname(__file__))

    def test_mpv_available(self):
        """Test that mpv is available for testing."""
        try:
            result = subprocess.run(
                ["mpv", "--version"], capture_output=True, text=True, timeout=10
            )
            assert result.returncode == 0, "mpv is not available for testing"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("mpv not available for integration testing")

    def test_player_lua_syntax_validation(self, project_root):
        """Test that player.lua has valid Lua syntax."""
        player_lua = os.path.join(project_root, "core", "player.lua")
        assert os.path.exists(player_lua), "player.lua not found"

        try:
            result = subprocess.run(
                ["luac", "-p", player_lua], capture_output=True, text=True, timeout=10
            )
            assert result.returncode == 0, f"player.lua syntax error: {result.stderr}"
        except FileNotFoundError:
            pytest.skip("luac not available for syntax checking")

    def test_player_lua_loads_in_mpv(self, temp_config_dir, project_root):
        """Test that player.lua can be loaded by mpv without errors."""
        # Copy player.lua to temp config
        player_src = os.path.join(project_root, "core", "player.lua")
        player_dst = os.path.join(temp_config_dir, "player.lua")

        with open(player_src, "r") as src, open(player_dst, "w") as dst:
            dst.write(src.read())

        # Create a minimal message file
        messages_dir = os.path.join(temp_config_dir, "messages")
        os.makedirs(messages_dir, exist_ok=True)
        with open(os.path.join(messages_dir, "default.txt"), "w") as f:
            f.write("Test message 1\nTest message 2\n")

        try:
            # Test mpv with the Lua script (dry run)
            result = subprocess.run(
                [
                    "mpv",
                    "--no-video",
                    "--no-audio",
                    "--script=" + player_dst,
                    "--idle=yes",
                    "--msg-level=all=debug",
                    "--frames=1",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            # Check that script loaded without fatal errors
            assert "player.lua" in result.stderr, "player.lua script not loaded"
            assert (
                "fatal" not in result.stderr.lower()
            ), f"Fatal error in mpv: {result.stderr}"

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("mpv not available or timed out during testing")

    def test_hud_modules_syntax_validation(self, project_root):
        """Test that all HUD modules have valid Lua syntax."""
        hud_modules_dir = os.path.join(project_root, "core", "hud", "modules")

        if not os.path.exists(hud_modules_dir):
            pytest.skip("HUD modules directory not found")

        lua_files = [f for f in os.listdir(hud_modules_dir) if f.endswith(".lua")]
        assert len(lua_files) > 0, "No HUD modules found"

        try:
            for lua_file in lua_files:
                lua_path = os.path.join(hud_modules_dir, lua_file)
                result = subprocess.run(
                    ["luac", "-p", lua_path], capture_output=True, text=True, timeout=10
                )
                assert (
                    result.returncode == 0
                ), f"{lua_file} syntax error: {result.stderr}"
        except FileNotFoundError:
            pytest.skip("luac not available for syntax checking")

    def test_hud_modules_can_be_required(self, temp_config_dir, project_root):
        """Test that HUD modules can be required and have expected functions."""
        hud_modules_dir = os.path.join(project_root, "core", "hud", "modules")

        if not os.path.exists(hud_modules_dir):
            pytest.skip("HUD modules directory not found")

        # Copy HUD modules to temp config
        temp_hud_dir = os.path.join(temp_config_dir, "hud", "modules")
        os.makedirs(temp_hud_dir, exist_ok=True)

        lua_files = [f for f in os.listdir(hud_modules_dir) if f.endswith(".lua")]
        for lua_file in lua_files:
            src_path = os.path.join(hud_modules_dir, lua_file)
            dst_path = os.path.join(temp_hud_dir, lua_file)
            with open(src_path, "r") as src, open(dst_path, "w") as dst:
                dst.write(src.read())

        # Create a test script to require each module
        test_script = os.path.join(temp_config_dir, "test_modules.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
-- Test script to validate HUD modules
package.path = package.path .. ";{temp_hud_dir}/?.lua"

local modules = {{}}
"""
            )

            for lua_file in lua_files:
                module_name = lua_file.replace(".lua", "")
                f.write(
                    f"""
-- Test {module_name} module
local {module_name} = require('{module_name}')
assert({module_name}, "Failed to load {module_name} module")
assert(type({module_name}.get) == "function", "{module_name} module missing get() function")

-- Test that get() function returns a string
local result = {module_name}.get()
assert(type(result) == "string", "{module_name}.get() should return a string")
assert(#result > 0, "{module_name}.get() should return non-empty string")

print("{module_name} module OK: " .. result)
"""
                )

        try:
            # Run the test script with lua
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=15
            )

            assert result.returncode == 0, f"HUD module test failed: {result.stderr}"

            # Verify each module was tested
            for lua_file in lua_files:
                module_name = lua_file.replace(".lua", "")
                assert (
                    f"{module_name} module OK" in result.stdout
                ), f"{module_name} module test did not pass"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for module testing")
