"""
Section 40 calls out "Authorization" as its own test category, distinct
from authentication: being logged in is not the same as being allowed to
touch a specific resource. Every user-owned resource type gets one test
here proving user B cannot read, modify, or delete user A's data.
"""

import io

from PIL import Image

from app.models.user import User


def _jpeg_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (400, 600), color=(80, 80, 80)).save(buffer, format="JPEG")
    return buffer.getvalue()


def _admin_headers(client, db_session, email="admin@example.com"):
    client.post("/api/auth/register", json={"email": email, "password": "password123"})
    user = db_session.query(User).filter(User.email == email).first()
    user.is_admin = True
    db_session.commit()
    login = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _create_shirt(client, db_session):
    admin = _admin_headers(client, db_session)
    response = client.post(
        "/api/clothes",
        headers=admin,
        json={
            "name": "Auth Test Shirt",
            "category": "Shirt",
            "primary_color": "Navy",
            "available_colors": ["Navy"],
            "price": 42,
        },
    )
    return response.json()["id"]


def test_cannot_delete_another_users_tryon_job(client, auth_headers, db_session):
    owner = auth_headers("owner@example.com")
    intruder = auth_headers("intruder@example.com")
    clothing_id = _create_shirt(client, db_session)

    client.post(
        "/api/users/photo", headers=owner, files={"file": ("p.jpg", _jpeg_bytes(), "image/jpeg")}
    )
    job = client.post(
        "/api/tryon",
        headers=owner,
        json={"clothing_id": clothing_id, "selected_size": "M", "selected_color": "Navy"},
    ).json()

    assert client.get(f"/api/tryon/{job['id']}", headers=intruder).status_code == 404
    assert client.delete(f"/api/tryon/{job['id']}", headers=intruder).status_code == 404
    # And the owner can still see it — the job wasn't actually deleted.
    assert client.get(f"/api/tryon/{job['id']}", headers=owner).status_code == 200


def test_cannot_access_another_users_wardrobe_item(client, auth_headers):
    owner = auth_headers("wardrobe-owner@example.com")
    intruder = auth_headers("wardrobe-intruder@example.com")

    item = client.post(
        "/api/wardrobe",
        headers=owner,
        files={"file": ("shirt.jpg", _jpeg_bytes(), "image/jpeg")},
        data={"category": "Shirt", "color": "Black"},
    ).json()

    assert client.get(f"/api/wardrobe/{item['id']}/file", headers=intruder).status_code == 404
    assert client.delete(f"/api/wardrobe/{item['id']}", headers=intruder).status_code == 404


def test_cannot_delete_another_users_outfit(client, auth_headers, db_session):
    owner = auth_headers("outfit-owner@example.com")
    intruder = auth_headers("outfit-intruder@example.com")
    clothing_id = _create_shirt(client, db_session)

    outfit = client.post(
        "/api/outfits", headers=owner, json={"clothing_id": clothing_id}
    ).json()

    assert client.patch(
        f"/api/outfits/{outfit['id']}", headers=intruder, json={"liked": True}
    ).status_code == 404
    assert client.delete(f"/api/outfits/{outfit['id']}", headers=intruder).status_code == 404


def test_cannot_build_outfit_from_another_users_wardrobe_item(client, auth_headers):
    owner = auth_headers("builder-owner@example.com")
    intruder = auth_headers("builder-intruder@example.com")

    item = client.post(
        "/api/wardrobe",
        headers=owner,
        files={"file": ("shoes.jpg", _jpeg_bytes(), "image/jpeg")},
        data={"category": "Shoes", "color": "White"},
    ).json()

    # Intruder tries to reference the owner's wardrobe item in their own
    # outfit — must fail, not silently succeed and leak/borrow the item.
    response = client.post(
        "/api/outfits", headers=intruder, json={"items": [{"wardrobe_item_id": item["id"]}]}
    )
    assert response.status_code == 404


def test_guest_and_registered_accounts_are_fully_isolated(client, auth_headers):
    real_user = auth_headers("real@example.com")
    guest = client.post("/api/auth/guest").json()
    guest_headers = {"Authorization": f"Bearer {guest['access_token']}"}

    client.put("/api/users/profile", headers=real_user, json={"name": "Real Person"})
    client.put("/api/users/profile", headers=guest_headers, json={"name": "Guest Name"})

    assert client.get("/api/users/profile", headers=real_user).json()["name"] == "Real Person"
    assert client.get("/api/users/profile", headers=guest_headers).json()["name"] == "Guest Name"
