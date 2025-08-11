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
