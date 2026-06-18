def test_list_analyses_empty(client, auth_headers):
    resp = client.get("/analyses/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_analyses_pagination(client, auth_headers):
    resp = client.get("/analyses/?skip=0&limit=5", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["limit"] == 5


def test_invalid_analysis_limit(client, auth_headers):
    resp = client.get("/analyses/?limit=500", headers=auth_headers)
    assert resp.status_code == 422


def test_create_analysis_resume_not_found(client, auth_headers):
    resp = client.post("/analyses/", json={
        "resume_id": "00000000-0000-0000-0000-000000000099",
        "job_description": "Looking for a Python developer with FastAPI experience.",
        "job_title": "Backend Developer"
    }, headers=auth_headers)
    assert resp.status_code == 404


def test_create_analysis_short_job_description(client, auth_headers):
    resp = client.post("/analyses/", json={
        "resume_id": "00000000-0000-0000-0000-000000000099",
        "job_description": "hi",
        "job_title": "Dev"
    }, headers=auth_headers)
    assert resp.status_code == 422


def test_get_analysis_not_found(client, auth_headers):
    resp = client.get("/analyses/00000000-0000-0000-0000-000000000099", headers=auth_headers)
    assert resp.status_code == 404


def test_analyses_requires_auth(client):
    resp = client.get("/analyses/")
    assert resp.status_code == 401