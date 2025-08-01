FROM python:3.12-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .
COPY requirements-full.txt .

# Установка Python зависимостей (без telethon для минимального режима)
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание директории для логов и базы данных
RUN mkdir -p logs

# Переменные окружения
ENV PYTHONPATH=/app
ENV PORT=8000
ENV HOST=0.0.0.0

# Открытие порта
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда запуска
CMD ["python", "-m", "backend.main_minimal"]