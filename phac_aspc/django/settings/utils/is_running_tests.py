"""This file contains a utility for detecting when the django is running inside
of a test framework environment
"""
import sys


def is_running_tests():
    """Detect if the app process was launched by a test-runner command"""
    return "test" in sys.argv or any("pytest" in arg for arg in sys.argv)
