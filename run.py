#!/usr/bin/env python3
"""
Unified runner for Telegram Claude Agent
Запускает backend и frontend в одном процессе для локальной разработки
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def run_backend():
    """Запуск FastAPI backend"""
    print("🚀 Запуск Backend (FastAPI)...")
    os.chdir("backend")
    subprocess.run([sys.executable, "main.py"])

def run_frontend():
    """Запуск Streamlit frontend"""
    print("🖥️ Запуск Frontend (Streamlit)...")
    time.sleep(3)  # Ждем запуска backend
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

if __name__ == "__main__":
    print("🤖 Telegram Claude Agent - Unified Runner")
    print("=" * 50)
    
    # Проверка переменных окружения
    required_vars = ["TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_PHONE"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("📝 Создайте .env файл с необходимыми переменными")
        sys.exit(1)
    
    # Запуск в отдельных потоках
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    
    backend_thread.start()
    frontend_thread.start()
    
    print("✅ Backend запущен на http://127.0.0.1:8000")
    print("✅ Frontend запущен на http://127.0.0.1:8501")
    print("📖 API документация: http://127.0.0.1:8000/docs")
    print("\n🔄 Нажмите Ctrl+C для остановки")
    
    try:
        backend_thread.join()
        frontend_thread.join()
    except KeyboardInterrupt:
        print("\n👋 Остановка приложения...")
        sys.exit(0)