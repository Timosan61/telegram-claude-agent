# 🚀 Развертывание Backend API для Telegram Claude Agent

Пошаговое руководство по развертыванию backend API с новыми функциями мониторинга чатов.

## 🎯 Статус Backend

✅ **Backend код полностью готов!**
- ✅ API эндпоинты для кампаний (`/campaigns`)
- ✅ API эндпоинты для логов (`/logs`)
- ✅ **НОВЫЕ** API эндпоинты для чатов (`/chats`) 
- ✅ Поддержка мониторинга активных чатов
- ✅ Отправка сообщений от имени бота
- ✅ Принудительные ответы на сообщения
- ✅ Файлы конфигурации: `Procfile`, `runtime.txt`, `requirements.txt`

## 🌐 Варианты развертывания

### Вариант 1: Heroku (рекомендуется для быстрого старта)

#### Шаг 1: Подготовка Heroku CLI
```bash
# Установка Heroku CLI (если не установлен)
curl https://cli-assets.heroku.com/install.sh | sh

# Логин в Heroku
heroku login
```

#### Шаг 2: Создание приложения Heroku
```bash
# Клонирование или переход в папку проекта
cd telegram-claude-agent

# Создание Heroku приложения
heroku create telegram-claude-backend-[your-name]

# Пример:
heroku create telegram-claude-backend-timosan
```

#### Шаг 3: Настройка переменных окружения
```bash
# Обязательные переменные Telegram
heroku config:set TELEGRAM_API_ID=21220429
heroku config:set TELEGRAM_API_HASH=your_telegram_api_hash
heroku config:set TELEGRAM_PHONE=+79885517453

# AI провайдеры
heroku config:set OPENAI_API_KEY=sk-proj-your_openai_key
heroku config:set ANTHROPIC_API_KEY=sk-ant-api03-your_claude_key

# База данных PostgreSQL (автоматически создается)
heroku addons:create heroku-postgresql:essential-0

# Для DigitalOcean App Platform нужна TELEGRAM_SESSION_STRING
# Получить можно через локальный запуск и генерацию сессии
heroku config:set TELEGRAM_SESSION_STRING=your_session_string_here

# Платформенные настройки
heroku config:set PORT=8080
heroku config:set HOST=0.0.0.0
```

#### Шаг 4: Развертывание
```bash
# Добавление Heroku remote (если не добавлен)
heroku git:remote -a telegram-claude-backend-[your-name]

# Деплой
git push heroku main

# Проверка логов
heroku logs --tail
```

#### Шаг 5: Проверка работоспособности
```bash
# Проверка статуса приложения
heroku ps:scale web=1

# Открыть приложение
heroku open

# Проверить health endpoint
curl https://telegram-claude-backend-[your-name].herokuapp.com/health
```

### Вариант 2: DigitalOcean App Platform

#### Шаг 1: Создание app.yaml
```yaml
name: telegram-claude-backend
services:
- name: api
  source_dir: /
  github:
    repo: Timosan61/telegram-claude-agent
    branch: main
  run_command: python -m backend.main_app_platform
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: TELEGRAM_API_ID
    value: "21220429"
  - key: TELEGRAM_API_HASH
    value: "your_telegram_api_hash"
  - key: TELEGRAM_PHONE
    value: "+79885517453"
  - key: OPENAI_API_KEY
    value: "sk-proj-your_openai_key"
  - key: ANTHROPIC_API_KEY
    value: "sk-ant-api03-your_claude_key"
  - key: TELEGRAM_SESSION_STRING
    value: "your_session_string"
  - key: PORT
    value: "8080"
  - key: HOST
    value: "0.0.0.0"
databases:
- name: main-db
  engine: PG
  num_nodes: 1
  size: db-s-dev-database
```

