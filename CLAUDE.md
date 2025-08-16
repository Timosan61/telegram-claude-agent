# 🤖 CLAUDE.md - Правила проекта Telegram Claude Agent

## 📋 Описание проекта

**Telegram Claude Agent** - это ИИ-агент для автоматического мониторинга Telegram-чатов с аналитикой и генерацией ответов через Claude и OpenAI.

**🌐 Официальный сайт**: https://answerbo1.streamlit.app/

### Архитектура системы:
- **Backend**: FastAPI (Python) - API сервер и Telegram агент
- **Frontend**: Streamlit - веб-интерфейс управления  
- **База данных**: PostgreSQL/SQLite - хранение кампаний и логов
- **AI провайдеры**: Claude (Anthropic) и OpenAI GPT
- **Аналитика**: Telethon для прямого анализа каналов *(NEW)*

### Ключевые компоненты:
- **backend/main.py**: Локальная разработка с TelegramAgent
- **backend/main_app_platform.py**: Продакшн сервер для DigitalOcean
- **backend/core/telegram_agent.py**: Локальный Telegram клиент
- **backend/core/telegram_agent_app_platform.py**: Продакшн Telegram клиент
- **backend/services/analytics_service.py**: Сервис аналитики с Telethon
- **frontend/app.py**: Главное Streamlit приложение с навигацией
- **frontend/components/api_client.py**: Унифицированный API клиент
- **frontend/pages/analytics.py**: Страница аналитики чатов
- **run.py**: Unified runner для локальной разработки
- **streamlit_app.py**: Точка входа для Streamlit Cloud

---

## 🛠️ Правила разработки

### ⚠️ ГЛАВНОЕ ПРАВИЛО:
**ВСЕГДА отвечать на русском языке** - все взаимодействия с пользователем должны быть на русском языке, включая объяснения, ошибки, диагностику.

### Общие принципы:
1. **Язык**: Все комментарии, сообщения пользователю, логи - на русском языке
2. **Безопасность**: Никогда не логировать API ключи и секретные данные
3. **Производительность**: Использовать кэширование для частых операций
4. **UX**: Интерфейс должен быть понятным русскоязычному пользователю
5. **Модульность**: Четкое разделение на backend/frontend компоненты

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
gh run list --limit 1
```

#### Структура commit сообщений:
- `🐛 Исправление:` - багфиксы
- `✨ Добавлено:` - новые функции
- `🔧 Настройка:` - конфигурация
- `📝 Документация:` - обновление docs
- `🧪 Тестирование:` - тесты и диагностика
- `🗑️ Очистка:` - удаление ненужного кода
- `♻️ Рефакторинг:` - улучшение структуры кода

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

## 🔧 Команды разработки

### Основные команды (Makefile):
```bash
make help                # Показать все доступные команды
make install            # Установить зависимости
make setup              # Настроить проект (создать .env)
make dev-setup          # Полная настройка для разработки
make run                # Запустить систему (unified runner)
make run-backend        # Запустить только backend (FastAPI)
make run-frontend       # Запустить только frontend (Streamlit)
make test               # Запустить тесты API
make check              # Проверить конфигурацию
make clean              # Очистить временные файлы
make init-db            # Инициализировать базу данных
```

### Команды Python:
```bash
# Backend разработка
python backend/main.py                    # Локальный режим
python backend/main_app_platform.py      # Продакшн режим

# Frontend разработка  
streamlit run streamlit_app.py           # Streamlit интерфейс
streamlit run frontend/app.py            # Прямой запуск

# Unified runner (рекомендуется)
python run.py                            # Backend + Frontend

# Тестирование
python tests/test_api.py                 # API тесты
python -m pytest tests/                  # Pytest runner

