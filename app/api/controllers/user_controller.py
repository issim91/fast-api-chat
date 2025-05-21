from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, User
from app.services.user_service import UserService
from app.core.database import get_db
from app.core.auth import get_current_user

router = APIRouter(tags=["users"])

@router.post("/users/", response_model=User)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    return await user_service.create_user(user_data)

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    return await user_service.authenticate_user(form_data.username, form_data.password)

@router.get("/users/me", response_model=User)
async def get_current_user_route(
    current_user: User = Depends(get_current_user)
):
    return current_user 