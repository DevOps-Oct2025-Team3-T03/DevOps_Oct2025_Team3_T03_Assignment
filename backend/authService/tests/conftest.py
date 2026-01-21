# conftest.py

"""
conftest.py is used to define shared pytest fixtures 
such as the Flask test client and environment setup, 
allowing consistent test configuration across all test cases without duplication.
"""

import sys, os
import pytest
from authService.app import app

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client