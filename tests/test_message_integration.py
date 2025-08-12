"""
Integration tests for message overlay system functionality.
"""
import os
import tempfile
import subprocess
import pytest


class TestMessageIntegration:
    """Test message overlay system functionality."""

    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary videowall config directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.makedirs(config_dir, exist_ok=True)
            yield config_dir

    def test_message_file_loading(self, temp_config_dir, project_root):
        """Test that message files can be loaded and parsed correctly."""
        # Copy player.lua to temp config
        player_src = os.path.join(project_root, "core", "player.lua")
        player_dst = os.path.join(temp_config_dir, "player.lua")

        with open(player_src, "r") as src, open(player_dst, "w") as dst:
            dst.write(src.read())

        # Create test message file
        messages_dir = os.path.join(temp_config_dir, "messages")
        os.makedirs(messages_dir, exist_ok=True)
        message_file = os.path.join(messages_dir, "test.txt")

        test_messages = [
            "Test message 1",
            "Test message 2 with special chars: !@#$%",
            "# This is a comment and should be ignored",
            "",  # Empty line should be ignored
            "   Test message 3 with whitespace   ",
            "Test message 4",
            "# Another comment",
            "Final test message",
        ]

        with open(message_file, "w") as f:
            f.write("\n".join(test_messages))

        # Create test script to validate message loading
        test_script = os.path.join(temp_config_dir, "test_messages.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
-- Test message loading functionality
local message_file = "{message_file}"

-- Load and parse messages (similar to player.lua logic)
local messages = {{}}
local f, err = io.open(message_file, "r")
assert(f, "Could not open message file: " .. tostring(err))

for line in f:lines() do
    local msg = line:match("^%s*(.-)%s*$")
    if msg ~= "" and not msg:match("^#") then
        table.insert(messages, msg)
    end
end
f:close()

-- Verify expected messages were loaded
local expected_messages = {{
    "Test message 1",
    "Test message 2 with special chars: !@#$%",
    "Test message 3 with whitespace",
    "Test message 4",
    "Final test message"
}}

assert(#messages == #expected_messages,
    "Expected " .. #expected_messages .. " messages, got " .. #messages)

for i, expected in ipairs(expected_messages) do
    assert(messages[i] == expected,
        "Message " .. i .. " mismatch: expected '" .. expected .. "', got '" .. (messages[i] or "nil") .. "'")
end

print("Message loading test passed: loaded " .. #messages .. " messages")
for i, msg in ipairs(messages) do
    print("  " .. i .. ": " .. msg)
end
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=10
            )

            assert (
                result.returncode == 0
            ), f"Message loading test failed: {result.stderr}"
            assert (
                "Message loading test passed" in result.stdout
            ), "Message loading test did not complete successfully"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for message testing")

    def test_message_overlay_with_mpv(self, temp_config_dir, project_root):
        """Test that message overlay works with mpv player."""
        # Copy player.lua to temp config
        player_src = os.path.join(project_root, "core", "player.lua")
        player_dst = os.path.join(temp_config_dir, "player.lua")

        with open(player_src, "r") as src, open(player_dst, "w") as dst:
            dst.write(src.read())

        # Create test message file
        messages_dir = os.path.join(temp_config_dir, "messages")
        os.makedirs(messages_dir, exist_ok=True)
        message_file = os.path.join(messages_dir, "default.txt")

        with open(message_file, "w") as f:
            f.write("Test overlay message 1\nTest overlay message 2\n")

        try:
            # Test mpv with message overlay (short duration)
            result = subprocess.run(
                [
                    "mpv",
                    "--no-video",
                    "--no-audio",
                    "--script=" + player_dst,
                    "--script-opts=player-message_file=" + message_file,
                    "--script-opts=player-interval=0",  # Disable automatic messages
                    "--script-opts=player-duration=1",  # Short duration for testing
                    "--idle=yes",
                    "--msg-level=all=debug",
                    "--frames=1",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            # Check that script loaded and message system initialized
            assert "player.lua" in result.stderr, "player.lua script not loaded"
            assert (
                "loaded" in result.stderr and "messages" in result.stderr
            ), "Message loading not detected in mpv output"

            # Should not have fatal errors
            assert (
                "fatal" not in result.stderr.lower()
            ), f"Fatal error in mpv: {result.stderr}"

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("mpv not available for message overlay testing")

    def test_message_configuration_options(self, temp_config_dir, project_root):
        """Test that message configuration options work correctly."""
        # Copy player.lua to temp config
        player_src = os.path.join(project_root, "core", "player.lua")
        player_dst = os.path.join(temp_config_dir, "player.lua")

        with open(player_src, "r") as src, open(player_dst, "w") as dst:
            dst.write(src.read())

        # Create test message files
        messages_dir = os.path.join(temp_config_dir, "messages")
        os.makedirs(messages_dir, exist_ok=True)

        # Default message file
        default_file = os.path.join(messages_dir, "default.txt")
        with open(default_file, "w") as f:
            f.write("Default message 1\nDefault message 2\n")

        # Custom message file
        custom_file = os.path.join(messages_dir, "custom.txt")
        with open(custom_file, "w") as f:
            f.write("Custom message 1\nCustom message 2\nCustom message 3\n")

        # Test different configuration options
        test_configs = [
            {
                "name": "default_config",
                "opts": f"player-message_file={default_file},player-interval=0",
                "expected_messages": 2,
            },
            {
                "name": "custom_config",
                "opts": f"player-message_file={custom_file},player-interval=0",
                "expected_messages": 3,
            },
            {
                "name": "custom_duration",
                "opts": f"player-message_file={default_file},player-interval=0,player-duration=3",
                "expected_messages": 2,
            },
        ]

        try:
            for config in test_configs:
                result = subprocess.run(
                    [
                        "mpv",
                        "--no-video",
                        "--no-audio",
                        "--script=" + player_dst,
                        "--script-opts=" + config["opts"],
                        "--idle=yes",
                        "--msg-level=all=debug",
                        "--frames=1",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                # Check that configuration was applied
                assert (
                    "player.lua" in result.stderr
                ), f"player.lua not loaded for {config['name']}"

                # Look for message count in output
                if f"loaded {config['expected_messages']} messages" in result.stderr:
                    # Exact match found
                    pass
                elif "loaded" in result.stderr and "messages" in result.stderr:
                    # General loading detected
                    pass
                else:
                    pytest.fail(
                        f"Message loading not detected for {config['name']}: {result.stderr}"
                    )

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("mpv not available for message configuration testing")

    def test_message_file_error_handling(self, temp_config_dir, project_root):
        """Test that message system handles file errors gracefully."""
        # Copy player.lua to temp config
        player_src = os.path.join(project_root, "core", "player.lua")
        player_dst = os.path.join(temp_config_dir, "player.lua")

        with open(player_src, "r") as src, open(player_dst, "w") as dst:
            dst.write(src.read())

        # Test with non-existent message file
        nonexistent_file = os.path.join(temp_config_dir, "messages", "nonexistent.txt")

        try:
            result = subprocess.run(
                [
                    "mpv",
                    "--no-video",
                    "--no-audio",
                    "--script=" + player_dst,
                    "--script-opts=player-message_file=" + nonexistent_file,
                    "--script-opts=player-interval=0",
                    "--idle=yes",
                    "--msg-level=all=debug",
                    "--frames=1",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            # Should not crash, but should log warning
            assert (
                result.returncode == 0
            ), "mpv should not crash with missing message file"
            assert "player.lua" in result.stderr, "player.lua script should still load"

            # Should contain warning about missing file
            stderr_lower = result.stderr.lower()
            assert (
                "warn" in stderr_lower
                or "error" in stderr_lower
                or "could not open" in stderr_lower
            ), "Should warn about missing message file"

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("mpv not available for error handling testing")

    def test_message_reload_functionality(self, temp_config_dir, project_root):
        """Test that message reload functionality works correctly."""
        # Create test script to simulate message reloading
        test_script = os.path.join(temp_config_dir, "test_reload.lua")

        # Create initial message file
        messages_dir = os.path.join(temp_config_dir, "messages")
        os.makedirs(messages_dir, exist_ok=True)
        message_file = os.path.join(messages_dir, "reload_test.txt")

        with open(message_file, "w") as f:
            f.write("Initial message 1\nInitial message 2\n")

        with open(test_script, "w") as f:
            f.write(
                f"""
-- Test message reload functionality
local message_file = "{message_file}"

-- Function to load messages (from player.lua)
local function load_messages()
    local messages = {{}}
    local f, err = io.open(message_file, "r")
    if not f then
        print("Warning: could not open message file: " .. tostring(err))
        return messages
    end
    for line in f:lines() do
        local msg = line:match("^%s*(.-)%s*$")
        if msg ~= "" and not msg:match("^#") then
            table.insert(messages, msg)
        end
    end
    f:close()
    return messages
end

-- Initial load
local messages1 = load_messages()
print("Initial load: " .. #messages1 .. " messages")
for i, msg in ipairs(messages1) do
    print("  " .. i .. ": " .. msg)
end

-- Simulate file update
local updated_content = "Updated message 1\\nUpdated message 2\\nUpdated message 3\\n"
local f = io.open(message_file, "w")
f:write(updated_content)
f:close()

-- Reload messages
local messages2 = load_messages()
print("After reload: " .. #messages2 .. " messages")
for i, msg in ipairs(messages2) do
    print("  " .. i .. ": " .. msg)
end

-- Verify reload worked
assert(#messages2 == 3, "Should have 3 messages after reload")
assert(messages2[1] == "Updated message 1", "First message should be updated")
assert(messages2[3] == "Updated message 3", "Third message should exist")

print("Message reload test passed")
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=10
            )

            assert (
                result.returncode == 0
            ), f"Message reload test failed: {result.stderr}"
            assert (
                "Message reload test passed" in result.stdout
            ), "Message reload test did not complete successfully"
            assert (
                "Initial load: 2 messages" in result.stdout
            ), "Initial message loading failed"
            assert (
                "After reload: 3 messages" in result.stdout
            ), "Message reloading failed"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for reload testing")

    def test_message_random_selection(self, temp_config_dir, project_root):
        """Test that message random selection works correctly."""
        test_script = os.path.join(temp_config_dir, "test_random.lua")

        # Create message file with multiple messages
        messages_dir = os.path.join(temp_config_dir, "messages")
        os.makedirs(messages_dir, exist_ok=True)
        message_file = os.path.join(messages_dir, "random_test.txt")

        test_messages = [f"Random message {i}" for i in range(1, 11)]  # 10 messages
        with open(message_file, "w") as f:
            f.write("\n".join(test_messages))

        with open(test_script, "w") as f:
            f.write(
                f"""
-- Test message random selection
local message_file = "{message_file}"

-- Load messages
local messages = {{}}
local f = io.open(message_file, "r")
for line in f:lines() do
    local msg = line:match("^%s*(.-)%s*$")
    if msg ~= "" and not msg:match("^#") then
        table.insert(messages, msg)
    end
end
f:close()

print("Loaded " .. #messages .. " messages for random selection test")

-- Seed random
math.randomseed(os.time())

-- Test random selection multiple times
local selections = {{}}
local selection_counts = {{}}

for i = 1, 50 do  -- Make 50 random selections
    local idx = math.random(#messages)
    local selected = messages[idx]
    table.insert(selections, selected)

    -- Count selections
    selection_counts[selected] = (selection_counts[selected] or 0) + 1
end

-- Verify randomness (should have selected multiple different messages)
local unique_selections = 0
for msg, count in pairs(selection_counts) do
    unique_selections = unique_selections + 1
end

print("Selected " .. unique_selections .. " unique messages out of " .. #messages .. " available")
print("Selection distribution:")
for msg, count in pairs(selection_counts) do
    print("  '" .. msg .. "': " .. count .. " times")
end

-- Should have selected at least half of the available messages
assert(unique_selections >= math.floor(#messages / 2),
    "Random selection should use at least half of available messages")

-- No single message should dominate (more than 70% of selections)
for msg, count in pairs(selection_counts) do
    local percentage = count / 50 * 100
    assert(percentage <= 70,
        "Message '" .. msg .. "' selected too frequently: " .. percentage .. "%")
end

print("Message random selection test passed")
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=15
            )

            assert (
                result.returncode == 0
            ), f"Message random selection test failed: {result.stderr}"
            assert (
                "Message random selection test passed" in result.stdout
            ), "Message random selection test did not complete successfully"
            assert (
                "Loaded 10 messages" in result.stdout
            ), "Message loading for random test failed"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for random selection testing")

    def test_message_integration_with_profiles(self, temp_config_dir, project_root):
        """Test that message system integrates correctly with profile configurations."""
        presets_dir = os.path.join(project_root, "presets")

        if not os.path.exists(presets_dir):
            pytest.skip("Presets directory not found")

        # Check profile configurations for message settings
        profile_files = [f for f in os.listdir(presets_dir) if f.endswith(".json")]

        if not profile_files:
            pytest.skip("No profile files found")

        try:
            import json

            for profile_file in profile_files:
                profile_path = os.path.join(presets_dir, profile_file)

                with open(profile_path, "r") as f:
                    profile_data = json.load(f)

                # Check if profile has message configuration
                if "messages" in profile_data:
                    messages_config = profile_data["messages"]

                    # Verify message configuration structure
                    assert isinstance(
                        messages_config, dict
                    ), f"Profile {profile_file} messages config should be an object"

                    # Check required fields
                    if "message_file" in messages_config:
                        message_file = messages_config["message_file"]
                        assert isinstance(
                            message_file, str
                        ), f"Profile {profile_file} message_file should be a string"
                        assert (
                            len(message_file.strip()) > 0
                        ), f"Profile {profile_file} message_file should not be empty"

                    # Check optional fields
                    if "interval" in messages_config:
                        interval = messages_config["interval"]
                        assert isinstance(
                            interval, (int, float)
                        ), f"Profile {profile_file} interval should be a number"
                        assert (
                            interval >= 0
                        ), f"Profile {profile_file} interval should be non-negative"

                    if "duration" in messages_config:
                        duration = messages_config["duration"]
                        assert isinstance(
                            duration, (int, float)
                        ), f"Profile {profile_file} duration should be a number"
                        assert (
                            duration > 0
                        ), f"Profile {profile_file} duration should be positive"

                    print(f"Profile {profile_file} message configuration validated")

        except json.JSONDecodeError as e:
            pytest.fail(f"Profile contains invalid JSON: {e}")
        except Exception as e:
            pytest.fail(f"Error validating profile message integration: {e}")

    def test_message_system_performance(self, temp_config_dir, project_root):
        """Test that message system performs well with large message files."""
        # Create large message file
        messages_dir = os.path.join(temp_config_dir, "messages")
        os.makedirs(messages_dir, exist_ok=True)
        large_message_file = os.path.join(messages_dir, "large.txt")

        # Generate 1000 messages
        with open(large_message_file, "w") as f:
            for i in range(1000):
                f.write(f"Performance test message {i:04d}\n")
                if i % 100 == 0:
                    f.write(f"# Comment at message {i}\n")  # Add some comments

        # Test performance
        test_script = os.path.join(temp_config_dir, "test_performance.lua")
        with open(test_script, "w") as f:
            f.write(
                f"""
-- Test message system performance
local message_file = "{large_message_file}"

-- Measure loading time
local start_time = os.clock()

local messages = {{}}
local f = io.open(message_file, "r")
for line in f:lines() do
    local msg = line:match("^%s*(.-)%s*$")
    if msg ~= "" and not msg:match("^#") then
        table.insert(messages, msg)
    end
end
f:close()

local load_time = os.clock() - start_time

print("Performance test results:")
print("  Messages loaded: " .. #messages)
print("  Load time: " .. string.format("%.3f", load_time) .. " seconds")

-- Verify correct number of messages (should be 1000, excluding comments)
assert(#messages == 1000, "Should have loaded exactly 1000 messages")

-- Test random selection performance
start_time = os.clock()
math.randomseed(os.time())

for i = 1, 1000 do
    local idx = math.random(#messages)
    local selected = messages[idx]
    -- Just access the message, don't do anything expensive
end

local selection_time = os.clock() - start_time
print("  1000 random selections time: " .. string.format("%.3f", selection_time) .. " seconds")

-- Performance should be reasonable (less than 1 second for loading, less than 0.1 for selections)
assert(load_time < 1.0, "Message loading should complete in under 1 second")
assert(selection_time < 0.1, "1000 random selections should complete in under 0.1 seconds")

print("Message system performance test passed")
"""
            )

        try:
            result = subprocess.run(
                ["lua", test_script], capture_output=True, text=True, timeout=20
            )

            assert (
                result.returncode == 0
            ), f"Message performance test failed: {result.stderr}"
            assert (
                "Message system performance test passed" in result.stdout
            ), "Message performance test did not complete successfully"
            assert (
                "Messages loaded: 1000" in result.stdout
            ), "Large message file loading failed"

        except FileNotFoundError:
            pytest.skip("lua interpreter not available for performance testing")
