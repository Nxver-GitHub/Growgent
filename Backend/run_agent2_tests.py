#!/usr/bin/env python3
"""
Test runner for Agent 2 E2E tests.

This script runs the water efficiency and PSPS anticipation agent tests
against the PostgreSQL database.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run Agent 2 E2E tests."""
    backend_dir = Path(__file__).parent
    
    print("=" * 70)
    print("Agent 2 E2E Tests - Water Efficiency & PSPS Anticipation")
    print("=" * 70)
    print()
    
    # Test files to run
    test_files = [
        "tests/test_integration_agents.py::TestWaterEfficiencyAgentIntegration",
        "tests/test_integration_agents.py::TestPSPSAgentIntegration",
        "tests/test_e2e_agent2.py::TestWaterEfficiencyE2E",
        "tests/test_e2e_agent2.py::TestPSPSE2E",
    ]
    
    # Run each test file
    for test_file in test_files:
        print(f"\n{'=' * 70}")
        print(f"Running: {test_file}")
        print(f"{'=' * 70}\n")
        
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                test_file,
                "-v",
                "--tb=short",
                "--color=yes",
            ],
            cwd=backend_dir,
        )
        
        if result.returncode != 0:
            print(f"\n❌ Tests failed for {test_file}")
            return result.returncode
        else:
            print(f"\n✅ Tests passed for {test_file}")
    
    print("\n" + "=" * 70)
    print("✅ All Agent 2 E2E tests passed!")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())


