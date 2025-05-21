import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, WebSocketDisconnect
from app.api.controllers.websocket_controller import router
from app.core.websocket_manager import manager
from unittest.mock import AsyncMock, patch
import asyncio

app = FastAPI()
app.include_router(router)
client = TestClient(app)

@pytest.fixture(autouse=True)
async def cleanup_connections():
    # Clean up connections before each test
    manager.active_connections.clear()
    yield
    # Clean up connections after each test
    manager.active_connections.clear()

@pytest.fixture
def mock_chat_service():
    with patch('app.api.controllers.websocket_controller.ChatService') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
async def test_websocket_connection(mock_chat_service, mock_db):
    # Test successful connection
    with client.websocket_connect("/ws/1") as websocket:
        assert websocket is not None
        mock_chat_service.handle_websocket_connection.assert_called_once()

@pytest.mark.asyncio
async def test_websocket_disconnect(mock_chat_service, mock_db):
    # handle_websocket_connection сразу выбрасывает WebSocketDisconnect
    mock_chat_service.handle_websocket_connection.side_effect = WebSocketDisconnect()
    with client.websocket_connect("/ws/1"):
        pass
    assert 1 not in manager.active_connections

@pytest.mark.asyncio
async def test_websocket_invalid_user_id(mock_chat_service, mock_db):
    # Test with invalid user_id
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/invalid") as websocket:
            pass 
