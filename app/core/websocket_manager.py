from fastapi import WebSocket
from typing import Dict, Set
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # Хранение активных соединений по user_id
        self.active_connections: Dict[int, WebSocket] = {}
        # Хранение участников чатов
        self.chat_members: Dict[int, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    def add_user_to_chat(self, chat_id: int, user_id: int):
        if chat_id not in self.chat_members:
            self.chat_members[chat_id] = set()
        self.chat_members[chat_id].add(user_id)

    def remove_user_from_chat(self, chat_id: int, user_id: int):
        if chat_id in self.chat_members:
            self.chat_members[chat_id].discard(user_id)

    async def send_message(self, message: dict, chat_id: int):
        if chat_id in self.chat_members:
            for user_id in self.chat_members[chat_id]:
                if user_id in self.active_connections:
                    await self.active_connections[user_id].send_json(message)

    async def send_read_receipt(self, message_id: int, chat_id: int, reader_id: int):
        read_receipt = {
            "type": "read_receipt",
            "message_id": message_id,
            "chat_id": chat_id,
            "reader_id": reader_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(read_receipt, chat_id)

# Создаем глобальный экземпляр менеджера
manager = ConnectionManager() 