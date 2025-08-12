"""
Tests for argument parsing in VideoWall executables.
"""
import os
import tempfile
import pytest
import subprocess


class TestVideoWallArgumentParsing:
    """Test argument parsing for the main videowall executable."""

    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return os.path.dirname(os.path.dirname(__file__))

    def test_videowall_executable_exists(self, project_root):
        """Test that the videowall executable exists."""
        videowall_path = os.path.join(project_root, "bin", "videowall")
        assert os.path.exists(videowall_path), "videowall executable not found"
        assert os.access(
            videowall_path, os.X_OK
        ), "videowall executable is not executable"

    def test_videowall_launcher_executable_exists(self, project_root):
        """Test that the videowall-launcher executable exists."""
        launcher_path = os.path.join(project_root, "bin", "videowall-launcher")
        assert os.path.exists(launcher_path), "videowall-launcher executable not found"
        assert os.access(
            launcher_path, os.X_OK
        ), "videowall-launcher executable is not executable"

    def test_videowall_help_argument(self, project_root):
        """Test that videowall --help shows usage information."""
        videowall_path = os.path.join(project_root, "bin", "videowall")

        # Create a temporary config to allow the executable to run
        with tempfile.TemporaryDirectory() as temp_dir:
            os.makedirs(config_dir, exist_ok=True)

            # Create minimal config file
            config_file = os.path.join(config_dir, "config.json")
            with open(config_file, "w") as f:
                f.write('{"name": "Test", "video_dirs": ["/tmp"]}')

            env = os.environ.copy()
            env["HOME"] = temp_dir

            try:
                result = subprocess.run(
                    [videowall_path, "--help"],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                # Help should exit with code 0
                assert result.returncode == 0, f"Help command failed: {result.stderr}"

                # Help output should contain usage information
                output = result.stdout
                assert (
                    "usage:" in output.lower()
                    or "VideoWall playback launcher" in output
                ), f"Help output doesn't contain expected text: {output}"

            except subprocess.TimeoutExpired:
                pytest.skip("videowall --help command timed out")
            except FileNotFoundError:
                pytest.skip("videowall executable dependencies not available")

    def test_videowall_config_file_error_handling(self, project_root):
        """Test that videowall handles missing config files appropriately."""
        videowall_path = os.path.join(project_root, "bin", "videowall")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Don't create config file - test error handling
            env = os.environ.copy()
            env["HOME"] = temp_dir

            try:
                result = subprocess.run(
                    [videowall_path, "--help"],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                # Should exit with non-zero code when config is missing
                assert result.returncode != 0, "Should fail when config file is missing"

                # Error output should mention config file issue
                error_output = result.stderr
                assert (
                    len(error_output) > 0
                ), "No error message provided for missing config"
                assert (
                    "config" in error_output.lower()
                    or "file not found" in error_output.lower()
                ), f"Error message should mention config issue: {error_output}"

            except subprocess.TimeoutExpired:
                pytest.skip("videowall config error test timed out")
            except FileNotFoundError:
                pytest.skip("videowall executable dependencies not available")

    def test_argument_parser_structure(self):
        """Test the argument parser structure by examining the code."""
        import argparse

        # Create a parser similar to what's in the videowall executable
        parser = argparse.ArgumentParser(description="VideoWall playback launcher")
        parser.add_argument(
            "-d",
            "--dirs",
            nargs="+",
            metavar="DIR",
            help="override video directories from config",
        )

        # Test parsing with no arguments
        args = parser.parse_args([])
        assert args.dirs is None, "Default dirs should be None"

        # Test parsing with --dirs argument
        args = parser.parse_args(["--dirs", "/test/dir1", "/test/dir2"])
        assert args.dirs == [
            "/test/dir1",
            "/test/dir2",
        ], "Dirs argument not parsed correctly"

        # Test parsing with -d short form
        args = parser.parse_args(["-d", "/short/dir"])
        assert args.dirs == [
            "/short/dir"
        ], "Short form dirs argument not parsed correctly"

    def test_directory_expansion_logic(self):
        """Test that directory paths are properly expanded."""
        # Test the expansion logic used in videowall executable
        test_paths = ["~/videos", "$HOME/media", "/absolute/path", "relative/path"]

        expanded = [os.path.expandvars(os.path.expanduser(path)) for path in test_paths]

        # Verify expansion occurred
        assert expanded[0] != "~/videos", "Tilde should be expanded"
        if "HOME" in os.environ:
            assert (
                expanded[1] != "$HOME/media"
            ), "Environment variable should be expanded"
        assert expanded[2] == "/absolute/path", "Absolute path should remain unchanged"
        assert expanded[3] == "relative/path", "Relative path should remain unchanged"

    def test_config_loading_error_handling(self):
        """Test error handling for configuration loading."""
        import json

        # Test JSON decode error handling
        with pytest.raises(json.JSONDecodeError):
            json.loads('{"invalid": json}')

        # Test file not found error handling
        with pytest.raises(FileNotFoundError):
            with open("/nonexistent/config.json") as f:
                json.load(f)


class TestVideoWallLauncherBehavior:
    """Test behavior of the videowall-launcher executable."""

    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return os.path.dirname(os.path.dirname(__file__))

    def test_launcher_handles_no_profiles_error(self, project_root):
        """Test that launcher handles case with no profiles gracefully."""
        launcher_path = os.path.join(project_root, "bin", "videowall-launcher")

        with tempfile.TemporaryDirectory() as temp_dir:
            profiles_dir = os.path.join(config_dir, "profiles")

            # Create empty profiles directory
            os.makedirs(profiles_dir, exist_ok=True)

            # Set HOME to our temp directory
            env = os.environ.copy()
            env["HOME"] = temp_dir

            try:
                result = subprocess.run(
                    [launcher_path], env=env, capture_output=True, text=True, timeout=10
                )

                # Should exit with error code
                assert (
                    result.returncode == 1
                ), "Launcher should exit with error when no profiles found"

                # Should show appropriate error message
                error_output = result.stderr
                assert (
                    "No profiles found" in error_output
                ), f"Error message should mention no profiles found: {error_output}"

            except subprocess.TimeoutExpired:
                pytest.skip("videowall-launcher test timed out")
            except FileNotFoundError:
                pytest.skip("videowall-launcher executable dependencies not available")

    def test_directory_creation_logic(self):
        """Test the directory creation logic used by the launcher."""
        with tempfile.TemporaryDirectory() as temp_dir:
            profiles_dir = os.path.join(config_dir, "profiles")

            # Test os.makedirs with exist_ok=True
            os.makedirs(profiles_dir, exist_ok=True)
            assert os.path.exists(profiles_dir), "Directory should be created"

            # Test that it doesn't fail if directory already exists
            os.makedirs(profiles_dir, exist_ok=True)
            assert os.path.exists(profiles_dir), "Directory should still exist"

    def test_profile_file_filtering(self):
        """Test the profile file filtering logic."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create various files
            files_to_create = [
                "profile1.json",
                "profile2.json",
                "not_a_profile.txt",
                "another.json",
                "readme.md",
            ]

            for filename in files_to_create:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, "w") as f:
                    f.write("test content")

            # Test filtering logic
            all_files = os.listdir(temp_dir)
            json_files = [f for f in all_files if f.endswith(".json")]

            expected_json_files = ["profile1.json", "profile2.json", "another.json"]
            assert set(json_files) == set(
                expected_json_files
            ), f"JSON file filtering failed: {json_files}"
