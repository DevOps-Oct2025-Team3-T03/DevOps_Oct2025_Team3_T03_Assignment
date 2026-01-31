"""Tests for authService module."""

from authService.app import app
from unittest.mock import patch, MagicMock
import uuid

class TestAuthService:

    # login Unit Tests
    def test_login_success_unit(self, client):
        fake_user = {
            "user_id": "u1",
            "role": "user",
            "password": b"fakehashed"
        }

        with patch("authService.auth_service_routes.users_col.find_one", return_value=fake_user), \
             patch("authService.auth_service_routes.bcrypt.checkpw", return_value=True):

            res = client.post("/login", json={"username": "user1", "password": "UserPass123!"})
            assert res.status_code == 200
            data = res.get_json()
            assert data["username"] == "user1"
            assert data["role"] == "user"
            assert data["user_id"] == "u1"

    def test_login_invalid_password_unit(self, client):
        fake_user = {
            "user_id": "u1",
            "role": "user",
            "password": b"fakehashed"
        }

        with patch("authService.auth_service_routes.users_col.find_one", return_value=fake_user), \
            patch("authService.auth_service_routes.bcrypt.checkpw", return_value=False):

            res = client.post("/login", json={"username": "user1", "password": "WrongPass"})
            assert res.status_code == 401
            assert "error" in res.get_json()

    def test_login_invalid_username_unit(self, client):
        with patch("authService.auth_service_routes.users_col.find_one", return_value=None):
            res = client.post("/login", json={"username": "invalidUser", "password": "UserPass123!"})
            assert res.status_code == 401
            assert "error" in res.get_json()

    def test_login_missing_password_unit(self, client):
        with patch("authService.auth_service_routes.users_col.find_one") as mock_find:
            res = client.post("/login", json={"username": "user1"})
            assert res.status_code == 401
            assert "error" in res.get_json()
            mock_find.assert_not_called()

    def test_login_missing_username_unit(self, client):
        with patch("authService.auth_service_routes.users_col.find_one") as mock_find:
            res = client.post("/login", json={"password": "UserPass123!"})
            assert res.status_code == 401
            assert "error" in res.get_json()
            mock_find.assert_not_called()

    # Admin Unit Tests

    def test_list_users_unauthorized_unit(self, client):

        res = client.get("/admin")
        assert res.status_code == 403
        data = res.get_json()
        assert "error" in data

    def test_list_users_as_non_admin_unit(self, client):

        fake_users = [
            {"user_id": "u1", "role": "user"},
            {"user_id": "admin1", "role": "admin"}
        ]
        
        with client.session_transaction() as sess:
            sess["role"] = "user"

        with patch("authService.auth_service_routes.users_col.find", return_value=fake_users):
            res = client.get("/admin")
            assert res.status_code == 403
            data = res.get_json()
            assert "error" in data

    def test_list_users_as_admin_unit(self, client):

        fake_users = [
            {"user_id": "u1", "username": "user1", "role": "user"},
            {"user_id": "admin1", "username": "admin", "role": "admin"}
        ]

        with client.session_transaction() as sess:
            sess["role"] = "admin"

        with patch("authService.auth_service_routes.users_col.find", return_value=fake_users):
            res = client.get("/admin")
            assert res.status_code == 200
            data = res.get_json()
            assert isinstance(data, list)
            assert len(data) == 2

    def test_list_users_no_users_unit(self, client):
        with client.session_transaction() as sess:
            sess["role"] = "admin"

        with patch("authService.auth_service_routes.users_col.find", return_value=[]):
            res = client.get("/admin")
            assert res.status_code == 200
            data = res.get_json()
            assert isinstance(data, list)
            assert len(data) == 0

    # Admin Create User Unit Tests
    def test_admin_create_user_success_unit(self, client):
        with client.session_transaction() as sess:
            sess["role"] = "admin"

        fake_existing_user = {
            "user_id": "u1",
            "role": "user",
            "password": b"existinghashed"
        }

        with patch("authService.auth_service_routes.users_col.find_one", side_effect=[fake_existing_user, None]), \
             patch("authService.auth_service_routes.bcrypt.hashpw", return_value=b"newhashed"), \
             patch("authService.auth_service_routes.users_col.insert_one") as mock_insert:
            res = client.post("/admin/create_user", json={
                "username": "newuser",
                "password": "NewPass123!",
                "role": "user"
            })
            assert res.status_code == 200
            data = res.get_json()
            assert data["status"] == "User created"
            mock_insert.assert_called_once()

    def test_admin_create_user_existing_username_unit(self, client):
        with client.session_transaction() as sess:
            sess["role"] = "admin"
        
        fake_existing_user = {
            "user_id": "u1",
            "role": "user",
            "password": b"existinghashed"
        }

        with patch("authService.auth_service_routes.users_col.find_one", return_value=fake_existing_user):
            res = client.post("/admin/create_user", json={
                "username": "user1",
                "password": "AltPass123!",
                "role": "user"
            })
            assert res.status_code == 400
            data = res.get_json()
            assert "error" in data

    def test_admin_create_user_as_user_unit(self, client):
        with client.session_transaction() as sess:
            sess["role"] = "user"
        
        fake_existing_user = {
            "user_id": "u1",
            "role": "user",
            "password": b"fakehashed"
        }

        with patch("authService.auth_service_routes.users_col.find_one", return_value=fake_existing_user):
            res = client.post("/admin/create_user", json={
                "username": "anotheruser",
                "password": "AnotherPass123!",
                "role": "user"
            })
            assert res.status_code == 403
            data = res.get_json()
            assert "error" in data


    def test_admin_create_user_unauthorized_unit(self, client):
        fake_existing_user = {
            "user_id": "u1",
            "role": "user",
            "password": b"fakehashed"
        }

        with patch("authService.auth_service_routes.users_col.find_one", return_value=fake_existing_user):
            res = client.post("/admin/create_user", json={
                "username": "anotheruser",
                "password": "AnotherPass123!",
                "role": "user"
            })
            assert res.status_code == 403
            data = res.get_json()
            assert "error" in data

    # Admin Delete User Unit Tests
    def test_admin_delete_user_success_unit(self, client):
        with client.session_transaction() as sess:
            sess["role"] = "admin"

        fake_user_to_delete = {
            "user_id": "u2",
            "role": "user",
            "password": b"deletehashed"
        }

        with patch("authService.auth_service_routes.users_col.find_one", return_value=fake_user_to_delete), \
             patch("authService.auth_service_routes.users_col.delete_one") as mock_delete:
            res = client.post("/admin/delete_user/existinguser")
            assert res.status_code == 200
            data = res.get_json()
            assert "message" in data
            mock_delete.assert_called_once()

    def test_admin_delete_user_not_found_unit(self, client):
        with client.session_transaction() as sess:
            sess["role"] = "admin"

        with patch("authService.auth_service_routes.users_col.find_one", return_value=None):
            res = client.post("/admin/delete_user/nonexistentuser")
            assert res.status_code == 404
            data = res.get_json()
            assert "error" in data

    def test_admin_delete_user_as_user_unit(self, client):
        with client.session_transaction() as sess:
            sess["role"] = "user"

        fake_user_to_delete = {
            "user_id": "u2",
            "role": "user",
            "password": b"deletehashed"
        }

        with patch("authService.auth_service_routes.users_col.find_one", return_value=fake_user_to_delete):
            res = client.post("/admin/delete_user/existinguser2")
            assert res.status_code == 403
            data = res.get_json()
            assert "error" in data

    def test_admin_delete_user_unauthorized_unit(self, client):
        fake_user_to_delete = {
            "user_id": "u2",
            "role": "user",
            "password": b"deletehashed"
        }

        with patch("authService.auth_service_routes.users_col.find_one", return_value=fake_user_to_delete):
            res = client.post("/admin/delete_user/existinguser2")
            assert res.status_code == 403
            data = res.get_json()
            assert "error" in data

    # Logout Unit Test
    def test_logout_as_user_unit(self, client):
        with client.session_transaction() as sess:
            sess["role"] = "user"
        res = client.get("/logout")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "logged out"

    def test_logout_as_admin_unit(self, client):
        with client.session_transaction() as sess:
            sess["role"] = "admin"
        res = client.get("/logout")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "logged out"

    def test_logout_unauthorized_unit(self, client):
        res = client.get("/logout")
        assert res.status_code == 403
        data = res.get_json()
        assert "error" in data
    
    # Integration Tests

    # login Integration Tests
    def test_login_valid_credentials(self, client, temp_user):

        #  Login to admin first to ensure user exists
        res = client.post("/login", json={
            "username": temp_user["username"],
            "password": temp_user["password"]
        })
        assert res.status_code == 200 # verify successful login
        data = res.get_json()
        assert data["username"] == temp_user["username"] # verify username in response
        assert data["role"] == "user" # verify role in response
        assert "user_id" in data # verify user_id in response

    def test_login_invalid_username(self, client):
        res = client.post("/login", json={
            "username": "invalidUser",
            "password": "UserPass123!"
        })
        assert res.status_code == 401 # verify unauthorized access
        assert "error" in res.get_json() # verify response JSON contains error message

    def test_login_invalid_password(self, client):
        res = client.post("/login", json={
            "username": "user1",
            "password": "WrongPass"
        })
        assert res.status_code == 401 # verify unauthorized access
        assert "error" in res.get_json() # verify response JSON contains error message

    def test_login_missing_username(self, client):
        res = client.post("/login", json={
            "username": "user1",
        })
        assert res.status_code == 401 # verify unauthorized access
        assert "error" in res.get_json() # verify response JSON contains error message

    def test_login_missing_password(self, client):
        res = client.post("/login", json={
            "password": "UserPass123!",
        })
        assert res.status_code == 401 # verify unauthorized access
        assert "error" in res.get_json() # verify response JSON contains error message
    
    # Logout Integration Tests

    def test_logout_after_login(self, client, temp_user):
        # First, login
        res = client.post("/login", json={
            "username": temp_user["username"],
            "password": temp_user["password"]
        })

        assert res.status_code == 200 # verify successful login

        res = client.get("/logout")
        assert res.status_code == 200
        assert res.get_json()["status"] == "logged out"

    def test_logout_without_login(self, client):
        res = client.get("/logout")
        assert res.status_code == 401 # verify unauthorized access
        assert "error" in res.get_json() # verify response JSON contains error message

    # Admin List Users Integration Tests

    def test_admin_list_users_success(self, admin_client, temp_user):
        # Access admin route
        res = admin_client.get("/admin")
        assert res.status_code == 200 # verify successful access
        data = res.get_json()

        assert isinstance(data, list) # verify response JSON is a list
        assert any(u["username"] == temp_user["username"] for u in data) # verify temp user is listed

    def test_admin_list_users_without_login(self, client):
        res = client.get("/admin")
        assert res.status_code == 403 # verify unauthorized access
        data = res.get_json()
        assert "error" in data # verify response JSON contains error message

    def test_admin_list_users_with_user_role(self, client, temp_user):
        # Login as regular user
        res = client.post("/login", json={
            "username": temp_user["username"],
            "password": temp_user["password"]
        })
        assert res.status_code == 200 # verify successful login

        # Attempt to access admin route
        res = client.get("/admin")
        assert res.status_code == 403 # verify forbidden access
        data = res.get_json()
        assert "error" in data # verify response JSON contains error message
        
    # Admin Create User Integration Tests
    def test_admin_create_user_existing_username(self, admin_client, temp_user):
        # Attempt to create user with existing username
        res = admin_client.post("/admin/create_user", json={
            "username": temp_user["username"],
            "password": temp_user["password"],
            "role": "user"
        })
        assert res.status_code == 400 # verify bad request
        data = res.get_json()
        assert "error" in data # verify response JSON contains error message

    def test_admin_create_user_without_login(self, client):
        res = client.post("/admin/create_user", json={
            "username": "newuser",
            "password": "NewUserPass123!",
            "role": "user"
        })
        assert res.status_code == 403 # verify forbidden access
        data = res.get_json()
        assert "error" in data # verify response JSON contains error message
    
    def test_user_create_user_with_user_role(self, client, temp_user):
        # Login as regular user
        res = client.post("/login", json={
            "username": temp_user["username"],
            "password": temp_user["password"]
        })
        assert res.status_code == 200 # verify successful login

        # Attempt to create new user
        res = client.post("/admin/create_user", json={
            "username": "anotheruser",
            "password": "AnotherPass123!",
            "role": "user"
        })
        assert res.status_code == 403 # verify forbidden access
        data = res.get_json()
        assert "error" in data # verify response JSON contains error message

    # Admin Delete User Integration Tests
    def test_admin_delete_user_nonexistent(self, admin_client):
        # Attempt to delete non-existent user
        res = admin_client.post("/admin/delete_user/nonexistentuser")
        assert res.status_code == 404 # verify not found
        data = res.get_json()
        assert "error" in data # verify response JSON contains error message

    def test_admin_delete_user_without_login(self, client, temp_user):
        # Attempt to delete a user without login
        res = client.post(f"/admin/delete_user/{temp_user['user_id']}")
        assert res.status_code == 403 # verify forbidden access
        data = res.get_json()
        assert "error" in data # verify response JSON contains error message

    def test_admin_delete_user_with_user_role(self, client, temp_user):
        # Login as regular user
        res = client.post("/login", json={
            "username": temp_user["username"],
            "password": temp_user["password"]
        })
        assert res.status_code == 200 # verify successful login

        # Attempt to delete a user
        res = client.post(f"/admin/delete_user/{temp_user['user_id']}")
        assert res.status_code == 403 # verify forbidden access
        data = res.get_json()
        assert "error" in data # verify response JSON contains error message

    def test_admin_delete_user_success(self, admin_client):
        username = f"del_{uuid.uuid4().hex[:8]}"

        # create
        res = admin_client.post("/admin/create_user", json={
            "username": username,
            "password": "UserPass123!",
            "role": "user"
        })
        assert res.status_code == 200
        assert res.get_json()["status"] == "created"

        # list -> id
        res = admin_client.get("/admin")
        users = res.get_json()
        user_id = next(u["user_id"] for u in users if u["username"] == username)

        # delete
        res = admin_client.post(f"/admin/delete_user/{user_id}")
        assert res.status_code == 200
        assert res.get_json()["status"] == "User deleted"