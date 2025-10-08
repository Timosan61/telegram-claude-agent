# 🤖 Telegram Claude Agent

**Intelligent Telegram monitoring agent with Claude/OpenAI integration**

Автоматический мониторинг Telegram-чатов с генерацией ответов через ИИ-провайдеров (Claude, OpenAI).

---

## ✨ Основные возможности

### 📋 **Управление кампаниями**
- Создание кампаний мониторинга Telegram-чатов
- Настройка ключевых слов и AI-провайдеров
- Автоматические ответы с контекстом сообщений

### 📈 **Аналитика чатов** (NEW)
- **Прямой анализ каналов** без привязки к кампаниям
- Анализ сообщений за период с фильтрами
- Статистика участников и активности
- Временные паттерны (по часам/дням)
- Анализ ключевых слов, хештегов, упоминаний
- Статистика медиафайлов
- Экспорт в CSV/JSON

### 🏢 **Настройки компании**
- Управление Telegram аккаунтами
- Конфигурация AI провайдеров (Claude/OpenAI)
- Системные инструкции по умолчанию

### 📊 **Мониторинг и логи**
- Отслеживание активности бота
- Статистика ответов и производительности
- Детальные логи операций

---

## 🏗️ Архитектура

```
telegram-claude-agent/
├── backend/                    # FastAPI сервер
│   ├── api/                   # API эндпоинты
│   │   ├── campaigns.py       # Управление кампаниями
│   │   ├── chats.py          # Мониторинг чатов
│   │   ├── company.py        # Настройки компании
│   │   ├── analytics.py      # Аналитика чатов (NEW)
│   │   └── logs.py           # Логи и статистика
│   ├── core/                 # Ядро системы
│   │   ├── telegram_agent.py # Локальный Telegram агент
│   │   └── telegram_agent_app_platform.py # Продакшн агент
│   ├── services/             # Сервисы
│   │   └── analytics_service.py # Сервис аналитики (NEW)
│   ├── main.py              # Локальная разработка
│   └── main_app_platform.py # Продакшн сервер
├── frontend/                # Streamlit веб-интерфейс
│   ├── app.py              # Главное приложение
│   ├── components/         # Переиспользуемые компоненты
│   │   └── api_client.py   # Унифицированный API клиент
│   └── pages/              # Страницы интерфейса
│       ├── analytics.py    # Аналитика чатов (NEW)
│       └── statistics.py   # Статистика системы
├── database/               # База данных
│   ├── models/            # SQLAlchemy модели
│   └── migrations/        # Миграции БД
└── streamlit_app.py       # Точка входа Streamlit
```

---

## 🚀 Быстрый старт

### 1. **Клонирование репозитория**
```bash
git clone https://github.com/Timosan61/telegram-claude-agent.git
cd telegram-claude-agent
```

### 2. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

### 3. **Настройка переменных окружения**
Создайте `.env` файл:
```bash
# Telegram API (обязательно)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890

# AI провайдеры (один на выбор)
ANTHROPIC_API_KEY=sk-ant-api03-...     # Для Claude
OPENAI_API_KEY=sk-proj-...             # Для OpenAI

# База данных (опционально)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Backend настройки
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True
```

### 4. **Получение Telegram API credentials**
1. Идите на https://my.telegram.org
2. Войдите с вашим номером телефона
3. **API development tools → Create application**
4. Получите `API_ID` и `API_HASH`

### 5. **Запуск приложения**

**Локальная разработка:**
```bash
# Терминал 1: Backend
python backend/main.py

# Терминал 2: Frontend  
streamlit run streamlit_app.py
```

**Один процесс (рекомендуется):**
```bash
python run.py
```

### 6. **Открыть интерфейс**
- **Streamlit**: http://localhost:8501
- **API документация**: http://localhost:8000/docs

---

## 📱 Использование

### 📋 **Создание кампании**
1. **🏢 Компания** → Настройте Telegram аккаунты и AI
2. **📋 Кампании** → Создать кампанию
3. Укажите чаты для мониторинга
4. Настройте ключевые слова-триггеры
5. Выберите AI провайдера и инструкции

### 📈 **Анализ чатов** (Новая функция)
1. **📈 Аналитика чатов** → Новый анализ
2. Введите название канала (`@channel` или ID)
3. Настройте параметры анализа:
   - Количество сообщений (100-10000)
   - Временной период (опционально)
   - Фильтры (медиа, ответы)
   - Ключевые слова для поиска
4. **🚀 Запустить анализ**
5. Просмотрите результаты на вкладке **📊 Результаты**

### 📊 **Мониторинг**
- **💬 Чаты** → Активные диалоги и сообщения
- **📝 Логи** → История активности бота
- **📊 Статистика** → Метрики производительности

---

## ⚙️ Конфигурация

### **AI Провайдеры**

**Claude (Anthropic):**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

**OpenAI:**
```bash
OPENAI_API_KEY=sk-proj-...
```

### **База данных**

**Разработка (SQLite):**
```bash
# Автоматически создается campaigns.db
```

**Продакшн (PostgreSQL):**
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

### **Telegram Session**

**Локальная разработка:**
- Автоматическая авторизация при первом запуске
- Сохранение в `telegram_agent.session`

**Продакшн (DigitalOcean/Heroku):**
- Использует `TELEGRAM_SESSION_STRING`
- Настраивается автоматически

---

## 🌐 Deployment

### **DigitalOcean App Platform** (Рекомендуется)

