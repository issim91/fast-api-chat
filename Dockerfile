FROM python:3.11-slim AS base

WORKDIR /app

# Установка базовых зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Этап для тестов
FROM base AS test
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["pytest", "tests/", "-v", "--cov=app"]

# Этап для продакшена
FROM base AS production
COPY . .
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
