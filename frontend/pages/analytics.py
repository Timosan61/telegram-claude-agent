import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

from components.api_client import api_client


def show_analytics_page():
    """Страница аналитики чатов"""
    st.header("📈 Аналитика чатов")
    st.markdown("Анализ сообщений, участников и активности в Telegram-чатах")
    
    # Проверяем статус сервиса аналитики
    analytics_status = api_client.make_request("/analytics/health")
    
    if not analytics_status:
        st.error("❌ Сервис аналитики недоступен")
        st.info("Убедитесь, что backend сервер запущен и сервис аналитики инициализирован")
        return
    
    # Инициализация сервиса если необходимо
    if not analytics_status.get("telegram_connected"):
        st.warning("⚠️ Сервис аналитики не подключен к Telegram")
        if st.button("🔄 Инициализировать сервис аналитики"):
            with st.spinner("Подключение к Telegram..."):
                init_response = api_client.make_request("/analytics/initialize", method="POST")
                if init_response:
                    st.success("✅ Сервис аналитики инициализирован!")
                    st.rerun()
                else:
                    st.error("❌ Ошибка инициализации сервиса аналитики")
        return
    
    # Табы для организации интерфейса
    tab1, tab2, tab3 = st.tabs(["🔍 Новый анализ", "📊 Результаты", "📋 История"])
    
    with tab1:
        show_new_analysis_form()
    
    with tab2:
        show_analysis_results()
    
    with tab3:
        show_analysis_history()


