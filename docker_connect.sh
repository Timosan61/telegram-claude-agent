#!/bin/bash

# 🐳 Автоматический поиск и подключение к Docker контейнеру Telegram Agent
# Используйте этот скрипт на DigitalOcean сервере после SSH подключения

echo "🔍 Поиск Docker контейнера Telegram Agent..."
echo "================================================"

# Проверка что Docker установлен и запущен
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден! Установите Docker и попробуйте снова."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker не запущен или нет прав доступа."
    echo "💡 Попробуйте: sudo systemctl start docker"
    echo "💡 Или добавьте пользователя в группу docker: sudo usermod -aG docker $USER"
    exit 1
fi

echo "✅ Docker доступен"
echo ""

# Поиск всех запущенных контейнеров
echo "📋 Запущенные Docker контейнеры:"
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}"
echo ""

# Автоматический поиск контейнера Telegram Agent
echo "🎯 Поиск контейнера Telegram Agent..."

# Возможные паттерны для поиска
PATTERNS=(
    "telegram"
    "agent"
    "python.*backend"
    "8000"
    "uvicorn"
    "fastapi"
)

FOUND_CONTAINERS=()

for pattern in "${PATTERNS[@]}"; do
    echo "   Поиск по паттерну: $pattern"
    while IFS= read -r container_id; do
        if [[ ! " ${FOUND_CONTAINERS[@]} " =~ " ${container_id} " ]]; then
            FOUND_CONTAINERS+=("$container_id")
        fi
    done < <(docker ps --format "{{.ID}}" --filter "name=$pattern" 2>/dev/null)
    
    while IFS= read -r container_id; do
        if [[ ! " ${FOUND_CONTAINERS[@]} " =~ " ${container_id} " ]]; then
            FOUND_CONTAINERS+=("$container_id")
        fi
    done < <(docker ps --format "{{.ID}}" | xargs -I {} docker inspect {} --format "{{.Id}} {{.Config.Cmd}}" 2>/dev/null | grep -i "$pattern" | cut -d' ' -f1 | cut -c1-12)
done

# Удаление дубликатов
UNIQUE_CONTAINERS=($(printf "%s\n" "${FOUND_CONTAINERS[@]}" | sort -u))

echo ""
echo "🔍 Найденные кандидаты:"

if [ ${#UNIQUE_CONTAINERS[@]} -eq 0 ]; then
    echo "❌ Контейнеры не найдены автоматически."
    echo ""
    echo "📋 Все запущенные контейнеры:"
    docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "💡 Выберите CONTAINER ID вручную и выполните:"
    echo "   docker exec -it YOUR_CONTAINER_ID /bin/bash"
    exit 1
fi

# Показать детали найденных контейнеров
for i in "${!UNIQUE_CONTAINERS[@]}"; do
    container_id="${UNIQUE_CONTAINERS[$i]}"
    container_info=$(docker ps --format "{{.ID}}\t{{.Image}}\t{{.Command}}\t{{.Status}}\t{{.Ports}}" --filter "id=$container_id")
    echo "   $((i+1)). $container_info"
done

echo ""

# Автоматический выбор если найден только один контейнер
if [ ${#UNIQUE_CONTAINERS[@]} -eq 1 ]; then
    SELECTED_CONTAINER="${UNIQUE_CONTAINERS[0]}"
    echo "✅ Найден один подходящий контейнер: $SELECTED_CONTAINER"
else
    # Интерактивный выбор
    echo "🔢 Выберите контейнер (введите номер 1-${#UNIQUE_CONTAINERS[@]}):"
    read -r choice
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#UNIQUE_CONTAINERS[@]} ]; then
        SELECTED_CONTAINER="${UNIQUE_CONTAINERS[$((choice-1))]}"
        echo "✅ Выбран контейнер: $SELECTED_CONTAINER"
    else
        echo "❌ Неверный выбор. Попробуйте снова."
        exit 1
    fi
fi

echo ""
echo "🚀 Подключение к контейнеру $SELECTED_CONTAINER..."
echo "================================================"

# Проверка что контейнер все еще запущен
if ! docker ps -q --filter "id=$SELECTED_CONTAINER" | grep -q .; then
    echo "❌ Контейнер $SELECTED_CONTAINER больше не запущен."
    exit 1
fi

# Попытка подключения с bash
echo "💻 Попытка подключения с bash..."
if docker exec -it "$SELECTED_CONTAINER" /bin/bash -c "echo '✅ Bash доступен'" &>/dev/null; then
    echo "🎉 Подключение к контейнеру с bash..."
    echo "📁 Вы будете в директории приложения. Используйте команды:"
    echo "   ls -la                    # просмотр файлов"
    echo "   python reauth_telegram.py # авторизация Telegram"
    echo "   exit                      # выход из контейнера"
    echo ""
    echo "🔐 Нажмите Enter для подключения..."
    read -r
    
    docker exec -it "$SELECTED_CONTAINER" /bin/bash
    
elif docker exec -it "$SELECTED_CONTAINER" /bin/sh -c "echo '✅ Sh доступен'" &>/dev/null; then
    echo "🎉 Подключение к контейнеру с sh..."
    echo "📁 Вы будете в директории приложения. Используйте команды:"
    echo "   ls -la                    # просмотр файлов"
    echo "   python reauth_telegram.py # авторизация Telegram"
    echo "   exit                      # выход из контейнера"
    echo ""
    echo "🔐 Нажмите Enter для подключения..."
    read -r
    
    docker exec -it "$SELECTED_CONTAINER" /bin/sh
    
else
    echo "❌ Не удалось подключиться к контейнеру."
    echo "💡 Попробуйте вручную:"
    echo "   docker exec -it $SELECTED_CONTAINER /bin/bash"
    echo "   docker exec -it $SELECTED_CONTAINER /bin/sh"
    exit 1
fi

echo ""
echo "👋 Вы вышли из контейнера."
echo "💡 Для повторного подключения выполните этот скрипт снова или используйте:"
echo "   docker exec -it $SELECTED_CONTAINER /bin/bash"