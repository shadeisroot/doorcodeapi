def test_generate_requires_auth(client):        # ← client injected by the fixture
    response = client.post("/codes/")
    assert response.status_code == 401


def test_verify_invalid_code(client):
    response = client.post("/codes/verify/doesnotexist")
    assert response.status_code == 403


def test_full_code_lifecycle(client):
    client.post("/auth/register", params={"username": "tester", "password": "pass123"})
    login = client.post("/auth/login", data={"username": "tester", "password": "pass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    gen = client.post("/codes/", headers=headers)
    assert gen.status_code == 201
    code = gen.json()["code"]

    first = client.post(f"/codes/verify/{code}")
    assert first.status_code == 200

    second = client.post(f"/codes/verify/{code}")
    assert second.status_code == 403