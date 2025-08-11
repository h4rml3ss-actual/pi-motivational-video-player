"""
Tests for profile validation and schema compliance.
"""
import json
import os
import tempfile
import pytest
from unittest.mock import patch

try:
    from jsonschema import validate, ValidationError
except ImportError:
    pytest.skip(
        "jsonschema not installed, skipping profile validation tests",
        allow_module_level=True,
    )


class TestProfileValidation:
    """Test profile validation against schema."""

    @pytest.fixture
    def schema(self):
        """Load and return the configuration schema."""
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "docs", "config-schema.json"
        )
        with open(schema_path) as f:
            return json.load(f)

    @pytest.fixture
    def preset_profiles(self):
        """Load all preset profile files."""
        presets_dir = os.path.join(os.path.dirname(__file__), "..", "presets")
        profiles = {}

        for filename in os.listdir(presets_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(presets_dir, filename)
                with open(filepath) as f:
                    profiles[filename] = json.load(f)

        return profiles

    def test_all_preset_profiles_are_valid(self, preset_profiles, schema):
        """Test that all preset profiles validate against the schema."""
        for profile_name, profile_data in preset_profiles.items():
            try:
                validate(instance=profile_data, schema=schema)
            except ValidationError as e:
                pytest.fail(f"Profile {profile_name} failed validation: {e.message}")

    def test_cyberpunk_hud_profile_structure(self, preset_profiles):
        """Test specific structure of cyberpunk_hud profile."""
        profile = preset_profiles.get("cyberpunk_hud.json")
        assert profile is not None, "cyberpunk_hud.json profile not found"

        # Check required fields
        assert profile["name"] == "Cyberpunk HUD"
        assert isinstance(profile["video_dirs"], list)
        assert len(profile["video_dirs"]) > 0

        # Check optional fields are present and valid
        assert profile["playlist_mode"] in ["random", "ordered"]
        assert isinstance(profile["effects"], list)

        # Check nested objects
        assert "messages" in profile
        assert "message_file" in profile["messages"]
        assert "interval" in profile["messages"]
        assert "duration" in profile["messages"]

        assert "fonts" in profile
        assert "primary" in profile["fonts"]
        assert "fallback" in profile["fonts"]

        assert "hud" in profile
        assert "modules" in profile["hud"]
        assert "position" in profile["hud"]
        assert profile["hud"]["position"] in ["top", "bottom", "left", "right"]

        assert profile["aspect"] in ["4:3", "16:9", "stretch"]

    def test_pure_vhs_profile_structure(self, preset_profiles):
        """Test specific structure of pure_vhs profile."""
        profile = preset_profiles.get("pure_vhs.json")
        assert profile is not None, "pure_vhs.json profile not found"

        # Check required fields
        assert profile["name"] == "Pure VHS"
        assert isinstance(profile["video_dirs"], list)
        assert len(profile["video_dirs"]) > 0

        # Check that it has different settings from cyberpunk profile
        assert profile["playlist_mode"] == "random"
        assert "vhs-clean" in profile["effects"]
        assert profile["aspect"] == "4:3"

    def test_profile_with_missing_required_fields_fails(self, schema):
        """Test that profiles missing required fields fail validation."""
        invalid_profiles = [
            # Missing name
            {"video_dirs": ["/tmp"]},
            # Missing video_dirs
            {"name": "Test Profile"},
        ]

        for invalid_profile in invalid_profiles:
            with pytest.raises(ValidationError):
                validate(instance=invalid_profile, schema=schema)

        # Empty video_dirs is actually valid according to the schema
        valid_empty_dirs = {"name": "Test Profile", "video_dirs": []}
        # Should not raise an exception
        validate(instance=valid_empty_dirs, schema=schema)

    def test_profile_with_invalid_enum_values_fails(self, schema):
        """Test that profiles with invalid enum values fail validation."""
        base_profile = {"name": "Test Profile", "video_dirs": ["/tmp"]}

        invalid_enum_profiles = [
            # Invalid playlist_mode
            {**base_profile, "playlist_mode": "invalid_mode"},
            # Invalid aspect ratio
            {**base_profile, "aspect": "invalid_aspect"},
            # Invalid HUD position
            {
                **base_profile,
                "hud": {"modules": ["clock"], "position": "invalid_position"},
            },
        ]

        for invalid_profile in invalid_enum_profiles:
            with pytest.raises(ValidationError):
                validate(instance=invalid_profile, schema=schema)

    def test_profile_with_invalid_nested_objects_fails(self, schema):
        """Test that profiles with invalid nested objects fail validation."""
        base_profile = {"name": "Test Profile", "video_dirs": ["/tmp"]}

        invalid_nested_profiles = [
            # Messages object missing required field
            {**base_profile, "messages": {"interval": 60, "duration": 5}},
            # Fonts object missing required field
            {**base_profile, "fonts": {"fallback": ["Arial"]}},
            # HUD object missing required field
            {**base_profile, "hud": {"position": "top"}},
            # Messages with additional invalid property
            {
                **base_profile,
                "messages": {"message_file": "/tmp/msg.txt", "invalid_prop": "value"},
            },
        ]

        for invalid_profile in invalid_nested_profiles:
            with pytest.raises(ValidationError):
                validate(instance=invalid_profile, schema=schema)

    def test_profile_with_additional_properties_fails(self, schema):
        """Test that profiles with additional properties fail validation."""
        invalid_profile = {
            "name": "Test Profile",
            "video_dirs": ["/tmp"],
            "invalid_additional_property": "should_fail",
        }

        with pytest.raises(ValidationError):
            validate(instance=invalid_profile, schema=schema)

    def test_profile_type_validation(self, schema):
        """Test that profiles with incorrect types fail validation."""
        invalid_type_profiles = [
            # name should be string
            {"name": 123, "video_dirs": ["/tmp"]},
            # video_dirs should be array
            {"name": "Test", "video_dirs": "/tmp"},
            # video_dirs items should be strings
            {"name": "Test", "video_dirs": [123, 456]},
            # effects should be array
            {"name": "Test", "video_dirs": ["/tmp"], "effects": "single_effect"},
            # messages.interval should be number
            {
                "name": "Test",
                "video_dirs": ["/tmp"],
                "messages": {"message_file": "/tmp/msg.txt", "interval": "60"},
            },
        ]

        for invalid_profile in invalid_type_profiles:
            with pytest.raises(ValidationError):
                validate(instance=invalid_profile, schema=schema)

    def test_create_valid_profile_programmatically(self, schema):
        """Test creating a valid profile programmatically and validating it."""
        new_profile = {
            "name": "Test Generated Profile",
            "video_dirs": ["/home/user/videos", "/media/external"],
            "playlist_mode": "ordered",
            "effects": ["pixel-grid", "glitch-storm"],
            "messages": {
                "message_file": "/home/user/.config/videowall/messages/custom.txt",
                "interval": 45,
                "duration": 3,
            },
            "fonts": {
                "primary": "Courier New",
                "fallback": ["DejaVu Sans Mono", "Liberation Mono"],
            },
            "hud": {
                "modules": ["clock", "cpu", "mem", "net", "uptime"],
                "position": "bottom",
            },
            "aspect": "stretch",
        }

        # Should validate without raising an exception
        validate(instance=new_profile, schema=schema)

    def test_profile_loading_from_file(self, schema):
        """Test loading and validating a profile from a file."""
        test_profile = {"name": "File Test Profile", "video_dirs": ["/tmp/test"]}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_profile, f)
            f.flush()

            try:
                # Load profile from file
                with open(f.name) as profile_file:
                    loaded_profile = json.load(profile_file)

                # Validate loaded profile
                validate(instance=loaded_profile, schema=schema)

                # Verify content matches
                assert loaded_profile["name"] == test_profile["name"]
                assert loaded_profile["video_dirs"] == test_profile["video_dirs"]

            finally:
                os.unlink(f.name)

    def test_schema_completeness(self, schema):
        """Test that the schema covers all expected properties."""
        # Check that schema has all expected top-level properties
        expected_properties = {
            "name",
            "video_dirs",
            "playlist_mode",
            "effects",
            "messages",
            "fonts",
            "hud",
            "aspect",
        }

        schema_properties = set(schema["properties"].keys())
        assert expected_properties.issubset(
            schema_properties
        ), f"Schema missing properties: {expected_properties - schema_properties}"

        # Check required fields
        assert "required" in schema
        assert "name" in schema["required"]
        assert "video_dirs" in schema["required"]

        # Check that additional properties are not allowed
        assert schema.get("additionalProperties") is False