def show_new_analysis_form():
    """Форма для создания нового анализа"""
    st.subheader("🔍 Создание нового анализа")
    
    # Получаем список доступных чатов
    chats_response = api_client.make_request("/analytics/chats/available")
    available_chats = chats_response.get("chats", []) if chats_response else []
    
    if not available_chats:
        st.warning("⚠️ Доступные чаты не найдены")
        if st.button("🔄 Обновить список чатов"):
            st.rerun()
        return
    
    # Форма создания анализа
    with st.form("new_analysis_form"):
        st.write("**Выберите чат для анализа:**")
        
        # Выбор чата
        chat_options = {}
        for chat in available_chats:
            display_name = f"{chat['title']} ({chat['type']})"
            if chat.get('username'):
                display_name += f" @{chat['username']}"
            chat_options[display_name] = chat
        
        selected_chat_display = st.selectbox(
            "Чат:",
            options=list(chat_options.keys()),
            help="Выберите чат для анализа из списка доступных"
        )
        
        selected_chat = chat_options[selected_chat_display] if selected_chat_display else None
        
        if selected_chat:
            # Отображаем информацию о выбранном чате
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**ID:** `{selected_chat['id']}`")
            with col2:
                st.write(f"**Тип:** {selected_chat['type']}")
            with col3:
                if selected_chat.get('participant_count'):
                    st.write(f"**Участников:** {selected_chat['participant_count']}")
        
        st.write("---")
        
        # Параметры анализа
        st.write("**Параметры анализа:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Временной период
            use_date_filter = st.checkbox("Ограничить по времени", value=False)
            
            if use_date_filter:
                start_date = st.date_input(
                    "Дата начала:",
                    value=datetime.now().date() - timedelta(days=30),
                    help="Анализировать сообщения начиная с этой даты"
                )
                
                end_date = st.date_input(
                    "Дата окончания:",
                    value=datetime.now().date(),
                    help="Анализировать сообщения до этой даты"
                )
            else:
                start_date = None
                end_date = None
            
            # Лимит сообщений
            limit_messages = st.number_input(
                "Максимум сообщений:",
                min_value=100,
                max_value=10000,
                value=1000,
                step=100,
                help="Максимальное количество сообщений для анализа"
            )
        
        with col2:
            # Дополнительные параметры
            include_media = st.checkbox(
                "Включить медиафайлы",
                value=False,
                help="Анализировать сообщения с медиафайлами"
            )
            
            include_replies = st.checkbox(
                "Включить ответы",
                value=True,
                help="Анализировать сообщения-ответы"
            )
            
            analyze_participants = st.checkbox(
                "Анализ участников",
                value=True,
                help="Анализировать активность участников чата"
            )
        
        # Фильтр по ключевым словам
        st.write("**Фильтр по ключевым словам (опционально):**")
        keywords_text = st.text_area(
            "Ключевые слова:",
            height=80,
            help="По одному ключевому слову на строку. Будет подсчитано количество упоминаний каждого слова.",
            placeholder="новость\\nанонс\\nобновление"
        )
        
        # Кнопка запуска анализа
        submit_button = st.form_submit_button("🚀 Запустить анализ", type="primary")
        
        if submit_button and selected_chat:
            # Подготовка данных запроса
            keywords_filter = [kw.strip() for kw in keywords_text.split('\\n') if kw.strip()] if keywords_text else None
            
            analysis_request = {
                "chat_id": selected_chat["id"],
                "chat_username": selected_chat.get("username"),
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "limit_messages": limit_messages,
                "include_media": include_media,
                "include_replies": include_replies,
                "analyze_participants": analyze_participants,
                "keywords_filter": keywords_filter
            }
            
            # Запуск анализа
            with st.spinner("Запускаем анализ..."):
                response = api_client.make_request("/analytics/analyze", method="POST", data=analysis_request)
                
                if response:
                    analysis_id = response["analysis_id"]
                    st.success(f"✅ Анализ запущен! ID: `{analysis_id}`")
                    st.info("💡 Анализ выполняется в фоновом режиме. Вы можете перейти на вкладку 'Результаты' для отслеживания прогресса.")
                    
                    # Сохраняем ID для отслеживания
                    if 'analysis_ids' not in st.session_state:
                        st.session_state.analysis_ids = []
                    st.session_state.analysis_ids.append(analysis_id)
                    
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Ошибка запуска анализа")


def show_analysis_results():
    """Отображение результатов анализа"""
    st.subheader("📊 Результаты анализа")
    
    # Получаем список всех анализов
    analyses_response = api_client.make_request("/analytics/analyze")
    analyses = analyses_response.get("analyses", []) if analyses_response else []
    
    if not analyses:
        st.info("📭 Нет завершенных анализов. Создайте новый анализ на первой вкладке.")
        return
    
    # Выбор анализа для просмотра
    analysis_options = {}
    for analysis in analyses:
        display_name = f"{analysis['chat_title']} - {analysis['total_messages']} сообщений"
        if analysis['status'] == 'error':
            display_name += " ❌"
        analysis_options[display_name] = analysis['analysis_id']
    
    selected_analysis_display = st.selectbox(
        "Выберите анализ для просмотра:",
        options=list(analysis_options.keys())
    )
    
    if not selected_analysis_display:
        return
    
    analysis_id = analysis_options[selected_analysis_display]
    
    # Получаем детальные результаты
    results_response = api_client.make_request(f"/analytics/analyze/{analysis_id}/results")
    
    if not results_response:
        st.error("❌ Не удалось загрузить результаты анализа")
        return
    
    # Отображаем результаты
    display_analysis_results(analysis_id, results_response)


def display_analysis_results(analysis_id: str, results: dict):
    """Отображение детальных результатов анализа"""
    chat_info = results.get("chat_info", {})
    message_stats = results.get("message_stats", {})
    participant_stats = results.get("participant_stats", {})
    time_analysis = results.get("time_analysis", {})
    keyword_analysis = results.get("keyword_analysis", {})
    media_analysis = results.get("media_analysis", {})
    
    # Информация о чате
    st.write("### 💬 Информация о чате")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Название чата", chat_info.get("title", "N/A"))
    with col2:
        st.metric("Тип", chat_info.get("type", "N/A"))
    with col3:
        if chat_info.get("participant_count"):
            st.metric("Участников", chat_info["participant_count"])
    
    # Статистика сообщений
    st.write("### 📈 Статистика сообщений")
    
    if message_stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Всего", message_stats.get("total", 0))
        with col2:
            st.metric("Текстовые", message_stats.get("text_messages", 0))
        with col3:
            st.metric("С медиа", message_stats.get("media_messages", 0))
        with col4:
            st.metric("Ответы", message_stats.get("reply_messages", 0))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Средняя длина", f"{message_stats.get('avg_message_length', 0)} символов")
        with col2:
            st.metric("Сообщений в день", message_stats.get("messages_per_day", 0))
        with col3:
            date_range = message_stats.get("date_range", {})
            if date_range.get("days"):
                st.metric("Период анализа", f"{date_range['days']} дней")
    
    # Анализ времени
    if time_analysis and time_analysis.get("hourly_distribution"):
        st.write("### ⏰ Временные паттерны")
        
        # График активности по часам
        hourly_data = time_analysis["hourly_distribution"]
        hours = list(range(24))
        counts = [hourly_data.get(hour, 0) for hour in hours]
        
        fig_hourly = px.bar(
            x=hours,
            y=counts,
            title="Активность по часам",
            labels={"x": "Час", "y": "Количество сообщений"}
        )
        fig_hourly.update_layout(showlegend=False)
        st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Пиковые часы
        peak_hour = time_analysis.get("peak_hour", {})
        if peak_hour:
            st.info(f"🕐 **Пиковый час активности:** {peak_hour['hour']}:00 ({peak_hour['count']} сообщений)")
    
    # Анализ участников
    if participant_stats.get("analyzed") and participant_stats.get("top_participants"):
        st.write("### 👥 Топ участников")
        
        # Общая статистика
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Всего участников", participant_stats.get("total_participants", 0))
        with col2:
            st.metric("Ботов", participant_stats.get("total_bots", 0))
        
        # Таблица топ участников
        top_participants = participant_stats["top_participants"][:10]
        
        participants_data = []
        for participant in top_participants:
            info = participant.get("info", {})
            name = info.get("first_name", "Unknown")
            if info.get("last_name"):
                name += f" {info['last_name']}"
            if info.get("username"):
                name += f" (@{info['username']})"
            
            participants_data.append({
                "Участник": name,
                "Сообщений": participant["message_count"],
                "Бот": "🤖" if info.get("is_bot") else "👤"
            })
        
        if participants_data:
            df_participants = pd.DataFrame(participants_data)
            st.dataframe(df_participants, use_container_width=True)
    
    # Анализ ключевых слов
    if keyword_analysis:
        st.write("### 🔤 Анализ ключевых слов")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Топ слова
            top_words = keyword_analysis.get("top_words", [])[:15]
            if top_words:
                words_df = pd.DataFrame(top_words, columns=["Слово", "Количество"])
                
                fig_words = px.bar(
                    words_df.head(10),
                    x="Количество",
                    y="Слово",
                    orientation="h",
                    title="Топ-10 популярных слов"
                )
                fig_words.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_words, use_container_width=True)
        
        with col2:
            # Хештеги и упоминания
            hashtags = keyword_analysis.get("hashtags", {})
            mentions = keyword_analysis.get("mentions", {})
            
            st.metric("Всего слов", keyword_analysis.get("total_words", 0))
            st.metric("Уникальных слов", keyword_analysis.get("unique_words", 0))
            
            if hashtags.get("total", 0) > 0:
                st.metric("Хештегов", f"{hashtags['total']} ({hashtags['unique']} уникальных)")
            
            if mentions.get("total", 0) > 0:
                st.metric("Упоминаний", f"{mentions['total']} ({mentions['unique']} уникальных)")
        
        # Фильтр по ключевым словам (если был применен)
        filtered_keywords = keyword_analysis.get("filtered_keywords")
        if filtered_keywords:
            st.write("**Результаты фильтра по ключевым словам:**")
            for keyword, count in filtered_keywords.items():
                st.write(f"- **{keyword}**: {count} упоминаний")
    
    # Анализ медиа
    if media_analysis and media_analysis.get("total_media", 0) > 0:
        st.write("### 📎 Медиафайлы")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Всего медиа", media_analysis["total_media"])
        with col2:
            st.metric("% сообщений с медиа", f"{media_analysis.get('media_percentage', 0)}%")
        
        # Типы медиа
        media_types = media_analysis.get("media_types", {})
        if media_types:
            media_df = pd.DataFrame(list(media_types.items()), columns=["Тип", "Количество"])
            
            fig_media = px.pie(
                media_df,
                values="Количество",
                names="Тип",
                title="Распределение типов медиафайлов"
            )
            st.plotly_chart(fig_media, use_container_width=True)
    
    # Кнопки экспорта
    st.write("### 💾 Экспорт данных")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📊 Экспорт CSV", key=f"export_csv_{analysis_id}"):
            export_data("csv", analysis_id)
    
    with col2:
        if st.button("📄 Экспорт JSON", key=f"export_json_{analysis_id}"):
            export_data("json", analysis_id)
    
    with col3:
        if st.button("🗑️ Удалить анализ", key=f"delete_{analysis_id}"):
            delete_response = api_client.make_request(f"/analytics/analyze/{analysis_id}", method="DELETE")
            if delete_response:
                st.success("✅ Анализ удален")
                st.rerun()


