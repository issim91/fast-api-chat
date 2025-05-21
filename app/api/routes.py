from fastapi import APIRouter
from app.api.controllers import user_controller, chat_controller, websocket_controller
from app.core.settings import settings

api_router = APIRouter()

# Подключаем все роутеры
api_router.include_router(
    user_controller.router,
    prefix=settings.API_V1_STR
)
api_router.include_router(
    chat_controller.router,
    prefix=settings.API_V1_STR
)
api_router.include_router(
    websocket_controller.router,
    prefix=settings.API_V1_STR
) 