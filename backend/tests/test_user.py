import pytest


@pytest.mark.asyncio
async def test_get_profile(client, auth_header):
    resp = await client.get("/api/me", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_profile_no_token(client, db_session):
    resp = await client.get("/api/me")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_profile_invalid_token(client, db_session):
    resp = await client.get("/api/me", headers={"Authorization": "Bearer invalid-token"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_change_password_success(client, auth_header):
    resp = await client.put(
        "/api/me/password",
        json={"old_password": "password123", "new_password": "newpass456"},
        headers=auth_header,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Password changed successfully"

    # Verify login with new password works
    resp = await client.post("/api/login", json={"login": "test@example.com", "password": "newpass456"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_old(client, auth_header):
    resp = await client.put(
        "/api/me/password",
        json={"old_password": "wrongpass", "new_password": "newpass456"},
        headers=auth_header,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_change_password_too_short(client, auth_header):
    resp = await client.put(
        "/api/me/password",
        json={"old_password": "password123", "new_password": "short"},
        headers=auth_header,
    )
    assert resp.status_code == 400