#### Шаг 2: Развертывание через Web UI
1. Зайдите на [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Создайте новое приложение
3. Подключите GitHub репозиторий `Timosan61/telegram-claude-agent`
4. Используйте конфигурацию выше
5. Добавьте PostgreSQL базу данных
6. Установите переменные окружения
7. Запустите деплой

### Вариант 3: Railway

#### Создание через Railway CLI
```bash
# Установка Railway CLI
npm install -g @railway/cli

# Логин
railway login

# Инициализация проекта
railway init

# Настройка переменных
railway variables set TELEGRAM_API_ID=21220429
railway variables set TELEGRAM_API_HASH=your_hash
railway variables set TELEGRAM_PHONE=+79885517453
railway variables set OPENAI_API_KEY=sk-proj-your_key
railway variables set TELEGRAM_SESSION_STRING=your_session

# Добавление PostgreSQL
railway add postgresql

# Деплой
railway up
```

## 🔑 Получение TELEGRAM_SESSION_STRING

Для работы в production нужна сессионная строка. Получить её можно:

### Метод 1: Локальная генерация
```python
# Создайте файл generate_session.py
from telethon import TelegramClient
import os
from dotenv import load_dotenv
import base64

load_dotenv()

API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')

async def main():
    client = TelegramClient('session', API_ID, API_HASH)
    await client.start(phone=PHONE)
    
    # Получение строки сессии
    session_string = client.session.save()
    
    # Кодирование в base64 для удобства
    session_b64 = base64.b64encode(session_string).decode()
    
    print(f"TELEGRAM_SESSION_STRING={session_string}")
    print(f"TELEGRAM_SESSION_B64={session_b64}")
    
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

```bash
# Запуск генерации
python generate_session.py
```

### Метод 2: Через Docker
```bash
# Создание временного контейнера для генерации сессии
docker run -it --rm \
  -e TELEGRAM_API_ID=21220429 \
  -e TELEGRAM_API_HASH=your_hash \
  -e TELEGRAM_PHONE=+79885517453 \
  python:3.11 bash

# Внутри контейнера
pip install telethon python-dotenv
python generate_session.py
```

## 📝 Обновление Frontend

После развертывания backend, обновите URL в Streamlit Cloud:

### В Settings → Secrets добавьте:
```toml
BACKEND_API_URL = "https://your-backend-app.herokuapp.com"
# или
BACKEND_API_URL = "https://your-app-platform-url.ondigitalocean.app"
```

## 🧪 Тестирование API

### Проверка здоровья системы
```bash
curl https://your-backend.herokuapp.com/health
```

### Тестирование эндпоинтов чатов
```bash
# Получение активных чатов
curl https://your-backend.herokuapp.com/chats/active

# Информация о чате
curl https://your-backend.herokuapp.com/chats/{chat_id}/info

# Сообщения чата
curl https://your-backend.herokuapp.com/chats/{chat_id}/messages
```

### Проверка документации API
```
https://your-backend.herokuapp.com/docs
```

## 🚨 Решение проблем

### Проблема: "Application Error" на Heroku
**Решение:**
```bash
# Проверка логов
heroku logs --tail

# Проверка статуса
heroku ps

# Перезапуск
heroku restart
```

### Проблема: "Database connection failed"
**Решение:**
```bash
# Проверка переменных БД
heroku config | grep DATABASE

# Добавление PostgreSQL addon
heroku addons:create heroku-postgresql:essential-0
```

### Проблема: "Telegram not authorized"
**Решение:**
1. Убедитесь, что TELEGRAM_SESSION_STRING корректная
2. Сгенерируйте новую сессию локально
3. Проверьте правильность API_ID и API_HASH

### Проблема: "CORS errors"
**Решение:**
Backend уже настроен с разрешением всех origins для разработки.
В production рекомендуется ограничить origins:

```python
# В main_app_platform.py или main.py
allow_origins=["https://your-streamlit-app.streamlit.app"]
```

## ✅ Чек-лист развертывания

- [ ] Backend развернут на выбранной платформе
- [ ] Все переменные окружения настроены
- [ ] PostgreSQL база данных подключена  
- [ ] TELEGRAM_SESSION_STRING настроена
- [ ] Health endpoint отвечает успешно
- [ ] API документация доступна на `/docs`
- [ ] Эндпоинты `/chats/active` работают
- [ ] BACKEND_API_URL обновлен в Streamlit Cloud
- [ ] Streamlit приложение подключается к backend
- [ ] Мониторинг чатов работает в интерфейсе

## 📞 Поддержка

Если возникают проблемы:

1. Проверьте логи платформы развертывания
2. Убедитесь в корректности всех переменных окружения
3. Проверьте подключение к базе данных
4. Убедитесь, что Telegram сессия активна

**Backend API готов к развертыванию с полной поддержкой мониторинга чатов!** 🎉