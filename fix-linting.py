#!/usr/bin/env python3
"""
Quick script to fix common linting issues in test files.
"""
import os
import re

def fix_file(filepath):
    """Fix common linting issues in a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Remove unused imports
    unused_imports = [
        'from unittest.mock import patch, mock_open',
        'from unittest.mock import patch',
        'from unittest.mock import MagicMock',
        'from io import StringIO',
        'import sys',
        'import time',
        'import re',
        'from pathlib import Path',
        'import json',
    ]
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Skip unused imports that aren't actually used
        skip_line = False
        for unused in unused_imports:
            if line.strip() == unused:
                # Check if the import is actually used in the file
                if unused == 'import json' and 'json.' in content:
                    continue
                if unused == 'import sys' and 'sys.' in content:
                    continue
                if unused == 'import time' and 'time.' in content:
                    continue
                if unused == 'import re' and 're.' in content:
                    continue
                if 'ValidationError' in unused and 'ValidationError' in content:
                    continue
                skip_line = True
                break
        
        if not skip_line:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Fix long lines by breaking them
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if len(line) > 88 and 'assert' in line and 'f"' in line:
            # Break long assert lines
            if '), f"' in line:
                parts = line.split('), f"', 1)
                if len(parts) == 2:
                    new_lines.append(parts[0] + '), (')
                    new_lines.append('                            f"' + parts[1])
                    continue
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Only write if content changed
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed {filepath}")

# Fix all test files
test_dir = 'tests'
for filename in os.listdir(test_dir):
    if filename.endswith('.py') and filename.startswith('test_'):
        filepath = os.path.join(test_dir, filename)
        fix_file(filepath)