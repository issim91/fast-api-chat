import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.chat_repository import ChatRepository
from app.models.chat import Chat, ChatType

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def chat_repository(mock_db):
    return ChatRepository(mock_db)

@pytest.mark.asyncio
async def test_create_private_chat(chat_repository, mock_db):
    # Arrange
    name = "Private Chat"
    chat_type = ChatType.PRIVATE
    expected_chat = Chat(name=name, type=chat_type)
    mock_db.refresh = AsyncMock()
    mock_db.refresh.return_value = expected_chat

    # Act
    result = await chat_repository.create(name=name, type=chat_type)

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert result.name == expected_chat.name
    assert result.type == expected_chat.type

@pytest.mark.asyncio
async def test_create_group_chat(chat_repository, mock_db):
    # Arrange
    name = "Group Chat"
    chat_type = ChatType.GROUP
    expected_chat = Chat(name=name, type=chat_type)
    mock_db.refresh = AsyncMock()
    mock_db.refresh.return_value = expected_chat

    # Act
    result = await chat_repository.create(name=name, type=chat_type)

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert result.name == expected_chat.name
    assert result.type == expected_chat.type


@pytest.mark.asyncio
async def test_get_by_id_found(chat_repository, mock_db):
    # Arrange
    chat_id = 1
    expected_chat = Chat(id=chat_id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_chat
    mock_db.execute.return_value = mock_result

    # Act
    result = await chat_repository.get_by_id(chat_id)

    # Assert
    mock_db.execute.assert_called_once()
    assert result == expected_chat

@pytest.mark.asyncio
async def test_get_by_id_not_found(chat_repository, mock_db):
    # Arrange
    chat_id = 999
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await chat_repository.get_by_id(chat_id)

    # Assert
    mock_db.execute.assert_called_once()
    assert result is None

@pytest.mark.asyncio
async def test_has_access_private_chat(chat_repository, mock_db):
    # Arrange
    chat_id = 1
    user_id = 1
    chat = Chat(id=chat_id, type=ChatType.PRIVATE)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = chat
    mock_db.execute.return_value = mock_result

    # Act
    result = await chat_repository.has_access(chat_id, user_id)

    # Assert
    assert result is True
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_has_access_group_chat_member(chat_repository, mock_db):
    # Arrange
    chat_id = 1
    user_id = 1
    chat = Chat(id=chat_id, type=ChatType.GROUP)
    mock_chat_result = MagicMock()
    mock_chat_result.scalar_one_or_none.return_value = chat
    mock_group_result = MagicMock()
    mock_group_result.scalar_one_or_none.return_value = MagicMock()
    mock_db.execute.side_effect = [mock_chat_result, mock_group_result]

    # Act
    result = await chat_repository.has_access(chat_id, user_id)

    # Assert
    assert result is True
    assert mock_db.execute.call_count == 2

@pytest.mark.asyncio
async def test_has_access_group_chat_non_member(chat_repository, mock_db):
    # Arrange
    chat_id = 1
    user_id = 1
    chat = Chat(id=chat_id, type=ChatType.GROUP)
    mock_chat_result = MagicMock()
    mock_chat_result.scalar_one_or_none.return_value = chat
    mock_group_result = MagicMock()
    mock_group_result.scalar_one_or_none.return_value = None
    mock_db.execute.side_effect = [mock_chat_result, mock_group_result]

    # Act
    result = await chat_repository.has_access(chat_id, user_id)

    # Assert
    assert result is False
    assert mock_db.execute.call_count == 2

@pytest.mark.asyncio
async def test_has_access_nonexistent_chat(chat_repository, mock_db):
    # Arrange
    chat_id = 999
    user_id = 1
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await chat_repository.has_access(chat_id, user_id)

    # Assert
    assert result is False
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_is_group_member_true(chat_repository, mock_db):
    # Arrange
    chat_id = 1
    user_id = 1
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock()
    mock_db.execute.return_value = mock_result

    # Act
    result = await chat_repository.is_group_member(chat_id, user_id)

    # Assert
    assert result is True
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_is_group_member_false(chat_repository, mock_db):
    # Arrange
    chat_id = 1
    user_id = 1
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await chat_repository.is_group_member(chat_id, user_id)

    # Assert
    assert result is False
    mock_db.execute.assert_called_once() 
