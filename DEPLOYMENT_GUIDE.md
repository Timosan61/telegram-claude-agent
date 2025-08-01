# 🚀 Руководство по развертыванию Telegram Claude Agent

## 📋 Обзор

Telegram Claude Agent - это комплексное решение для мониторинга Telegram-чатов с использованием ИИ. Система состоит из:

- **Frontend**: Streamlit интерфейс управления (уже развернут в Streamlit Cloud)
- **Backend**: FastAPI сервер с Telegram интеграцией
- **Database**: SQLite (локально) или PostgreSQL (продакшн)

## 🎯 Варианты развертывания

### 1. 🏠 Локальное развертывание

#### Требования
- Python 3.9+
- Git
- API ключи (см. раздел "Получение API ключей")

#### Быстрый старт
```bash
# 1. Клонирование репозитория
git clone https://github.com/YOUR_USERNAME/telegram-claude-agent.git
cd telegram-claude-agent

# 2. Установка зависимостей
pip install -r requirements-full.txt

# 3. Настройка окружения
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами

# 4. Инициализация базы данных
python -c "from database.models.base import create_tables; create_tables()"

# 5. Запуск backend сервера
python backend/main.py

# 6. Запуск frontend (в отдельном терминале)
streamlit run streamlit_app.py
```

#### Доступ к приложению
- **Backend API**: http://127.0.0.1:8000
- **API документация**: http://127.0.0.1:8000/docs
- **Frontend**: http://127.0.0.1:8501

### 2. ☁️ Облачное развертывание

#### Frontend (Streamlit Cloud)
✅ **Уже развернут**: https://telegram-claude-agent.streamlit.app

#### Backend варианты

##### Option A: Railway
```bash
# 1. Установите Railway CLI
npm install -g @railway/cli

# 2. Логин в Railway
railway login

# 3. Инициализация проекта
railway init

# 4. Настройка переменных окружения
railway variables:set ANTHROPIC_API_KEY=your_key_here
railway variables:set TELEGRAM_API_ID=your_id
railway variables:set TELEGRAM_API_HASH=your_hash
railway variables:set TELEGRAM_PHONE=your_phone

# 5. Создание Procfile
echo "web: python backend/main.py" > Procfile

# 6. Деплой
railway up
```

##### Option B: Heroku
```bash
# 1. Установите Heroku CLI
# 2. Создайте приложение
heroku create your-telegram-agent-backend

# 3. Настройка переменных
heroku config:set ANTHROPIC_API_KEY=your_key_here
heroku config:set TELEGRAM_API_ID=your_id
heroku config:set TELEGRAM_API_HASH=your_hash
heroku config:set TELEGRAM_PHONE=your_phone

# 4. Деплой
git push heroku main
```

##### Option C: Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-full.txt .
RUN pip install -r requirements-full.txt

COPY . .
EXPOSE 8000

CMD ["python", "backend/main.py"]
```

```bash
# Сборка и запуск
docker build -t telegram-claude-agent .
docker run -p 8000:8000 --env-file .env telegram-claude-agent
```

### 3. 🐳 Docker Compose (Полный стек)

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/telegram_agent
    depends_on:
      - db
    env_file:
      - .env

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: telegram_agent
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - BACKEND_API_URL=http://backend:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 🔑 Получение API ключей

### 1. Telegram API
1. Перейдите на https://my.telegram.org/auth
2. Войдите с вашим номером телефона
3. Перейдите в "API development tools"
4. Создайте новое приложение
5. Скопируйте `api_id` и `api_hash`

### 2. Anthropic Claude
1. Перейдите на https://console.anthropic.com
2. Создайте аккаунт или войдите
3. Перейдите в раздел "API Keys"
4. Создайте новый ключ
5. Скопируйте ключ (начинается с `sk-ant-`)

### 3. OpenAI (опционально)
1. Перейдите на https://platform.openai.com/api-keys
2. Создайте новый API ключ
3. Скопируйте ключ (начинается с `sk-`)

### 4. Zep Memory (опционально)
1. Перейдите на https://www.getzep.com
2. Создайте аккаунт
3. Получите API ключ и URL

## ⚙️ Конфигурация

### Минимальная конфигурация .env
```env
# Обязательные
TELEGRAM_API_ID=your_id
TELEGRAM_API_HASH=your_hash
TELEGRAM_PHONE=+your_phone
ANTHROPIC_API_KEY=sk-ant-your-key

