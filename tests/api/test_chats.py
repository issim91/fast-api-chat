import pytest
from httpx import AsyncClient
from app.models.user import User
from app.models.chat import ChatType

pytestmark = pytest.mark.asyncio

async def auth_headers(client: AsyncClient, username: str, password: str):
    response = await client.post(
        "/api/v1/token",
        data={"username": username, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

async def test_create_chat(client: AsyncClient, test_user: User):
    headers = await auth_headers(client, test_user.username, "testpass123")
    response = await client.post(
        "/api/v1/chats/",
        json={
            "name": "Test Chat",
            "type": ChatType.PRIVATE.value
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Chat"
    assert data["type"] == ChatType.PRIVATE.value
    assert "id" in data

async def test_create_group(client: AsyncClient, test_user: User):
    headers = await auth_headers(client, test_user.username, "testpass123")
    response = await client.post(
        "/api/v1/chats/groups/",
        json={"name": "Test Group"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Group"
    assert "id" in data
    assert "chat_id" in data
    assert "creator_id" in data

async def test_get_chat_history(client: AsyncClient, test_user: User):
    headers = await auth_headers(client, test_user.username, "testpass123")
    # Сначала создаём чат
    chat_resp = await client.post(
        "/api/v1/chats/",
        json={
            "name": "History Chat",
            "type": ChatType.PRIVATE.value
        },
        headers=headers
    )
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "id" in chat_data
    chat_id = chat_data["id"]

    # Получаем историю (ожидаем пустой список)
    response = await client.get(
        f"/api/v1/chats/{chat_id}/history",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) 
