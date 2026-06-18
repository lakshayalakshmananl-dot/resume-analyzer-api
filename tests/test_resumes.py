def test_list_resumes_empty(client, auth_headers):
    resp = client.get("/resumes/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["skip"] == 0
    assert data["limit"] == 10


def test_list_resumes_pagination_params(client, auth_headers):
    resp = client.get("/resumes/?skip=0&limit=5", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["limit"] == 5


def test_invalid_limit_too_high(client, auth_headers):
    resp = client.get("/resumes/?limit=200", headers=auth_headers)
    assert resp.status_code == 422


def test_invalid_skip_negative(client, auth_headers):
    resp = client.get("/resumes/?skip=-1", headers=auth_headers)
    assert resp.status_code == 422


def test_get_resume_not_found(client, auth_headers):
    resp = client.get("/resumes/00000000-0000-0000-0000-000000000099", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_resume_not_found(client, auth_headers):
    resp = client.delete("/resumes/00000000-0000-0000-0000-000000000099", headers=auth_headers)
    assert resp.status_code == 404