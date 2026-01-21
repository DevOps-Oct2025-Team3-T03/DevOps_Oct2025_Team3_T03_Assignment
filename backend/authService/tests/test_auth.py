"""Tests for authService module."""

from authService.app import app

class TestAuthService:

    def test_login_valid_credentials(self, client):
        res = client.post("/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
        assert "user_id" in data

    def test_login_invalid_credentials(self, client):
        res = client.post("/login", json={
            "username": "invalid_user",
            "password": "wrong_password"
        })
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_login_missing_fields(self, client):
        res = client.post("/login", json={
            "username": "admin",
        })
        assert res.status_code == 400
        assert "error" in res.get_json()

    def test_logout_without_login(self, client):
        res = client.get("/logout")
        assert res.status_code == 200
        assert res.get_json()["status"] == "logged out"