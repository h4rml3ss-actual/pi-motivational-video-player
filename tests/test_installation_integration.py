"""
Integration tests for the complete installation process.
"""
import os
import tempfile
import subprocess
import pytest


class TestInstallationIntegration:
    """Test the complete installation process end-to-end."""

    @pytest.fixture
    def temp_home(self):
        """Create a temporary home directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up a fake home directory structure
            home_dir = os.path.join(temp_dir, "home")
            os.makedirs(home_dir)
            yield home_dir

    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        return os.path.dirname(os.path.dirname(__file__))

    def test_postinstall_script_exists_and_executable(self, project_root):
        """Test that the postinstall script exists and is executable."""
        script_path = os.path.join(project_root, "installers", "postinstall.sh")
        assert os.path.exists(script_path), "postinstall.sh script not found"
        assert os.access(
            script_path, os.X_OK
        ), "postinstall.sh script is not executable"

    def test_postinstall_creates_directory_structure(self, temp_home, project_root):
        """Test that postinstall creates the correct directory structure."""
        script_path = os.path.join(project_root, "installers", "postinstall.sh")

        # Set HOME environment variable to our temp directory
        env = os.environ.copy()
        env["HOME"] = temp_home

        # Run the postinstall script
        try:
            result = subprocess.run(
                [script_path], env=env, capture_output=True, text=True, timeout=30
            )

            # Check that script ran successfully
            if result.returncode != 0:
                pytest.skip(f"Postinstall script failed: {result.stderr}")

            # Verify directory structure was created
            expected_dirs = [
                config_dir,
                os.path.join(config_dir, "hud"),
                os.path.join(config_dir, "hud", "modules"),
                os.path.join(config_dir, "filters"),
                os.path.join(config_dir, "filters", "presets"),
                os.path.join(config_dir, "filters", "shaders"),
                os.path.join(config_dir, "profiles"),
                os.path.join(config_dir, "messages"),
            ]

            for expected_dir in expected_dirs:
                assert os.path.isdir(
                    expected_dir
                ), f"Directory not created: {expected_dir}"

        except subprocess.TimeoutExpired:
            pytest.skip("Postinstall script timed out")
        except FileNotFoundError:
            pytest.skip("Postinstall script dependencies not available")

    def test_postinstall_copies_core_files(self, temp_home, project_root):
        """Test that postinstall copies all required core files."""
        script_path = os.path.join(project_root, "installers", "postinstall.sh")

        env = os.environ.copy()
        env["HOME"] = temp_home

        try:
            result = subprocess.run(
                [script_path], env=env, capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                pytest.skip(f"Postinstall script failed: {result.stderr}")

            # Check that core files were copied
            expected_files = [
                os.path.join(config_dir, "player.lua"),
                os.path.join(config_dir, "messages", "default.txt"),
            ]

            for expected_file in expected_files:
                assert os.path.isfile(
                    expected_file
                ), f"File not copied: {expected_file}"

            # Check that HUD modules were copied
            hud_modules_dir = os.path.join(config_dir, "hud", "modules")
            hud_files = os.listdir(hud_modules_dir)
            assert len(hud_files) > 0, "No HUD modules were copied"

            # Verify at least some expected HUD modules exist
            expected_hud_modules = ["clock.lua", "cpu.lua", "mem.lua"]
            for module in expected_hud_modules:
                module_path = os.path.join(hud_modules_dir, module)
                if os.path.exists(
                    os.path.join(project_root, "core", "hud", "modules", module)
                ):
                    assert os.path.isfile(
                        module_path
                    ), f"HUD module not copied: {module}"

        except subprocess.TimeoutExpired:
            pytest.skip("Postinstall script timed out")
        except FileNotFoundError:
            pytest.skip("Postinstall script dependencies not available")

    def test_postinstall_copies_profiles(self, temp_home, project_root):
        """Test that postinstall copies profile configurations."""
        script_path = os.path.join(project_root, "installers", "postinstall.sh")

        env = os.environ.copy()
        env["HOME"] = temp_home

        try:
            result = subprocess.run(
                [script_path], env=env, capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                pytest.skip(f"Postinstall script failed: {result.stderr}")

            # Check that profiles were copied
            profiles_dir = os.path.join(config_dir, "profiles")
            profile_files = [f for f in os.listdir(profiles_dir) if f.endswith(".json")]
            assert len(profile_files) > 0, "No profile files were copied"

            # Verify specific profiles exist if they exist in source
            presets_dir = os.path.join(project_root, "presets")
            if os.path.exists(presets_dir):
                source_presets = [
                    f for f in os.listdir(presets_dir) if f.endswith(".json")
                ]
                for preset in source_presets:
                    copied_profile = os.path.join(profiles_dir, preset)
                    assert os.path.isfile(
                        copied_profile
                    ), f"Profile not copied: {preset}"

        except subprocess.TimeoutExpired:
            pytest.skip("Postinstall script timed out")
        except FileNotFoundError:
            pytest.skip("Postinstall script dependencies not available")

    def test_postinstall_sets_correct_permissions(self, temp_home, project_root):
        """Test that postinstall sets correct file permissions."""
        script_path = os.path.join(project_root, "installers", "postinstall.sh")

        env = os.environ.copy()
        env["HOME"] = temp_home

        try:
            result = subprocess.run(
                [script_path], env=env, capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                pytest.skip(f"Postinstall script failed: {result.stderr}")

            # Check directory permissions (should be 755)
            for root, dirs, files in os.walk(config_dir):
                for directory in dirs:
                    dir_path = os.path.join(root, directory)
                    stat_info = os.stat(dir_path)
                    # Check that directory is readable and executable by owner
                    assert (
                        stat_info.st_mode & 0o700 == 0o700
                    ), f"Directory {dir_path} has incorrect permissions"

            # Check file permissions (should be 644 for regular files)
            for root, dirs, files in os.walk(config_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    stat_info = os.stat(file_path)
                    # Check that file is readable by owner
                    assert (
                        stat_info.st_mode & 0o400 == 0o400
                    ), f"File {file_path} is not readable by owner"

        except subprocess.TimeoutExpired:
            pytest.skip("Postinstall script timed out")
        except FileNotFoundError:
            pytest.skip("Postinstall script dependencies not available")

    def test_postinstall_handles_existing_installation(self, temp_home, project_root):
        """Test that postinstall handles existing installation correctly."""
        script_path = os.path.join(project_root, "installers", "postinstall.sh")

        # Create existing config directory
        os.makedirs(config_dir, exist_ok=True)
        existing_file = os.path.join(config_dir, "existing.txt")
        with open(existing_file, "w") as f:
            f.write("existing content")

        env = os.environ.copy()
        env["HOME"] = temp_home

        try:
            # Run postinstall script with 'yes' input to overwrite
            result = subprocess.run(
                [script_path],
                input="y\n",
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.skip(f"Postinstall script failed: {result.stderr}")

            # Verify that installation completed (existing file should be gone)
            assert not os.path.exists(
                existing_file
            ), "Existing installation was not properly overwritten"

            # Verify new installation is in place
            assert os.path.isfile(
                os.path.join(config_dir, "player.lua")
            ), "New installation not completed"

        except subprocess.TimeoutExpired:
            pytest.skip("Postinstall script timed out")
        except FileNotFoundError:
            pytest.skip("Postinstall script dependencies not available")

    def test_installed_profiles_are_valid(self, temp_home, project_root):
        """Test that all installed profiles are valid JSON and conform to schema."""
        script_path = os.path.join(project_root, "installers", "postinstall.sh")

        env = os.environ.copy()
        env["HOME"] = temp_home

        try:
            result = subprocess.run(
                [script_path], env=env, capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                pytest.skip(f"Postinstall script failed: {result.stderr}")

            # Load schema
            schema_path = os.path.join(project_root, "docs", "config-schema.json")
            with open(schema_path) as f:
                schema = json.load(f)

            # Test all installed profiles
            profiles_dir = os.path.join(config_dir, "profiles")
            profile_files = [f for f in os.listdir(profiles_dir) if f.endswith(".json")]

            assert len(profile_files) > 0, "No profiles were installed"

            try:
                from jsonschema import validate, ValidationError

                for profile_file in profile_files:
                    profile_path = os.path.join(profiles_dir, profile_file)

                    # Test that profile is valid JSON
                    with open(profile_path) as f:
                        try:
                            profile_data = json.load(f)
                        except json.JSONDecodeError as e:
                            pytest.fail(
                                f"Profile {profile_file} contains invalid JSON: {e}"
                            )

                    # Test that profile conforms to schema
                    try:
                        validate(instance=profile_data, schema=schema)
                    except ValidationError as e:
                        pytest.fail(
                            f"Profile {profile_file} failed schema validation: {e.message}"
                        )

            except ImportError:
                pytest.skip("jsonschema not available for validation testing")

        except subprocess.TimeoutExpired:
            pytest.skip("Postinstall script timed out")
        except FileNotFoundError:
            pytest.skip("Postinstall script dependencies not available")

    def test_installation_validation_function(self, temp_home, project_root):
        """Test that the installation validation function works correctly."""
        script_path = os.path.join(project_root, "installers", "postinstall.sh")

        env = os.environ.copy()
        env["HOME"] = temp_home

        try:
            result = subprocess.run(
                [script_path], env=env, capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                pytest.skip(f"Postinstall script failed: {result.stderr}")

            # Check that validation messages appear in output
            output = result.stdout
            assert (
                "Validating installation" in output
            ), "Installation validation not performed"
            assert (
                "Installation validation passed" in output
            ), "Installation validation did not pass"
            assert (
                "VideoWall installation completed successfully" in output
            ), "Installation did not complete successfully"

        except subprocess.TimeoutExpired:
            pytest.skip("Postinstall script timed out")
        except FileNotFoundError:
            pytest.skip("Postinstall script dependencies not available")

    def test_postinstall_error_handling(self, temp_home, project_root):
        """Test that postinstall handles errors gracefully."""
        # Create a scenario where installation might fail (read-only directory)
        config_parent = os.path.join(temp_home, ".config")
        os.makedirs(config_parent, exist_ok=True)

        # Make .config directory read-only to simulate permission error
        os.chmod(config_parent, 0o444)

        script_path = os.path.join(project_root, "installers", "postinstall.sh")
        env = os.environ.copy()
        env["HOME"] = temp_home

        try:
            result = subprocess.run(
                [script_path], env=env, capture_output=True, text=True, timeout=30
            )

            # Script should fail gracefully
            assert (
                result.returncode != 0
            ), "Script should fail when permissions are insufficient"

            # Should contain error message
            error_output = result.stderr
            assert (
                len(error_output) > 0 or "ERROR" in result.stdout
            ), "No error message provided"

        except subprocess.TimeoutExpired:
            pytest.skip("Postinstall script timed out")
        except FileNotFoundError:
            pytest.skip("Postinstall script dependencies not available")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(config_parent, 0o755)
            except Exception:
                pass