# База данных
python database/seed_data.py             # Инициализация данных
```

### Требования к окружению:
- **Python**: 3.11+ (backend), 3.13+ (Streamlit Cloud)
- **База данных**: SQLite (dev), PostgreSQL (prod)
- **Telegram API**: Обязательные credentials
- **AI провайдеры**: Claude или OpenAI (минимум один)

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

#### DirectChannelAnalysisRequest (Прямой анализ канала) *(NEW)*
```python
{
    "channel_name": str,            # @channel или ID или username
    "limit_messages": int,          # 100-10000 сообщений
    "start_date": datetime,         # Начало периода (опционально)
    "end_date": datetime,           # Конец периода (опционально)  
    "include_media": bool,          # Включить медиафайлы
    "include_replies": bool,        # Включить ответы
    "keywords_filter": list         # Ключевые слова для поиска
}
```

---

## 🌐 API правила

### Endpoints структура:
- `/campaigns/` - Управление кампаниями
- `/chats/` - Мониторинг чатов  
- `/logs/` - Логи активности
- `/company/` - Настройки компании
- `/analytics/` - Аналитика чатов *(NEW)*

### Новые Analytics endpoints *(NEW)*:
```bash
POST /analytics/analyze-channel       # Прямой анализ канала
GET /analytics/channel-info/{name}    # Информация о канале
GET /analytics/analyze/{id}/status    # Статус анализа
GET /analytics/analyze/{id}/results   # Результаты анализа
GET /analytics/analyze               # Список всех анализов
DELETE /analytics/analyze/{id}       # Удалить анализ
```

### Кэширование:
- **Campaign cache TTL**: 10 секунд (быстрый отклик на изменения)
- **Принудительное обновление**: При всех изменениях кампаний
- **API endpoint**: `POST /campaigns/refresh-cache`
- **Analytics результаты**: В памяти до перезапуска сервиса

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
│   ├── analytics.py      # 📈 Аналитика чатов (NEW)
│   └── statistics.py    # 📊 Статистика
└── utils/               # Утилиты
    ├── helpers.py        # Общие функции
    └── demo_data.py      # Демо данные
```

### Унифицированный API клиент *(NEW)*:
```python
# frontend/components/api_client.py
class APIClient:
    # Кампании
    def get_campaigns(self) -> Optional[list]
    def create_campaign(self, data) -> Optional[Dict]
    
    # Аналитика (NEW)
    def get_channel_info(self, channel_name) -> Optional[Dict]
    def start_channel_analysis(self, data) -> Optional[Dict]
    def get_analysis_status(self, analysis_id) -> Optional[Dict]
    def get_analysis_results(self, analysis_id) -> Optional[Dict]
    def list_analyses(self) -> Optional[Dict]
    def delete_analysis(self, analysis_id) -> Optional[Dict]
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
5. **Прогресс операций**: Индикаторы выполнения длительных операций *(NEW)*

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

### Новые переменные для Analytics *(NEW)*:
```bash
# Telegram API для аналитики (те же что и для основного бота)
TELEGRAM_API_ID=12345678           # Обязательно для analytics
TELEGRAM_API_HASH=your_api_hash    # Обязательно для analytics
TELEGRAM_PHONE=+1234567890         # Обязательно для analytics
```

### База данных:
- **Разработка**: SQLite (campaigns.db)
- **Продакшн**: PostgreSQL
- **Миграции**: Ручные SQL файлы в `database/migrations/`

---

## 🔧 Services Architecture *(NEW)*

### Analytics Service:
```python
# backend/services/analytics_service.py
class AnalyticsService:
    """Сервис для аналитики Telegram чатов с Telethon"""
    
    async def initialize() -> bool           # Инициализация Telegram клиента
    async def get_channel_info(name) -> dict # Информация о канале
    async def analyze_chat(config) -> ChatAnalytics # Полный анализ
    
    # Внутренние методы анализа
    def _analyze_messages(messages) -> dict   # Анализ сообщений
    def _analyze_participants(chat) -> dict  # Анализ участников
    def _analyze_time_patterns(messages) -> dict # Временные паттерны
    def _analyze_keywords(messages) -> dict   # Анализ слов
    def _analyze_media(messages) -> dict     # Анализ медиа
```

### Безопасная инициализация *(NEW)*:
```python
def __init__(self):
    # Безопасная инициализация с проверкой переменных окружения
    api_id_str = os.getenv("TELEGRAM_API_ID")
    self.api_id = int(api_id_str) if api_id_str else None
    
    if self.api_id and self.api_hash:
        self.client = TelegramClient("analytics_session", self.api_id, self.api_hash)
    else:
        self.client = None
        print("⚠️ Analytics Service: Telegram API credentials не настроены")
