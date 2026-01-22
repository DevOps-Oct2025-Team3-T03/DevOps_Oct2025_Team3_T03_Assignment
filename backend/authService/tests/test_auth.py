"""Tests for authService module."""

from authService.app import app

class TestAuthService:

    def test_login_valid_credentials(self, client):
        res = client.post("/login", json={
            "username": "user1",
            "password": "UserPass123!"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["username"] == "user1"
        assert data["role"] == "user"
        assert "user_id" in data

    def test_login_invalid_username(self, client):
        res = client.post("/login", json={
            "username": "invalidUser",
            "password": "UserPass123!"
        })
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_login_invalid_password(self, client):
        res = client.post("/login", json={
            "username": "user1",
            "password": "WrongPass"
        })
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_login_missing_username(self, client):
        res = client.post("/login", json={
            "username": "user1",
        })
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_login_missing_password(self, client):
        res = client.post("/login", json={
            "password": "UserPass123!",
        })
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_logout_with_login(self, client):
        #simulate logged-in user
        with client.session_transaction() as sess:
            sess["username"] = "user1"
            sess["role"] = "user"

        res = client.get("/logout")
        assert res.status_code == 200
        assert "error" in res.get_json()

        # session should be cleared
        with client.session_transaction() as sess:
            assert "username" not in sess
            assert "role" not in sess

    def test_logout_without_login(self, client):
        res = client.get("/logout")
        assert res.status_code == 200
        assert "error" in res.get_json()

    def test_admin_with_admin_role(self, client):
        # Login as admin
        res = client.post("/login", json={
            "username": "admin",
            "password": "AdminPass123!"
        })
        assert res.status_code == 200
        assert "error" in res.get_json()

        # Access admin route
        res = client.get("/admin")
        assert res.status_code == 200

    def test_admin_with_user_role(self, client):
        # Login as regular user
        res = client.post("/login", json={
            "username": "user1",
            "password": "UserPass123!"
        })
        assert res.status_code == 200

        # Attempt to access admin route
        res = client.get("/admin")
        assert res.status_code == 403
        assert "error" in res.get_json()

    def test_admin_without_login(self, client):
        res = client.get("/admin")
        assert res.status_code == 403
        assert "error" in res.get_json()