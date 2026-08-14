def test_register_creates_user_without_leaking_password(client):
    response = client.post(
        "/api/auth/register", json={"email": "new@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_email_conflicts(client):
    client.post("/api/auth/register", json={"email": "dup@example.com", "password": "password123"})
    response = client.post(
        "/api/auth/register", json={"email": "dup@example.com", "password": "password123"}
    )
    assert response.status_code == 409


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/auth/register", json={"email": "short@example.com", "password": "short"}
    )
    assert response.status_code == 422


def test_login_wrong_password_rejected(client):
    client.post("/api/auth/register", json={"email": "u@example.com", "password": "password123"})
    response = client.post("/api/auth/login", json={"email": "u@example.com", "password": "wrong"})
    assert response.status_code == 401


def test_login_returns_usable_token(client):
    client.post("/api/auth/register", json={"email": "u2@example.com", "password": "password123"})
    login = client.post("/api/auth/login", json={"email": "u2@example.com", "password": "password123"})
    token = login.json()["access_token"]

    me = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "u2@example.com"
    assert me.json()["is_guest"] is False


def test_guest_session_is_flagged_as_guest(client):
    guest = client.post("/api/auth/guest")
    token = guest.json()["access_token"]
    me = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["is_guest"] is True


def test_protected_route_requires_token(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_protected_route_rejects_garbage_token(client):
    response = client.get("/api/users/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
