#!/usr/bin/env python3
"""
🤖 Telegram Claude Agent - Streamlit Cloud Entry Point

Главный файл запуска для Streamlit Cloud.
Этот файл должен называться именно 'streamlit_app.py' для автоматического запуска в облаке.
Версия: v1.2 - Модульная архитектура с полной системой статистики и аналитики
Исправление Python 3.13 совместимости: 2025-08-04 02:55 UTC - psycopg вместо psycopg2-binary

GitHub: https://github.com/YOUR_USERNAME/telegram-claude-agent
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию в Python path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Проверяем платформу развертывания и окружение
def is_streamlit_cloud():
    """Определяет, запущено ли приложение в Streamlit Cloud"""
    return (
        "STREAMLIT_CLOUD" in os.environ or 
        "streamlit.app" in os.environ.get("SERVER_NAME", "") or
        "streamlit" in os.environ.get("HOSTNAME", "").lower()
    )

# Информация об окружении для диагностики
print(f"🔍 Python версия: {sys.version}")
print(f"🔍 Streamlit Cloud: {is_streamlit_cloud()}")
print(f"🔍 Переменные окружения: {list(os.environ.keys())}")

# Импортируем основное приложение
try:
    import streamlit as st
    st.set_page_config(
        page_title="Telegram Claude Agent",
        page_icon="🤖",
        layout="wide"
    )
    
    # Показываем информацию об окружении в интерфейсе
    if is_streamlit_cloud():
        st.sidebar.info("🌐 Работает в Streamlit Cloud")
        st.sidebar.info(f"🐍 Python {sys.version.split()[0]}")
    
    from frontend.app import main
    # Запускаем главное приложение
    main()
except ImportError as e:
    import streamlit as st
    st.error(f"❌ Ошибка импорта: {e}")
    st.write("**Детали ошибки:**")
    st.code(str(e))
    st.write("**Python версия:**")
    st.code(sys.version)
    st.write("**Модули в sys.path:**")
    st.write(sys.path)
    st.write("**Streamlit Cloud:**")
    st.write(is_streamlit_cloud())
except Exception as e:
    import streamlit as st
    st.error(f"❌ Ошибка запуска приложения: {e}")
    st.write("**Тип ошибки:**", type(e).__name__)
    st.write("**Детали:**", str(e))
    st.write("**Python версия:**")
    st.code(sys.version)
    import traceback
    st.code(traceback.format_exc())