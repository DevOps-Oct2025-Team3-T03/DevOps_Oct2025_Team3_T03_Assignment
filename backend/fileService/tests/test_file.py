"""Tests for fileService module."""

from fileService.app import app

class TestFileService:

    def test_upload_file(self, client):
        with open("tests/test_file.txt", "rb") as f:
            res = client.post("/dashboard/upload", files={"files": f})
        assert res.status_code == 200
        assert "files" in res.get_json()

    def test_upload_without_login(self, client):
        res = client.post("/dashboard/upload")
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_upload_no_file(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"
            sess["username"] = "user1"

        res = client.post("/dashboard/upload")
        assert res.status_code == 400
        assert "error" in res.get_json()

    def test_list_files(self, client):
        res = client.get("/dashboard")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_list_files_unauthorized(self, client):
        res = client.get("/dashboard")
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_list_files_logged_in(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"

        res = client.get("/dashboard")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_download_file(self, client):
        # First, upload a file
        with open("tests/test_file.txt", "rb") as f:
            client.post("/dashboard/upload", files={"files": f})

        # Now, get the file ID from the upload response
        file_id = res.get_json()["files"][0]["file_id"]

        res = client.get(f"/dashboard/download/{file_id}")
        assert res.status_code == 200
        assert res.headers["Content-Disposition"] == f"attachment; filename=test_file.txt"

    def test_download_unauthorized(self, client):
        res = client.get("/dashboard/download/123")
        assert res.status_code == 401
        assert "error" in res.get_json()

    def test_download_other_users_file(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "userA"

        res = client.get("/dashboard/download/507f1f77bcf86cd799439011")
        assert res.status_code == 404
        assert "error" in res.get_json()

    def test_delete_file(self, client):
        # First, upload a file
        with open("tests/test_file.txt", "rb") as f:
            res = client.post("/dashboard/upload", files={"files": f})
        file_id = res.get_json()["files"][0]["file_id"]

        res = client.post(f"/dashboard/delete/{file_id}")
        assert res.status_code == 200
        assert res.get_json()["status"] == "File deleted"

    def test_delete_unauthorized(self, client):
        res = client.post("/dashboard/delete/123")
        assert res.status_code == 401
        assert "error" in res.get_json()
    
    def test_delete_other_users_file(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "userA"

        res = client.post("/dashboard/delete/507f1f77bcf86cd799439011")
        assert res.status_code == 404
        assert "error" in res.get_json()

    def test_delete_nonexistent_file(self, client):
        with client.session_transaction() as sess:
            sess["user_id"] = "user1"

        res = client.post("/dashboard/delete/507f1f77bcf86cd799439099")
        assert res.status_code == 404
        assert "error" in res.get_json()
