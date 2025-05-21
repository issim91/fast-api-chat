# Chat Application

Веб-приложение для обмена сообщениями в реальном времени с поддержкой групповых чатов, построенное на FastAPI.

## Технологии

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, WebSockets
- **База данных**: PostgreSQL
- **Аутентификация**: JWT (JSON Web Tokens)
- **Контейнеризация**: Docker, Docker Compose
- **Асинхронность**: asyncio, asyncpg

## Функциональность

- Регистрация и аутентификация пользователей
- Создание приватных и групповых чатов
- Обмен сообщениями в реальном времени через WebSocket
- История сообщений с пагинацией
- Статусы прочтения сообщений
- Управление участниками групповых чатов

## Структура проекта

```
app/
├── api/
│   ├── controllers/     # Обработчики HTTP и WebSocket запросов
│   └── routes.py        # Маршрутизация API
├── core/
│   ├── database/        # Конфигурация базы данных
│   ├── security.py      # Безопасность и JWT
│   ├── auth.py          # Аутентификация
│   ├── settings.py      # Настройки приложения
│   └── websocket_manager.py  # Управление WebSocket соединениями
├── models/              # SQLAlchemy модели
├── schemas/             # Pydantic схемы
├── services/           # Бизнес-логика
├── repositories/       # Работа с базой данных
└── main.py            # Точка входа приложения
```

## Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd chat-application
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
.\venv\Scripts\activate  # для Windows
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

### Запуск в Docker

1. Соберите и запустите контейнеры:
```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000

## API Endpoints

### Аутентификация
- `POST /api/v1/users/` - Регистрация нового пользователя
- `POST /api/v1/users/token` - Получение JWT токена
- `GET /api/v1/users/me` - Получение информации о текущем пользователе

### Чаты
- `POST /api/v1/chats/` - Создание приватного чата
- `POST /api/v1/chats/groups/` - Создание группового чата
- `GET /api/v1/chats/{chat_id}/history` - Получение истории сообщений
- `GET /api/v1/chats/` - Получение списка чатов пользователя
- `GET /api/v1/chats/{chat_id}` - Получение информации о чате
- `POST /api/v1/chats/{chat_id}/members` - Добавление участника в групповой чат
- `DELETE /api/v1/chats/{chat_id}/members/{user_id}` - Удаление участника из группового чата

### Сообщения
- `POST /api/v1/messages/` - Отправка сообщения
- `GET /api/v1/messages/{message_id}` - Получение информации о сообщении
- `PUT /api/v1/messages/{message_id}/read` - Отметка сообщения как прочитанного

### WebSocket
- `WS /api/v1/ws/{user_id}` - WebSocket соединение для обмена сообщениями

### Форматы сообщений WebSocket

#### Отправка сообщения
```json
{
    "type": "message",
    "chat_id": 1,
    "text": "Текст сообщения"
}
```

#### Получение сообщения
```json
{
    "type": "message",
    "id": 1,
    "chat_id": 1,
    "sender_id": 1,
    "text": "Текст сообщения",
    "created_at": "2024-03-20T12:00:00Z",
    "is_read": false
}
```

#### Отметка о прочтении
```json
{
    "type": "read_receipt",
    "message_id": 1,
    "chat_id": 1,
    "reader_id": 1,
    "timestamp": "2024-03-20T12:00:00Z"
}
```

### Примеры запросов

#### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"username": "user1", "password": "password123"}'
```

#### Получение токена
```bash
curl -X POST "http://localhost:8000/api/v1/users/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user1&password=password123"
```

#### Создание приватного чата
```bash
curl -X POST "http://localhost:8000/api/v1/chats/" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 2}'
```

#### Создание группового чата
```bash
curl -X POST "http://localhost:8000/api/v1/chats/groups/" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{"name": "Группа 1", "user_ids": [2, 3]}'
```
