#!/usr/bin/env python3
"""
Скрипт запуска Telegram Claude Agent
"""
import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def check_requirements():
    """Проверка установленных зависимостей"""
    try:
        import fastapi
        import streamlit
        import telethon
        import anthropic
        import sqlalchemy
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Выполните: pip install -r requirements.txt")
        return False


def check_env_file():
    """Проверка наличия .env файла"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Файл .env не найден")
        print("Создайте .env файл на основе .env.example")
        return False
    
    # Проверка ключевых переменных
    required_vars = [
        "ANTHROPIC_API_KEY",
        "TELEGRAM_API_ID", 
        "TELEGRAM_API_HASH",
        "TELEGRAM_PHONE"
    ]
    
    missing_vars = []
    with open(env_file) as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=" in content and not content.split(f"{var}=")[1].split('\n')[0].strip():
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        return False
    
    print("✅ Конфигурация .env корректна")
    return True


def start_backend():
    """Запуск FastAPI сервера"""
    print("🚀 Запуск FastAPI сервера...")
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ]
    
    return subprocess.Popen(cmd)


def start_frontend():
    """Запуск Streamlit интерфейса"""
    print("🌐 Запуск Streamlit интерфейса...")
    
    cmd = [
        sys.executable, "-m", "streamlit",
        "run", "frontend/app.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1"
    ]
    
    return subprocess.Popen(cmd)


def wait_for_server(url, timeout=30):
    """Ожидание запуска сервера"""
    import requests
    
    for i in range(timeout):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    
    return False


def main():
    """Главная функция"""
    print("🤖 Telegram Claude Agent - Запуск системы")
    print("=" * 50)
    
    # Проверки
    if not check_requirements():
        sys.exit(1)
    
    if not check_env_file():
        sys.exit(1)
    
    # Запуск процессов
    backend_process = None
    frontend_process = None
    
    try:
        # Запуск backend
        backend_process = start_backend()
        
        # Ожидание запуска backend
        print("⏳ Ожидание запуска API сервера...")
        if not wait_for_server("http://127.0.0.1:8000/health"):
            print("❌ Не удалось запустить API сервер")
            sys.exit(1)
        
        print("✅ API сервер запущен: http://127.0.0.1:8000")
        
        # Запуск frontend
        frontend_process = start_frontend()
        
        # Ожидание запуска frontend
        print("⏳ Ожидание запуска Streamlit...")
        time.sleep(3)  # Streamlit запускается дольше
        
        print("✅ Streamlit запущен: http://127.0.0.1:8501")
        print()
        print("🎉 Система запущена успешно!")
        print("📖 Документация API: http://127.0.0.1:8000/docs")
        print("🌐 Веб-интерфейс: http://127.0.0.1:8501")
        print()
        print("Нажмите Ctrl+C для остановки...")
        
        # Ожидание сигнала завершения
        while True:
            time.sleep(1)
            
            # Проверка состояния процессов
            if backend_process.poll() is not None:
                print("❌ API сервер завершился неожиданно")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Streamlit завершился неожиданно")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
    
    finally:
        # Остановка процессов
        if backend_process:
            print("🔄 Остановка API сервера...")
            backend_process.terminate()
            backend_process.wait()
        
        if frontend_process:
            print("🔄 Остановка Streamlit...")
            frontend_process.terminate()
            frontend_process.wait()
        
        print("👋 Система остановлена")


if __name__ == "__main__":
    main()