```

---

## 📈 Analytics Features *(NEW)*

### Прямой анализ каналов:
- **Независимость от кампаний**: Анализ любого канала без настройки мониторинга
- **Flexible параметры**: Период, количество сообщений, фильтры
- **Фоновая обработка**: Асинхронное выполнение через BackgroundTasks
- **Rich analytics**: Участники, временные паттерны, ключевые слова, медиа

### Поддерживаемые типы анализа:
1. **Статистика сообщений**: Общее количество, типы, средняя длина
2. **Анализ участников**: Топ авторы, боты, активность
3. **Временные паттерны**: Активность по часам, пиковые периоды  
4. **Ключевые слова**: Популярные слова, хештеги, упоминания
5. **Медиафайлы**: Типы медиа, статистика вложений
6. **Экспорт данных**: CSV/JSON для внешнего анализа

### UI для аналитики:
- **Форма анализа**: Ввод канала, настройка параметров
- **Проверка канала**: Валидация доступности перед анализом
- **Прогресс трекинг**: Отслеживание статуса выполнения
- **Результаты**: Интерактивные графики и таблицы
- **История**: Список всех выполненных анализов

---

## 🛠️ Troubleshooting

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

#### 2. Analytics Service не работает *(NEW)*
**Симптомы**: 
- `Analytics Service не инициализирован`
- `Analytics Service НЕ авторизован`
- `The key is not registered in the system`
- Запрос кода авторизации при каждом деплое

**Решение по авторизации**:
```bash
# 1. Локальная авторизация (ОДНОРАЗОВО)
cd telegram_claude_agent
export TELEGRAM_API_ID=your_api_id
export TELEGRAM_API_HASH=your_api_hash
export TELEGRAM_PHONE=your_phone

python authorize_telegram.py
# Введите код из SMS

# 2. Загрузите файл analytics_session.session на продакшн
# Для DigitalOcean App Platform - через git commit
git add analytics_session.session
git commit -m "🔐 Добавлен файл сессии Telegram"
git push

# 3. В production добавить только переменные окружения:
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash  
TELEGRAM_PHONE=your_phone

# Больше НЕ будет запросов кода авторизации!
```

#### 3. Изменения в инструкциях не применяются
**Симптомы**: Бот отвечает по старым инструкциям
**Решение**:
- Подождать 10 секунд (автообновление кэша)
- Или нажать "🔄 Обновить кэш кампаний"

#### 4. Telegram агент не подключается
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
print("✅ Analytics Service подключен к Telegram")
print("❌ Ошибка анализа канала @test: Connection timeout")

# ❌ Неправильно - неинформативно
print("Cache updated")
print("Connected")
print("Error")
```

---

## 💡 Особенности работы с проектом

### Многофайловые зависимости:
- **TelegramAgent**: Два варианта - локальный (`telegram_agent.py`) и продакшн (`telegram_agent_app_platform.py`)
- **Main файлы**: `main.py` для разработки, `main_app_platform.py` для продакшна
- **Requirements**: Разные файлы для разных окружений (Python 3.11 vs 3.13)
- **Session управление**: `analytics_session.session` для Telethon авторизации

### Стратегия разработки:
1. **Локальная разработка**: Используй `python run.py` или Makefile команды
2. **Тестирование**: API тесты требуют запущенный backend (`make test`)
3. **База данных**: SQLite создается автоматически, PostgreSQL для продакшна
4. **Telegram авторизация**: Одноразовая настройка через `authorize_telegram.py`
5. **Frontend/Backend связь**: API client автоматически переключается на demo режим

### Важные паттерны:
- **Модульная архитектура**: frontend/pages/ + components/ + utils/
- **Unified API Client**: Централизованная работа с backend
- **Кэширование**: TTL 10 секунд для campaigns, в памяти для analytics
- **Обработка ошибок**: Русские сообщения, graceful degradation
- **Async/Await**: Telethon и FastAPI полностью асинхронные

---

## 🔐 Безопасность

### Правила безопасности:
1. **API ключи**: Только в переменных окружения, никогда в коде
2. **Логирование**: Никогда не логировать секретные данные
3. **CORS**: В продакшн указать конкретные домены вместо "*"
4. **Telegram Sessions**: Безопасное хранение session файлов
5. **Analytics Data**: Не сохранять чувствительные данные из чатов *(NEW)*

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
- **Анализы за день**: Количество выполненных анализов каналов *(NEW)*
- **Analytics статус**: Доступность Telegram API для аналитики *(NEW)*

