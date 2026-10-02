#!/usr/bin/env python3
"""
Test Runner for Low-Level Design Implementations
Discovers and executes all unit test suites in tests/
"""
import unittest
import sys
import os

def run_all_tests():
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n" + "=" * 60)
        print("🎉 SUCCESS: All Low-Level Design test suites passed!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ FAILURE: One or more test suites failed.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
