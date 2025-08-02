# 🚀 Быстрое руководство: SSH авторизация на DigitalOcean

## 📋 Краткие инструкции для авторизации Telegram Agent

### 🎯 Ваша задача
Авторизовать Telegram агента на продакшн сервере DigitalOcean через SSH подключение к Docker контейнеру.

---

## ⚡ Быстрый старт (5 минут)

### Шаг 1: SSH подключение
```bash
ssh root@YOUR_DIGITALOCEAN_IP
```

### Шаг 2: Автоматический поиск и подключение к контейнеру
```bash
# Скачайте и запустите автоматический скрипт
wget https://raw.githubusercontent.com/YOUR_REPO/docker_connect.sh
chmod +x docker_connect.sh
./docker_connect.sh
```

### Шаг 3: Авторизация внутри контейнера
```bash
# После входа в контейнер
./container_auth.sh
# ИЛИ напрямую:
python reauth_telegram.py
```

### Шаг 4: Проверка результатов
```bash
# Выйти из контейнера
exit
# Запустить проверку
./verify_auth_results.sh
```

---

## 🔧 Ручные команды (если автоскрипты недоступны)

### На сервере DigitalOcean:
```bash
# 1. Найти контейнер
docker ps

# 2. Войти в контейнер (замените CONTAINER_ID)
docker exec -it CONTAINER_ID /bin/bash

# 3. В контейнере - авторизация
python reauth_telegram.py

# 4. Выйти и перезапустить
exit
docker restart CONTAINER_ID

# 5. Проверить результат
docker exec CONTAINER_ID python check_session_status.py
```

---

## 📱 Что понадобится

- **SSH доступ** к DigitalOcean серверу
- **Телефон** +79885517453 для получения SMS
- **2FA пароль** (если настроен в Telegram)

---

## ✅ Ожидаемый результат

После успешной авторизации:

```bash
curl http://YOUR_SERVER_IP:8000/health
```

Должен вернуть:
```json
{
  "status": "healthy",
  "telegram_connected": true,
  "ai_providers": {"openai": true},
  "database": "connected"
}
```

---

## 🆘 Если что-то не работает

1. **SSH не подключается**: Проверьте IP адрес дроплета в DigitalOcean панели
2. **Контейнер не найден**: `docker ps -a` для просмотра всех контейнеров
3. **Код не приходит**: Проверьте что телефон +79885517453 активен
4. **API не отвечает**: `docker logs CONTAINER_ID` для проверки ошибок

---

## 📚 Подробные инструкции

Полные инструкции доступны в файлах:
- `SSH_TELEGRAM_AUTH_GUIDE.md` - детальное руководство
- `docker_connect.sh` - автопоиск контейнера  
- `container_auth.sh` - автоавторизация
- `verify_auth_results.sh` - проверка результатов

---

## 🎉 Готово!

После авторизации ваш **Telegram Claude Agent** полностью готов к работе! 

🔗 **Следующие шаги:**
1. Откройте Streamlit интерфейс
2. Создайте кампанию мониторинга 
3. Запустите мониторинг канала @eslitotoeto