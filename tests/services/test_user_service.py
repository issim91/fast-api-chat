import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from app.services.user_service import UserService
from app.schemas.user import UserCreate

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_user_repository():
    with patch('app.services.user_service.UserRepository') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def user_service(mock_db, mock_user_repository):
    return UserService(mock_db)

@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_user_repository):
    # Arrange
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    expected_user = MagicMock(
        username=user_data.username,
        email=user_data.email
    )
    mock_user_repository.get_by_username.return_value = None
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.create.return_value = expected_user

    # Act
    result = await user_service.create_user(user_data)

    # Assert
    mock_user_repository.get_by_username.assert_called_once_with(user_data.username)
    mock_user_repository.get_by_email.assert_called_once_with(user_data.email)
    mock_user_repository.create.assert_called_once()
    assert result == expected_user

@pytest.mark.asyncio
async def test_create_user_username_exists(user_service, mock_user_repository):
    # Arrange
    user_data = UserCreate(
        username="existinguser",
        email="test@example.com",
        password="password123"
    )
    mock_user_repository.get_by_username.return_value = MagicMock()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.create_user(user_data)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Username already registered"
    mock_user_repository.get_by_username.assert_called_once_with(user_data.username)
    mock_user_repository.create.assert_not_called()

@pytest.mark.asyncio
async def test_create_user_email_exists(user_service, mock_user_repository):
    # Arrange
    user_data = UserCreate(
        username="newuser",
        email="existing@example.com",
        password="password123"
    )
    mock_user_repository.get_by_username.return_value = None
    mock_user_repository.get_by_email.return_value = MagicMock()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.create_user(user_data)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Email already registered"
    mock_user_repository.get_by_username.assert_called_once_with(user_data.username)
    mock_user_repository.get_by_email.assert_called_once_with(user_data.email)
    mock_user_repository.create.assert_not_called()

@pytest.mark.asyncio
async def test_authenticate_user_success(user_service, mock_user_repository):
    # Arrange
    username = "testuser"
    password = "password123"
    hashed_password = "hashed_password_here"
    user = MagicMock(
        username=username,
        hashed_password=hashed_password
    )
    mock_user_repository.get_by_username.return_value = user

    with patch('app.services.user_service.verify_password', return_value=True) as mock_verify:
        with patch('app.services.user_service.create_access_token', return_value="test_token") as mock_create_token:
            # Act
            result = await user_service.authenticate_user(username, password)

            # Assert
            mock_user_repository.get_by_username.assert_called_once_with(username)
            mock_verify.assert_called_once_with(password, hashed_password)
            mock_create_token.assert_called_once_with(data={"sub": username})
            assert result == {"access_token": "test_token", "token_type": "bearer"}

@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(user_service, mock_user_repository):
    # Arrange
    username = "testuser"
    password = "wrongpassword"
    mock_user_repository.get_by_username.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.authenticate_user(username, password)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Incorrect username or password"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    mock_user_repository.get_by_username.assert_called_once_with(username)

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(user_service, mock_user_repository):
    # Arrange
    username = "testuser"
    password = "wrongpassword"
    hashed_password = "hashed_password_here"
    user = MagicMock(
        username=username,
        hashed_password=hashed_password
    )
    mock_user_repository.get_by_username.return_value = user

    with patch('app.services.user_service.verify_password', return_value=False):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await user_service.authenticate_user(username, password)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Incorrect username or password"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
        mock_user_repository.get_by_username.assert_called_once_with(username) 