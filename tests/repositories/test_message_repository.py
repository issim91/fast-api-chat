import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.message_repository import MessageRepository
from app.models.message import Message

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def message_repository(mock_db):
    return MessageRepository(mock_db)

@pytest.mark.asyncio
async def test_create_message(message_repository, mock_db):
    # Arrange
    chat_id = 1
    sender_id = 1
    text = "Hello, world!"
    expected_message = Message(
        chat_id=chat_id,
        sender_id=sender_id,
        text=text
    )
    mock_db.refresh = AsyncMock()
    mock_db.refresh.return_value = expected_message

    # Act
    result = await message_repository.create(chat_id, sender_id, text)

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert result.chat_id == expected_message.chat_id
    assert result.sender_id == expected_message.sender_id
    assert result.text == expected_message.text

@pytest.mark.asyncio
async def test_get_by_id_found(message_repository, mock_db):
    # Arrange
    message_id = 1
    expected_message = Message(id=message_id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_message
    mock_db.execute.return_value = mock_result

    # Act
    result = await message_repository.get_by_id(message_id)

    # Assert
    mock_db.execute.assert_called_once()
    assert result == expected_message

@pytest.mark.asyncio
async def test_get_by_id_not_found(message_repository, mock_db):
    # Arrange
    message_id = 999
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await message_repository.get_by_id(message_id)

    # Assert
    mock_db.execute.assert_called_once()
    assert result is None

@pytest.mark.asyncio
async def test_get_chat_messages_with_pagination(message_repository, mock_db):
    # Arrange
    chat_id = 1
    limit = 10
    offset = 20
    expected_messages = [Message(id=i) for i in range(3)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected_messages
    mock_db.execute.return_value = mock_result

    # Act
    result = await message_repository.get_chat_messages(chat_id, limit, offset)

    # Assert
    mock_db.execute.assert_called_once()
    assert result == expected_messages

@pytest.mark.asyncio
async def test_get_chat_messages_empty(message_repository, mock_db):
    # Arrange
    chat_id = 1
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    # Act
    result = await message_repository.get_chat_messages(chat_id)

    # Assert
    mock_db.execute.assert_called_once()
    assert result == []

@pytest.mark.asyncio
async def test_mark_as_read_success(message_repository, mock_db):
    # Arrange
    message_id = 1
    message = Message(id=message_id, is_read=False)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = message
    mock_db.execute.return_value = mock_result
    mock_db.refresh = AsyncMock()
    mock_db.refresh.return_value = message

    # Act
    result = await message_repository.mark_as_read(message_id)

    # Assert
    assert result.is_read is True
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_mark_as_read_message_not_found(message_repository, mock_db):
    # Arrange
    message_id = 999
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await message_repository.mark_as_read(message_id)

    # Assert
    assert result is None
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called() 