def export_data(format_type: str, analysis_id: str):
    """Экспорт данных анализа"""
    export_request = {
        "analysis_id": analysis_id,
        "format": format_type
    }
    
    with st.spinner(f"Подготовка экспорта {format_type.upper()}..."):
        # В реальном приложении здесь была бы ссылка для скачивания
        # Пока просто показываем сообщение об успехе
        st.info(f"💡 Экспорт в формате {format_type.upper()} будет реализован в следующей версии")


def show_analysis_history():
    """История анализов"""
    st.subheader("📋 История анализов")
    
    # Получаем список всех анализов
    analyses_response = api_client.make_request("/analytics/analyze")
    analyses = analyses_response.get("analyses", []) if analyses_response else []
    
    if not analyses:
        st.info("📭 История анализов пуста")
        return
    
    # Отображаем в виде таблицы
    history_data = []
    for analysis in analyses:
        status_icon = "✅" if analysis["status"] == "completed" else "❌"
        history_data.append({
            "Статус": f"{status_icon} {analysis['status']}",
            "Чат": analysis["chat_title"],
            "Сообщений": analysis["total_messages"],
            "Участников": analysis.get("analyzed_participants", 0),
            "ID": analysis["analysis_id"][:8] + "..."
        })
    
    if history_data:
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True)
        
        # Кнопка очистки истории
        if st.button("🗑️ Очистить всю историю", type="secondary"):
            if st.session_state.get("confirm_clear_history"):
                # Удаляем все анализы
                for analysis in analyses:
                    api_client.make_request(f"/analytics/analyze/{analysis['analysis_id']}", method="DELETE")
                
                st.success("✅ История очищена")
                st.session_state.confirm_clear_history = False
                st.rerun()
            else:
                st.session_state.confirm_clear_history = True
                st.warning("⚠️ Нажмите еще раз для подтверждения очистки истории")


