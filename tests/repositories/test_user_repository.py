import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.user import User

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def user_repository(mock_db):
    return UserRepository(mock_db)

@pytest.mark.asyncio
async def test_create_user(user_repository, mock_db):
    # Arrange
    username = "testuser"
    email = "test@example.com"
    hashed_password = "hashed_password"
    expected_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    mock_db.refresh = AsyncMock()
    mock_db.refresh.return_value = expected_user

    # Act
    result = await user_repository.create(username, email, hashed_password)

    # Assert
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert result.username == expected_user.username
    assert result.email == expected_user.email
    assert result.hashed_password == expected_user.hashed_password

@pytest.mark.asyncio
async def test_get_by_username_found(user_repository, mock_db):
    # Arrange
    username = "testuser"
    expected_user = User(username=username)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_db.execute.return_value = mock_result

    # Act
    result = await user_repository.get_by_username(username)

    # Assert
    mock_db.execute.assert_called_once()
    assert result == expected_user

@pytest.mark.asyncio
async def test_get_by_username_not_found(user_repository, mock_db):
    # Arrange
    username = "nonexistent"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await user_repository.get_by_username(username)

    # Assert
    mock_db.execute.assert_called_once()
    assert result is None

@pytest.mark.asyncio
async def test_get_by_email_found(user_repository, mock_db):
    # Arrange
    email = "test@example.com"
    expected_user = User(email=email)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_db.execute.return_value = mock_result

    # Act
    result = await user_repository.get_by_email(email)

    # Assert
    mock_db.execute.assert_called_once()
    assert result == expected_user

@pytest.mark.asyncio
async def test_get_by_email_not_found(user_repository, mock_db):
    # Arrange
    email = "nonexistent@example.com"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await user_repository.get_by_email(email)

    # Assert
    mock_db.execute.assert_called_once()
    assert result is None

@pytest.mark.asyncio
async def test_get_by_id_found(user_repository, mock_db):
    # Arrange
    user_id = 1
    expected_user = User(id=user_id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_db.execute.return_value = mock_result

    # Act
    result = await user_repository.get_by_id(user_id)

    # Assert
    mock_db.execute.assert_called_once()
    assert result == expected_user

@pytest.mark.asyncio
async def test_get_by_id_not_found(user_repository, mock_db):
    # Arrange
    user_id = 999
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    # Act
    result = await user_repository.get_by_id(user_id)

    # Assert
    mock_db.execute.assert_called_once()
    assert result is None 