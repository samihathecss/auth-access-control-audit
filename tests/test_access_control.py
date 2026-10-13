import pytest
from app import create_app


@pytest.fixture()
def app():
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "local-test-only-secret",
    })


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username, password="Secret123!"):
    token_response = client.get("/login")
    token = token_response.json["csrf_token"]

    return client.post(
        "/login",
        json={"username": username, "password": password},
        headers={"X-CSRFToken": token},
    )

def test_unauthenticated_user_cannot_read_record(client):
    response = client.get("/records/A1")
    assert response.status_code == 302


def test_owner_can_read_own_record(client):
    login(client, "alice")
    response = client.get("/records/A1")

    assert response.status_code == 200
    assert response.json["id"] == "A1"


def test_user_cannot_read_another_users_record(client):
    login(client, "alice")
    response = client.get("/records/B1")

    assert response.status_code == 404


def test_user_sees_only_owned_records(client):
    login(client, "alice")
    response = client.get("/records")

    assert response.status_code == 200
    record_ids = {record["id"] for record in response.json["records"]}
    assert record_ids == {"A1", "A2"}


def test_unauthenticated_user_cannot_access_admin(client):
    response = client.get("/admin")
    assert response.status_code == 302


def test_regular_user_cannot_access_admin(client):
    login(client, "alice")
    response = client.get("/admin")

    assert response.status_code == 403


def test_admin_can_access_admin(client):
    login(client, "admin", "AdminPass456!")
    response = client.get("/admin")

    assert response.status_code == 200
    assert response.json["section"] == "admin"


