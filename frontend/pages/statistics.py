import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import json

from frontend.components.api_client import api_client


def show_statistics_page():
    """Расширенная страница статистики с интерактивными графиками"""
    st.header("📊 Расширенная статистика системы")
    st.markdown("Детальная аналитика работы Telegram Claude Agent с интерактивными графиками")
    
    # Проверяем доступность сервиса статистики
    stats_health = api_client.make_request("/statistics/health")
    
    if not stats_health:
        st.error("❌ Сервис статистики недоступен")
        st.info("Показываем демо-данные для демонстрации интерфейса")
        show_demo_statistics_page()
        return
    
    # Основные вкладки
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Дашборд", "📈 Тренды", "🎯 Кампании", "💬 Чаты", "⚙️ Система"
    ])
    
    with tab1:
        show_dashboard_tab()
    
    with tab2:
        show_trends_tab()
    
    with tab3:
        show_campaigns_tab()
    
    with tab4:
        show_chats_tab()
    
    with tab5:
        show_system_tab()


def show_dashboard_tab():
    """Главный дашборд с ключевыми метриками"""
    st.subheader("🎯 Общий дашборд")
    
    # Автообновление
    col1, col2 = st.columns([1, 4])
    with col1:
        auto_refresh = st.checkbox("🔄 Автообновление", key="dashboard_refresh")
    with col2:
        if st.button("📊 Обновить данные", key="dashboard_update"):
            st.rerun()
    
    # Получаем данные дашборда
    dashboard_data = api_client.make_request("/statistics/dashboard")
    
    if not dashboard_data:
        st.error("❌ Не удалось загрузить данные дашборда")
        return
    
    # Основные метрики
    st.write("### 📋 Основные метрики")
    
    campaigns = dashboard_data.get("campaigns", {})
    activity = dashboard_data.get("activity_24h", {})
    system = dashboard_data.get("system", {})
    
    # Верхний ряд метрик
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Всего кампаний", campaigns.get("total", 0))
        st.metric("Активных", campaigns.get("active", 0))
    
    with col2:
        st.metric("Сообщений за 24ч", activity.get("messages_processed", 0))
        st.metric("Ответов отправлено", activity.get("responses_sent", 0))
    
    with col3:
        success_rate = activity.get("success_rate", 0)
        st.metric("Успешность", f"{success_rate}%")
        st.metric("Активных чатов", activity.get("active_chats", 0))
    
    with col4:
        avg_time = activity.get("avg_response_time_ms", 0)
        st.metric("Среднее время ответа", f"{avg_time:.0f}мс")
        uptime = system.get("uptime_hours", 0)
        st.metric("Время работы", f"{uptime:.1f}ч")
    
    # Системные ресурсы
    st.write("### 💻 Системные ресурсы")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cpu = system.get("cpu_usage_percent", 0)
        st.metric("CPU", f"{cpu:.1f}%")
    
    with col2:
        memory = system.get("memory_usage_percent", 0)
        st.metric("Память", f"{memory:.1f}%")
    
    with col3:
        api_requests = system.get("api_requests", 0)
        st.metric("API запросов", api_requests)
    
    # График активности за 24 часа
    st.write("### 📈 Активность за 24 часа")
    
    historical_data = api_client.make_request("/statistics/historical?days_back=1")
    if historical_data:
        hourly_stats = historical_data.get("historical_data", {}).get("hourly_stats", [])
        
        if hourly_stats:
            df_hourly = pd.DataFrame(hourly_stats)
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Сообщения
            fig.add_trace(
                go.Scatter(
                    x=df_hourly['hour'],
                    y=df_hourly['messages_processed'],
                    name="Сообщений обработано",
                    line=dict(color="blue")
                ),
                secondary_y=False
            )
            
            # Ответы
            fig.add_trace(
                go.Scatter(
                    x=df_hourly['hour'],
                    y=df_hourly['responses_sent'],
                    name="Ответов отправлено",
                    line=dict(color="green")
                ),
                secondary_y=False
            )
            
            fig.update_xaxes(title_text="Час")
            fig.update_yaxes(title_text="Количество", secondary_y=False)
            fig.update_layout(
                title="Активность по часам",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Автообновление
    if auto_refresh:
        time.sleep(10)
        st.rerun()


def show_trends_tab():
    """Вкладка с трендами производительности"""
    st.subheader("📈 Тренды производительности")
    
    # Выбор метрики и периода
    col1, col2 = st.columns(2)
    
    with col1:
        metric_type = st.selectbox(
            "Метрика:",
            options=["response_time", "cpu_usage", "memory_usage", "api_calls"],
            format_func=lambda x: {
                "response_time": "Время ответа",
                "cpu_usage": "Использование CPU",
                "memory_usage": "Использование памяти",
                "api_calls": "API вызовы"
            }.get(x, x)
        )
    
    with col2:
        hours_back = st.selectbox(
            "Период:",
            options=[1, 6, 24, 72, 168],
            format_func=lambda x: f"Последние {x}ч",
            index=2
        )
    
    # Получаем тренды
    trends_data = api_client.make_request(
        f"/statistics/performance/trends?metric_type={metric_type}&hours_back={hours_back}"
    )
    
    if trends_data and trends_data.get("trends"):
        trends = trends_data["trends"]
        df_trends = pd.DataFrame(trends)
        
        if not df_trends.empty:
            # График трендов
            fig = px.line(
                df_trends,
                x='timestamp',
                y='value',
                title=f"Тренд: {trends_data['metric_type']}",
                labels={'timestamp': 'Время', 'value': f"Значение ({df_trends['unit'].iloc[0]})"}
            )
            
            fig.update_layout(
                hovermode='x unified',
                xaxis_title="Время",
                yaxis_title=f"Значение ({df_trends['unit'].iloc[0]})"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Статистика тренда
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Среднее", f"{df_trends['value'].mean():.2f}")
            with col2:
                st.metric("Максимум", f"{df_trends['value'].max():.2f}")
            with col3:
                st.metric("Минимум", f"{df_trends['value'].min():.2f}")
            with col4:
                st.metric("Точек данных", len(df_trends))
        else:
            st.info("📊 Нет данных для выбранного периода")
    else:
        st.warning("⚠️ Данные трендов недоступны")
    
    # Исторические данные
    st.write("### 📅 Исторические данные")
    
    days_back = st.slider("Период (дни):", 1, 30, 7)
    
    historical_data = api_client.make_request(f"/statistics/historical?days_back={days_back}")
    
    if historical_data:
        daily_stats = historical_data.get("historical_data", {}).get("daily_stats", [])
        
        if daily_stats:
            df_daily = pd.DataFrame(daily_stats)
            
            # График по дням
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Bar(
                    x=df_daily['date'],
                    y=df_daily['messages_processed'],
                    name="Сообщения",
                    opacity=0.7,
                    marker_color="lightblue"
                ),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df_daily['date'],
                    y=df_daily['success_rate'],
                    name="Успешность (%)",
                    line=dict(color="red", width=3)
                ),
                secondary_y=True
            )
            
            fig.update_xaxes(title_text="Дата")
            fig.update_yaxes(title_text="Количество сообщений", secondary_y=False)
            fig.update_yaxes(title_text="Успешность (%)", secondary_y=True)
            fig.update_layout(title="Динамика по дням")
            
            st.plotly_chart(fig, use_container_width=True)


