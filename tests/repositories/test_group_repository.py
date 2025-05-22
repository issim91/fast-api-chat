import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.group_repository import GroupRepository
from app.models.group import Group

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def group_repository(mock_db):
    return GroupRepository(mock_db)

@pytest.mark.asyncio
async def test_create_group(group_repository, mock_db):
    # Arrange
    chat_id = 1
    name = "Test Group"
    creator_id = 1
    expected_group = Group(
        chat_id=chat_id,
        name=name,
        creator_id=creator_id
    )
    mock_db.refresh = AsyncMock()
    mock_db.refresh.return_value = expected_group

    # Act
    result = await group_repository.create(chat_id, name, creator_id)

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert result.chat_id == expected_group.chat_id
    assert result.name == expected_group.name
    assert result.creator_id == expected_group.creator_id


@pytest.mark.asyncio
async def test_get_by_id_found(group_repository, mock_db):
    # Arrange
    group_id = 1
    expected_group = Group(id=group_id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_group
    mock_db.execute.return_value = mock_result

    # Act
    result = await group_repository.get_by_id(group_id)

    # Assert
    mock_db.execute.assert_called_once()
    assert result == expected_group

@pytest.mark.asyncio
async def test_get_by_id_not_found(group_repository, mock_db):
    # Arrange
    group_id = 999
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await group_repository.get_by_id(group_id)

    # Assert
    mock_db.execute.assert_called_once()
    assert result is None

@pytest.mark.asyncio
async def test_add_member_success(group_repository, mock_db):
    # Arrange
    group_id = 1
    user_id = 1
    group = Group(id=group_id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = group
    mock_db.execute.return_value = mock_result
    mock_db.refresh = AsyncMock()
    mock_db.refresh.return_value = group

    # Act
    result = await group_repository.add_member(group_id, user_id)

    # Assert
    mock_db.execute.assert_called()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert result == group

@pytest.mark.asyncio
async def test_add_member_group_not_found(group_repository, mock_db):
    # Arrange
    group_id = 999
    user_id = 1
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await group_repository.add_member(group_id, user_id)

    # Assert
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()
    assert result is None

@pytest.mark.asyncio
async def test_remove_member_success(group_repository, mock_db):
    # Arrange
    group_id = 1
    user_id = 1
    group = Group(id=group_id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = group
    mock_db.execute.return_value = mock_result
    mock_db.refresh = AsyncMock()
    mock_db.refresh.return_value = group

    # Act
    result = await group_repository.remove_member(group_id, user_id)

    # Assert
    mock_db.execute.assert_called()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert result == group

@pytest.mark.asyncio
async def test_remove_member_group_not_found(group_repository, mock_db):
    # Arrange
    group_id = 999
    user_id = 1
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await group_repository.remove_member(group_id, user_id)

    # Assert
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()
    assert result is None 
