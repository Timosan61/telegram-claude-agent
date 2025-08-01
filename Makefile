# Makefile для Telegram Claude Agent

.PHONY: help install run test clean setup check

help:  ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Установить зависимости
	pip install -r requirements.txt

setup:  ## Настроить проект (создать .env из примера)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Создан файл .env из примера"; \
		echo "⚠️  Отредактируйте .env файл с вашими API ключами"; \
	else \
		echo "ℹ️  Файл .env уже существует"; \
	fi

check:  ## Проверить конфигурацию
	@echo "🔍 Проверка конфигурации..."
	@python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ ANTHROPIC_API_KEY настроен' if os.getenv('ANTHROPIC_API_KEY') else '❌ ANTHROPIC_API_KEY отсутствует')"
	@python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ TELEGRAM_API_ID настроен' if os.getenv('TELEGRAM_API_ID') else '❌ TELEGRAM_API_ID отсутствует')"
	@python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ TELEGRAM_API_HASH настроен' if os.getenv('TELEGRAM_API_HASH') else '❌ TELEGRAM_API_HASH отсутствует')"

run:  ## Запустить систему
	python run.py

run-backend:  ## Запустить только backend
	python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

run-frontend:  ## Запустить только frontend
	streamlit run frontend/app.py --server.port 8501

test:  ## Запустить тесты
	@echo "🧪 Запуск тестов..."
	@echo "⚠️  Убедитесь, что сервер запущен на http://127.0.0.1:8000"
	python tests/test_api.py

lint:  ## Проверить код линтером
	flake8 --max-line-length=120 --ignore=E203,W503 backend/ utils/
	
format:  ## Отформатировать код
	black --line-length=120 backend/ utils/ tests/

clean:  ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -name "*.log" -delete
	rm -f *.session
	rm -f *.session-journal
	rm -f campaigns.db
	rm -f local_memory.json

init-db:  ## Инициализировать базу данных
	@echo "🗄️  Инициализация базы данных..."
	@python -c "from database.models.base import create_tables; create_tables(); print('✅ База данных инициализирована')"

dev-setup: install setup init-db  ## Полная настройка для разработки
	@echo "🚀 Проект настроен для разработки!"
	@echo "📝 Следующие шаги:"
	@echo "  1. Отредактируйте .env файл с вашими API ключами"
	@echo "  2. Запустите: make run"

prod-setup: install init-db  ## Настройка для продакшена
	@echo "🏭 Проект настроен для продакшена!"

docker-build:  ## Собрать Docker образ
	@echo "🐳 Сборка Docker образа..."
	@echo "⚠️  Docker интеграция будет добавлена в следующих версиях"

backup-db:  ## Создать резервную копию базы данных
	@if [ -f campaigns.db ]; then \
		cp campaigns.db campaigns_backup_$(shell date +%Y%m%d_%H%M%S).db; \
		echo "✅ Резервная копия создана"; \
	else \
		echo "❌ База данных не найдена"; \
	fi

stats:  ## Показать статистику проекта
	@echo "📊 Статистика проекта:"
	@echo "Строк кода Python:"
	@find . -name "*.py" -not -path "./venv/*" -not -path "./.env/*" | xargs wc -l | tail -1
	@echo "Файлов Python:"
	@find . -name "*.py" -not -path "./venv/*" -not -path "./.env/*" | wc -l
	@echo "Размер проекта:"
	@du -sh . --exclude=venv --exclude=.git

logs:  ## Показать логи системы
	@if [ -f logs/app.log ]; then \
		tail -f logs/app.log; \
	else \
		echo "📭 Файл логов не найден"; \
	fi