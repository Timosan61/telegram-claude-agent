# 🤖 CLAUDE.md - Правила проекта Telegram Claude Agent

## 📋 Описание проекта

**Telegram Claude Agent** - это ИИ-агент для автоматического мониторинга Telegram-чатов и генерации ответов с использованием Claude и OpenAI.

### Архитектура системы:
- **Backend**: FastAPI (Python) - API сервер и Telegram агент
- **Frontend**: Streamlit - веб-интерфейс управления
- **База данных**: PostgreSQL/SQLite - хранение кампаний и логов
- **AI провайдеры**: Claude (Anthropic) и OpenAI GPT

---

## 🛠️ Правила разработки

### Общие принципы:
1. **Язык**: Все комментарии, сообщения пользователю, логи - на русском языке
2. **Безопасность**: Никогда не логировать API ключи и секретные данные
3. **Производительность**: Использовать кэширование для частых операций
4. **UX**: Интерфейс должен быть понятным русскоязычному пользователю

### 🔄 Обязательный workflow после изменений:

#### После каждого изменения/исправления:
```bash
# 1. Коммит и пуш изменений
git add .
git commit -m "🐛 Исправление: описание проблемы"
git push origin main

# 2. ОБЯЗАТЕЛЬНОЕ ожидание деплоя
sleep 130  # Ждать 130 секунд для полного деплоя

# 3. АВТОМАТИЧЕСКАЯ проверка логов деплоя
# - GitHub Actions: gh run list --limit 1
# - Heroku: heroku logs --tail --app your-app-name
# - Streamlit Cloud: проверка dashboard
```

#### Структура commit сообщений:
- `🐛 Исправление:` - багфиксы
- `✨ Добавлено:` - новые функции
- `🔧 Настройка:` - конфигурация
- `📝 Документация:` - обновление docs
- `🧪 Тестирование:` - тесты и диагностика

### 🤖 Автоматическая проверка логов деплоя:

#### После 130 секунд ожидания автоматически выполнить:
```bash
# Проверка GitHub Actions
echo "🔍 Проверка статуса GitHub Actions..."
gh run list --limit 1 --json status,conclusion,createdAt

# Проверка статуса приложения (если есть health endpoint)
echo "🔍 Проверка здоровья приложения..."
curl -f https://your-app.herokuapp.com/health || echo "❌ Приложение недоступно"

# Проверка логов (если настроен Heroku)
echo "🔍 Последние логи Heroku..."
heroku logs --tail --num 20 --app your-app-name

# Альтернативно для Streamlit Cloud
echo "🔍 Проверьте Streamlit Cloud dashboard: https://share.streamlit.io/"
```

#### Критерии успешного деплоя:
- ✅ GitHub Actions status: "completed" с conclusion: "success"
- ✅ Health endpoint отвечает 200 OK
- ✅ В логах нет критических ошибок (ERROR, CRITICAL)
- ✅ Приложение доступно по URL

### Стандарты кода:
```python
# ✅ Правильно - комментарии на русском
def create_campaign(campaign_data):
    """Создание новой кампании мониторинга"""
    # Проверяем дублирование имени
    if existing_campaign_exists(campaign_data.name):
        raise HTTPException(detail="Кампания с таким именем уже существует")

# ❌ Неправильно - комментарии на английском  
def create_campaign(campaign_data):
    """Create new monitoring campaign"""
    # Check for duplicate name
```

---

## 🗄️ Структура данных

### Основные модели:

#### Campaign (Кампания)
```python
{
    "id": int,
    "name": str,                    # Название кампании
    "active": bool,                 # Статус активности
    "telegram_chats": list,         # Список ID чатов для мониторинга
    "keywords": list,               # Ключевые слова-триггеры
    "telegram_account": str,        # Аккаунт для отправки ответов
    "ai_provider": str,             # "claude" | "openai"
    "system_instruction": str,      # Системная инструкция для ИИ
    "context_messages_count": int   # Количество контекстных сообщений
}
```

#### CompanySettings (Настройки компании)  
```python
{
    "name": str,                    # Название компании
    "telegram_accounts": list,      # Настроенные Telegram аккаунты
    "ai_providers": dict,           # Настройки AI провайдеров
    "default_settings": dict        # Настройки по умолчанию
}
```

---

## 🌐 API правила

### Endpoints структура:
- `/campaigns/` - Управление кампаниями
- `/chats/` - Мониторинг чатов  
- `/logs/` - Логи активности
- `/company/` - Настройки компании
- `/analytics/` - Аналитика чатов (НОВЫЙ)

