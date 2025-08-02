#!/usr/bin/env python3
"""
Диагностический файл для проверки проблем со Streamlit
"""

import streamlit as st

st.title("🔍 Диагностика Streamlit")
st.write("Если вы видите это сообщение, значит основное приложение Streamlit работает")

# Проверим импорты
try:
    import requests
    st.success("✅ requests импортирован успешно")
except Exception as e:
    st.error(f"❌ Ошибка импорта requests: {e}")

try:
    import pandas as pd
    st.success("✅ pandas импортирован успешно")
except Exception as e:
    st.error(f"❌ Ошибка импорта pandas: {e}")

try:
    from datetime import datetime
    st.success("✅ datetime импортирован успешно")
except Exception as e:
    st.error(f"❌ Ошибка импорта datetime: {e}")

# Проверим secrets
try:
    api_url = st.secrets.get("BACKEND_API_URL", "НЕ НАЙДЕН")
    st.info(f"BACKEND_API_URL: {api_url}")
except Exception as e:
    st.warning(f"⚠️ Не удалось получить secrets: {e}")

# Попробуем импортировать наш модуль
try:
    from frontend.app import main
    st.success("✅ frontend.app импортирован успешно")
except Exception as e:
    st.error(f"❌ Ошибка импорта frontend.app: {e}")
    st.code(str(e))