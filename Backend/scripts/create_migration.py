#!/usr/bin/env python3
"""
Helper script to create Alembic migrations.

Usage:
    python scripts/create_migration.py "Initial schema"
    python scripts/create_migration.py "Add user table"
"""

import os
import sys
import subprocess
from pathlib import Path

# Change to backend directory
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)

if len(sys.argv) < 2:
    print("Usage: python scripts/create_migration.py 'Migration message'")
    sys.exit(1)

message = sys.argv[1]

# Run alembic revision --autogenerate
result = subprocess.run(
    ["alembic", "revision", "--autogenerate", "-m", message],
    capture_output=True,
    text=True,
)

print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)

sys.exit(result.returncode)