### Кэширование:
- **Campaign cache TTL**: 10 секунд (быстрый отклик на изменения)
- **Принудительное обновление**: При всех изменениях кампаний
- **API endpoint**: `POST /campaigns/refresh-cache`

### Обработка ошибок:
```python
# ✅ Правильно - сообщения на русском
raise HTTPException(
    status_code=404,
    detail="Кампания не найдена"
)

# ❌ Неправильно
raise HTTPException(
    status_code=404, 
    detail="Campaign not found"
)
```

---

## 🖥️ Frontend правила

### Streamlit архитектура (модульная):
```
frontend/
├── app.py                 # Главное приложение (навигация + main)
├── components/           # Переиспользуемые компоненты  
│   ├── api_client.py     # Унифицированный API клиент
│   ├── forms.py          # Общие формы
│   └── ui_components.py  # UI компоненты
├── pages/               # Отдельные страницы
│   ├── company.py        # 🏢 Компания
│   ├── campaigns.py      # 📋 Кампании
│   ├── chats.py         # 💬 Чаты
│   ├── statistics.py    # 📊 Статистика
│   ├── analytics.py     # 📈 Аналитика чатов (НОВАЯ)
│   ├── logs.py          # 📝 Логи
│   └── settings.py      # ⚙️ Настройки
└── utils/               # Утилиты
    ├── helpers.py        # Общие функции
    └── demo_data.py      # Демо данные
```

### Логика отображения данных:
```python
# Проверка статуса backend
server_status = check_server_status()

if server_status:
    show_real_data_page()    # Реальные данные из API
else:
    show_demo_page()         # Демо-данные (заглушки)
```

### UX принципы:
1. **Статус-индикаторы**: Всегда показывать статус подключений (🟢🔴)
2. **Уведомления**: Информировать о результатах операций
3. **Время отклика**: Показывать когда изменения применятся
4. **Автообновление**: Опция автообновления для live-мониторинга

---

## ⚙️ Конфигурация

### Обязательные переменные окружения:
```bash
# Telegram API
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890

# AI провайдеры (по выбору)
ANTHROPIC_API_KEY=sk-ant-api03-...     # Для Claude
OPENAI_API_KEY=sk-proj-...             # Для OpenAI

# Backend
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True

# Streamlit Cloud (опционально)
BACKEND_API_URL=https://your-backend.herokuapp.com
```

### База данных:
- **Разработка**: SQLite (campaigns.db)
- **Продакшн**: PostgreSQL
- **Миграции**: Ручные SQL файлы в `database/migrations/`

---

## 🧪 Тестирование и диагностика

### MCP серверы для диагностики:

#### 1. MCP Playwright - тестирование интерфейса
```bash
# Использовать для:
- E2E тестирование Streamlit интерфейса
- Проверка работы форм и кнопок
- Скриншоты состояний системы
- Автоматизация пользовательских сценариев
```

#### 2. MCP Supabase - проверка базы данных
```bash
# Использовать для:
- Диагностика подключения к БД
- Проверка целостности данных
- Мониторинг производительности запросов
- Анализ структуры таблиц
```

#### 3. Context7 - изучение документации
```bash
# Использовать при проблемах с:
- Telegram API интеграцией
- Claude/OpenAI API
- Streamlit компонентами
- FastAPI endpoints
```

### Алгоритм диагностики:
1. **Playwright** → Проверить UI и пользовательские сценарии
2. **Supabase** → Проверить состояние базы данных  
3. **Context7** → Изучить документацию при обнаружении проблем
4. **Исправить** → Применить решение
5. **Push** → Закоммитить изменения в GitHub
6. **Wait** → ОБЯЗАТЕЛЬНО ожидать 130 секунд деплоя
7. **Auto-check logs** → АВТОМАТИЧЕСКИ проверить логи деплоя

### Примеры использования MCP:

#### Проверка UI с Playwright:
```bash
# Открыть Streamlit и проверить основные функции
playwright.navigate("http://localhost:8501")
playwright.click("button[data-testid='campaigns-refresh']") 
playwright.screenshot("campaign-page.png")
```

#### Диагностика БД с Supabase:
```bash
# Проверить подключение и структуру
supabase.list_tables()
supabase.execute_sql("SELECT COUNT(*) FROM campaigns WHERE active = true")
```

#### Изучение документации с Context7:
```bash
# При проблемах с Telegram API
context7.get_library_docs("/telegram/bot-api")
# При проблемах со Streamlit
context7.get_library_docs("/streamlit/streamlit")

---

## 🚨 Troubleshooting

### Частые проблемы:

#### 1. Backend недоступен
**Симптомы**: Показываются демо-данные вместо реальных
**Решение**:
```bash
# Проверить запущен ли backend
curl http://127.0.0.1:8000/health