# Опциональные
OPENAI_API_KEY=sk-your-openai-key
DATABASE_URL=sqlite:///./campaigns.db
```

### Продакшн конфигурация
```env
# Используйте PostgreSQL в продакшне
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Настройте CORS для безопасности
ALLOWED_ORIGINS=https://your-streamlit-app.streamlit.app

# Используйте сильный секретный ключ
SECRET_KEY=your-super-secret-key-here

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=logs/telegram_agent.log
```

## 🔒 Безопасность

### Обязательные меры безопасности
1. **Никогда не коммитьте .env файлы**
2. **Используйте сильные секретные ключи**
3. **Настройте CORS для продакшна**
4. **Используйте HTTPS в продакшне**
5. **Регулярно обновляйте зависимости**

### Рекомендации
- Используйте переменные окружения для всех секретов
- Настройте мониторинг и алерты
- Регулярно делайте бэкапы базы данных
- Используйте rate limiting для API

## 🔧 Troubleshooting

### Частые проблемы

#### "No module named 'telethon'"
```bash
pip install telethon cryptg
```

#### "Database connection error"
```bash
# Проверьте DATABASE_URL в .env
# Для SQLite убедитесь, что директория существует
mkdir -p database
```

#### "Telegram authentication error"
```bash
# Проверьте правильность API_ID, API_HASH и номера телефона
# Убедитесь, что номер телефона имеет доступ к Telegram
```

#### "Claude API error"
```bash
# Проверьте ANTHROPIC_API_KEY
# Убедитесь, что у вас есть кредиты на счету Anthropic
```

### Логи и отладка
```bash
# Проверка логов FastAPI
tail -f logs/telegram_agent.log

# Проверка статуса API
curl http://127.0.0.1:8000/health

# Тестирование подключения к Telegram
python -c "from backend.core.telegram_agent import TelegramAgent; import asyncio; asyncio.run(TelegramAgent().initialize())"
```

## 📊 Мониторинг

### Health Checks
- **Backend**: `GET /health`
- **Database**: Проверяется автоматически
- **Telegram**: Показано в `/health` ответе

### Метрики
- Количество активных кампаний
- Статистика обработанных сообщений
- Время отклика API
- Статус соединений (Telegram, Database)

## 🔄 Обновления

### Обновление кода
```bash
git pull origin main
pip install -r requirements-full.txt --upgrade
# Перезапустите сервисы
```

### Миграции базы данных
```bash
# При изменении моделей данных
python -c "from database.models.base import create_tables; create_tables()"
```

## 📞 Поддержка

### Документация
- **API документация**: http://your-backend-url/docs
- **GitHub**: https://github.com/YOUR_USERNAME/telegram-claude-agent
- **Issues**: https://github.com/YOUR_USERNAME/telegram-claude-agent/issues

### Сообщество
- Создайте issue в GitHub для багов
- Используйте Discussions для вопросов
- Contribution guidelines в CONTRIBUTING.md

---

## 🚀 Быстрый старт для разработчиков

```bash
# Полная настройка за 5 минут
git clone https://github.com/YOUR_USERNAME/telegram-claude-agent.git
cd telegram-claude-agent
pip install -r requirements-full.txt
cp .env.example .env
# Отредактируйте .env с вашими ключами
python -c "from database.models.base import create_tables; create_tables()"
python backend/main_minimal.py  # Для тестирования без Telegram
```

**Frontend уже доступен**: https://telegram-claude-agent.streamlit.app