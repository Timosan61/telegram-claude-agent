# 🚀 Быстрый старт - Авторизация Telegram Agent

## ⚡ Шаг 1: Создайте сессию на своем компьютере

Скачайте проект и запустите на **своем компьютере**:

```bash
# Клонируйте проект
git clone [your-repo-url]
cd telegram_claude_agent

# Установите зависимости
pip install telethon cryptg python-dotenv

# Создайте сессию
python create_session_for_app_platform.py
```

**Что произойдет:**
1. Отправится SMS-код на +79885517453
2. Вы введете код
3. Создастся файл `telegram_session_for_app_platform.json`

## ⚡ Шаг 2: Автоматическое обновление App Platform

После создания сессии запустите:

```bash
python update_app_env_vars.py
```

**Этот скрипт автоматически:**
- ✅ Загрузит сессию из файла
- ✅ Обновит переменные окружения в App Platform
- ✅ Запустит автодеплой
- ✅ Проверит статус авторизации

## 🎯 Результат

После успешного выполнения:

```bash
curl https://answerbot-magph.ondigitalocean.app/health
```

Должен вернуть:
```json
{
  "status": "healthy",
  "telegram_connected": true,
  "session_type": "StringSession"
}
```

## 🔄 Альтернативный способ (ручной)

Если автоматический скрипт не работает:

1. Создайте сессию командой выше
2. Откройте файл `telegram_session_for_app_platform.json`
3. Скопируйте значение `session_string`
4. Зайдите в [DigitalOcean Dashboard](https://cloud.digitalocean.com/apps)
5. Найдите приложение "answerbot"
6. Settings → Environment Variables
7. Добавьте: `TELEGRAM_SESSION_STRING = [скопированное значение]`
8. App Platform автоматически сделает редеплой

---

**🎉 После этого ваш Telegram Claude Agent будет полностью авторизован и готов к работе!**