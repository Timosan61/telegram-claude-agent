#!/bin/bash

# ✅ Скрипт проверки результатов авторизации Telegram Agent
# Выполняйте на DigitalOcean сервере ПОСЛЕ авторизации

echo "✅ Проверка результатов авторизации Telegram Agent"
echo "=================================================="

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден!"
    exit 1
fi

echo "🐳 Поиск контейнера Telegram Agent..."

# Поиск контейнера
CONTAINER_ID=$(docker ps --format "{{.ID}}" | head -1)
if [ -z "$CONTAINER_ID" ]; then
    echo "❌ Активные контейнеры не найдены"
    echo "📋 Все контейнеры:"
    docker ps -a
    exit 1
fi

echo "✅ Найден контейнер: $CONTAINER_ID"
echo ""

# Проверка статуса контейнера
echo "📊 Статус контейнера:"
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" --filter "id=$CONTAINER_ID"
echo ""

# Проверка авторизации внутри контейнера
echo "🔐 Проверка авторизации внутри контейнера..."
AUTH_CHECK=$(docker exec "$CONTAINER_ID" python check_session_status.py 2>/dev/null)

if echo "$AUTH_CHECK" | grep -q "АВТОРИЗАЦИЯ ДЕЙСТВИТЕЛЬНА"; then
    echo "✅ Telegram авторизация УСПЕШНА!"
    echo ""
    echo "📋 Детали авторизации:"
    echo "$AUTH_CHECK" | grep -E "(Телефон|Пользователь|Всего диалогов|Целевой канал)"
else
    echo "❌ Telegram авторизация НЕ РАБОТАЕТ"
    echo ""
    echo "📋 Детали ошибки:"
    echo "$AUTH_CHECK"
    echo ""
    echo "💡 Попробуйте переавторизацию:"
    echo "   docker exec -it $CONTAINER_ID bash"
    echo "   python reauth_telegram.py"
    exit 1
fi

echo ""

# Проверка API эндпоинта
echo "🌐 Проверка API эндпоинта..."

# Проверка что порт 8000 слушается
if docker exec "$CONTAINER_ID" netstat -tln 2>/dev/null | grep -q ":8000"; then
    echo "✅ Порт 8000 прослушивается внутри контейнера"
elif docker exec "$CONTAINER_ID" ss -tln 2>/dev/null | grep -q ":8000"; then
    echo "✅ Порт 8000 прослушивается внутри контейнера"
else
    echo "⚠️  Порт 8000 не найден внутри контейнера"
fi