def test_inconsistent_session_role_is_denied_and_cleared(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["role"] = "admin"

    response = client.get("/admin")

    assert response.status_code == 403
    assert response.json == {"error": "Forbidden"}

    with client.session_transaction() as sess:
        assert len(sess) == 0

def test_login_rejects_missing_csrf_token(client):
    response = client.post(
        "/login",
        json={
            "username": "alice",
            "password": "Secret123!",
        },
    )

    assert response.status_code == 400

def test_logout_rejects_missing_csrf_token(client):
    response = client.post("/logout")
    assert response.status_code == 400


def test_security_headers_present(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_login_rejects_invalid_credentials(client):
    token_response = client.get("/login")
    token = token_response.json["csrf_token"]

    response = client.post(
        "/login",
        json={"username": "alice", "password": "wrong"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 401
    assert response.json["error"] == "Invalid username or password"


def test_login_rejects_nonexistent_user(client):
    token_response = client.get("/login")
    token = token_response.json["csrf_token"]

    response = client.post(
        "/login",
        json={"username": "nonexistent", "password": "anything"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 401
    assert response.json["error"] == "Invalid username or password"


def test_logout_clears_session(client):
    login(client, "alice")

    token_response = client.get("/login")
    token = token_response.json["csrf_token"]

    response = client.post(
        "/logout",
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 200
    assert response.json["message"] == "Logout successful"

    response = client.get("/records/A1")
    assert response.status_code == 302


def test_csrf_token_returned_on_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "csrf_token" in response.json
    assert isinstance(response.json["csrf_token"], str)
    assert len(response.json["csrf_token"]) > 0


def test_create_record_success(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.post(
        "/records",
        json={"title": "New Note", "content": "New content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 201
    assert response.json["title"] == "New Note"
    assert response.json["content"] == "New content"
    assert "id" in response.json


def test_create_record_rejects_missing_csrf(client):
    login(client, "alice")

    response = client.post(
        "/records",
        json={"title": "New Note", "content": "New content"},
    )

    assert response.status_code == 400


def test_create_record_rejects_missing_title(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.post(
        "/records",
        json={"content": "New content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title is required"


def test_create_record_rejects_empty_title(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.post(
        "/records",
        json={"title": "   ", "content": "New content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title is required"


def test_create_record_unauthenticated_rejected(client):
    # Without CSRF token, CSRF protection rejects first (400)
    # With CSRF token but no auth, login_required would redirect (302)
    response = client.post("/records", json={"title": "New Note"})
    assert response.status_code == 400


def test_update_own_record_success(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.put(
        "/records/A1",
        json={"title": "Updated Title", "content": "Updated content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 200
    assert response.json["title"] == "Updated Title"
    assert response.json["content"] == "Updated content"
    assert response.json["id"] == "A1"


def test_update_record_rejects_missing_csrf(client):
    login(client, "alice")

    response = client.put(
        "/records/A1",
        json={"title": "Updated", "content": "Content"},
    )

    assert response.status_code == 400


def test_update_record_rejects_missing_title(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.put(
        "/records/A1",
        json={"content": "Content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title is required"


def test_update_another_users_record_rejected(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.put(
        "/records/B1",
        json={"title": "Hacked", "content": "Hacked content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 404


def test_update_nonexistent_record_rejected(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.put(
        "/records/NONEXISTENT",
        json={"title": "Title", "content": "Content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 404


def test_update_record_unauthenticated_rejected(client):
    # Without CSRF token, CSRF protection rejects first (400)
    response = client.put("/records/A1", json={"title": "Title", "content": "Content"})
    assert response.status_code == 400


def test_delete_own_record_success(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.delete(
        "/records/A1",
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 200
    assert response.json["message"] == "Record deleted"

    # Verify it's gone
    response = client.get("/records/A1")
    assert response.status_code == 404


def test_delete_record_rejects_missing_csrf(client):
    login(client, "alice")

    response = client.delete("/records/A1")
    assert response.status_code == 400


def test_delete_another_users_record_rejected(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.delete(
        "/records/B1",
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 404


def test_delete_nonexistent_record_rejected(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.delete(
        "/records/NONEXISTENT",
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 404


def test_delete_record_unauthenticated_rejected(client):
    # Without CSRF token, CSRF protection rejects first (400)
    response = client.delete("/records/A1")
    assert response.status_code == 400


def test_created_record_owned_by_creator(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.post(
        "/records",
        json={"title": "My Record", "content": "My content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 201
    new_id = response.json["id"]

    # Verify it appears in alice's list
    response = client.get("/records")
    record_ids = {r["id"] for r in response.json["records"]}
    assert new_id in record_ids

    # Verify bob cannot see it
    token = client.get("/login").json["csrf_token"]
    client.post(
        "/login",
        json={"username": "bob", "password": "Secret123!"},
        headers={"X-CSRFToken": token},
    )
    response = client.get("/records")
    record_ids = {r["id"] for r in response.json["records"]}
    assert new_id not in record_ids


def test_cannot_specify_owner_on_create(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    # Attempt to create record with explicit owner field (should be ignored)
    response = client.post(
        "/records",
        json={"title": "Test", "content": "Content", "owner": "bob"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 201
    new_id = response.json["id"]

    # Verify owner is alice, not bob
    from app.models import RECORDS
    assert RECORDS[new_id]["owner"] == "alice"


def test_create_record_rejects_null_title(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.post(
        "/records",
        json={"title": None, "content": "Content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title is required"


def test_create_record_rejects_non_string_title(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    response = client.post(
        "/records",
        json={"title": 123, "content": "Content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title is required"


def test_update_record_rejects_null_title(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    # Create a record to update
    response = client.post(
        "/records",
        json={"title": "Original", "content": "Content"},
        headers={"X-CSRFToken": token},
    )
    record_id = response.json["id"]

    response = client.put(
        f"/records/{record_id}",
        json={"title": None, "content": "Content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title is required"


def test_update_record_rejects_non_string_title(client):
    login(client, "alice")
    token = client.get("/login").json["csrf_token"]

    # Create a record to update
    response = client.post(
        "/records",
        json={"title": "Original", "content": "Content"},
        headers={"X-CSRFToken": token},
    )
    record_id = response.json["id"]

    response = client.put(
        f"/records/{record_id}",
        json={"title": 123, "content": "Content"},
        headers={"X-CSRFToken": token},
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title is required"