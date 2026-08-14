from app.models.user import User


def _admin_headers(client, db_session, email="admin@example.com"):
    client.post("/api/auth/register", json={"email": email, "password": "password123"})
    user = db_session.query(User).filter(User.email == email).first()
    user.is_admin = True
    db_session.commit()
    login = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_clothing(client, headers, **overrides):
    payload = {
        "name": "Test Shirt",
        "category": "Shirt",
        "primary_color": "Navy",
        "available_colors": ["Navy", "White"],
        "price": 42,
        **overrides,
    }
    return client.post("/api/clothes", headers=headers, json=payload)


def test_catalog_browsing_requires_no_auth(client, db_session):
    admin = _admin_headers(client, db_session)
    _create_clothing(client, admin)

    response = client.get("/api/clothes")
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_create_requires_authentication(client):
    response = _create_clothing(client, headers={})
    assert response.status_code == 401


def test_create_requires_admin_not_just_login(client, auth_headers):
    headers = auth_headers()
    response = _create_clothing(client, headers)
    assert response.status_code == 403


def test_admin_can_create_and_it_is_then_browsable(client, db_session):
    admin = _admin_headers(client, db_session)
    created = _create_clothing(client, admin, name="Navy Blazer")
    assert created.status_code == 201

    detail = client.get(f"/api/clothes/{created.json()['id']}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Navy Blazer"


def test_category_filter(client, db_session):
    admin = _admin_headers(client, db_session)
    _create_clothing(client, admin, name="A Shirt", category="Shirt")
    _create_clothing(client, admin, name="Some Jeans", category="Jeans", primary_color="Indigo")

    response = client.get("/api/clothes", params={"category": "Jeans"})
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "Some Jeans"


def test_get_nonexistent_product_404s(client):
    response = client.get("/api/clothes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
