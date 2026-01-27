# conftest.py

"""
conftest.py is used to define shared pytest fixtures 
such as the Flask test client and environment setup, 
allowing consistent test configuration across all test cases without duplication.
"""

import sys, os
import pytest
import uuid
from authService.app import app

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def admin_client(client):
    res = client.post("/login", json={
        "username": "admin", 
        "password": "AdminPass123!"
    })
    assert res.status_code == 200
    yield client
    client.get("/logout")  # logout after test

@pytest.fixture
def temp_user(admin_client):
    username = f"test_{uuid.uuid4().hex[:8]}"
    password = "UserPass123!"

    res = admin_client.post("/admin/create_user", json={
        "username": username,
        "password": password,
        "role": "user"
    })

    assert res.status_code == 200
    assert res.get_json()["status"] == "created"

    # get user_id
    res = admin_client.get("/admin")
    assert res.status_code == 200
    users = res.get_json()
    user_id = next(u["user_id"] for u in users if u["username"] == username)

    yield {"username": username, "password": password, "user_id": user_id}

    # cleanup (always runs)
    admin_client.post(f"/admin/delete_user/{user_id}")