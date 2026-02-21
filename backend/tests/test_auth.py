import pytest


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    resp = await client.post("/api/login", json={"email": "test@example.com", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    resp = await client.post("/api/login", json={"email": "test@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client, db_session):
    resp = await client.post("/api/login", json={"email": "nobody@example.com", "password": "password123"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_email(client, db_session):
    resp = await client.post("/api/login", json={"email": "not-an-email", "password": "password123"})
    assert resp.status_code == 422
