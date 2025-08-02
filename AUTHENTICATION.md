# 🔐 Руководство по авторизации Telegram Agent

Полное руководство по авторизации Telegram агента для различных платформ развертывания.

## 📋 Обзор методов авторизации

| Платформа | Метод | Сложность | Статус |
|-----------|-------|-----------|--------|
| **DigitalOcean App Platform** | Переменные окружения | 🟢 Простой | ✅ Рекомендуется |
| **Локальная разработка** | Файловая сессия | 🟡 Средний | ✅ Поддерживается |
| **VPS/Дроплет** | SSH + интерактивная авторизация | 🔴 Сложный | ⚠️ Legacy |

---

## 🎯 Метод 1: DigitalOcean App Platform (Рекомендуется)

### Преимущества
- ✅ Не требует SSH доступа
- ✅ Безопасное хранение в переменных окружения
- ✅ Автоматическое развертывание
- ✅ Подходит для продакшена

### Шаг 1: Локальное создание сессии

**На своем компьютере** выполните:

```bash
# Клонируйте репозиторий (если еще не сделано)
git clone YOUR_REPO_URL
cd telegram-claude-agent

# Установите зависимости
pip install telethon cryptg python-dotenv

# Создайте сессию
python create_session_for_app_platform.py
```

**Что происходит:**
1. Скрипт запросит номер телефона
2. Отправит код подтверждения в Telegram
3. Создаст StringSession и закодирует в base64
4. Выведет готовую переменную для App Platform

### Шаг 2: Настройка переменных окружения

В панели **DigitalOcean App Platform**:

1. Перейдите в **Settings → Environment Variables**
2. Добавьте переменную:

```env
TELEGRAM_SESSION_STRING=YOUR_GENERATED_SESSION_STRING_HERE
```

3. Дополнительно добавьте:

```env
TELEGRAM_API_ID=YOUR_API_ID
TELEGRAM_API_HASH=YOUR_API_HASH
TELEGRAM_PHONE=+YOUR_PHONE_NUMBER
```

### Шаг 3: Перезапуск приложения

```bash
# Приложение автоматически перезапустится после изменения переменных
# Проверьте логи в разделе "Runtime Logs"
```

### Проверка авторизации

```bash
curl "https://your-app-name.ondigitalocean.app/telegram/status"
```

**Ожидаемый результат:**
```json
{
  "status": "initialized",
  "details": {
    "connected": true,
    "authorized": true,
    "active_campaigns": 1
  }
}
```

---

## 💻 Метод 2: Локальная разработка

### Для локальной разработки и тестирования

```bash
# Создайте .env файл
cp .env.example .env

# Отредактируйте .env с вашими данными
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+your_phone

# Запустите интерактивную авторизацию
python authorize_telegram.py
```

**Результат**: Создается файл `telegram_agent.session` для локального использования.

---

## 🖥️ Метод 3: VPS/Дроплет (Legacy)

### Только для VPS с SSH доступом

```bash
# SSH в ваш сервер
ssh root@your_droplet_ip

# Перейдите в директорию проекта
cd /path/to/telegram-claude-agent

# Запустите интерактивную авторизацию
python3 authorize_telegram.py

# Следуйте инструкциям для ввода кода
```

**Примечание**: Этот метод не подходит для App Platform, так как там нет SSH доступа.

---

## 🔧 Troubleshooting

### Проблема: "unpack requires a buffer of 275 bytes"

**Причина**: Неправильная StringSession или повреждение данных

**Решение**:
1. Удалите старые сессии: `rm -f *.session*`
2. Пересоздайте сессию: `python create_session_for_app_platform.py`
3. Обновите переменную `TELEGRAM_SESSION_STRING`

### Проблема: "Telegram не авторизован"

**Диагностика**:
```bash
# Проверьте переменные окружения
curl "https://your-app.ondigitalocean.app/telegram/status"
```

**Решение**:
1. Убедитесь, что `TELEGRAM_SESSION_STRING` правильно установлена
2. Проверьте, что сессия была создана для того же номера телефона
3. Пересоздайте сессию, если необходимо

### Проблема: "Session file not found"

**Причина**: Попытка использовать файловую сессию на App Platform

**Решение**: Используйте метод с переменными окружения (Метод 1)

### Проблема: API credentials

**Получение API credentials**:
1. Идите на https://my.telegram.org/auth
2. Войдите с номером телефона
3. Перейдите в "API development tools"
4. Создайте новое приложение
5. Скопируйте `api_id` и `api_hash`

---

## 📊 Проверка статуса

### Веб-интерфейс
Откройте: `https://your-app.ondigitalocean.app/` и проверьте статус агента.

### API endpoint
```bash
curl "https://your-app.ondigitalocean.app/telegram/status"
```

### Логи приложения
В панели DigitalOcean App Platform → Runtime Logs:
```
✅ TelegramClient инициализован с StringSession
✅ Telegram авторизация активна
✅ Пользователь: [Имя пользователя], телефон: +[номер]
✅ Telegram Agent запущен и готов к работе!
```

---

## 🚨 Безопасность

### Рекомендации:
- ✅ Используйте переменные окружения для продакшена
- ✅ Никогда не коммитьте `.session` файлы в git
- ✅ Никогда не публикуйте `TELEGRAM_SESSION_STRING`
- ✅ Регулярно ротируйте API ключи
- ❌ Не используйте файловые сессии в продакшене

### Переменные окружения:
```env
# Обязательные
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+your_phone
TELEGRAM_SESSION_STRING=your_session_string

# Опциональные для AI
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
```

---

## 📞 Поддержка

При проблемах с авторизацией:

1. **Проверьте статус**: `curl your-app.ondigitalocean.app/telegram/status`
2. **Посмотрите логи**: DigitalOcean App Platform → Runtime Logs
3. **Пересоздайте сессию**: Используйте `create_session_for_app_platform.py`
4. **Проверьте переменные**: Убедитесь в правильности всех переменных окружения

**Готовый результат**: Рабочий Telegram агент с мониторингом комментариев на DigitalOcean App Platform 🚀