1. **Форк репозитория** на GitHub
2. **DigitalOcean** → Create App → GitHub
3. **Environment Variables:**
   ```bash
   TELEGRAM_API_ID=your_id
   TELEGRAM_API_HASH=your_hash
   TELEGRAM_PHONE=your_phone
   ANTHROPIC_API_KEY=your_claude_key
   DATABASE_URL=your_postgres_url
   ```
4. **Deploy** → Автоматический CI/CD

### **Streamlit Cloud** (Frontend)

1. **Streamlit Cloud** → New app
2. **Repository:** your-fork/telegram-claude-agent
3. **Main file:** `streamlit_app.py`
4. **Environment Variables:**
   ```bash
   BACKEND_API_URL=https://your-app.ondigitalocean.app
   ```

### **Heroku** (Альтернатива)
```bash
heroku create your-app-name
heroku config:set TELEGRAM_API_ID=your_id
heroku config:set TELEGRAM_API_HASH=your_hash
# ... другие переменные
git push heroku main
```

---

## 🔧 API Reference

### **Основные эндпоинты**

```bash
# Проверка здоровья
GET /health

# Кампании
GET /campaigns/                 # Список кампаний
POST /campaigns/               # Создать кампанию
PUT /campaigns/{id}            # Обновить кампанию
DELETE /campaigns/{id}         # Удалить кампанию

# Аналитика (NEW)
POST /analytics/analyze-channel      # Прямой анализ канала
GET /analytics/channel-info/{name}   # Информация о канале
GET /analytics/analyze/{id}/results  # Результаты анализа
GET /analytics/analyze/{id}/status   # Статус анализа

# Чаты
GET /chats/active              # Активные чаты
GET /chats/{id}/messages       # Сообщения чата
POST /chats/{id}/send          # Отправить сообщение

# Компания
GET /company/settings          # Настройки компании
PUT /company/settings          # Обновить настройки

# Логи
GET /logs/                     # Логи активности
GET /logs/stats/overview       # Общая статистика
```

### **Полная документация**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🛠️ Разработка

### **Структура проекта**
- **Модульная архитектура**: Разделение на backend/frontend
- **Унифицированный API клиент**: Централизованная работа с API
- **Автоматическое кэширование**: Оптимизация производительности
- **Валидация данных**: Pydantic модели
- **Миграции БД**: Структурированные обновления

### **Coding Standards**
- **Язык**: Комментарии и сообщения на русском языке
- **Безопасность**: API ключи только в переменных окружения
- **Логирование**: Информативные логи операций
- **Тестирование**: Покрытие критических функций

### **Добавление новых функций**
1. **Backend**: Создать API эндпоинт в `backend/api/`
2. **Frontend**: Добавить страницу в `frontend/pages/`  
3. **API Client**: Добавить методы в `api_client.py`
4. **Тестирование**: Проверить через Swagger UI
5. **Документация**: Обновить README и CLAUDE.md

---

## 📈 Changelog

### **v1.3 (2025-08-06) - Analytics & Refactoring**
- ✅ **Полный рефакторинг проекта**: Очистка ненужных файлов
- ✅ **Аналитика чатов**: Прямой анализ каналов без кампаний
- ✅ **Модульная архитектура**: Разделение компонентов
- ✅ **Исправления API**: TypeError с json параметрами
- ✅ **Безопасная инициализация**: Analytics service с проверками

### **v1.2 (2025-08-03) - Модульная архитектура**
- ✅ **Модульная архитектура frontend**: pages/, components/, utils/
- ✅ **Унифицированный API клиент**: Централизованная работа с backend
- ✅ **Backend сервисы**: Analytics service с Telethon интеграцией
- ✅ **Асинхронная обработка**: Фоновое выполнение анализа

### **v1.1 (2025-08-03)**
- ✅ API настроек компании (`/company/`)
- ✅ Улучшен контекст постов в чатах
- ✅ Оптимизирован кэш кампаний (60→10 сек)
- ✅ Индикаторы обновления

### **v1.0**
- ✅ Базовая функциональность кампаний
- ✅ Интеграция с Claude и OpenAI  
- ✅ Streamlit интерфейс
- ✅ Мониторинг чатов

---

## 🤝 Contributing

1. **Fork** репозиторий
2. **Create branch**: `git checkout -b feature/amazing-feature`
3. **Commit**: `git commit -m 'Add amazing feature'`
4. **Push**: `git push origin feature/amazing-feature`
5. **Pull Request**

---

## 📄 License

MIT License - см. [LICENSE](LICENSE) файл.

---

## 🔗 Links

- **GitHub**: [https://github.com/Timosan61/telegram-claude-agent](https://github.com/Timosan61/telegram-claude-agent)
- **Issues**: [https://github.com/Timosan61/telegram-claude-agent/issues](https://github.com/Timosan61/telegram-claude-agent/issues)
- **Telegram API**: [https://core.telegram.org/api](https://core.telegram.org/api)
- **Claude API**: [https://docs.anthropic.com/claude/reference](https://docs.anthropic.com/claude/reference)
- **OpenAI API**: [https://platform.openai.com/docs](https://platform.openai.com/docs)

---

## 📞 Support

Если у вас возникли вопросы или проблемы:
1. Проверьте [Issues](https://github.com/Timosan61/telegram-claude-agent/issues)
2. Создайте новый Issue с подробным описанием
3. Укажите версию проекта и шаги воспроизведения

**Made with ❤️ for intelligent Telegram automation**

<!-- Security scan triggered at 2025-10-08 08:49:49 -->