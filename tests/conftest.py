"""
Shared pytest configuration and fixtures for all tests

This file eliminates code duplication by providing common setup
for all test modules.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
