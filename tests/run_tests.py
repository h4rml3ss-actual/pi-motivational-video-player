#!/usr/bin/env python3
"""
Test runner script for VideoWall Python testing and validation.
"""
import subprocess
import sys
import os


def main():
    """Run all VideoWall tests."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(__file__))

    # Test files to run
    test_files = [
        "tests/test_configuration_loading.py",
        "tests/test_argument_parsing.py",
        "tests/test_profile_validation.py",
        "tests/test_installation_integration.py",
        "tests/test_mpv_integration.py",
        "tests/test_filter_integration.py",
        "tests/test_hud_integration.py",
        "tests/test_message_integration.py",
    ]

    print("Running VideoWall Python tests...")
    print("=" * 50)

    # Check if pytest is available
    try:
        subprocess.run(
            ["python", "-c", "import pytest"], check=True, capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: pytest not found. Please install pytest:")
        print("  pip install pytest jsonschema")
        return 1

    # Run the tests
    cmd = ["python", "-m", "pytest"] + test_files + ["-v"]

    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
