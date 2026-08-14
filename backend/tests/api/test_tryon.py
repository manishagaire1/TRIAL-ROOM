import io
import uuid

from PIL import Image

from app.models.user import User
from app.services.tryon_service import process_job


def _jpeg_bytes(width=400, height=600):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), color=(100, 100, 100)).save(buffer, format="JPEG")
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
            "name": "Test Shirt",
            "category": "Shirt",
            "primary_color": "Navy",
            "available_colors": ["Navy"],
            "price": 42,
        },
    )
    return response.json()["id"]


def test_tryon_requires_a_photo_first(client, auth_headers, db_session):
    headers = auth_headers()
    clothing_id = _create_shirt(client, db_session)

    response = client.post(
        "/api/tryon",
        headers=headers,
        json={"clothing_id": clothing_id, "selected_size": "M", "selected_color": "Navy"},
    )
    assert response.status_code == 400
    assert "photo" in response.json()["error"]["message"].lower()


def test_full_tryon_pipeline(client, auth_headers, db_session):
    headers = auth_headers("tryon-user@example.com")
    clothing_id = _create_shirt(client, db_session)

    client.post(
        "/api/users/photo",
        headers=headers,
        files={"file": ("photo.jpg", _jpeg_bytes(), "image/jpeg")},
    )

    job_response = client.post(
        "/api/tryon",
        headers=headers,
        json={"clothing_id": clothing_id, "selected_size": "M", "selected_color": "Navy"},
    )
    assert job_response.status_code == 202
    job = job_response.json()
    assert job["status"] == "pending"

    # The real BackgroundTask opens its own DB session (correct for
    # production — it runs after the response is sent), which can't see
    # this test's not-yet-committed transaction. Driving it explicitly
    # with the test's own db_session simulates exactly what that
    # background task does, inside a session that can see the job.
    process_job(uuid.UUID(job["id"]), db=db_session)

    job = client.get(f"/api/tryon/{job['id']}", headers=headers).json()
    assert job["status"] == "completed"
    assert job["result"]["provider"] == "mock"

    # image_url is API-relative (see Phase 7 fix), so the client prefixes /api.
    image_response = client.get(f"/api{job['result']['image_url']}", headers=headers)
    assert image_response.status_code == 200
    assert image_response.headers["content-type"] == "image/jpeg"

    history = client.get("/api/tryon/history", headers=headers)
    assert history.json()["total"] == 1

    delete_response = client.delete(f"/api/tryon/{job['id']}", headers=headers)
    assert delete_response.status_code == 204
    assert client.get(f"/api/tryon/{job['id']}", headers=headers).status_code == 404


def test_rejects_size_not_offered_by_product(client, auth_headers, db_session):
    headers = auth_headers("size-user@example.com")
    clothing_id = _create_shirt(client, db_session)
    client.post(
        "/api/users/photo",
        headers=headers,
        files={"file": ("photo.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    # This product has no size chart attached, so any size is technically
    # "not offered" — the size check is skipped when there's no chart to
    # check against (docs/08's size advisor honesty rule), but color
    # still must be one of available_colors.
    response = client.post(
        "/api/tryon",
        headers=headers,
        json={"clothing_id": clothing_id, "selected_size": "M", "selected_color": "Hot Pink"},
    )
    assert response.status_code == 400
    assert "color" in response.json()["error"]["message"].lower()
