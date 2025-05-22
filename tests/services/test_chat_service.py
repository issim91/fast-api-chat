import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from app.services.chat_service import ChatService
from app.models.chat import ChatType
from app.schemas.chat import ChatCreate
from app.schemas.group import GroupCreate
from app.models.user import User

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_chat_repository():
    with patch('app.services.chat_service.ChatRepository') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_message_repository():
    with patch('app.services.chat_service.MessageRepository') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_group_repository():
    with patch('app.services.chat_service.GroupRepository') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_websocket_manager():
    with patch('app.services.chat_service.manager', new_callable=AsyncMock) as mock:
        mock.connect = AsyncMock()
        mock.disconnect = AsyncMock()
        mock.send_message = AsyncMock()
        mock.send_read_receipt = AsyncMock()
        yield mock

@pytest.fixture
def chat_service(mock_db, mock_chat_repository, mock_message_repository, mock_group_repository):
    return ChatService(mock_db)

@pytest.mark.asyncio
async def test_create_chat(chat_service, mock_chat_repository):
    # Arrange
    chat_data = ChatCreate(name="Test Chat", type=ChatType.PRIVATE)
    expected_chat = MagicMock()
    mock_chat_repository.create.return_value = expected_chat

    # Act
    result = await chat_service.create_chat(chat_data)

    # Assert
    mock_chat_repository.create.assert_called_once_with(
        name=chat_data.name,
        type=chat_data.type
    )
    assert result == expected_chat

@pytest.mark.asyncio
async def test_create_group(chat_service, mock_chat_repository, mock_group_repository):
    # Arrange
    group_data = GroupCreate(name="Test Group")
    current_user_id = 1
    expected_chat = MagicMock(id=1)
    expected_group = MagicMock()
    
    mock_chat_repository.create.return_value = expected_chat
    mock_group_repository.create.return_value = expected_group

    # Act
    result = await chat_service.create_group(group_data, current_user_id)

    # Assert
    mock_chat_repository.create.assert_called_once_with(type=ChatType.GROUP)
    mock_group_repository.create.assert_called_once_with(
        chat_id=expected_chat.id,
        creator_id=current_user_id,
        name=group_data.name
    )
    mock_group_repository.add_member.assert_called_once_with(expected_group.id, current_user_id)
    assert result == expected_group

@pytest.mark.asyncio
async def test_get_chat_history_success(chat_service, mock_chat_repository, mock_message_repository):
    # Arrange
    chat_id = 1
    current_user = User(id=1)
    expected_messages = [MagicMock()]
    
    mock_chat_repository.has_access.return_value = True
    mock_message_repository.get_chat_messages.return_value = expected_messages

    # Act
    result = await chat_service.get_chat_history(chat_id, limit=10, offset=0, current_user=current_user)

    # Assert
    mock_chat_repository.has_access.assert_called_once_with(chat_id, current_user.id)
    mock_message_repository.get_chat_messages.assert_called_once_with(
        chat_id=chat_id,
        limit=10,
        offset=0
    )
    assert result == expected_messages

@pytest.mark.asyncio
async def test_get_chat_history_access_denied(chat_service, mock_chat_repository):
    # Arrange
    chat_id = 1
    current_user = User(id=1)
    mock_chat_repository.has_access.return_value = False

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await chat_service.get_chat_history(chat_id, limit=10, offset=0, current_user=current_user)
    
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Access denied"

def make_async_side_effect(sequence):
    counter = {"i": 0}
    async def side_effect(*args, **kwargs):
        i = counter["i"]
        counter["i"] += 1
        value = sequence[i]
        if callable(value):
            return await value()
        if isinstance(value, Exception):
            raise value
        return value
    return side_effect
