# conftest.py

"""
conftest.py is used to define shared pytest fixtures 
such as the Flask test client and environment setup, 
allowing consistent test configuration across all test cases without duplication.
"""

import sys, os
import pytest
import uuid
from fileService.app import app
from fileService.file_service_routes import fs

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

@pytest.fixture(scope="session", autouse=True)
def ensure_test_file():
    test_file_path = os.path.join(os.path.dirname(__file__), "test_file.txt")
    if not os.path.exists(test_file_path):
        with open(test_file_path, "w") as f:
            f.write("test file\n")
    yield
    # Optionally, cleanup after tests (uncomment if you want to remove after tests)
    # if os.path.exists(test_file_path):
    #     os.remove(test_file_path)

def _cleanup_test_files():
    # Remove all files owned by test users
    for owner_id in ["user1", "user2", "u_user1", "u_user2", "u_user_1"]:
        files = list(fs.find({"owner_id": owner_id}))
        for f in files:
            fs.delete(f._id)

@pytest.fixture(autouse=True)
def cleanup_files():
    yield
    _cleanup_test_files()

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def user1(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "u_user1"
        sess["username"] = "user1"
        sess["role"] = "user"
    return client

@pytest.fixture
def user2(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "u_user2"
        sess["username"] = "user2"
        sess["role"] = "user"
    return client

@pytest.fixture
def user_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "u_user_1"
        sess["username"] = "user"
        sess["role"] = "user"
    return client

@pytest.fixture
def admin_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "u_admin_1"
        sess["username"] = "admin"
        sess["role"] = "admin"
    return client