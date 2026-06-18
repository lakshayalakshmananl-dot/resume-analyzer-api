def test_register_success(client):
    resp = client.post("/users/register", json={
        "email": "new@example.com",
        "username": "newuser",
        "password": "password123"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client, registered_user):
    resp = client.post("/users/register", json={
        "email": "test@example.com",
        "username": "anotheruser",
        "password": "password123"
    })
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


def test_register_duplicate_username(client, registered_user):
    resp = client.post("/users/register", json={
        "email": "another@example.com",
        "username": "testuser",
        "password": "password123"
    })
    assert resp.status_code == 400
    assert "already taken" in resp.json()["detail"]


def test_login_success(client, registered_user):
    resp = client.post("/users/login", data={
        "username": "test@example.com",
        "password": "secret123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    resp = client.post("/users/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401


def test_login_wrong_email(client, registered_user):
    resp = client.post("/users/login", data={
        "username": "wrong@example.com",
        "password": "secret123"
    })
    assert resp.status_code == 401


def test_get_me(client, auth_headers):
    resp = client.get("/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_protected_route_without_token(client):
    resp = client.get("/resumes/")
    assert resp.status_code == 401


def test_protected_route_invalid_token(client):
    resp = client.get("/resumes/", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401