def show_campaigns_tab():
    """Вкладка статистики по кампаниям"""
    st.subheader("🎯 Статистика кампаний")
    
    # Период анализа
    hours_back = st.selectbox(
        "Период анализа:",
        options=[1, 6, 24, 72, 168],
        format_func=lambda x: f"Последние {x} часов",
        index=2
    )
    
    # Получаем статистику кампаний
    campaigns_data = api_client.make_request(f"/statistics/campaigns?hours_back={hours_back}")
    
    if not campaigns_data or not campaigns_data.get("campaigns"):
        st.info("📊 Нет данных по кампаниям для выбранного периода")
        return
    
    campaigns = campaigns_data["campaigns"]
    df_campaigns = pd.DataFrame(campaigns)
    
    # Общая статистика
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Кампаний в анализе", len(campaigns))
    with col2:
        total_messages = df_campaigns['messages_processed'].sum()
        st.metric("Всего сообщений", total_messages)
    with col3:
        total_responses = df_campaigns['responses_sent'].sum()
        success_rate = (total_responses / max(1, total_messages)) * 100
        st.metric("Общая успешность", f"{success_rate:.1f}%")
    
    # Топ кампаний
    st.write("### 🏆 Топ кампаний по активности")
    
    top_campaigns = df_campaigns.nlargest(10, 'messages_processed')
    
    fig = px.bar(
        top_campaigns,
        x='campaign_name',
        y='messages_processed',
        color='success_rate',
        title="Топ-10 кампаний по количеству обработанных сообщений",
        labels={'messages_processed': 'Сообщений обработано', 'campaign_name': 'Кампания'},
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Детальная таблица
    st.write("### 📋 Детальная статистика кампаний")
    
    # Подготавливаем данные для таблицы
    display_columns = [
        'campaign_name', 'messages_processed', 'responses_sent', 
        'success_rate', 'avg_response_time_ms', 'unique_chats_active'
    ]
    
    display_df = df_campaigns[display_columns].copy()
    display_df.columns = [
        'Кампания', 'Сообщений', 'Ответов', 
        'Успешность %', 'Среднее время (мс)', 'Активных чатов'
    ]
    
    # Раскрашиваем успешность
    def color_success_rate(val):
        if val >= 80:
            return 'background-color: #d4edda'
        elif val >= 60:
            return 'background-color: #fff3cd'
        else:
            return 'background-color: #f8d7da'
    
    styled_df = display_df.style.applymap(color_success_rate, subset=['Успешность %'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Анализ ключевых слов
    if not df_campaigns.empty and 'keywords_triggered' in df_campaigns.columns:
        st.write("### 🔤 Популярные ключевые слова")
        
        all_keywords = {}
        for _, campaign in df_campaigns.iterrows():
            keywords = campaign.get('keywords_triggered', {})
            if isinstance(keywords, dict):
                for keyword, count in keywords.items():
                    all_keywords[keyword] = all_keywords.get(keyword, 0) + count
        
        if all_keywords:
            # Топ-20 ключевых слов
            top_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:20]
            
            if top_keywords:
                keywords_df = pd.DataFrame(top_keywords, columns=['Ключевое слово', 'Количество'])
                
                fig = px.bar(
                    keywords_df.head(10),
                    x='Количество',
                    y='Ключевое слово',
                    orientation='h',
                    title="Топ-10 ключевых слов",
                    labels={'Количество': 'Количество срабатываний'}
                )
                
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)


def show_chats_tab():
    """Вкладка статистики по чатам"""
    st.subheader("💬 Статистика чатов")
    
    # Период анализа
    hours_back = st.selectbox(
        "Период анализа:",
        options=[1, 6, 24, 72, 168],
        format_func=lambda x: f"Последние {x} часов",
        index=2,
        key="chats_period"
    )
    
    # Получаем статистику чатов
    chats_data = api_client.make_request(f"/statistics/chats?hours_back={hours_back}")
    
    if not chats_data or not chats_data.get("chats"):
        st.info("📊 Нет данных по чатам для выбранного периода")
        return
    
    chats = chats_data["chats"]
    df_chats = pd.DataFrame(chats)
    
    # Общая статистика
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Активных чатов", len(chats))
    with col2:
        total_messages = df_chats['messages_count'].sum()
        st.metric("Всего сообщений", total_messages)
    with col3:
        total_responses = df_chats['bot_responses_count'].sum()
        st.metric("Ответов бота", total_responses)
    with col4:
        avg_response_rate = df_chats['response_rate'].mean()
        st.metric("Средний отклик", f"{avg_response_rate:.1f}%")
    
    # Самые активные чаты
    st.write("### 🏆 Самые активные чаты")
    
    top_chats = df_chats.nlargest(10, 'messages_count')
    
    fig = px.bar(
        top_chats,
        x='chat_title',
        y='messages_count',
        color='response_rate',
        title="Топ-10 чатов по активности",
        labels={'messages_count': 'Количество сообщений', 'chat_title': 'Чат'},
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Анализ активности по времени
    st.write("### ⏰ Анализ активности по времени")
    
    # Собираем данные по часам из всех чатов
    all_hours_data = {}
    for _, chat in df_chats.iterrows():
        messages_per_hour = chat.get('messages_per_hour', {})
        if isinstance(messages_per_hour, dict):
            for hour, count in messages_per_hour.items():
                try:
                    hour_int = int(hour)
                    all_hours_data[hour_int] = all_hours_data.get(hour_int, 0) + count
                except (ValueError, TypeError):
                    continue
    
    if all_hours_data:
        hours_df = pd.DataFrame([
            {'hour': hour, 'messages': count}
            for hour, count in sorted(all_hours_data.items())
        ])
        
        fig = px.bar(
            hours_df,
            x='hour',
            y='messages',
            title="Распределение активности по часам",
            labels={'hour': 'Час', 'messages': 'Количество сообщений'}
        )
        
        fig.update_xaxes(tickmode='linear', dtick=2)
        st.plotly_chart(fig, use_container_width=True)
    
    # Детальная таблица чатов
    st.write("### 📋 Детальная статистика чатов")
    
    display_columns = [
        'chat_title', 'messages_count', 'bot_responses_count', 
        'response_rate', 'unique_users_count', 'avg_message_length'
    ]
    
    display_df = df_chats[display_columns].copy()
    display_df.columns = [
        'Чат', 'Сообщений', 'Ответов бота', 
        'Отклик %', 'Пользователей', 'Средняя длина'
    ]
    
    st.dataframe(display_df, use_container_width=True)


def show_system_tab():
    """Вкладка системной статистики"""
    st.subheader("⚙️ Системная статистика")
    
    # Получаем системную статистику
    system_data = api_client.make_request("/statistics/system")
    
    if not system_data:
        st.error("❌ Не удалось загрузить системную статистику")
        return
    
    # Основные системные метрики
    st.write("### 💻 Системные ресурсы")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        uptime = system_data.get('system_uptime_hours', 0)
        st.metric("Время работы", f"{uptime:.1f}ч")
    
    with col2:
        cpu = system_data.get('cpu_usage_percent', 0)
        st.metric("CPU", f"{cpu:.1f}%")
    
    with col3:
        memory = system_data.get('memory_usage_mb', 0)
        st.metric("Память", f"{memory:.0f}МБ")
    
    with col4:
        api_requests = system_data.get('api_requests_count', 0)
        st.metric("API запросов", api_requests)
    
    # Статистика API
    st.write("### 🌐 API статистика")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        api_errors = system_data.get('api_errors_count', 0)
        error_rate = (api_errors / max(1, api_requests)) * 100
        st.metric("Ошибки API", api_errors)
        st.metric("Частота ошибок", f"{error_rate:.1f}%")
    
    with col2:
        avg_api_time = system_data.get('avg_api_response_time_ms', 0)
        st.metric("Среднее время API", f"{avg_api_time:.1f}мс")
    
    with col3:
        telegram_calls = system_data.get('telegram_api_calls', 0)
        rate_limits = system_data.get('telegram_rate_limit_hits', 0)
        st.metric("Вызовов Telegram API", telegram_calls)
        st.metric("Rate limit", rate_limits)
    
    # Telegram статистика
    st.write("### 📱 Telegram статистика")
    
    col1, col2 = st.columns(2)
    
    with col1:
        telegram_connected = system_data.get('telegram_connected', False)
        connection_status = "🟢 Подключен" if telegram_connected else "🔴 Отключен"
        st.metric("Статус подключения", connection_status)
    
    with col2:
        telegram_uptime = system_data.get('telegram_connection_uptime_hours', 0)
        st.metric("Время подключения", f"{telegram_uptime:.1f}ч")
    
    # Метрики в реальном времени
    st.write("### ⚡ Метрики в реальном времени")
    
    if st.button("🔄 Обновить метрики реального времени"):
        realtime_data = api_client.make_request("/statistics/realtime")
        
        if realtime_data:
            rt_system = realtime_data.get('system', {})
            rt_service = realtime_data.get('service', {})
            
            # Системные метрики в реальном времени
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("CPU сейчас", f"{rt_system.get('cpu_percent', 0):.1f}%")
            with col2:
                st.metric("Память сейчас", f"{rt_system.get('memory_percent', 0):.1f}%")
            with col3:
                uptime_sec = rt_service.get('uptime_seconds', 0)
                uptime_min = uptime_sec / 60
                st.metric("Uptime", f"{uptime_min:.1f}мин")
            with col4:
                st.metric("API запросов", rt_service.get('api_requests_total', 0))
            
            # График использования памяти
            memory_used = rt_system.get('memory_used_mb', 0)
            memory_available = rt_system.get('memory_available_mb', 0)
            memory_total = memory_used + memory_available
            
            if memory_total > 0:
                fig = go.Figure(data=[
                    go.Pie(
                        labels=['Используется', 'Доступно'],
                        values=[memory_used, memory_available],
                        hole=.3,
                        title="Использование памяти"
                    )
                ])
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Управление статистикой
    st.write("### 🛠️ Управление")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Принудительный сбор статистики"):
            with st.spinner("Собираем статистику..."):
                result = api_client.make_request("/statistics/collect/all", method="POST")
                if result:
                    st.success("✅ Сбор статистики завершен!")
                    st.json(result.get("collected", {}))
    
    with col2:
        days_to_cleanup = st.number_input("Очистить старше (дни):", 7, 90, 30)
        if st.button("🗑️ Очистить старую статистику"):
            with st.spinner("Очищаем старые данные..."):
                result = api_client.make_request(
                    f"/statistics/cleanup?days_older_than={days_to_cleanup}", 
                    method="DELETE"
                )
                if result:
                    st.success("✅ Очистка завершена!")
                    st.info(f"Удалено записей: {result.get('total_deleted', 0)}")


def show_demo_statistics_page():
    """Демо-страница статистики"""
    st.header("📊 Расширенная статистика (Демо-режим)")
    st.warning("⚠️ Backend недоступен - показаны демо-данные")
    
    # Основные метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Всего кампаний", "5")
        st.metric("Активных", "3")
    
    with col2:
        st.metric("Сообщений за 24ч", "1,247")
        st.metric("Ответов отправлено", "892")
    
    with col3:
        st.metric("Успешность", "71.5%")
        st.metric("Активных чатов", "12")
    
    with col4:
        st.metric("Среднее время ответа", "1,340мс")
        st.metric("Время работы", "47.2ч")
    
    # Демо график активности
    st.write("### 📈 Активность за 24 часа (демо)")
    
    # Генерируем демо-данные
    demo_hours = list(range(24))
    demo_messages = [5, 3, 1, 0, 0, 2, 8, 15, 25, 30, 45, 50, 55, 48, 40, 35, 38, 42, 35, 28, 20, 15, 10, 7]
    demo_responses = [int(m * 0.7) for m in demo_messages]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=demo_hours, y=demo_messages, name="Сообщения", line=dict(color="blue")),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=demo_hours, y=demo_responses, name="Ответы", line=dict(color="green")),
        secondary_y=False
    )
    
    fig.update_layout(title="Демо: Активность по часам")
    st.plotly_chart(fig, use_container_width=True)
    
    # Демо топ кампаний
    st.write("### 🏆 Топ кампаний (демо)")
    
    demo_campaigns = pd.DataFrame({
        'Кампания': ['Новости', 'Техподдержка', 'Маркетинг', 'Аналитика'],
        'Сообщений': [324, 267, 189, 156],
        'Ответов': [231, 203, 142, 98],
        'Успешность %': [71.3, 76.0, 75.1, 62.8]
    })
    
    fig = px.bar(
        demo_campaigns,
        x='Кампания',
        y='Сообщений',
        color='Успешность %',
        title="Демо: Топ кампаний по активности",
        color_continuous_scale='Viridis'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Демо таблица
    st.dataframe(demo_campaigns)