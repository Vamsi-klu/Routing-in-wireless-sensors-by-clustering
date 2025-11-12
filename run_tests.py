#!/usr/bin/env python3
"""
Test runner with coverage reporting for WSN Routing project

Runs all tests and generates coverage report.
Verifies 95%+ coverage across all modules.
"""

import sys
import subprocess
import os


def run_tests_with_coverage():
    """Run all tests with coverage reporting"""

    print("="*70)
    print("RUNNING WSN ROUTING TESTS WITH COVERAGE")
    print("="*70)

    # Run pytest with coverage
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-fail-under=95",
        "--tb=short"
    ]

    try:
        result = subprocess.run(cmd, check=True)

        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED WITH 95%+ COVERAGE")
        print("="*70)
        print("\nHTML coverage report generated in: htmlcov/index.html")

        return 0

    except subprocess.CalledProcessError as e:
        print("\n" + "="*70)
        print("❌ TESTS FAILED OR COVERAGE BELOW 95%")
        print("="*70)
        print(f"\nError code: {e.returncode}")
        print("\nCheck the output above for details.")
        print("HTML coverage report: htmlcov/index.html")

        return e.returncode

    except FileNotFoundError:
        print("\n❌ pytest not found. Install requirements:")
        print("   pip install -r requirements.txt")
        return 1


def run_specific_module(module_name):
    """Run tests for a specific module"""

    test_file = f"tests/test_{module_name}.py"

    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return 1

    cmd = [
        "pytest",
        test_file,
        "-v",
        f"--cov=src/{module_name}.py",
        "--cov-report=term-missing"
    ]

    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific module tests
        module = sys.argv[1]
        sys.exit(run_specific_module(module))
    else:
        # Run all tests
        sys.exit(run_tests_with_coverage())