def show_demo_analytics_page():
    """Демо-страница аналитики"""
    st.header("📈 Аналитика чатов (Демо-режим)")
    st.warning("⚠️ Backend недоступен - показан демо-интерфейс")
    
    st.info("В этом разделе вы можете анализировать активность в Telegram-чатах, получать статистику участников и экспортировать данные")
    
    # Демо форма
    with st.expander("🔍 Пример формы анализа", expanded=True):
        st.selectbox("Чат:", ["@tech_news_channel", "@startup_chat", "@crypto_discussions"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("Дата начала:", value=datetime.now().date() - timedelta(days=30))
            st.number_input("Максимум сообщений:", value=1000)
        
        with col2:
            st.date_input("Дата окончания:", value=datetime.now().date())
            st.checkbox("Анализ участников", value=True)
        
        st.button("🚀 Запустить анализ", disabled=True)
    
    # Демо результаты
    st.write("### 📊 Пример результатов анализа")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Всего сообщений", "1,247")
    with col2:
        st.metric("Участников", "85")
    with col3:
        st.metric("Сообщений в день", "41.6")
    with col4:
        st.metric("С медиа", "23%")
    
    # Демо график
    st.write("**Активность по часам:**")
    demo_hours = list(range(24))
    demo_activity = [5, 3, 1, 0, 0, 2, 8, 15, 25, 30, 45, 50, 55, 48, 40, 35, 38, 42, 35, 28, 20, 15, 10, 7]
    
    fig = px.bar(x=demo_hours, y=demo_activity, title="Демо: Активность по часам")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)