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
try:
    from frontend.app import main
    # Запускаем главное приложение
    main()
except Exception as e:
    import streamlit as st
    st.error(f"Ошибка запуска приложения: {e}")
    st.write("Проверьте логи для подробной информации")