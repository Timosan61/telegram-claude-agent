# 🚀 Быстрая настройка Streamlit Cloud

## Что нужно для развертывания

### 1️⃣ Файлы готовы к GitHub
- ✅ `streamlit_app.py` - главный файл запуска
- ✅ `requirements.txt` - зависимости только для Streamlit
- ✅ `.streamlit/config.toml` - конфигурация интерфейса  
- ✅ `.streamlit/secrets.toml.example` - шаблон секретов
- ✅ `.gitignore` - исключает чувствительные данные
- ✅ `README.md` - подробная документация
- ✅ `LICENSE` - MIT лицензия

### 2️⃣ Переменные для Streamlit Secrets

Скопируйте в **Settings → Secrets** в Streamlit Cloud:

```toml
# Обязательно
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR_ACTUAL_KEY_HERE"

# Для подключения к backend (если развернете отдельно)
BACKEND_API_URL = "https://your-backend.herokuapp.com"

# Опционально (для отображения настроек в интерфейсе)
TELEGRAM_API_ID = "YOUR_API_ID"
TELEGRAM_API_HASH = "YOUR_API_HASH"
TELEGRAM_PHONE = "+YOUR_PHONE_NUMBER"
ADMIN_USERNAMES = "@yourusername"

# Zep Memory (если используете)
ZEP_API_KEY = "z_YOUR_ZEP_KEY_HERE"
ZEP_API_URL = "https://api.getzep.com"
```

### 3️⃣ Пошаговая инструкция

1. **Загрузите на GitHub:**
```bash
git init
git add .
git commit -m "Initial commit: Telegram Claude Agent"
git remote add origin https://github.com/YOUR_USERNAME/telegram-claude-agent.git
git push -u origin main
```

2. **Перейдите на [share.streamlit.io](https://share.streamlit.io)**

3. **Нажмите "New app"**

4. **Выберите настройки:**
   - Repository: `YOUR_USERNAME/telegram-claude-agent`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - App URL: `your-app-name` (будет доступно как your-app-name.streamlit.app)

5. **Добавьте секреты** (см. выше)

6. **Нажмите "Deploy!"**

### 4️⃣ Что получите

- 🌐 **Веб-интерфейс управления кампаниями**
- 📊 **Статистика и аналитика** (базовая, без backend)
- 🎯 **Демо функциональности** для презентации
- 📋 **Управление настройками** через удобный интерфейс

### 5️⃣ Ограничения облачной версии

**Без backend сервера:**
- ❌ Реальный мониторинг Telegram каналов
- ❌ Автоматические ответы агента
- ❌ Сохранение данных между сессиями

**С backend сервером:**
- ✅ Полная функциональность
- ✅ Реальная работа Telegram агента
- ✅ Постоянная база данных

## 🔧 Для полной функциональности

Развертите backend отдельно на:
- **Heroku** (простой, есть бесплатный план)
- **Railway** (современный, удобный CLI)
- **Render** (хорошие бесплатные лимиты)

Затем добавьте URL backend'а в `BACKEND_API_URL` в секретах Streamlit.

## 📞 Поддержка

Если что-то не работает:
1. Проверьте логи в Streamlit Cloud
2. Убедитесь что все секреты настроены
3. Проверьте что репозиторий публичный
4. Посмотрите файл `DEPLOYMENT.md` для подробностей