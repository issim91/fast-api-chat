import pytest
from httpx import AsyncClient
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/users/",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "password" not in data

async def test_create_user_duplicate_username(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/v1/users/",
        json={
            "username": test_user.username,
            "email": "another@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

async def test_create_user_invalid_data(client: AsyncClient):
    response = await client.post(
        "/api/v1/users/",
        json={
            "username": "te",
            "email": "invalid-email",
            "password": "123"
        }
    )
    assert response.status_code == 422

async def test_get_token(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/v1/token",
        data={
            "username": test_user.username,
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_get_token_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/token",
        data={
            "username": "nonexistent",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

async def test_get_current_user(client: AsyncClient, test_user: User):
    token_response = await client.post(
        "/api/v1/token",
        data={
            "username": test_user.username,
            "password": "testpass123"
        }
    )
    token = token_response.json()["access_token"]
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert "id" in data
    assert "password" not in data

async def test_get_current_user_no_token(client: AsyncClient):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

async def test_get_current_user_invalid_token(client: AsyncClient):
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"] 
