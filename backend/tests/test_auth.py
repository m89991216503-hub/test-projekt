import pytest


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    resp = await client.post("/api/login", json={"login": "test@example.com", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    resp = await client.post("/api/login", json={"login": "test@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client, db_session):
    resp = await client.post("/api/login", json={"login": "nobody@example.com", "password": "password123"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_by_username(client, test_user):
    # Login field without @ routes to username lookup → should fail (test_user has no username)
    resp = await client.post("/api/login", json={"login": "testuser", "password": "password123"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_missing_fields(client, db_session):
    resp = await client.post("/api/login", json={"password": "password123"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_success(client, db_session):
    resp = await client.post("/api/register", json={"email": "new@example.com", "password": "secret123"})
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user):
    resp = await client.post("/api/register", json={"email": "test@example.com", "password": "secret123"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password(client, db_session):
    resp = await client.post("/api/register", json={"email": "new@example.com", "password": "12345"})
    assert resp.status_code == 422
