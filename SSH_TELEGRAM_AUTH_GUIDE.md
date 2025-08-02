# 🔐 SSH Авторизация Telegram Agent на DigitalOcean

## 📋 Полное руководство по авторизации через SSH на продакшн сервере

### 🎯 Цель
Выполнить авторизацию Telegram агента непосредственно на DigitalOcean сервере через SSH, где развернут Docker контейнер с приложением.

---

## 🚀 Шаг 1: SSH подключение к серверу

### Вариант A: Подключение по IP адресу
```bash
# Замените YOUR_SERVER_IP на фактический IP вашего дроплета
ssh root@YOUR_SERVER_IP

# Или если используете не-root пользователя:
ssh your-username@YOUR_SERVER_IP
```

### Вариант B: Подключение по SSH ключу (рекомендуется)
```bash
# Если настроен SSH ключ
ssh -i ~/.ssh/your_private_key root@YOUR_SERVER_IP
```

### 💡 Как узнать IP адрес DigitalOcean дроплета:
1. Войдите в [DigitalOcean Dashboard](https://cloud.digitalocean.com/)
2. Перейдите в раздел "Droplets"
3. Найдите ваш дроплет и скопируйте IP адрес

---

## 🐳 Шаг 2: Поиск активного Docker контейнера

После подключения к серверу выполните:

```bash
# Посмотреть все запущенные контейнеры
docker ps

# Результат будет примерно такой:
# CONTAINER ID   IMAGE              COMMAND                  CREATED        STATUS       PORTS                    NAMES
# a1b2c3d4e5f6   telegram-agent     "python -m backend.m…"   2 hours ago    Up 2 hours   0.0.0.0:8000->8000/tcp   telegram_agent_app
```

### 🔍 Найдите контейнер по признакам:
- **IMAGE**: содержит название вашего приложения
- **COMMAND**: содержит `python -m backend` или `uvicorn`
- **PORTS**: слушает порт 8000
- **STATUS**: Up (запущен)

**Скопируйте CONTAINER ID** (например: `a1b2c3d4e5f6`)

---

## 📂 Шаг 3: Вход в Docker контейнер

```bash
# Замените CONTAINER_ID на скопированный ID
docker exec -it CONTAINER_ID /bin/bash

# Альтернативно, если bash недоступен:
docker exec -it CONTAINER_ID /bin/sh
```

После успешного входа вы должны увидеть prompt внутри контейнера:
```bash
root@a1b2c3d4e5f6:/app#
```

---

## 🔧 Шаг 4: Проверка структуры приложения

```bash
# Убедитесь что вы в правильной директории
pwd
# Должно показать: /app

# Посмотрите содержимое
ls -la

# Проверьте наличие необходимых файлов
ls -la *.py | grep -E "(reauth|auth|session)"
```

Должны быть видны файлы:
- `reauth_telegram.py`
- `check_session_status.py`
- `*.session` файлы

---

## 📱 Шаг 5: Запуск авторизации Telegram

### Проверка конфигурации
```bash
# Проверьте переменные окружения
env | grep -E "(TELEGRAM|API)"

# Должны быть установлены:
# TELEGRAM_API_ID=21220429
# TELEGRAM_API_HASH=2f4d35cf...
# TELEGRAM_PHONE=+79885517453
```

### Запуск переавторизации
```bash
python reauth_telegram.py
```

**Ожидаемый вывод:**
```
🔐 ПЕРЕАВТОРИЗАЦИЯ TELEGRAM АГЕНТА
==================================================
📋 Конфигурация:
   📱 Телефон: +79885517453
   🔑 API ID: 21220429

🔗 Подключение к Telegram...
📞 Отправка кода авторизации...
📱 Код будет отправлен на: +79885517453
✅ Код отправлен!

🔢 Введите 5-значный код из Telegram:
```

### Ввод данных авторизации

1. **SMS-код**: Получите 5-значный код из Telegram на телефон +79885517453
2. **Введите код**: Наберите код и нажмите Enter
3. **2FA пароль** (если настроен): Введите пароль двухфакторной авторизации

**Успешная авторизация:**
```
🔐 Авторизация...
✅ АВТОРИЗАЦИЯ УСПЕШНА!
👤 Пользователь: [Ваше имя]
📱 Телефон: +79885517453
🆔 ID: [Ваш ID]

📁 Обновлен файл: telegram_agent.session
🎯 Агент готов к работе!
```

---

## ✅ Шаг 6: Проверка результатов

### Проверка статуса сессии
```bash
python check_session_status.py
```

**Ожидаемый успешный результат:**
```
🔍 ДИАГНОСТИКА TELEGRAM СЕССИИ
=============================================
📋 Конфигурация:
   📱 Телефон: +79885517453
   🔑 API ID: 21220429
   📁 Сессия: telegram_agent.session (28672 байт)

🔗 Подключение к Telegram...
🔐 Проверка авторизации...
✅ АВТОРИЗАЦИЯ ДЕЙСТВИТЕЛЬНА
👤 Пользователь: [Ваше имя]
📱 Телефон: +79885517453

📋 Проверка доступа к диалогам...
📊 Статус доступа:
   Всего диалогов: 10
   Целевой канал: ✅ Найден

✅ СЕССИЯ РАБОТАЕТ КОРРЕКТНО
```

### Дополнительная проверка
```bash
python test_after_reauth.py
```

---

## 🔄 Шаг 7: Перезапуск приложения

### Выход из контейнера
```bash
exit
```

### Перезапуск Docker контейнера
```bash
# Мягкий перезапуск (рекомендуется)
docker restart CONTAINER_ID

# Проверка что контейнер запустился
docker ps | grep CONTAINER_ID
```

### Проверка логов
```bash
# Посмотреть логи запуска
docker logs CONTAINER_ID --tail 20

# Следить за логами в реальном времени
docker logs -f CONTAINER_ID
```

---

## 🌐 Шаг 8: Проверка API

### Проверка статуса через API
```bash
# На сервере
curl http://localhost:8000/health

# Или с вашего компьютера (замените IP)
curl http://YOUR_SERVER_IP:8000/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "telegram_connected": true,
  "ai_providers": {
    "openai": true,
    "claude": false
  },
  "database": "connected"
}
```

---

## 🛠️ Устранение неполадок

### Проблема: "docker: command not found"
```bash
# Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Проблема: "Permission denied"
```bash
# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER
# Перелогиньтесь
```

### Проблема: "Container not found"
```bash
# Посмотрите все контейнеры (включая остановленные)
docker ps -a

# Запустите остановленный контейнер
docker start CONTAINER_ID
```

### Проблема: "Invalid phone code"
- Проверьте что вводят правильный 5-значный код
- Код действителен только несколько минут
- Запросите новый код: перезапустите `reauth_telegram.py`

### Проблема: "Session password needed"
- У вас включена двухфакторная авторизация в Telegram
- Введите пароль 2FA после ввода SMS-кода

---

## 📊 Мониторинг после авторизации

### Проверка работы агента
```bash
# Войдите в контейнер
docker exec -it CONTAINER_ID /bin/bash

# Проверьте логи
tail -f logs/telegram_agent.log

# Или проверьте через API
curl http://localhost:8000/campaigns/
```

### Проверка подключения к каналу
```bash
# В контейнере
python -c "
from backend.core.telegram_agent import TelegramAgent
import asyncio

async def test():
    agent = TelegramAgent()
    await agent.client.connect()
    if await agent.client.is_user_authorized():
        print('✅ Авторизован')
        channel = await agent.client.get_entity('@eslitotoeto')
        print(f'✅ Канал найден: {channel.title}')
    await agent.client.disconnect()

asyncio.run(test())
"
```

---

## 🎉 Успешное завершение

После выполнения всех шагов у вас должно быть:

- ✅ SSH доступ к DigitalOcean серверу
- ✅ Авторизованный Telegram агент в Docker контейнере  
- ✅ Рабочий API endpoint с `telegram_connected: true`
- ✅ Доступ к мониторингу Telegram каналов
- ✅ Готовая система для создания кампаний

**Ваш Telegram Claude Agent полностью готов к работе!** 🚀

---

## 📞 Контакты для поддержки

Если возникли проблемы:
1. Проверьте логи: `docker logs CONTAINER_ID`
2. Убедитесь в правильности API ключей
3. Проверьте доступность Telegram API
4. Создайте issue в GitHub репозитории