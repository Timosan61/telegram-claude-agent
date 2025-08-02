# 🤖 Telegram Claude Agent

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://telegram-claude-agent.streamlit.app/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.2-FF6B6B.svg)](https://streamlit.io)

Автономный ИИ-агент для мониторинга Telegram-каналов и чатов с интеллектуальными ответами через Claude AI и OpenAI. **Специализируется на автоматических ответах на комментарии к постам каналов.**

## 🚀 Быстрый старт

### 1. Попробуйте демо (без установки)
👉 **[Откройте веб-приложение](https://telegram-claude-agent.streamlit.app/)**

### 2. Запуск за 5 минут
```bash
git clone https://github.com/YOUR_USERNAME/telegram-claude-agent.git
cd telegram-claude-agent
pip install -r requirements-full.txt
cp .env.example .env
# Отредактируйте .env с вашими API ключами
python run_full_stack.py
```

**Готово!** Откройте http://127.0.0.1:8501

## 🌟 Особенности

- **💬 Мониторинг комментариев** - Автоматические ответы на комментарии к постам Telegram каналов
- **🔍 Автоматический мониторинг** Telegram каналов и чатов
- **🧠 Интеграция с Claude AI** для генерации интеллектуальных ответов
- **📊 Веб-интерфейс** для управления кампаниями и просмотра статистики
- **💾 Долгосрочная память** с интеграцией Zep для контекстных ответов
- **📈 Аналитика** активности агента и производительности
- **☁️ Облачное развертывание** на Streamlit Cloud и DigitalOcean App Platform
- **🔒 Безопасность** с защищенным хранением API ключей

### 💬 Мониторинг комментариев каналов

Уникальная возможность автоматического ответа на комментарии к постам в Telegram каналах:

- **Автоматическое обнаружение** групп обсуждений, связанных с каналами
- **Умное определение комментариев** через анализ reply_to_msg_id
- **Правильная структура ответов** - ответы отображаются как комментарии к постам
- **Настраиваемые триггеры** - реакция на ключевые слова в комментариях
- **Живой мониторинг** - мгновенное реагирование на новые комментарии

**Пример работы**: Когда пользователь пишет комментарий "вопрос" или "помощь" к посту в канале, бот автоматически отвечает соответствующим комментарием.

## 🚀 Быстрый старт

### 🌐 Веб-интерфейс (Streamlit Cloud)

**Попробуйте прямо сейчас:** [https://your-app-name.streamlit.app/](https://your-app-name.streamlit.app/)

Веб-интерфейс позволяет:
- Управлять кампаниями мониторинга
- Просматривать статистику и логи
- Настраивать системные инструкции для агента

> **Примечание**: Для полной функциональности Telegram-агента необходим отдельный backend сервер.

### 💻 Локальная установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/YOUR_USERNAME/telegram-claude-agent.git
cd telegram-claude-agent
```

2. **Создайте виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\\Scripts\\activate  # Windows  
```

3. **Установите зависимости**
```bash
# Только веб-интерфейс
pip install -r requirements.txt

# Полная функциональность (включая Telegram агент)
pip install -r requirements-full.txt
```

4. **Настройте переменные окружения**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Отредактируйте secrets.toml с вашими API ключами
```

5. **Запустите приложение**
```bash
# Только веб-интерфейс
streamlit run streamlit_app.py

# Полная система (backend + frontend)
# Терминал 1: backend
python -m uvicorn backend.main:app --reload

# Терминал 2: frontend
streamlit run streamlit_app.py
```

После запуска:
- 🌐 **Веб-интерфейс**: http://localhost:8501
- 📖 **API документация**: http://localhost:8000/docs

## 📋 Основные функции

### ✅ Управление кампаниями
- Создание кампаний через веб-интерфейс
- Настройка ключевых слов и отслеживаемых чатов
- Конфигурация системных инструкций для ИИ
- Активация/деактивация кампаний

### ✅ Интеллектуальные ответы
- Анализ контекста предыдущих сообщений
- Генерация ответов через Claude Code SDK
- Использование примеров для обучения стиля
- Сохранение истории в долгосрочную память

### ✅ Мониторинг и аналитика
- Статистика работы агента в реальном времени
- Логи всех взаимодействий с детальной информацией
- Метрики производительности и успешности
- Фильтрация и поиск по логам

### ✅ Техническая интеграция
- REST API для программного управления
- Поддержка Zep Cloud для памяти
- Fallback на локальное хранение
- Telegram session management

## ⚙️ Конфигурация

### Обязательные переменные окружения

```env
# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE

# Telegram Configuration
TELEGRAM_API_ID=YOUR_API_ID
TELEGRAM_API_HASH=YOUR_API_HASH
TELEGRAM_PHONE=+YOUR_PHONE_NUMBER

# Database
DATABASE_URL=sqlite:///./campaigns.db
```

### Опциональные переменные

```env
# Zep Memory Integration
ZEP_API_KEY=z_YOUR_ZEP_KEY_HERE
ZEP_API_URL=https://api.getzep.com

# FastAPI Settings
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True

# Streamlit Cloud (только для облачного развертывания)
BACKEND_API_URL=https://your-backend.herokuapp.com
```

## 🌐 Развертывание в облаке

### Streamlit Cloud

1. **Загрузите проект на GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Подключитесь к [share.streamlit.io](https://share.streamlit.io)**
   - Войдите через GitHub
   - Выберите репозиторий
   - Укажите файл: `streamlit_app.py`

3. **Настройте секреты в Settings → Secrets:**
```toml
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR_KEY_HERE"
BACKEND_API_URL = "https://your-backend.herokuapp.com"

# Опционально (для отображения настроек)
TELEGRAM_API_ID = "YOUR_API_ID"
TELEGRAM_API_HASH = "YOUR_API_HASH"
TELEGRAM_PHONE = "+YOUR_PHONE_NUMBER"
```

### Backend сервер (Heroku/Railway/Render)

Backend можно развернуть на любой платформе поддерживающей Python:

**Heroku:**
```bash
# Создайте Procfile
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Установите CLI и деплойте
heroku create your-backend-app
git push heroku main
```

**Railway:**
```bash
# Установите CLI
npm install -g @railway/cli

# Инициализируйте и деплойте
railway login
railway init
railway up
```

## 📖 Документация

- **[USAGE.md](USAGE.md)** - Подробное руководство по использованию
- **[COMMENT_MONITORING.md](COMMENT_MONITORING.md)** - Техническая документация мониторинга комментариев
- **[AUTHENTICATION.md](AUTHENTICATION.md)** - Полное руководство по авторизации для всех платформ
- **[API Documentation](http://127.0.0.1:8000/docs)** - Интерактивная документация API
- **Makefile** - Список всех доступных команд (`make help`)

## 🛠️ Доступные команды

```bash
make help         # Показать все команды
make dev-setup    # Полная настройка для разработки
make run          # Запуск системы
make test         # Тестирование API
make check        # Проверка конфигурации
make clean        # Очистка временных файлов
make backup-db    # Резервная копия базы данных
```

## 🏛️ Структура проекта

```
telegram_claude_agent/
├── backend/           # FastAPI backend
│   ├── api/          # REST API endpoints
│   ├── core/         # Основная логика агента
│   └── main.py       # Точка входа API
├── database/         # Модели базы данных
│   └── models/       # SQLAlchemy модели
├── frontend/         # Streamlit интерфейс
│   └── app.py        # Веб-приложение
├── utils/            # Утилиты интеграции
│   ├── claude/       # Claude Code SDK
│   └── zep/          # Zep память
├── tests/            # Тесты
├── config/           # Конфигурационные файлы
└── run.py            # Главный скрипт запуска
```

## 🔒 Безопасность

- Все API ключи хранятся в `.env` файле (не коммитится в git)
- Поддержка ограничения доступа через ADMIN_USERNAMES
- Валидация всех входных данных
- Логирование всех действий для аудита

## 🚨 Важные замечания

⚠️ **Использование личного аккаунта**: Агент работает от имени вашего личного Telegram аккаунта. Соблюдайте лимиты Telegram API и условия использования.

⚠️ **Ответственность**: Убедитесь, что системные инструкции корректны и не могут привести к нежелательному поведению агента.

⚠️ **Мониторинг**: Регулярно проверяйте логи системы для контроля качества ответов.

## 📊 Системные требования

- Python 3.11+
- 2GB RAM (минимум)
- Доступ к интернету
- Telegram аккаунт с активным номером телефона

## 🤝 Разработка

Проект готов для дальнейшего развития:
- Модульная архитектура для легкого расширения
- Comprehensive API для интеграции с внешними системами
- Документированный код и тесты
- Поддержка Docker (планируется)

## 📞 Поддержка

При возникновении проблем:
1. Изучите [USAGE.md](USAGE.md)
2. Проверьте статус системы: `make check`
3. Запустите тесты: `make test`
4. Проверьте логи в веб-интерфейсе