#!/usr/bin/env python3
"""
Helper script to run Alembic migrations.

Usage:
    python scripts/run_migrations.py          # Run all pending migrations
    python scripts/run_migrations.py upgrade  # Upgrade to head
    python scripts/run_migrations.py downgrade -1  # Downgrade one revision
"""

import os
import sys
import subprocess
from pathlib import Path

# Change to backend directory
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)

# Default to 'upgrade head' if no arguments
args = sys.argv[1:] if len(sys.argv) > 1 else ["upgrade", "head"]

# Run alembic
result = subprocess.run(
    ["alembic"] + args,
    capture_output=False,
)

sys.exit(result.returncode)


