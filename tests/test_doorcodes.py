from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_requires_auth():
    # No token → should be rejected
    response = client.post("/codes/")
    assert response.status_code == 401

def test_verify_invalid_code():
    # A code that doesn't exist → access denied
    response = client.post("/codes/verify/doesnotexist")
    assert response.status_code == 403

def test_full_code_lifecycle():
    # 1. Register + login to get a token
    client.post("/auth/register", params={"username": "tester", "password": "pass123"})
    login = client.post("/auth/login", data={"username": "tester", "password": "pass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Generate a code (authenticated)
    gen = client.post("/codes/", headers=headers)
    assert gen.status_code == 201
    code = gen.json()["code"]

    # 3. Verify it → should be granted
    first = client.post(f"/codes/verify/{code}")
    assert first.status_code == 200
    assert first.json()["access"] == "granted"

    # 4. Verify the SAME code again → one-time use, should now fail
    second = client.post(f"/codes/verify/{code}")
    assert second.status_code == 403