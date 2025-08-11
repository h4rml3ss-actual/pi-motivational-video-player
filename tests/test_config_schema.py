import json
import os
import pytest

try:
    from jsonschema import validate, ValidationError
except ImportError:
    pytest.skip(
        "jsonschema not installed, skipping config schema tests",
        allow_module_level=True,
    )

# Load schema
schema_path = os.path.join(
    os.path.dirname(__file__), "..", "docs", "config-schema.json"
)
with open(schema_path) as f:
    SCHEMA = json.load(f)


def test_valid_minimal_config():
    config = {"name": "TestProfile", "video_dirs": ["/tmp"]}
    # Should not raise
    validate(instance=config, schema=SCHEMA)


def test_invalid_missing_required():
    config = {"video_dirs": []}
    with pytest.raises(ValidationError):
        validate(instance=config, schema=SCHEMA)


def test_invalid_additional_property():
    config = {"name": "Test", "video_dirs": [], "foo": 1}
    with pytest.raises(ValidationError):
        validate(instance=config, schema=SCHEMA)


def test_valid_complete_config():
    """Test a complete valid configuration with all optional fields."""
    config = {
        "name": "Complete Test Profile",
        "video_dirs": ["/home/user/videos", "/media/external"],
        "playlist_mode": "random",
        "effects": ["cyberpunk-glow", "vhs-clean"],
        "messages": {
            "message_file": "/path/to/messages.txt",
            "interval": 30,
            "duration": 5,
        },
        "fonts": {
            "primary": "JetBrains Mono",
            "fallback": ["DejaVu Sans Mono", "Liberation Mono"],
        },
        "hud": {"modules": ["clock", "cpu", "mem", "net", "uptime"], "position": "top"},
        "aspect": "16:9",
    }
    # Should not raise
    validate(instance=config, schema=SCHEMA)


def test_enum_validation():
    """Test that enum fields are properly validated."""
    base_config = {"name": "Test", "video_dirs": ["/tmp"]}

    # Valid enum values should pass
    valid_configs = [
        {**base_config, "playlist_mode": "random"},
        {**base_config, "playlist_mode": "ordered"},
        {**base_config, "aspect": "4:3"},
        {**base_config, "aspect": "16:9"},
        {**base_config, "aspect": "stretch"},
        {**base_config, "hud": {"modules": ["clock"], "position": "top"}},
        {**base_config, "hud": {"modules": ["clock"], "position": "bottom"}},
        {**base_config, "hud": {"modules": ["clock"], "position": "left"}},
        {**base_config, "hud": {"modules": ["clock"], "position": "right"}},
    ]

    for config in valid_configs:
        validate(instance=config, schema=SCHEMA)

    # Invalid enum values should fail
    invalid_configs = [
        {**base_config, "playlist_mode": "invalid"},
        {**base_config, "aspect": "invalid"},
        {**base_config, "hud": {"modules": ["clock"], "position": "invalid"}},
    ]

    for config in invalid_configs:
        with pytest.raises(ValidationError):
            validate(instance=config, schema=SCHEMA)


def test_nested_object_validation():
    """Test validation of nested objects."""
    base_config = {"name": "Test", "video_dirs": ["/tmp"]}

    # Valid nested objects
    valid_configs = [
        {**base_config, "messages": {"message_file": "/path/to/file.txt"}},
        {
            **base_config,
            "messages": {
                "message_file": "/path/to/file.txt",
                "interval": 60,
                "duration": 5,
            },
        },
        {**base_config, "fonts": {"primary": "Arial"}},
        {
            **base_config,
            "fonts": {"primary": "Arial", "fallback": ["Times", "Helvetica"]},
        },
        {**base_config, "hud": {"modules": ["clock", "cpu"]}},
        {**base_config, "hud": {"modules": ["clock"], "position": "top"}},
    ]

    for config in valid_configs:
        validate(instance=config, schema=SCHEMA)

    # Invalid nested objects (missing required fields)
    invalid_configs = [
        {**base_config, "messages": {"interval": 60}},  # missing message_file
        {**base_config, "fonts": {"fallback": ["Arial"]}},  # missing primary
        {**base_config, "hud": {"position": "top"}},  # missing modules
    ]

    for config in invalid_configs:
        with pytest.raises(ValidationError):
            validate(instance=config, schema=SCHEMA)
