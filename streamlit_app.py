#!/usr/bin/env python3
"""
🤖 Telegram Claude Agent - Streamlit Cloud Entry Point

Главный файл запуска для Streamlit Cloud.
Этот файл должен называться именно 'streamlit_app.py' для автоматического запуска в облаке.
Версия: v1.2 - Модульная архитектура с полной системой статистики и аналитики
Принудительное обновление: 2025-08-04 02:21 UTC

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
    import streamlit as st
    st.set_page_config(
        page_title="Telegram Claude Agent",
        page_icon="🤖",
        layout="wide"
    )
    
    from frontend.app import main
    # Запускаем главное приложение
    main()
except ImportError as e:
    import streamlit as st
    st.error(f"❌ Ошибка импорта: {e}")
    st.write("**Детали ошибки:**")
    st.code(str(e))
    st.write("**Модули в sys.path:**")
    st.write(sys.path)
except Exception as e:
    import streamlit as st
    st.error(f"❌ Ошибка запуска приложения: {e}")
    st.write("**Тип ошибки:**", type(e).__name__)
    st.write("**Детали:**", str(e))
    import traceback
    st.code(traceback.format_exc())