#!/usr/bin/env python3
"""
Test runner for TradePal AI backend.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run the test suite using pytest."""
    print("🧪 TradePal AI - Backend Test Runner")
    print("=" * 50)
    
    # Check if test directory exists
    test_dir = Path(__file__).parent / "tests"
    if not test_dir.exists():
        print("❌ Test directory 'tests/' not found!")
        return False
    
    # Run tests using pytest
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  Warnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)





