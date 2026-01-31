"""Tests for fileService module."""

import io, os
from fileService.app import app
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage

class TestFileService:
    # Helper
    
    def _login_session(self, client, user_id="user1", username="user1", role="user"):
        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = username
            sess["role"] = role

    def _login_session_as_admin(self, client):
        self._login_session(client, user_id="admin", username="admin", role="admin")

    # Unit tests for file upload, listing, download, and deletion

    # User Dashboard Unit Test
    def test_user_dashboard_unauthorized_unit(self, client):
        res = client.get("/dashboard")
        assert res.status_code == 401
        data = res.get_json()
        assert "error" in data

    def test_user_dashboard_as_admin_unit(self, client):
        self._login_session_as_admin(client)

        res = client.get("/dashboard")
        assert res.status_code == 403
        data = res.get_json()
        assert "error" in data

    # User Dashboard List Unit Test
    def test_user_dashboard_returns_empty_list(self, client):
        self._login_session(client)
        # Mock the file listing
        with patch("fileService.file_service_routes.fs.find", return_value=[]):
            res = client.get("/dashboard")
            assert res.status_code == 200
            data = res.get_json()
            assert isinstance(data, list)
            assert len(data) == 0

    def test_list_files_returns_only_owner_files(self, client):
        self._login_session(client, user_id="u1")

        # Fake GridOut-like objects
        f1 = MagicMock()
        f1._id = "id1"
        f1.filename = "a.txt"
        f1.upload_date = "2026-01-01"

        f2 = MagicMock()
        f2._id = "id2"
        f2.filename = "b.txt"
        f2.upload_date = "2026-01-02"

        with patch("fileService.file_service_routes.fs.find", return_value=[f1, f2]) as mock_find:
            res = client.get("/dashboard")
            assert res.status_code == 200
            data = res.get_json()
            assert isinstance(data, list)
            assert len(data) == 2
            # verify correct fields exist
            assert "file_id" in data[0]
            assert "filename" in data[0]
            assert "upload_date" in data[0]
            # verify backend queried by owner_id
            mock_find.assert_called_once_with({"owner_id": "u1"})

    # User Dashboard Upload Unit Tests

    def test_upload_unauthorized(self, client):
        res = client.post("/dashboard/upload")
        assert res.status_code == 401
        data = res.get_json()
        assert "error" in res.get_json()

    def test_upload_as_admin(self, client):
        self._login_session_as_admin(client)
        
        res = client.post("/dashboard/upload")
        assert res.status_code == 400
        data = res.get_json()
        assert "error" in res.get_json()
        
    def test_upload_no_file_provided(self, client):
        self._login_session(client)
        res = client.post("/dashboard/upload", 
            data={}, 
            content_type="multipart/form-data"
        )
        assert res.status_code == 400
        data = res.get_json()
        assert "error" in res.get_json()

    def test_upload_single_file_success(self, client):
        self._login_session(client, user_id="u1", username="user1")

        fake_file_id = "507f1f77bcf86cd799439011"

        with patch("fileService.file_service_routes.fs.put", return_value=fake_file_id) as mock_put:
            data = {
                "files": (io.BytesIO(b"hello"), "hello.txt")
            }
            res = client.post("/dashboard/upload", data=data, content_type="multipart/form-data")
            assert res.status_code == 200

            payload = res.get_json()
            assert "files" in payload
            assert len(payload["files"]) == 1
            assert payload["files"][0]["file_id"] == str(fake_file_id)
            assert payload["files"][0]["filename"] == "hello.txt"

            # Validate fs.put called with correct metadata
            # stream is a file-like; we mainly validate kwargs
            _, kwargs = mock_put.call_args
            assert kwargs["filename"] == "hello.txt"
            assert kwargs["owner_id"] == "u1"
            assert kwargs["uploaded_by"] == "user1"

    # Download File Unit Tests
    def test_download_unauthorized(self, client):
        res = client.get("/dashboard/download/507f1f77bcf86cd799439011")
        assert res.status_code == 401
        assert "error" in res.get_json()
    
    def test_download_file_not_found_or_access_denied(self, client):
        self._login_session(client, user_id="u1")

        with patch("fileService.file_service_routes.fs.find_one", return_value=None):
            res = client.get("/dashboard/download/507f1f77bcf86cd799439011")
            assert res.status_code == 404
            assert "error" in res.get_json()
    
    def test_download_success_returns_attachment(self, client):
        self._login_session(client, user_id="u1")

        # Fake GridOut-like file object
        fake_gridout = MagicMock()
        fake_gridout.filename = "secret.txt"
        fake_gridout.read.return_value = b"topsecret"

        with patch("fileService.file_service_routes.fs.find_one", return_value=fake_gridout):
            res = client.get("/dashboard/download/507f1f77bcf86cd799439011")
            assert res.status_code == 200
            assert res.data == b"topsecret"
            # check filename is in Content-Disposition
            cd = res.headers.get("Content-Disposition", "")
            assert "attachment" in cd
            assert "secret.txt" in cd
    
    # Delete File Unit Tests
    def test_delete_unauthorized(self, client):
        res = client.post("/dashboard/delete/507f1f77bcf86cd799439011")
        assert res.status_code == 401
        assert "error" in res.get_json()
    
    def test_delete_not_found_or_access_denied(self, client):
        self._login_session(client, user_id="u1")

        with patch("fileService.file_service_routes.fs.find_one", return_value=None):
            res = client.post("/dashboard/delete/507f1f77bcf86cd799439011")
            assert res.status_code == 404
            assert "error" in res.get_json()

    def test_delete_success(self, client):
        self._login_session(client, user_id="u1")

        fake_gridout = MagicMock()
        fake_gridout._id = "507f1f77bcf86cd799439011"

        with patch("fileService.file_service_routes.fs.find_one", return_value=fake_gridout), \
             patch("fileService.file_service_routes.fs.delete") as mock_delete:

            res = client.post("/dashboard/delete/507f1f77bcf86cd799439011")
            assert res.status_code == 200
            assert res.get_json()["status"] == "File deleted"
            mock_delete.assert_called_once()
    # Integration tests
    
    # User Dashboard Integration Tests
    def test_user_dashboard_as_unauthorized(self, client):
        res = client.get("/dashboard")
        assert res.status_code == 403
        data = res.get_json()
        assert "error" in data

    def test_user_dashboard_as_user(self, user_session):
        res = user_session.get("/dashboard")
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)

    def test_user_dashboard_as_admin(self, admin_session):
        res = admin_session.get("/dashboard")
        assert res.status_code == 403
        data = res.get_json()
        assert "error" in data

    
    # User Dashboard Upload Integration Tests
    def test_upload_file_logged_in(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"
            sess["username"] = "user1"
        with open(os.path.join(os.path.dirname(__file__), "test_file.txt"), "rb") as f:
            res = client.post(
                "/dashboard/upload",
                data={"files": (f, "test_file.txt")},
                content_type="multipart/form-data"
            )
        assert res.status_code == 200
        assert "files" in res.get_json()

    def test_upload_file_unauthorized(self, client):
        res = client.post("/dashboard/upload")
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_upload_file_no_file(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"
            sess["username"] = "user1"
        res = client.post("/dashboard/upload")
        assert res.status_code == 400
        assert "error" in res.get_json()

    # User Dashboard Download Integration Tests
    def test_download_file_logged_in(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"
            sess["username"] = "user1"
        with open(os.path.join(os.path.dirname(__file__), "test_file.txt"), "rb") as f:
            upload_res = client.post(
                "/dashboard/upload",
                data={"files": (f, "test_file.txt")},
                content_type="multipart/form-data"
            )
        file_id = upload_res.get_json()["files"][0]["file_id"]
        res = client.get(f"/dashboard/download/{file_id}")
        assert res.status_code == 200
        assert res.headers["Content-Disposition"] == f"attachment; filename=test_file.txt"

    def test_download_file_unauthorized(self, client):
        res = client.get("/dashboard/download/123")
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_download_file_other_user(self, client):
        # Upload as user1
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"
            sess["username"] = "user1"
        with open(os.path.join(os.path.dirname(__file__), "test_file.txt"), "rb") as f:
            upload_res = client.post(
                "/dashboard/upload",
                data={"files": (f, "test_file.txt")},
                content_type="multipart/form-data"
            )
        file_id = upload_res.get_json()["files"][0]["file_id"]
        # Try to download as user2
        with client.session_transaction() as sess:
            sess["user_id"] = "user2"
            sess["username"] = "user2"
        res = client.get(f"/dashboard/download/{file_id}")
        assert res.status_code == 404
        assert "error" in res.get_json()

    # User Dashboard Delete Integration Tests
    def test_delete_file_logged_in(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"
            sess["username"] = "user1"
        with open(os.path.join(os.path.dirname(__file__), "test_file.txt"), "rb") as f:
            upload_res = client.post(
                "/dashboard/upload",
                data={"files": (f, "test_file.txt")},
                content_type="multipart/form-data"
            )
        file_id = upload_res.get_json()["files"][0]["file_id"]
        res = client.post(f"/dashboard/delete/{file_id}")
        assert res.status_code == 200
        assert res.get_json()["status"] == "File deleted"

    def test_delete_file_unauthorized(self, client):
        res = client.post("/dashboard/delete/123")
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_delete_file_other_user(self, client):
        # Upload as user1
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"
            sess["username"] = "user1"
        with open(os.path.join(os.path.dirname(__file__), "test_file.txt"), "rb") as f:
            upload_res = client.post(
                "/dashboard/upload",
                data={"files": (f, "test_file.txt")},
                content_type="multipart/form-data"
            )
        file_id = upload_res.get_json()["files"][0]["file_id"]
        # Try to delete as user2
        with client.session_transaction() as sess:
            sess["user_id"] = "user2"
            sess["username"] = "user2"
        res = client.post(f"/dashboard/delete/{file_id}")
        assert res.status_code == 404
        assert "error" in res.get_json()

    def test_delete_file_nonexistent(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"
            sess["username"] = "user1"
        res = client.post("/dashboard/delete/507f1f77bcf86cd799439099")
        assert res.status_code == 404
        assert "error" in res.get_json()
