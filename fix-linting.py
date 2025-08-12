#!/usr/bin/env python3
"""
Quick script to fix common linting issues in test files.
"""
import os
import re


def fix_file(filepath):
    """Fix common linting issues in a Python file."""
    with open(filepath, "r") as f:
        content = f.read()

    original_content = content

    # Remove unused imports (basic patterns)
    unused_patterns = [
        r"^import sys\n",
        r"^from unittest\.mock import patch, MagicMock\n",
        r"^from io import StringIO\n",
        r"^import time\n",
        r"^import re\n",
        r"^from pathlib import Path\n",
        r"^import json\n(?!.*json\.)",  # Remove json import if not used
    ]

    for pattern in unused_patterns:
        content = re.sub(pattern, "", content, flags=re.MULTILINE)

    # Fix long lines by breaking them
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        if len(line) > 88 and "assert" in line:
            # Break long assert lines
            if ', f"' in line:
                parts = line.split(', f"')
                if len(parts) == 2:
                    fixed_lines.append(parts[0] + ",")
                    fixed_lines.append('    f"' + parts[1])
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    content = "\n".join(fixed_lines)

    # Remove unused variables
    content = re.sub(r"^\s*config_dir = .*\n", "", content, flags=re.MULTILINE)

    # Fix bare except
    content = re.sub(r"except:", "except Exception:", content)

    if content != original_content:
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    return False


def main():
    """Fix linting issues in test files."""
    test_files = [
        "tests/test_argument_parsing.py",
        "tests/test_configuration_loading.py",
        "tests/test_filter_integration.py",
        "tests/test_hud_integration.py",
        "tests/test_installation_integration.py",
        "tests/test_message_integration.py",
        "tests/test_mpv_integration.py",
        "tests/test_profile_validation.py",
    ]

    fixed_count = 0
    for filepath in test_files:
        if os.path.exists(filepath):
            if fix_file(filepath):
                fixed_count += 1

    print(f"Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
