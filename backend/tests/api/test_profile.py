def test_measurements_start_empty_not_404(client, auth_headers):
    headers = auth_headers()
    response = client.get("/api/body-measurements", headers=headers)
    assert response.status_code == 200
    assert response.json()["height_cm"] is None


def test_quick_mode_then_accurate_mode_merges_without_overwriting(client, auth_headers):
    headers = auth_headers()

    client.put(
        "/api/body-measurements",
        headers=headers,
        json={"height_cm": 178, "weight_kg": 72, "usual_shirt_size": "M"},
    )
    response = client.put(
        "/api/body-measurements",
        headers=headers,
        json={"chest_cm": 98, "fit_preference": "regular"},
    )

    body = response.json()
    assert body["height_cm"] == 178
    assert body["weight_kg"] == 72
    assert body["usual_shirt_size"] == "M"
    assert body["chest_cm"] == 98
    assert body["fit_preference"] == "regular"


def test_measurements_rejects_invalid_fit_preference(client, auth_headers):
    headers = auth_headers()
    response = client.put(
        "/api/body-measurements", headers=headers, json={"fit_preference": "super-baggy"}
    )
    assert response.status_code == 422


def test_style_preferences_round_trip(client, auth_headers):
    headers = auth_headers()
    client.put(
        "/api/style-preferences",
        headers=headers,
        json={"favorite_colors": ["Navy", "Black"], "styles": ["Minimal"], "color_group": "dark"},
    )
    response = client.get("/api/style-preferences", headers=headers)
    body = response.json()
    assert body["favorite_colors"] == ["Navy", "Black"]
    assert body["color_group"] == "dark"


def test_profile_is_private_to_each_user(client, auth_headers):
    headers_a = auth_headers("a@example.com")
    headers_b = auth_headers("b@example.com")

    client.put("/api/users/profile", headers=headers_a, json={"name": "Alice"})
    client.put("/api/users/profile", headers=headers_b, json={"name": "Bob"})

    profile_a = client.get("/api/users/profile", headers=headers_a).json()
    profile_b = client.get("/api/users/profile", headers=headers_b).json()

    assert profile_a["name"] == "Alice"
    assert profile_b["name"] == "Bob"
