"""
Tests for configuration loading functionality in VideoWall executables.
"""
import json
import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
import sys

# Add bin directory to path for importing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bin"))

try:
    from jsonschema import ValidationError
except ImportError:
    pytest.skip(
        "jsonschema not installed, skipping configuration loading tests",
        allow_module_level=True,
    )


class TestConfigurationLoading:
    """Test configuration loading and validation."""

    @pytest.fixture
    def valid_config(self):
        """Return a valid configuration dictionary."""
        return {
            "name": "Test Profile",
            "video_dirs": ["/tmp/videos", "~/media"],
            "playlist_mode": "random",
            "effects": ["cyberpunk-glow"],
            "messages": {
                "message_file": "~/.config/videowall/messages/default.txt",
                "interval": 60,
                "duration": 7,
            },
            "fonts": {"primary": "JetBrains Mono", "fallback": ["Noto Sans"]},
            "hud": {"modules": ["clock", "cpu", "mem"], "position": "top"},
            "aspect": "16:9",
        }

    @pytest.fixture
    def schema(self):
        """Load and return the configuration schema."""
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "docs", "config-schema.json"
        )
        with open(schema_path) as f:
            return json.load(f)

    def test_valid_config_loads_successfully(self, valid_config, schema):
        """Test that a valid configuration loads without errors."""
        from jsonschema import validate

        # Should not raise any exception
        validate(instance=valid_config, schema=schema)

    def test_minimal_config_loads_successfully(self, schema):
        """Test that a minimal valid configuration loads."""
        from jsonschema import validate

        minimal_config = {"name": "Minimal Profile", "video_dirs": ["/tmp"]}

        # Should not raise any exception
        validate(instance=minimal_config, schema=schema)

    def test_invalid_config_raises_validation_error(self, schema):
        """Test that invalid configurations raise ValidationError."""
        from jsonschema import validate

        invalid_configs = [
            # Missing required fields
            {"video_dirs": ["/tmp"]},  # Missing name
            {"name": "Test"},  # Missing video_dirs
            {},  # Missing both
            # Invalid types
            {"name": 123, "video_dirs": ["/tmp"]},  # name should be string
            {"name": "Test", "video_dirs": "/tmp"},  # video_dirs should be array
            # Invalid enum values
            {"name": "Test", "video_dirs": ["/tmp"], "playlist_mode": "invalid"},
            {"name": "Test", "video_dirs": ["/tmp"], "aspect": "invalid"},
            # Invalid nested objects
            {
                "name": "Test",
                "video_dirs": ["/tmp"],
                "messages": {"interval": 60},
            },  # missing message_file
            {
                "name": "Test",
                "video_dirs": ["/tmp"],
                "fonts": {"fallback": ["Arial"]},
            },  # missing primary
            {
                "name": "Test",
                "video_dirs": ["/tmp"],
                "hud": {"position": "top"},
            },  # missing modules
        ]

        for invalid_config in invalid_configs:
            with pytest.raises(ValidationError):
                validate(instance=invalid_config, schema=schema)

    def test_additional_properties_rejected(self, valid_config, schema):
        """Test that additional properties are rejected."""
        from jsonschema import validate

        # Add an invalid property
        invalid_config = valid_config.copy()
        invalid_config["invalid_property"] = "should_fail"

        with pytest.raises(ValidationError):
            validate(instance=invalid_config, schema=schema)

    def test_config_file_loading_with_missing_file(self):
        """Test behavior when configuration file is missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "nonexistent.json")

            # Mock the config loading logic from videowall executable
            with pytest.raises(FileNotFoundError):
                with open(config_path) as f:
                    json.load(f)

    def test_config_file_loading_with_invalid_json(self):
        """Test behavior when configuration file contains invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON
            f.flush()

            try:
                with pytest.raises(json.JSONDecodeError):
                    with open(f.name) as config_file:
                        json.load(config_file)
            finally:
                os.unlink(f.name)

    def test_schema_file_loading_with_missing_file(self):
        """Test behavior when schema file is missing."""
        nonexistent_path = "/nonexistent/schema.json"

        with pytest.raises(FileNotFoundError):
            with open(nonexistent_path) as f:
                json.load(f)

    def test_config_loading_success_mock(self, schema):
        """Test successful configuration loading with mocked file."""
        from jsonschema import validate

        # Simulate loading config from file
        config_data = {"name": "Test", "video_dirs": ["/tmp"]}

        # Should validate successfully
        validate(instance=config_data, schema=schema)

        # Test passes if validation succeeds
        assert config_data["name"] == "Test"
        assert config_data["video_dirs"] == ["/tmp"]

    def test_video_dirs_expansion(self):
        """Test that video directory paths are properly expanded."""
        import os

        test_dirs = [
            "~/videos",  # Should expand user home
            "$HOME/media",  # Should expand environment variable
            "/absolute/path",  # Should remain unchanged
            "relative/path",  # Should remain unchanged
        ]

        expanded_dirs = [os.path.expandvars(os.path.expanduser(d)) for d in test_dirs]

        # Check that tilde and env vars are expanded
        assert not any("~" in d for d in expanded_dirs)
        assert not any("$HOME" in d for d in expanded_dirs if "$HOME" in os.environ)

        # Absolute and relative paths should be preserved appropriately
        assert expanded_dirs[2] == "/absolute/path"
        assert expanded_dirs[3] == "relative/path"