# Запустить backend локально
cd backend
python main.py
```

#### 2. Изменения в инструкциях не применяются
**Симптомы**: Бот отвечает по старым инструкциям
**Решение**:
- Подождать 10 секунд (автообновление кэша)
- Или нажать "🔄 Обновить кэш кампаний"

#### 3. Telegram агент не подключается
**Симптомы**: `telegram_connected: false` в /health
**Решение**:
```bash
# Проверить переменные окружения
echo $TELEGRAM_API_ID
echo $TELEGRAM_PHONE

# Проверить логи
tail -f backend/logs/telegram.log
```

### Логирование:
```python
# ✅ Правильно - информативные логи на русском
print("🔄 Кэш кампаний обновлен: 5 активных кампаний")
print("✅ Подключен к Telegram как +79001234567")
print("❌ Ошибка обработки кампании 'Новости': Connection timeout")

# ❌ Неправильно - неинформативно
print("Cache updated")
print("Connected")
print("Error")
```

---

## 🔐 Безопасность

### Правила безопасности:
1. **API ключи**: Только в переменных окружения, никогда в коде
2. **Логирование**: Никогда не логировать секретные данные
3. **CORS**: В продакшн указать конкретные домены вместо "*"
4. **Telegram**: Хранить session файлы в безопасном месте

### Пример небезопасного кода:
```python
# ❌ НИКОГДА НЕ ДЕЛАТЬ
claude_api_key = "sk-ant-api03-real-key-here"  # Захардкожен ключ
print(f"Using API key: {api_key}")             # Логирует секрет
```

### Правильный подход:
```python
# ✅ Правильно
claude_api_key = os.getenv("ANTHROPIC_API_KEY")
if not claude_api_key:
    print("❌ ANTHROPIC_API_KEY не установлен")
    
print("✅ Claude API ключ загружен")  # Не показываем сам ключ
```

---

## 📈 Мониторинг и метрики

### Ключевые метрики:
- **Активные кампании**: Количество работающих кампаний
- **Ответы за 24ч**: Количество сообщений обработанных ботом
- **Успешность**: Процент успешно отправленных ответов
- **Время обработки**: Среднее время генерации ответа

### Статусы системы:
- **🟢 Healthy**: Все компоненты работают
- **🟡 Degraded**: Частичная функциональность  
- **🔴 Down**: Критические ошибки

---

## 🚀 Deployment

### Локальная разработка:
```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd telegram-claude-agent

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить переменные
cp .env.example .env
# Отредактировать .env

# 4. Запустить компоненты
python backend/main.py          # Backend API
streamlit run streamlit_app.py  # Frontend
```

### Продакшн:
- **Backend**: Heroku, DigitalOcean, AWS
- **Frontend**: Streamlit Cloud  
- **База данных**: PostgreSQL (Heroku Postgres, DigitalOcean Managed DB)

---

## 📝 Changelog

### v1.2 (2025-08-03) - Модульная архитектура и аналитика
- ✅ **Модульная архитектура frontend**: Разделение на pages/, components/, utils/
- ✅ **Унифицированный API клиент**: Централизованная работа с backend API
- ✅ **Аналитика чатов**: Полнофункциональный анализ Telegram-чатов:
  - 🔍 Анализ сообщений за период с фильтрами
  - 👥 Статистика участников и их активности  
  - 📊 Временные паттерны активности (по часам/дням)
  - 🔤 Анализ ключевых слов, хештегов, упоминаний
  - 📎 Статистика медиафайлов
  - 💾 Экспорт данных в CSV/JSON
- ✅ **Backend сервисы**: Новый модуль /analytics/ с Telethon интеграцией
- ✅ **Асинхронная обработка**: Фоновое выполнение анализа чатов

### v1.1 (2025-08-03)
- ✅ Добавлен API настроек компании (`/company/`)
- ✅ Улучшен контекст постов в чатах (reply_info)
- ✅ Оптимизирован кэш кампаний (60→10 сек)
- ✅ Добавлены индикаторы обновления

### v1.0
- ✅ Базовая функциональность кампаний
- ✅ Интеграция с Claude и OpenAI
- ✅ Streamlit интерфейс
- ✅ Мониторинг чатов

---

## 📚 Полезные ссылки

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference)
- [OpenAI API](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

*Этот файл нужно обновлять при любых значимых изменениях в проекте* 🔄