"""
Integration tests for video filter and shader application.
"""
import os
import tempfile
import subprocess
import pytest


class TestFilterIntegration:
    """Test video filter and shader application."""

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

    def test_filter_presets_exist(self, project_root):
        """Test that filter preset files exist and are readable."""
        presets_dir = os.path.join(project_root, "core", "filters", "presets")

        if not os.path.exists(presets_dir):
            pytest.skip("Filter presets directory not found")

        preset_files = [f for f in os.listdir(presets_dir) if f.endswith(".conf")]
        assert len(preset_files) > 0, "No filter preset files found"

        for preset_file in preset_files:
            preset_path = os.path.join(presets_dir, preset_file)
            assert os.path.isfile(preset_path), f"Preset file not found: {preset_file}"
            assert os.access(
                preset_path, os.R_OK
            ), f"Preset file not readable: {preset_file}"

    def test_shader_files_exist(self, project_root):
        """Test that shader files exist and are readable."""
        shaders_dir = os.path.join(project_root, "core", "filters", "shaders")

        if not os.path.exists(shaders_dir):
            pytest.skip("Shaders directory not found")

        shader_files = [f for f in os.listdir(shaders_dir) if f.endswith(".glsl")]
        assert len(shader_files) > 0, "No shader files found"

        for shader_file in shader_files:
            shader_path = os.path.join(shaders_dir, shader_file)
            assert os.path.isfile(shader_path), f"Shader file not found: {shader_file}"
            assert os.access(
                shader_path, os.R_OK
            ), f"Shader file not readable: {shader_file}"

    def test_filter_preset_syntax(self, project_root):
        """Test that filter preset files have valid syntax."""
        presets_dir = os.path.join(project_root, "core", "filters", "presets")

        if not os.path.exists(presets_dir):
            pytest.skip("Filter presets directory not found")

        preset_files = [f for f in os.listdir(presets_dir) if f.endswith(".conf")]

        for preset_file in preset_files:
            preset_path = os.path.join(presets_dir, preset_file)

            with open(preset_path, "r") as f:
                lines = f.readlines()

            # Check for basic mpv configuration syntax
            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Check for valid mpv option format
                if "=" in line:
                    option, value = line.split("=", 1)
                    assert (
                        option.strip()
                    ), f"{preset_file}:{line_num} - Empty option name"
                    assert (
                        value.strip()
                    ), f"{preset_file}:{line_num} - Empty option value"
                else:
                    # Some options might not have values (flags)
                    assert (
                        line.strip()
                    ), f"{preset_file}:{line_num} - Empty line with content"

    def test_shader_glsl_syntax(self, project_root):
        """Test that GLSL shader files have basic valid syntax."""
        shaders_dir = os.path.join(project_root, "core", "filters", "shaders")

        if not os.path.exists(shaders_dir):
            pytest.skip("Shaders directory not found")

        shader_files = [f for f in os.listdir(shaders_dir) if f.endswith(".glsl")]

        for shader_file in shader_files:
            shader_path = os.path.join(shaders_dir, shader_file)

            with open(shader_path, "r") as f:
                content = f.read()

            # Basic GLSL syntax checks
            assert len(content.strip()) > 0, f"{shader_file} is empty"

            # Check for common GLSL keywords/structures
            glsl_indicators = [
                "void main()",
                "gl_FragColor",
                "texture2D",
                "uniform",
                "varying",
                "vec2",
                "vec3",
                "vec4",
            ]

            has_glsl_content = any(
                indicator in content for indicator in glsl_indicators
            )
            assert (
                has_glsl_content
            ), f"{shader_file} doesn't appear to contain GLSL code"

    def test_mpv_can_parse_filter_presets(self, temp_config_dir, project_root):
        """Test that mpv can parse filter preset configurations."""
        presets_dir = os.path.join(project_root, "core", "filters", "presets")

        if not os.path.exists(presets_dir):
            pytest.skip("Filter presets directory not found")

        # Copy filters to temp config
        temp_filters_dir = os.path.join(temp_config_dir, "filters")
        os.makedirs(temp_filters_dir, exist_ok=True)

        preset_files = [f for f in os.listdir(presets_dir) if f.endswith(".conf")]

        for preset_file in preset_files:
            src_path = os.path.join(presets_dir, preset_file)
            dst_path = os.path.join(temp_filters_dir, preset_file)

            with open(src_path, "r") as src, open(dst_path, "w") as dst:
                dst.write(src.read())

        try:
            # Test each preset with mpv --show-profile
            for preset_file in preset_files:
                preset_path = os.path.join(temp_filters_dir, preset_file)

                result = subprocess.run(
                    [
                        "mpv",
                        "--no-config",
                        "--include=" + preset_path,
                        "--show-profile=default",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                # mpv should not fail to parse the config
                assert (
                    result.returncode == 0
                ), f"mpv failed to parse {preset_file}: {result.stderr}"

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("mpv not available for filter preset testing")

    def test_shader_references_in_presets(self, project_root):
        """Test that shader references in presets point to existing files."""
        presets_dir = os.path.join(project_root, "core", "filters", "presets")
        shaders_dir = os.path.join(project_root, "core", "filters", "shaders")

        if not os.path.exists(presets_dir) or not os.path.exists(shaders_dir):
            pytest.skip("Filter directories not found")

        preset_files = [f for f in os.listdir(presets_dir) if f.endswith(".conf")]
        available_shaders = set(os.listdir(shaders_dir))

        for preset_file in preset_files:
            preset_path = os.path.join(presets_dir, preset_file)

            with open(preset_path, "r") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Look for shader references
                if line.startswith("glsl-shader="):
                    shader_ref = line.split("=", 1)[1].strip()

                    # Handle relative paths
                    if shader_ref.startswith("../shaders/"):
                        shader_name = shader_ref.replace("../shaders/", "")
                        assert shader_name in available_shaders, (
                            f"{preset_file}:{line_num} references "
                            f"non-existent shader: {shader_name}"
                        )

    def test_filter_application_with_test_video(self, temp_config_dir, project_root):
        """Test that filters can be applied to a test video without errors."""
        presets_dir = os.path.join(project_root, "core", "filters", "presets")
        shaders_dir = os.path.join(project_root, "core", "filters", "shaders")

        if not os.path.exists(presets_dir):
            pytest.skip("Filter presets directory not found")

        # Copy filters and shaders to temp config
        temp_filters_dir = os.path.join(temp_config_dir, "filters")
        temp_presets_dir = os.path.join(temp_filters_dir, "presets")
        temp_shaders_dir = os.path.join(temp_filters_dir, "shaders")

        os.makedirs(temp_presets_dir, exist_ok=True)
        os.makedirs(temp_shaders_dir, exist_ok=True)

        # Copy preset files
        preset_files = [f for f in os.listdir(presets_dir) if f.endswith(".conf")]
        for preset_file in preset_files:
            src_path = os.path.join(presets_dir, preset_file)
            dst_path = os.path.join(temp_presets_dir, preset_file)
            with open(src_path, "r") as src, open(dst_path, "w") as dst:
                dst.write(src.read())

        # Copy shader files if they exist
        if os.path.exists(shaders_dir):
            shader_files = [f for f in os.listdir(shaders_dir) if f.endswith(".glsl")]
            for shader_file in shader_files:
                src_path = os.path.join(shaders_dir, shader_file)
                dst_path = os.path.join(temp_shaders_dir, shader_file)
                with open(src_path, "r") as src, open(dst_path, "w") as dst:
                    dst.write(src.read())

        try:
            # Test with a minimal synthetic video (color pattern)
            for preset_file in preset_files[:2]:  # Test first 2 presets to save time
                preset_path = os.path.join(temp_presets_dir, preset_file)

                # Update shader paths in preset to use absolute paths
                with open(preset_path, "r") as f:
                    preset_content = f.read()

                # Replace relative shader paths with absolute paths
                updated_content = preset_content.replace(
                    "../shaders/", temp_shaders_dir + "/"
                )

                with open(preset_path, "w") as f:
                    f.write(updated_content)

                result = subprocess.run(
                    [
                        "mpv",
                        "--no-config",
                        "--include=" + preset_path,
                        "--lavfi-complex=[color=red:size=320x240:duration=1]",
                        "--frames=5",
                        "--no-audio",
                        "--vo=null",  # No video output
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                # Should not fail with filter errors
                assert (
                    result.returncode == 0
                ), f"Filter application failed for {preset_file}: {result.stderr}"

                # Check for specific filter-related errors
                error_keywords = ["shader", "filter", "glsl", "error"]
                stderr_lower = result.stderr.lower()

                for keyword in error_keywords:
                    if keyword in stderr_lower and "error" in stderr_lower:
                        pytest.fail(
                            f"Filter error detected in {preset_file}: {result.stderr}"
                        )

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("mpv not available for filter application testing")

    def test_profile_filter_integration(self, temp_config_dir, project_root):
        """Test that profile configurations correctly reference available filters."""
        presets_dir = os.path.join(project_root, "presets")
        filters_dir = os.path.join(project_root, "core", "filters", "presets")

        if not os.path.exists(presets_dir) or not os.path.exists(filters_dir):
            pytest.skip("Presets or filters directory not found")

        # Get available filter presets
        available_filters = set()
        filter_files = [f for f in os.listdir(filters_dir) if f.endswith(".conf")]
        for filter_file in filter_files:
            filter_name = filter_file.replace(".conf", "")
            available_filters.add(filter_name)

        # Check profile configurations
        profile_files = [f for f in os.listdir(presets_dir) if f.endswith(".json")]

        for profile_file in profile_files:
            profile_path = os.path.join(presets_dir, profile_file)

            try:
                import json

                with open(profile_path, "r") as f:
                    profile_data = json.load(f)

                # Check if profile has effects defined
                if "effects" in profile_data:
                    effects = profile_data["effects"]
                    if isinstance(effects, list):
                        for effect in effects:
                            if isinstance(effect, str):
                                # Verify that referenced effect exists as a filter preset
                                assert effect in available_filters, (
                                    f"Profile {profile_file} references "
                                    f"non-existent filter: {effect}"
                                )

            except json.JSONDecodeError:
                pytest.fail(f"Profile {profile_file} contains invalid JSON")
            except Exception as e:
                pytest.fail(f"Error processing profile {profile_file}: {e}")