### Статусы системы:
- **🟢 Healthy**: Все компоненты работают
- **🟡 Degraded**: Частичная функциональность  
- **🔴 Down**: Критические ошибки

### Health Check endpoints:
```bash
GET /health                    # Общий статус системы
GET /analytics/health          # Статус Analytics Service (NEW)
GET /telegram/status           # Статус Telegram агента
```

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

### Продакшн DigitalOcean App Platform:

#### Environment Variables (ОБЯЗАТЕЛЬНО):
```bash
# Основные
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef123456
TELEGRAM_PHONE=+1234567890

# AI провайдеры  
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...

# База данных
DATABASE_URL=postgresql://user:pass@host:port/db
```

#### Проверка деплоя:
```bash
# 1. GitHub Actions статус
gh run list --limit 1

# 2. Health check
curl https://your-app.ondigitalocean.app/health

# 3. Analytics health  
curl https://your-app.ondigitalocean.app/analytics/health

# 4. Проверка работы Streamlit Cloud
# Наш официальный сайт: https://answerbo1.streamlit.app/
```

---

## 📝 File Structure (После рефакторинга)

### Удаленные файлы:
```
❌ test_*.py              # Устаревшие тесты
❌ debug_*.py             # Отладочные скрипты
❌ create_session_*.py    # Скрипты создания сессий
❌ fix_*.py               # Временные исправления
❌ analyze_*.py           # Устаревшие анализы
❌ *.md (кроме README)    # Дублирующая документация
❌ *.png                  # Скриншоты из тестирования
❌ *.json (temp files)    # Временные конфиги
❌ playwright_env/        # Тестовое окружение
❌ test_env/              # Тестовое окружение
❌ utils/ (root)          # Дублирующие утилиты
❌ backend/models/        # Пустая директория
```

### Актуальная структура:
```
telegram-claude-agent/
├── README.md              # ✅ Обновленная документация
├── CLAUDE.md              # ✅ Правила разработки  
├── requirements*.txt      # ✅ Зависимости
├── Dockerfile, Procfile   # ✅ Деплой файлы
├── streamlit_app.py       # ✅ Точка входа
├── backend/               # ✅ FastAPI сервер
├── frontend/              # ✅ Streamlit компоненты  
├── database/              # ✅ Модели и миграции
└── tests/                 # ✅ Актуальные тесты
```

---

## 📚 Полезные ссылки

### 🌐 Проект:
- **Официальный сайт**: [https://answerbo1.streamlit.app/](https://answerbo1.streamlit.app/)

### 📖 Документация:
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telethon Documentation](https://docs.telethon.dev/) *(NEW)*
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference)
- [OpenAI API](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)

---

## 📈 Changelog

### v1.3 (2025-08-06) - Analytics & Refactoring
- ✅ **Полный рефакторинг проекта**: Удаление 50+ ненужных файлов
- ✅ **Аналитика чатов**: Прямой анализ каналов через Telethon
  - 🔍 Анализ сообщений за период с фильтрами  
  - 👥 Статистика участников и активности
  - 📊 Временные паттерны (по часам/дням)
  - 🔤 Анализ ключевых слов, хештегов, упоминаний
  - 📎 Статистика медиафайлов  
  - 💾 Экспорт в CSV/JSON
- ✅ **Безопасная инициализация**: Analytics service с проверками credentials
- ✅ **Исправления API**: TypeError с json параметрами
- ✅ **Обновленная документация**: README.md и CLAUDE.md

### v1.2 (2025-08-03) - Модульная архитектура
- ✅ **Модульная архитектура frontend**: pages/, components/, utils/
- ✅ **Унифицированный API клиент**: Централизованная работа с backend
- ✅ **Backend сервисы**: Analytics service с Telethon интеграцией
- ✅ **Асинхронная обработка**: Фоновое выполнение анализа

### v1.1 (2025-08-03)
- ✅ API настроек компании (`/company/`)
- ✅ Улучшен контекст постов в чатах
- ✅ Оптимизирован кэш кампаний (60→10 сек)
- ✅ Индикаторы обновления

### v1.0
- ✅ Базовая функциональность кампаний
- ✅ Интеграция с Claude и OpenAI
- ✅ Streamlit интерфейс
- ✅ Мониторинг чатов

---

*Этот файл обновляется при любых значимых изменениях в проекте* 🔄