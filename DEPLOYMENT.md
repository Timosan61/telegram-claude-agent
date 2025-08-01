# 🚀 Руководство по развертыванию

Подробные инструкции по развертыванию Telegram Claude Agent в различных облачных сервисах.

## 🌐 Streamlit Cloud (Рекомендуется)

### Шаг 1: Подготовка репозитория

1. **Создайте GitHub репозиторий**
```bash
git init
git add .
git commit -m "Initial commit: Telegram Claude Agent"
git remote add origin https://github.com/YOUR_USERNAME/telegram-claude-agent.git
git push -u origin main
```

2. **Убедитесь что `.gitignore` настроен правильно**
   - Файл `.env` не должен попасть в git
   - Сессии Telegram не должны коммититься
   - База данных должна быть исключена

### Шаг 2: Настройка Streamlit Cloud

1. **Перейдите на [share.streamlit.io](https://share.streamlit.io)**
2. **Войдите через GitHub аккаунт**
3. **Нажмите "New app"**
4. **Выберите ваш репозиторий**
5. **Настройте параметры:**
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL**: `your-app-name` (будет доступно как your-app-name.streamlit.app)

### Шаг 3: Настройка секретов

В разделе **Settings → Secrets** добавьте:

```toml
# Обязательные секреты
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR_ACTUAL_KEY_HERE"

# Для подключения к backend серверу (если есть)
BACKEND_API_URL = "https://your-backend.herokuapp.com"

# Опциональные (для отображения в интерфейсе)
TELEGRAM_API_ID = "21220429"
TELEGRAM_API_HASH = "your_hash_here"
TELEGRAM_PHONE = "+79885517453"
ADMIN_USERNAMES = "@yourusername"

# Zep Memory (если используете)
ZEP_API_KEY = "z_your_zep_key_here"
ZEP_API_URL = "https://api.getzep.com"

# Database (для SQLite в облаке)
DATABASE_URL = "sqlite:///./campaigns.db"
```

### Шаг 4: Развертывание

1. **Нажмите "Deploy!"**
2. **Дождитесь завершения сборки** (2-5 минут)
3. **Перейдите по ссылке вашего приложения**

Ваше приложение будет доступно по адресу: `https://your-app-name.streamlit.app`

---

## 🖥️ Backend сервер

### Heroku

1. **Установите Heroku CLI**
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Подготовьте файлы**
```bash
# Создайте Procfile
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Создайте runtime.txt (опционально)
echo "python-3.11.0" > runtime.txt
```

3. **Деплой на Heroku**
```bash
heroku login
heroku create your-backend-app-name
heroku config:set ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
heroku config:set TELEGRAM_API_ID=21220429
heroku config:set TELEGRAM_API_HASH=your_hash_here
heroku config:set TELEGRAM_PHONE=+79885517453
git push heroku main
```

4. **Откройте приложение**
```bash
heroku open
```

### Railway

1. **Установите Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Деплой**
```bash
railway login
railway init
railway add --name backend
railway up
```

3. **Настройте переменные**
```bash
railway variables:set ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
railway variables:set TELEGRAM_API_ID=21220429
railway variables:set TELEGRAM_API_HASH=your_hash_here
railway variables:set TELEGRAM_PHONE=+79885517453
```

### Render

1. **Создайте аккаунт на [render.com](https://render.com)**
2. **Подключите GitHub репозиторий**
3. **Выберите "Web Service"**
4. **Настройте:**
   - **Build Command**: `pip install -r requirements-full.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. **Добавьте переменные окружения**

---

## 🔧 Локальное развертывание

### Docker (Планируется)

```dockerfile
# Dockerfile для будущих версий
FROM python:3.11-slim

WORKDIR /app
COPY requirements-full.txt .
RUN pip install -r requirements-full.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "run.py"]
```

### Системный сервис (Linux)

Создайте systemd сервис для автозапуска:

```ini
# /etc/systemd/system/telegram-claude-agent.service
[Unit]
Description=Telegram Claude Agent
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/telegram-claude-agent
Environment=PATH=/path/to/telegram-claude-agent/venv/bin
ExecStart=/path/to/telegram-claude-agent/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:
```bash
sudo systemctl enable telegram-claude-agent
sudo systemctl start telegram-claude-agent
```

---

## 🛠️ Настройка CI/CD

### GitHub Actions

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    # Streamlit Cloud деплой происходит автоматически при push в main
```

---

## 🔍 Мониторинг и логи

### Streamlit Cloud
- **Логи**: В интерфейсе Streamlit Cloud перейдите в раздел "Logs"
- **Метрики**: Встроенные метрики производительности
- **Статус**: Статус приложения отображается в панели управления

### Heroku
```bash
# Просмотр логов
heroku logs --tail --app your-backend-app-name

# Статус приложения
heroku ps --app your-backend-app-name

# Метрики
heroku addons:create papertrail --app your-backend-app-name
```

### Railway
```bash
# Логи
railway logs

# Статус
railway status
```

---

## 🚨 Решение проблем

### Общие проблемы

1. **"Module not found"**
   - Проверьте requirements.txt
   - Убедитесь что все зависимости указаны

2. **"Connection refused"**
   - Проверьте URL backend сервера
   - Убедитесь что сервер запущен

3. **"Secrets not found"**
   - Проверьте настройки секретов в Streamlit Cloud
   - Убедитесь что имена переменных совпадают

### Специфичные для платформ

**Streamlit Cloud:**
- Ограничение на размер приложения: 1GB
- Тайм-аут: 30 минут неактивности
- Лимит CPU: Средний

**Heroku:**
- Бесплатный план засыпает через 30 минут
- Ограничения базы данных на бесплатном плане
- Ephemeral filesystem (файлы не сохраняются)

**Railway:**
- Лимит $5/месяц на бесплатном плане
- Автоматическое масштабирование
- Постоянное хранилище доступно

---

## 📊 Лучшие практики

1. **Безопасность**
   - Никогда не коммитьте секреты в git
   - Используйте переменные окружения
   - Ограничьте доступ к admin функциям

2. **Производительность**
   - Кэшируйте данные в Streamlit
   - Используйте async операции в FastAPI
   - Оптимизируйте запросы к базе данных

3. **Мониторинг**
   - Настройте уведомления об ошибках
   - Следите за использованием ресурсов
   - Регулярно проверяйте логи

4. **Обновления**
   - Используйте semantic versioning
   - Тестируйте в staging окружении
   - Создавайте резервные копии данных

---

## 🆘 Получение помощи

Если возникли проблемы с развертыванием:

1. **Проверьте логи** на соответствующей платформе
2. **Убедитесь что все секреты настроены** правильно
3. **Протестируйте локально** перед развертыванием
4. **Создайте Issue** в GitHub репозитории с подробным описанием проблемы

**Полезные ссылки:**
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)