# Проверка API health endpoint
echo "🏥 Проверка health endpoint..."
HEALTH_RESPONSE=$(docker exec "$CONTAINER_ID" curl -s http://localhost:8000/health 2>/dev/null)

if [ -n "$HEALTH_RESPONSE" ]; then
    echo "✅ API отвечает"
    
    # Проверка telegram_connected в ответе
    if echo "$HEALTH_RESPONSE" | grep -q '"telegram_connected".*true'; then
        echo "✅ Telegram подключение активно в API"
    else
        echo "⚠️  Telegram подключение не активно в API"
        echo "📋 Ответ API: $HEALTH_RESPONSE"
    fi
else
    echo "❌ API не отвечает на health endpoint"
    echo "💡 Возможно, приложение не запущено или запускается"
    
    # Проверка логов
    echo ""
    echo "📋 Последние логи контейнера:"
    docker logs "$CONTAINER_ID" --tail 10
fi

echo ""

# Проверка внешнего доступа к API
echo "🌍 Проверка внешнего доступа к API..."

# Получение внешнего IP сервера
EXTERNAL_IP=$(curl -s http://ifconfig.me 2>/dev/null || curl -s http://ipinfo.io/ip 2>/dev/null)

if [ -n "$EXTERNAL_IP" ]; then
    echo "🌐 Внешний IP сервера: $EXTERNAL_IP"
    
    # Проверка доступности API снаружи
    EXTERNAL_HEALTH=$(curl -s --max-time 10 "http://$EXTERNAL_IP:8000/health" 2>/dev/null)
    
    if [ -n "$EXTERNAL_HEALTH" ]; then
        echo "✅ API доступен снаружи"
        if echo "$EXTERNAL_HEALTH" | grep -q '"telegram_connected".*true'; then
            echo "✅ Telegram подключение работает через внешний API"
        fi
    else
        echo "⚠️  API не доступен снаружи (возможно, файрвол блокирует порт 8000)"
        echo "💡 Проверьте настройки файрвола DigitalOcean"
    fi
else
    echo "⚠️  Не удалось определить внешний IP"
fi

echo ""

# Проверка базы данных
echo "💾 Проверка базы данных..."
DB_CHECK=$(docker exec "$CONTAINER_ID" python -c "
from database.models.base import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    print('✅ База данных доступна')
    db.close()
except Exception as e:
    print(f'❌ Ошибка базы данных: {e}')
" 2>/dev/null)

echo "$DB_CHECK"

echo ""

# Проверка AI провайдеров
echo "🤖 Проверка AI провайдеров..."
AI_CHECK=$(docker exec "$CONTAINER_ID" python -c "
import os
openai_key = os.getenv('OPENAI_API_KEY')
claude_key = os.getenv('ANTHROPIC_API_KEY')

if openai_key and len(openai_key) > 20:
    print('✅ OpenAI API ключ настроен')
else:
    print('⚠️  OpenAI API ключ не настроен')

if claude_key and len(claude_key) > 20:
    print('✅ Claude API ключ настроен')
else:
    print('ℹ️  Claude API ключ не настроен (не обязательно)')
" 2>/dev/null)

echo "$AI_CHECK"

echo ""

# Итоговая проверка
echo "📊 ИТОГОВАЯ ПРОВЕРКА"
echo "===================="

# Счетчик успешных проверок
SUCCESS_COUNT=0
TOTAL_CHECKS=0

# Telegram авторизация
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if echo "$AUTH_CHECK" | grep -q "АВТОРИЗАЦИЯ ДЕЙСТВИТЕЛЬНА"; then
    echo "✅ Telegram авторизация: РАБОТАЕТ"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo "❌ Telegram авторизация: НЕ РАБОТАЕТ"
fi

# API доступность
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if [ -n "$HEALTH_RESPONSE" ]; then
    echo "✅ API доступность: РАБОТАЕТ"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo "❌ API доступность: НЕ РАБОТАЕТ"
fi

# Telegram в API
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if echo "$HEALTH_RESPONSE" | grep -q '"telegram_connected".*true'; then
    echo "✅ Telegram в API: ПОДКЛЮЧЕН"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo "❌ Telegram в API: НЕ ПОДКЛЮЧЕН"
fi

# База данных
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if echo "$DB_CHECK" | grep -q "База данных доступна"; then
    echo "✅ База данных: ДОСТУПНА"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo "❌ База данных: НЕДОСТУПНА"
fi

echo ""
echo "📈 Результат: $SUCCESS_COUNT/$TOTAL_CHECKS проверок пройдено"

if [ $SUCCESS_COUNT -eq $TOTAL_CHECKS ]; then
    echo "🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!"
    echo ""
    echo "🚀 Ваш Telegram Claude Agent полностью готов к работе!"
    echo ""
    echo "🔗 Полезные ссылки:"
    if [ -n "$EXTERNAL_IP" ]; then
        echo "   📡 API документация: http://$EXTERNAL_IP:8000/docs"
        echo "   🏥 Health check: http://$EXTERNAL_IP:8000/health"
        echo "   📋 Кампании: http://$EXTERNAL_IP:8000/campaigns/"
    fi
    echo ""
    echo "💡 Следующие шаги:"
    echo "   1. Откройте Streamlit интерфейс"
    echo "   2. Создайте новую кампанию мониторинга"
    echo "   3. Запустите мониторинг Telegram канала"
    
elif [ $SUCCESS_COUNT -ge 2 ]; then
    echo "⚠️  ЧАСТИЧНО РАБОТАЕТ - требуется доработка"
    echo ""
    echo "💡 Рекомендации по исправлению:"
    
    if ! echo "$AUTH_CHECK" | grep -q "АВТОРИЗАЦИЯ ДЕЙСТВИТЕЛЬНА"; then
        echo "   🔐 Переавторизуйтесь: docker exec -it $CONTAINER_ID python reauth_telegram.py"
    fi
    
    if [ -z "$HEALTH_RESPONSE" ]; then
        echo "   🔄 Перезапустите контейнер: docker restart $CONTAINER_ID"
    fi
    
    if ! echo "$DB_CHECK" | grep -q "База данных доступна"; then
        echo "   💾 Проверьте права доступа к файлам базы данных"
    fi
    
else
    echo "❌ КРИТИЧЕСКИЕ ОШИБКИ - система не работает"
    echo ""
    echo "🛠️  Необходимые действия:"
    echo "   1. Проверьте логи: docker logs $CONTAINER_ID"
    echo "   2. Перезапустите контейнер: docker restart $CONTAINER_ID"
    echo "   3. Повторите авторизацию: docker exec -it $CONTAINER_ID python reauth_telegram.py"
    echo "   4. Проверьте переменные окружения"
fi

echo ""
echo "📞 Для получения дополнительной помощи:"
echo "   - Проверьте логи: docker logs $CONTAINER_ID"
echo "   - Подключитесь к контейнеру: docker exec -it $CONTAINER_ID bash"
echo "   - Создайте issue в GitHub репозитории"