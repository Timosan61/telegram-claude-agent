#!/usr/bin/env python3
"""
🤖 Telegram Claude Agent - Streamlit Cloud Entry Point

Главный файл запуска для Streamlit Cloud.
Этот файл должен называться именно 'streamlit_app.py' для автоматического запуска в облаке.

GitHub: https://github.com/YOUR_USERNAME/telegram-claude-agent
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию в Python path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Импортируем основное приложение
from frontend.app import main

if __name__ == "__main__":
    # Запускаем главное приложение
    main()