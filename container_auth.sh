#!/bin/bash

# 📱 Автоматизированная авторизация Telegram внутри Docker контейнера
# Выполняйте этот скрипт ВНУТРИ Docker контейнера после подключения

echo "📱 Telegram Agent - Авторизация в контейнере"
echo "=============================================="

# Проверка что мы в контейнере
if [ ! -f /.dockerenv ] && [ ! -f /proc/1/cgroup ] || ! grep -q docker /proc/1/cgroup 2>/dev/null; then
    echo "⚠️  Предупреждение: Возможно, вы не в Docker контейнере"
    echo "    Этот скрипт предназначен для выполнения внутри контейнера"
    echo ""
fi

# Проверка рабочей директории
echo "📂 Текущая директория: $(pwd)"
if [ ! -f "reauth_telegram.py" ]; then
    echo "⚠️  Файл reauth_telegram.py не найден в текущей директории"
    echo "    Попробуем найти и перейти в правильную директорию..."
    
    # Поиск файла
    AUTH_FILE=$(find / -name "reauth_telegram.py" 2>/dev/null | head -1)
    if [ -n "$AUTH_FILE" ]; then
        AUTH_DIR=$(dirname "$AUTH_FILE")
        echo "✅ Найден файл в: $AUTH_DIR"
        cd "$AUTH_DIR" || exit 1
    else
        echo "❌ Файл reauth_telegram.py не найден в контейнере"
        echo "💡 Проверьте что контейнер содержит код приложения"
        exit 1
    fi
fi

echo "✅ Рабочая директория: $(pwd)"
echo ""

# Проверка Python
if ! command -v python &> /dev/null; then
    if command -v python3 &> /dev/null; then
        alias python=python3
        echo "✅ Используется python3"
    else
        echo "❌ Python не найден в контейнере"
        exit 1
    fi
else
    echo "✅ Python доступен: $(python --version)"
fi

echo ""

# Проверка необходимых файлов
echo "🔍 Проверка необходимых файлов:"
REQUIRED_FILES=(
    "reauth_telegram.py"
    "check_session_status.py"
    ".env"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - НЕ НАЙДЕН"
        if [ "$file" = ".env" ]; then
            echo "💡 Создайте файл .env с переменными окружения или убедитесь что они заданы"
        fi
    fi
done

echo ""

# Проверка переменных окружения
echo "🔑 Проверка переменных окружения:"
ENV_VARS=(
    "TELEGRAM_API_ID"
    "TELEGRAM_API_HASH"
    "TELEGRAM_PHONE"
)

ALL_ENV_OK=true
for var in "${ENV_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        if [ "$var" = "TELEGRAM_API_HASH" ]; then
            echo "✅ $var: ${!var:0:8}..."
        else
            echo "✅ $var: ${!var}"
        fi
    else
        echo "❌ $var: НЕ ЗАДАНА"
        ALL_ENV_OK=false
    fi
done

if [ "$ALL_ENV_OK" = false ]; then
    echo ""
    echo "❌ Не все переменные окружения заданы!"
    echo "💡 Убедитесь что в .env файле или переменных окружения заданы:"
    echo "   TELEGRAM_API_ID=21220429"
    echo "   TELEGRAM_API_HASH=2f4d35cf..."
    echo "   TELEGRAM_PHONE=+79885517453"
    exit 1
fi

echo ""

# Проверка текущего статуса авторизации
echo "🔍 Проверка текущего статуса авторизации..."
if python check_session_status.py 2>/dev/null | grep -q "АВТОРИЗАЦИЯ ДЕЙСТВИТЕЛЬНА"; then
    echo "✅ Telegram уже авторизован!"
    echo ""
    echo "📊 Хотите проверить детали? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        python check_session_status.py
    fi
    echo ""
    echo "🔄 Хотите переавторизоваться заново? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "👋 Авторизация не требуется. Выход."
        exit 0
    fi
else
    echo "❌ Требуется авторизация"
fi

echo ""

# Проверка доступности Telegram API
echo "🌐 Проверка доступности Telegram API..."
if timeout 10 python -c "
import asyncio
from telethon import TelegramClient
import os

async def test_api():
    client = TelegramClient('test_connection', 
                          int(os.getenv('TELEGRAM_API_ID')), 
                          os.getenv('TELEGRAM_API_HASH'))
    try:
        await client.connect()
        print('✅ Telegram API доступен')
        await client.disconnect()
        return True
    except Exception as e:
        print(f'❌ Ошибка подключения к Telegram API: {e}')
        return False

result = asyncio.run(test_api())
exit(0 if result else 1)
" 2>/dev/null; then
    echo "✅ Telegram API доступен"
else
    echo "❌ Не удается подключиться к Telegram API"
    echo "💡 Проверьте интернет соединение в контейнере"
    echo "💡 Возможно, API временно недоступен"
    echo ""
    echo "🔄 Продолжить авторизацию? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🚀 Запуск авторизации Telegram Agent..."
echo "======================================="
echo ""
echo "📱 ВАЖНО: Приготовьте телефон +${TELEGRAM_PHONE} для получения SMS-кода"
echo ""
echo "🔢 После запуска вам нужно будет ввести:"
echo "   1. 5-значный код из SMS от Telegram"
echo "   2. Пароль 2FA (если настроен в Telegram)"
echo ""
echo "▶️  Нажмите Enter для начала авторизации..."
read -r

# Запуск авторизации
echo "🔐 Запуск python reauth_telegram.py..."
echo ""

if python reauth_telegram.py; then
    echo ""
    echo "🎉 Авторизация завершена!"
    echo ""
    
    # Проверка результата
    echo "✅ Проверка результата авторизации..."
    python check_session_status.py
    
    echo ""
    echo "🎯 Следующие шаги:"
    echo "   1. Выйдите из контейнера: exit"
    echo "   2. Перезапустите контейнер: docker restart CONTAINER_ID"
    echo "   3. Проверьте API: curl http://localhost:8000/health"
    echo ""
    echo "🚀 Telegram Agent готов к работе!"
    
else
    echo ""
    echo "❌ Ошибка во время авторизации"
    echo ""
    echo "💡 Возможные причины:"
    echo "   - Неверный SMS-код"
    echo "   - Проблемы с сетью"
    echo "   - Неправильные API ключи"
    echo "   - Блокировка со стороны Telegram"
    echo ""
    echo "🔄 Попробуйте:"
    echo "   1. Проверить переменные окружения"
    echo "   2. Запустить авторизацию повторно"
    echo "   3. Проверить логи: python check_session_status.py"
    
    exit 1
fi