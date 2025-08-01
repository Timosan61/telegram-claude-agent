#!/usr/bin/env python3
"""
🚀 Telegram Claude Agent - Полный запуск системы

Запускает backend FastAPI сервер и frontend Streamlit приложение одновременно.
"""

import subprocess
import time
import os
import signal
import sys
from pathlib import Path

def check_dependencies():
    """Проверка установленных зависимостей"""
    try:
        import streamlit
        import fastapi
        import telethon
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Выполните: pip install -r requirements-full.txt")
        return False

def check_env_file():
    """Проверка файла конфигурации"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Файл .env не найден")
        print("Скопируйте .env.example в .env и заполните настройки:")
        print("cp .env.example .env")
        return False
    
    print("✅ Файл .env найден")
    return True

def check_database():
    """Проверка и инициализация базы данных"""
    try:
        from database.models.base import create_tables
        create_tables()
        print("✅ База данных готова")
        return True
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def start_backend():
    """Запуск backend сервера"""
    print("🚀 Запуск backend сервера...")
    
    # Проверяем, есть ли настроенные Telegram данные
    telegram_api_id = os.getenv("TELEGRAM_API_ID")
    if not telegram_api_id or telegram_api_id == "12345678":
        print("⚠️ Telegram API не настроен, запускаем в минимальном режиме")
        backend_process = subprocess.Popen([
            sys.executable, "backend/main_minimal.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        print("📱 Запускаем с полной Telegram интеграцией")
        backend_process = subprocess.Popen([
            sys.executable, "backend/main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    # Ждем запуска backend
    time.sleep(3)
    
    return backend_process

def start_frontend():
    """Запуск frontend приложения"""
    print("🎨 Запуск frontend приложения...")
    
    frontend_process = subprocess.Popen([
        "streamlit", "run", "streamlit_app.py", 
        "--server.port", "8501",
        "--server.address", "127.0.0.1"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    return frontend_process

def main():
    """Основная функция"""
    print("🤖 Telegram Claude Agent - Запуск полной системы")
    print("=" * 60)
    
    # Проверки
    if not check_dependencies():
        return 1
        
    if not check_env_file():
        return 1
        
    if not check_database():
        return 1
    
    # Запуск процессов
    backend_process = None
    frontend_process = None
    
    try:
        backend_process = start_backend()
        frontend_process = start_frontend()
        
        # Ожидание запуска
        time.sleep(5)
        
        print("\n🎉 Система запущена!")
        print("=" * 60)
        print("📊 Backend API:     http://127.0.0.1:8000")
        print("📚 API Docs:        http://127.0.0.1:8000/docs")
        print("🎨 Frontend:        http://127.0.0.1:8501")
        print("=" * 60)
        print("🔥 Система работает! Нажмите Ctrl+C для остановки")
        
        # Ожидание сигнала остановки
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал остановки...")
            
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return 1
        
    finally:
        # Остановка процессов
        print("🔄 Остановка процессов...")
        
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
            print("✅ Backend остановлен")
            
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
            print("✅ Frontend остановлен")
        
        print("👋 Система остановлена")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)