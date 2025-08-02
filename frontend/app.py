import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time

# Конфигурация страницы
st.set_page_config(
    page_title="Telegram Claude Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Конфигурация API
# Проверяем запуск в Streamlit Cloud или локально
try:
    import streamlit as st
    # В Streamlit Cloud используем переменную из secrets или дефолтный локальный URL
    API_BASE_URL = st.secrets.get("BACKEND_API_URL", "http://127.0.0.1:8000")
except:
    # Fallback для локального запуска без secrets
    API_BASE_URL = "http://127.0.0.1:8000"


def make_api_request(endpoint, method="GET", data=None):
    """Выполнение запроса к API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Ошибка API: {response.status_code} - {response.text}")
            return None
    
    except requests.exceptions.ConnectionError:
        if "127.0.0.1" in API_BASE_URL or "localhost" in API_BASE_URL:
            st.error("❌ Не удается подключиться к локальному серверу. Убедитесь, что FastAPI сервер запущен на http://127.0.0.1:8000")
        else:
            st.error(f"❌ Не удается подключиться к backend серверу: `{API_BASE_URL}`")
            st.markdown("**Возможные причины:**")
            st.markdown("- Backend сервер не запущен")
            st.markdown("- Неверный URL в настройках Streamlit Cloud")
            st.markdown("- Проблемы с сетевым подключением")
        return None
    except Exception as e:
        st.error(f"❌ Ошибка запроса: {e}")
        return None


def check_server_status():
    """Проверка статуса сервера"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        # В облачном режиме не показываем детали ошибки подключения
        return None


def main():
    """Главная функция приложения"""
    st.title("🤖 Telegram Claude Agent")
    st.markdown("Управление ИИ-агентом для мониторинга Telegram-чатов")
    
    # Информация о режиме работы
    if "127.0.0.1" not in API_BASE_URL and "localhost" not in API_BASE_URL:
        st.info(f"🌐 **Облачный режим**: Подключение к backend серверу `{API_BASE_URL}`")
        st.markdown("""
        **Примечание**: Это веб-интерфейс управления кампаниями. 
        Для полной функциональности Telegram-агента необходим отдельный backend сервер.
        """)
    else:
        st.success(f"🏠 **Локальный режим**: Backend сервер `{API_BASE_URL}`")
    
    # Проверка статуса сервера
    server_status = check_server_status()
    
    if server_status:
        col1, col2, col3 = st.columns(3)
        with col1:
            status_color = "🟢" if server_status.get("status") == "healthy" else "🔴"
            st.metric("Статус сервера", f"{status_color} {server_status.get('status', 'unknown')}")
        
        with col2:
            telegram_status = "🟢 Подключен" if server_status.get("telegram_connected") else "🔴 Отключен"
            st.metric("Telegram", telegram_status)
        
        with col3:
            db_status = "🟢 Подключена" if server_status.get("database") == "connected" else "🔴 Отключена"
            st.metric("База данных", db_status)
    else:
        st.warning("⚠️ Backend сервер недоступен")
        st.info("В демо-режиме интерфейс доступен для просмотра, но функциональность ограничена")
    
    # Боковая панель навигации
    st.sidebar.title("Навигация")
    page = st.sidebar.selectbox(
        "Выберите страницу",
        ["📋 Кампании", "💬 Чаты", "📊 Статистика", "📝 Логи активности", "⚙️ Настройки"]
    )
    
    # Отображение выбранной страницы
    if page == "📋 Кампании":
        if server_status:
            show_campaigns_page()
        else:
            show_demo_campaigns_page()
    elif page == "💬 Чаты":
        if server_status:
            show_chats_page()
        else:
            show_demo_chats_page()
    elif page == "📊 Статистика":
        if server_status:
            show_statistics_page()
        else:
            show_demo_statistics_page()
    elif page == "📝 Логи активности":
        if server_status:
            show_logs_page()
        else:
            show_demo_logs_page()
    elif page == "⚙️ Настройки":
        show_settings_page()


def show_campaigns_page():
    """Страница управления кампаниями"""
    st.header("📋 Управление кампаниями")
    
    # Получение списка кампаний
    campaigns_data = make_api_request("/campaigns/")
    
    if campaigns_data is None:
        return
    
    # Кнопка создания новой кампании
    if st.button("➕ Создать новую кампанию", type="primary"):
        st.session_state.show_create_form = True
    
    # Форма создания кампании
    if st.session_state.get('show_create_form', False):
        show_campaign_form()
    
    # Отображение существующих кампаний
    if campaigns_data:
        st.subheader(f"Активные кампании ({len(campaigns_data)})")
        
        for campaign in campaigns_data:
            with st.expander(f"🎯 {campaign['name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**ID:** {campaign['id']}")
                    st.write(f"**Аккаунт Telegram:** {campaign['telegram_account']}")
                    
                    # Показываем информацию об AI провайдере
                    ai_provider = campaign.get('ai_provider', 'claude')
                    if ai_provider == 'claude':
                        st.write(f"**AI провайдер:** 🧠 Claude ({campaign.get('claude_agent_id', 'N/A')})")
                    else:
                        st.write(f"**AI провайдер:** 🤖 OpenAI ({campaign.get('openai_model', 'gpt-4')})")
                    
                    st.write(f"**Чаты:** {', '.join(campaign['telegram_chats'])}")
                    st.write(f"**Ключевые слова:** {', '.join(campaign['keywords'])}")
                    st.write(f"**Контекст сообщений:** {campaign['context_messages_count']}")
                    
                    # Системная инструкция
                    with st.expander("Системная инструкция"):
                        st.text_area(
                            "Инструкция:",
                            value=campaign['system_instruction'],
                            height=100,
                            disabled=True,
                            key=f"instruction_{campaign['id']}"
                        )
                
                with col2:
                    # Статус активности
                    status_color = "🟢" if campaign['active'] else "🔴"
                    status_text = "Активна" if campaign['active'] else "Неактивна"
                    st.write(f"**Статус:** {status_color} {status_text}")
                    
                    # Кнопки управления
                    if st.button(
                        "🔄 Переключить статус",
                        key=f"toggle_{campaign['id']}"
                    ):
                        toggle_campaign_status(campaign['id'])
                        st.rerun()
                    
                    if st.button(
                        "✏️ Редактировать",
                        key=f"edit_{campaign['id']}"
                    ):
                        st.session_state.edit_campaign_id = campaign['id']
                        st.session_state.show_edit_form = True
                        st.rerun()
                    
                    if st.button(
                        "🗑️ Удалить",
                        key=f"delete_{campaign['id']}",
                        type="secondary"
                    ):
                        if st.session_state.get(f'confirm_delete_{campaign["id"]}', False):
                            delete_campaign(campaign['id'])
                            st.rerun()
                        else:
                            st.session_state[f'confirm_delete_{campaign["id"]}'] = True
                            st.warning("Нажмите еще раз для подтверждения удаления")
    else:
        st.info("📝 Нет созданных кампаний. Создайте первую кампанию для начала работы.")
    
    # Форма редактирования
    if st.session_state.get('show_edit_form', False):
        edit_campaign_id = st.session_state.get('edit_campaign_id')
        if edit_campaign_id:
            campaign_data = next(
                (c for c in campaigns_data if c['id'] == edit_campaign_id), 
                None
            )
            if campaign_data:
                show_campaign_form(edit_data=campaign_data)


def show_campaign_form(edit_data=None):
    """Форма создания/редактирования кампании"""
    is_edit = edit_data is not None
    form_title = "✏️ Редактирование кампании" if is_edit else "➕ Создание новой кампании"
    
    st.subheader(form_title)
    
    with st.form(key="campaign_form"):
        # Основные поля
        name = st.text_input(
            "Название кампании*",
            value=edit_data.get('name', '') if is_edit else '',
            help="Уникальное название для идентификации кампании"
        )
        
        # Telegram настройки
        st.subheader("🔵 Настройки Telegram")
        
        telegram_account = st.text_input(
            "Аккаунт Telegram*",
            value=edit_data.get('telegram_account', '') if is_edit else '',
            help="Имя или ID аккаунта, с которого будут отправляться ответы"
        )
        
        telegram_chats_text = st.text_area(
            "Отслеживаемые чаты*",
            value='\\n'.join(edit_data.get('telegram_chats', [])) if is_edit else '',
            help="По одному ID или username чата на строку (например: @mychat или -1001234567890)"
        )
        
        keywords_text = st.text_area(
            "Ключевые слова*",
            value='\\n'.join(edit_data.get('keywords', [])) if is_edit else '',
            help="По одному ключевому слову на строку"
        )
        
        # AI провайдер настройки
        st.subheader("🧠 Настройки AI провайдера")
        
        # Выбор AI провайдера
        ai_provider = st.selectbox(
            "AI провайдер*",
            options=["claude", "openai"],
            index=0 if not is_edit or edit_data.get('ai_provider', 'claude') == 'claude' else 1,
            help="Выберите AI модель для генерации ответов"
        )
        
        # Настройки Claude (показываем только если выбран Claude)
        if ai_provider == "claude":
            claude_agent_id = st.text_input(
                "ID Claude агента*",
                value=edit_data.get('claude_agent_id', '') if is_edit else '',
                help="Идентификатор или alias Claude Code агента"
            )
        else:
            claude_agent_id = None
        
        # Настройки OpenAI (показываем только если выбран OpenAI)
        if ai_provider == "openai":
            openai_model = st.selectbox(
                "Модель OpenAI*",
                options=["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo-preview"],
                index=0 if not is_edit else ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo-preview"].index(edit_data.get('openai_model', 'gpt-4')),
                help="Выберите модель OpenAI для генерации ответов"
            )
        else:
            openai_model = "gpt-4"
        
        context_messages_count = st.number_input(
            "Количество контекстных сообщений",
            min_value=1,
            max_value=20,
            value=edit_data.get('context_messages_count', 3) if is_edit else 3,
            help="Сколько предыдущих сообщений анализировать для контекста"
        )
        
        system_instruction = st.text_area(
            "Системная инструкция*",
            value=edit_data.get('system_instruction', '') if is_edit else '',
            height=150,
            help="Подробная инструкция о том, как должен себя вести агент"
        )
        
        # Примеры ответов
        st.subheader("💬 Примеры ответов")
        example_replies_text = st.text_area(
            "Примеры ответов (JSON)",
            value=json.dumps(edit_data.get('example_replies', {}), ensure_ascii=False, indent=2) if is_edit and edit_data.get('example_replies') else '{}',
            height=100,
            help="JSON объект с примерами ответов по ключевым словам"
        )
        
        # Статус активности
        active = st.checkbox(
            "Активировать кампанию сразу",
            value=edit_data.get('active', False) if is_edit else False
        )
        
        # Кнопки
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            submit_button = st.form_submit_button(
                "💾 Сохранить" if is_edit else "➕ Создать кампанию",
                type="primary"
            )
        
        with col2:
            if st.form_submit_button("❌ Отмена"):
                st.session_state.show_create_form = False
                st.session_state.show_edit_form = False
                if 'edit_campaign_id' in st.session_state:
                    del st.session_state.edit_campaign_id
                st.rerun()
        
        if submit_button:
            # Валидация полей
            required_fields = [name, telegram_account, telegram_chats_text, keywords_text, system_instruction]
            
            # Добавляем специфичные для провайдера поля
            if ai_provider == "claude" and not claude_agent_id:
                st.error("❌ ID Claude агента обязателен для провайдера Claude")
                return
            elif ai_provider == "openai" and not openai_model:
                st.error("❌ Модель OpenAI обязательна для провайдера OpenAI") 
                return
            
            if not all(required_fields):
                st.error("❌ Все обязательные поля должны быть заполнены")
                return
            
            # Подготовка данных
            telegram_chats = [chat.strip() for chat in telegram_chats_text.split('\\n') if chat.strip()]
            keywords = [keyword.strip() for keyword in keywords_text.split('\\n') if keyword.strip()]
            
            try:
                example_replies = json.loads(example_replies_text) if example_replies_text.strip() else {}
            except json.JSONDecodeError:
                st.error("❌ Некорректный формат JSON в примерах ответов")
                return
            
            campaign_data = {
                "name": name,
                "telegram_chats": telegram_chats,
                "keywords": keywords,
                "telegram_account": telegram_account,
                "ai_provider": ai_provider,
                "claude_agent_id": claude_agent_id if ai_provider == "claude" else None,
                "openai_model": openai_model if ai_provider == "openai" else "gpt-4",
                "context_messages_count": context_messages_count,
                "system_instruction": system_instruction,
                "example_replies": example_replies,
                "active": active
            }
            
            # Отправка данных
            if is_edit:
                response = make_api_request(
                    f"/campaigns/{edit_data['id']}",
                    method="PUT",
                    data=campaign_data
                )
            else:
                response = make_api_request(
                    "/campaigns/",
                    method="POST",
                    data=campaign_data
                )
            
            if response:
                success_message = "✅ Кампания обновлена!" if is_edit else "✅ Кампания создана!"
                st.success(success_message)
                
                # Сброс состояния формы
                st.session_state.show_create_form = False
                st.session_state.show_edit_form = False
                if 'edit_campaign_id' in st.session_state:
                    del st.session_state.edit_campaign_id
                
                time.sleep(1)
                st.rerun()


def toggle_campaign_status(campaign_id):
    """Переключение статуса кампании"""
    response = make_api_request(f"/campaigns/{campaign_id}/toggle", method="POST")
    if response:
        st.success(f"✅ {response['message']}")


def delete_campaign(campaign_id):
    """Удаление кампании"""
    response = make_api_request(f"/campaigns/{campaign_id}", method="DELETE")
    if response is not None:  # 204 статус не возвращает JSON
        st.success("✅ Кампания удалена!")


def show_statistics_page():
    """Страница статистики"""
    st.header("📊 Статистика системы")
    
    # Общая статистика
    overview_data = make_api_request("/logs/stats/overview")
    
    if overview_data:
        # Метрики кампаний
        st.subheader("🎯 Кампании")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Всего кампаний",
                overview_data['campaigns']['total']
            )
        
        with col2:
            st.metric(
                "Активных",
                overview_data['campaigns']['active'],
                delta=overview_data['campaigns']['active'] - overview_data['campaigns']['inactive']
            )
        
        with col3:
            st.metric(
                "Неактивных",
                overview_data['campaigns']['inactive']
            )
        
        # Метрики ответов
        st.subheader("💬 Ответы агента")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Всего ответов",
                overview_data['responses']['total']
            )
        
        with col2:
            st.metric(
                "За 24 часа",
                overview_data['responses']['last_24h']
            )
        
        with col3:
            st.metric(
                "Успешных за 24ч",
                overview_data['responses']['status_24h'].get('sent', 0)
            )
        
        with col4:
            st.metric(
                "Успешность %",
                f"{overview_data['success_rate_24h']}%"
            )
        
        # Статистика по статусам
        if overview_data['responses']['status_24h']:
            st.subheader("📈 Статусы ответов за 24 часа")
            
            status_data = overview_data['responses']['status_24h']
            
            # Создание DataFrame для графика
            df_status = pd.DataFrame(list(status_data.items()), columns=['Статус', 'Количество'])
            
            if not df_status.empty:
                # Перевод статусов
                status_translation = {
                    'sent': 'Отправлено',
                    'failed': 'Ошибки',
                    'pending': 'В очереди'
                }
                df_status['Статус'] = df_status['Статус'].map(status_translation)
                
                # График
                st.bar_chart(df_status.set_index('Статус'))
    
    # Статистика по кампаниям
    campaigns_data = make_api_request("/campaigns/")
    if campaigns_data:
        st.subheader("📋 Статистика по кампаниям")
        
        campaign_stats = []
        for campaign in campaigns_data:
            stats = make_api_request(f"/logs/campaign/{campaign['id']}/stats")
            if stats:
                campaign_stats.append(stats)
        
        if campaign_stats:
            df_campaigns = pd.DataFrame(campaign_stats)
            
            # Отображение таблицы
            st.dataframe(
                df_campaigns[['campaign_name', 'total_responses', 'responses_24h', 'success_rate', 'avg_processing_time_ms']],
                column_config={
                    'campaign_name': 'Название кампании',
                    'total_responses': 'Всего ответов',
                    'responses_24h': 'За 24ч',
                    'success_rate': 'Успешность %',
                    'avg_processing_time_ms': 'Среднее время (мс)'
                },
                use_container_width=True
            )


def show_logs_page():
    """Страница логов активности"""
    st.header("📝 Логи активности")
    
    # Фильтры
    col1, col2, col3 = st.columns(3)
    
    with col1:
        campaigns_data = make_api_request("/campaigns/")
        campaign_options = {"Все кампании": None}
        if campaigns_data:
            for campaign in campaigns_data:
                campaign_options[campaign['name']] = campaign['id']
        
        selected_campaign = st.selectbox(
            "Кампания",
            options=list(campaign_options.keys())
        )
        campaign_id = campaign_options[selected_campaign]
    
    with col2:
        status_options = {
            "Все статусы": None,
            "Отправлено": "sent",
            "Ошибки": "failed",
            "В очереди": "pending"
        }
        selected_status = st.selectbox("Статус", options=list(status_options.keys()))
        status_filter = status_options[selected_status]
    
    with col3:
        hours_back = st.selectbox(
            "Период",
            options=[None, 1, 6, 24, 72, 168],
            format_func=lambda x: "Все время" if x is None else f"Последние {x}ч"
        )
    
    # Получение логов
    params = {}
    if campaign_id:
        params['campaign_id'] = campaign_id
    if status_filter:
        params['status_filter'] = status_filter
    if hours_back:
        params['hours_back'] = hours_back
    
    # Формирование URL с параметрами
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    endpoint = f"/logs/{'?' + query_string if query_string else ''}"
    
    logs_data = make_api_request(endpoint)
    
    if logs_data:
        st.subheader(f"📄 Найдено записей: {len(logs_data)}")
        
        for log in logs_data:
            timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            local_time = timestamp.strftime('%d.%m.%Y %H:%M:%S')
            
            # Цвет статуса
            status_colors = {
                'sent': '🟢',
                'failed': '🔴',
                'pending': '🟡'
            }
            status_color = status_colors.get(log['status'], '⚪')
            
            with st.expander(f"{status_color} {local_time} - {log['chat_title']} - {log['trigger_keyword']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Чат:** {log['chat_title']} ({log['chat_id']})")
                    st.write(f"**Ключевое слово:** {log['trigger_keyword']}")
                    st.write(f"**Исходное сообщение:**")
                    st.text(log['original_message'])
                    
                    st.write(f"**Ответ агента:**")
                    st.text(log['agent_response'])
                    
                    if log['error_message']:
                        st.error(f"**Ошибка:** {log['error_message']}")
                
                with col2:
                    st.write(f"**ID сообщения:** {log['message_id']}")
                    st.write(f"**Время обработки:** {log['processing_time_ms']}мс" if log['processing_time_ms'] else "N/A")
                    
                    # Контекстные сообщения
                    if log['context_messages']:
                        with st.expander("Контекст"):
                            for ctx_msg in log['context_messages']:
                                st.text(f"[{ctx_msg['date']}] {ctx_msg['text']}")
    else:
        st.info("📭 Логи не найдены")


def show_settings_page():
    """Страница настроек"""
    st.header("⚙️ Настройки системы")
    
    # Статус системы
    server_status = check_server_status()
    
    # Вкладки для организации настроек
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Статус", "🌐 Конфигурация", "🔑 API Keys", "📊 Экспорт"])
    
    with tab1:
        st.subheader("Статус компонентов")
        
        if server_status:
            # Детальный статус компонентов
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                api_status = "🟢 Работает" if server_status.get("status") == "healthy" else "🔴 Ошибка"
                st.metric("API Сервер", api_status)
            
            with col2:
                db_status = "🟢 Подключена" if server_status.get("database") == "connected" else "🔴 Отключена"
                st.metric("База данных", db_status)
            
            with col3:
                telegram_status = "🟢 Подключен" if server_status.get("telegram_connected") else "🔴 Отключен"
                st.metric("Telegram", telegram_status)
            
            with col4:
                # Проверяем AI провайдеры через статистику
                ai_status = "🟢 Доступен" if server_status.get("status") == "healthy" else "🟡 Частично"
                st.metric("AI Провайдеры", ai_status)
            
            # Дополнительная информация
            st.subheader("Дополнительная информация")
            
            info_data = {
                "Параметр": [
                    "URL Backend API",
                    "Режим работы",
                    "Версия API",
                    "Время последней проверки"
                ],
                "Значение": [
                    API_BASE_URL,
                    "Облачный" if "127.0.0.1" not in API_BASE_URL else "Локальный",
                    "1.0.0",
                    datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                ]
            }
            
            df_info = pd.DataFrame(info_data)
            st.table(df_info)
            
        else:
            st.error("❌ Backend сервер недоступен")
            st.write(f"**Попытка подключения к:** `{API_BASE_URL}`")
            
            # Предложения по решению проблем
            st.subheader("Возможные решения:")
            st.markdown("""
            1. **Проверьте URL backend сервера** в настройках Streamlit Cloud
            2. **Убедитесь, что backend сервер запущен** и доступен
            3. **Проверьте настройки CORS** на backend сервере
            4. **Проверьте логи** backend сервера на наличие ошибок
            """)
        
        # Кнопка обновления статуса
        if st.button("🔄 Обновить статус", type="primary"):
            st.rerun()
    
    with tab2:
        st.subheader("Конфигурация подключений")
        
        # Конфигурация API
        with st.expander("🌐 Backend API", expanded=True):
            st.code(f"""
# Текущая конфигурация
API_BASE_URL = "{API_BASE_URL}"

# Доступные эндпоинты:
- Документация: {API_BASE_URL}/docs
- ReDoc: {API_BASE_URL}/redoc
- Health Check: {API_BASE_URL}/health
- Кампании: {API_BASE_URL}/campaigns/
- Логи: {API_BASE_URL}/logs/
- Чаты: {API_BASE_URL}/chats/active
            """, language="yaml")
        
        # Настройки Streamlit Cloud
        with st.expander("☁️ Streamlit Cloud"):
            st.markdown("""
            **Настройка в Streamlit Cloud:**
            
            1. Перейдите в **Settings → Secrets**
            2. Добавьте следующую строку:
            ```toml
            BACKEND_API_URL = "https://your-backend-server.herokuapp.com"
            ```
            3. Замените URL на актуальный адрес вашего backend сервера
            4. Сохраните и перезапустите приложение
            """)
        
        # Локальная разработка
        with st.expander("🏠 Локальная разработка"):
            st.markdown("""
            **Для локального запуска:**
            
            1. Создайте файл `.streamlit/secrets.toml`
            2. Добавьте настройки:
            ```toml
            BACKEND_API_URL = "http://127.0.0.1:8000"
            ```
            3. Запустите backend сервер: `python backend/main.py`
            4. Запустите Streamlit: `streamlit run streamlit_app.py`
            """)
    
    with tab3:
        st.subheader("Управление API ключами")
        
        # Отображение настроенных провайдеров
        st.markdown("**Статус AI провайдеров:**")
        
        # Получаем информацию о кампаниях для понимания используемых провайдеров
        campaigns_data = make_api_request("/campaigns/") if server_status else None
        
        if campaigns_data:
            openai_campaigns = len([c for c in campaigns_data if c.get('ai_provider') == 'openai'])
            claude_campaigns = len([c for c in campaigns_data if c.get('ai_provider') == 'claude'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "🤖 OpenAI", 
                    f"{openai_campaigns} кампаний",
                    delta="Основной провайдер" if openai_campaigns > 0 else None
                )
            
            with col2:
                st.metric(
                    "🧠 Claude", 
                    f"{claude_campaigns} кампаний",
                    delta="Доступен" if claude_campaigns > 0 else None
                )
        
        # Инструкции по настройке
        with st.expander("🔑 Настройка OpenAI API"):
            st.markdown("""
            1. Получите API ключ на [platform.openai.com](https://platform.openai.com/api-keys)
            2. В Streamlit Cloud добавьте в Secrets:
            ```toml
            OPENAI_API_KEY = "sk-proj-your-key-here"
            ```
            3. Доступные модели: gpt-4, gpt-3.5-turbo, gpt-4-turbo-preview
            """)
        
        with st.expander("🧠 Настройка Claude API"):
            st.markdown("""
            1. Получите API ключ на [console.anthropic.com](https://console.anthropic.com)
            2. В Streamlit Cloud добавьте в Secrets:
            ```toml
            ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
            ```
            3. Укажите Claude Agent ID в кампаниях
            """)
        
        with st.expander("📡 Настройка Telegram API"):
            st.markdown("""
            1. Получите API ID и Hash на [my.telegram.org/apps](https://my.telegram.org/apps)
            2. В Streamlit Cloud добавьте в Secrets:
            ```toml
            TELEGRAM_API_ID = "12345678"
            TELEGRAM_API_HASH = "your-api-hash-here"
            TELEGRAM_PHONE = "+1234567890"
            ```
            **Внимание:** Эти данные нужны только для backend сервера
            """)
    
    with tab4:
        st.subheader("Экспорт и резервное копирование")
        
        # Экспорт кампаний
        if st.button("📥 Экспорт кампаний", help="Сохранить все кампании в JSON файл"):
            if server_status:
                campaigns_data = make_api_request("/campaigns/")
                if campaigns_data:
                    # Создаем JSON файл для скачивания
                    export_data = {
                        "export_date": datetime.now().isoformat(),
                        "total_campaigns": len(campaigns_data),
                        "campaigns": campaigns_data
                    }
                    
                    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
                    
                    st.download_button(
                        label="💾 Скачать кампании (JSON)",
                        data=json_str,
                        file_name=f"telegram_agent_campaigns_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )
                    
                    st.success(f"✅ Готово к скачиванию: {len(campaigns_data)} кампаний")
                else:
                    st.error("❌ Не удалось получить данные кампаний")
            else:
                st.warning("⚠️ Backend недоступен для экспорта")
        
        # Экспорт логов
        if st.button("📊 Экспорт логов активности", help="Сохранить логи за последние 7 дней"):
            if server_status:
                logs_data = make_api_request("/logs/?hours_back=168")  # 7 дней
                if logs_data:
                    # Подготавливаем данные для CSV
                    logs_for_export = []
                    for log in logs_data:
                        logs_for_export.append({
                            "Дата": log['timestamp'],
                            "Чат": log['chat_title'],
                            "ID чата": log['chat_id'],
                            "Ключевое слово": log['trigger_keyword'],
                            "Исходное сообщение": log['original_message'],
                            "Ответ агента": log['agent_response'],
                            "Статус": log['status'],
                            "Время обработки (мс)": log.get('processing_time_ms', 0)
                        })
                    
                    df_export = pd.DataFrame(logs_for_export)
                    csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
                    
                    st.download_button(
                        label="💾 Скачать логи (CSV)",
                        data=csv_data,
                        file_name=f"telegram_agent_logs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                    
                    st.success(f"✅ Готово к скачиванию: {len(logs_data)} записей")
                else:
                    st.error("❌ Не удалось получить логи")
            else:
                st.warning("⚠️ Backend недоступен для экспорта")
        
        # Информация о резервном копировании
        st.subheader("📋 О резервном копировании")
        st.info("""
        **Рекомендации:**
        - Экспортируйте кампании перед важными изменениями
        - Сохраняйте логи для анализа эффективности
        - Храните резервные копии в безопасном месте
        - Регулярно проверяйте работоспособность экспорта
        """)


def show_demo_campaigns_page():
    """Демо-страница кампаний"""
    st.header("📋 Управление кампаниями (Демо-режим)")
    st.warning("⚠️ Backend недоступен - показан демо-интерфейс")
    
    st.info("В этом разделе вы можете создавать и управлять кампаниями мониторинга Telegram-чатов")
    
    # Пример кампании
    with st.expander("🎯 Пример кампании - Мониторинг новостей", expanded=True):
        st.write("**ID:** demo-001")
        st.write("**Аккаунт Telegram:** @demo_bot")
        st.write("**Claude агент:** claude-news-agent")
        st.write("**Чаты:** @news_channel, @tech_chat")
        st.write("**Ключевые слова:** новости, анонс, обновление")
        st.write("**Статус:** 🟢 Активна")


def show_demo_statistics_page():
    """Демо-страница статистики"""
    st.header("📊 Статистика системы (Демо-режим)")
    st.warning("⚠️ Backend недоступен - показаны демо-данные")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего кампаний", "3")
    with col2:
        st.metric("Активных", "2")
    with col3:
        st.metric("Ответов за 24ч", "15")


def show_demo_logs_page():
    """Демо-страница логов"""
    st.header("📝 Логи активности (Демо-режим)")
    st.warning("⚠️ Backend недоступен - показаны демо-данные")
    
    st.info("Здесь отображаются логи активности агента и история обработки сообщений")
    
    with st.expander("🟢 01.08.2025 14:30 - Новостной канал - ключевое слово: анонс"):
        st.write("**Исходное сообщение:** Анонс новой функции в приложении")
        st.write("**Ответ агента:** Интересная новость! Расскажите подробнее")


def show_chats_page():
    """Страница мониторинга чатов"""
    st.header("💬 Мониторинг чатов")
    
    # Получение списка активных чатов
    chats_data = make_api_request("/chats/active")
    
    if chats_data is None:
        return
    
    # Автообновление
    col1, col2 = st.columns([1, 4])
    with col1:
        auto_refresh = st.checkbox("🔄 Автообновление", value=False)
    with col2:
        if st.button("📥 Обновить сейчас"):
            st.rerun()
    
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    if chats_data and len(chats_data) > 0:
        st.subheader(f"Активные чаты ({len(chats_data)})")
        
        # Выбор чата для детального просмотра
        selected_chat = st.selectbox(
            "Выберите чат для просмотра",
            options=[None] + [chat["chat_id"] for chat in chats_data],
            format_func=lambda x: "Выберите чат..." if x is None else next(
                (chat["chat_title"] for chat in chats_data if chat["chat_id"] == x), x
            )
        )
        
        # Список чатов в виде карточек
        for chat in chats_data:
            with st.expander(f"💬 {chat['chat_title']}", expanded=(chat['chat_id'] == selected_chat)):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**ID чата:** `{chat['chat_id']}`")
                    st.write(f"**Кампаний:** {chat['campaign_count']}")
                    
                    if chat['last_activity']:
                        last_activity = datetime.fromisoformat(chat['last_activity'].replace('Z', '+00:00'))
                        st.write(f"**Последняя активность:** {last_activity.strftime('%d.%m.%Y %H:%M')}")
                    
                    if chat['last_message']:
                        st.write(f"**Последнее сообщение:** {chat['last_message']}")
                    
                    # Статус подключения
                    connection_status = "🟢 Подключен" if chat['is_connected'] else "🔴 Отключен"
                    st.write(f"**Статус:** {connection_status}")
                
                with col2:
                    # Кнопка для просмотра сообщений
                    if st.button(f"📜 Сообщения", key=f"messages_{chat['chat_id']}"):
                        st.session_state.selected_chat_for_messages = chat['chat_id']
                        st.session_state.show_chat_messages = True
                        st.rerun()
                    
                    # Кнопка для отправки сообщения
                    if st.button(f"✉️ Отправить", key=f"send_{chat['chat_id']}"):
                        st.session_state.selected_chat_for_send = chat['chat_id']
                        st.session_state.show_send_message = True
                        st.rerun()
                    
                    # Кнопка информации о чате
                    if st.button(f"ℹ️ Инфо", key=f"info_{chat['chat_id']}"):
                        show_chat_info(chat['chat_id'])
        
        # Отображение сообщений чата
        if st.session_state.get('show_chat_messages', False):
            show_chat_messages()
        
        # Форма отправки сообщения
        if st.session_state.get('show_send_message', False):
            show_send_message_form()
            
    else:
        st.info("📭 Нет активных чатов для мониторинга. Создайте кампании для начала работы.")


def show_chat_messages():
    """Отображение сообщений чата"""
    chat_id = st.session_state.get('selected_chat_for_messages')
    if not chat_id:
        return
    
    st.subheader(f"📜 Сообщения чата: {chat_id}")
    
    # Кнопка закрытия
    if st.button("❌ Закрыть", key="close_messages"):
        st.session_state.show_chat_messages = False
        st.rerun()
    
    # Получение сообщений
    messages_data = make_api_request(f"/chats/{chat_id}/messages?limit=30")
    
    if messages_data:
        st.write(f"**Чат:** {messages_data['chat_title']}")
        
        # Отображение сообщений
        for message in messages_data['messages']:
            message_time = datetime.fromisoformat(message['date'].replace('Z', '+00:00'))
            time_str = message_time.strftime('%H:%M:%S')
            
            # Определяем тип сообщения
            if message['is_bot']:
                message_type = "🤖"
            elif message['sender'].startswith('@'):
                message_type = "👤"
            else:
                message_type = "👥"
            
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{message_type} {message['sender']}** ({time_str})")
                    if message['text']:
                        st.write(message['text'])
                    
                    # Показываем ответ бота, если есть
                    if message.get('bot_response'):
                        bot_resp = message['bot_response']
                        status_color = "🟢" if bot_resp['status'] == 'sent' else "🔴"
                        st.info(f"{status_color} **Ответ бота** (кл.слово: {bot_resp['trigger_keyword']}):\n{bot_resp['response']}")
                
                with col2:
                    # Кнопка для принудительного ответа
                    if not message['is_bot'] and not message.get('bot_response'):
                        if st.button("🤖 Ответить", key=f"reply_{message['id']}"):
                            trigger_manual_response(chat_id, message['id'])
                
                st.divider()


def show_send_message_form():
    """Форма отправки сообщения"""
    chat_id = st.session_state.get('selected_chat_for_send')
    if not chat_id:
        return
    
    st.subheader(f"✉️ Отправка сообщения в чат: {chat_id}")
    
    # Кнопка закрытия
    if st.button("❌ Закрыть", key="close_send"):
        st.session_state.show_send_message = False
        st.rerun()
    
    with st.form("send_message_form"):
        message_text = st.text_area(
            "Текст сообщения:",
            height=100,
            help="Введите текст сообщения для отправки"
        )
        
        reply_to = st.number_input(
            "ID сообщения для ответа (опционально):",
            min_value=0,
            value=0,
            help="Если указать ID сообщения, ваше сообщение будет ответом на него"
        )
        
        submit = st.form_submit_button("📤 Отправить сообщение", type="primary")
        
        if submit:
            if not message_text.strip():
                st.error("Текст сообщения не может быть пустым")
                return
            
            # Подготовка данных
            message_data = {
                "text": message_text.strip(),
                "reply_to": reply_to if reply_to > 0 else None
            }
            
            # Отправка
            response = make_api_request(
                f"/chats/{chat_id}/send",
                method="POST",
                data=message_data
            )
            
            if response:
                st.success(f"✅ Сообщение отправлено! ID: {response['message_id']}")
                st.session_state.show_send_message = False
                time.sleep(1)
                st.rerun()


def show_chat_info(chat_id):
    """Отображение информации о чате"""
    info = make_api_request(f"/chats/{chat_id}/info")
    
    if info:
        st.subheader(f"ℹ️ Информация о чате")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**ID:** `{info['id']}`")
            st.write(f"**Название:** {info['title']}")
            st.write(f"**Тип:** {info['type']}")
        
        with col2:
            if info['username']:
                st.write(f"**Username:** {info['username']}")
            if info['participant_count']:
                st.write(f"**Участников:** {info['participant_count']}")
        
        if info['description']:
            st.write(f"**Описание:** {info['description']}")


def trigger_manual_response(chat_id, message_id):
    """Запуск принудительного ответа бота"""
    # Получаем список кампаний для выбора
    campaigns_data = make_api_request("/campaigns/")
    
    if campaigns_data:
        # Фильтруем кампании, которые мониторят данный чат
        relevant_campaigns = []
        for campaign in campaigns_data:
            if campaign['active'] and chat_id in campaign['telegram_chats']:
                relevant_campaigns.append(campaign)
        
        if relevant_campaigns:
            # Используем первую подходящую кампанию
            campaign = relevant_campaigns[0]
            
            trigger_data = {
                "message_id": message_id,
                "campaign_id": campaign['id']
            }
            
            response = make_api_request(
                f"/chats/{chat_id}/trigger",
                method="POST",
                data=trigger_data
            )
            
            if response:
                st.success(f"✅ Принудительный ответ запущен через кампанию '{campaign['name']}'")
            else:
                st.error("❌ Ошибка запуска принудительного ответа")
        else:
            st.warning("⚠️ Нет активных кампаний для этого чата")
    else:
        st.error("❌ Не удалось получить список кампаний")


def show_demo_chats_page():
    """Демо-страница чатов"""
    st.header("💬 Мониторинг чатов (Демо-режим)")
    st.warning("⚠️ Backend недоступен - показан демо-интерфейс")
    
    st.info("В этом разделе вы можете мониторить активность в Telegram-чатах в реальном времени")
    
    # Пример активного чата
    with st.expander("💬 @tech_news_channel", expanded=True):
        st.write("**ID чата:** `-1001234567890`")
        st.write("**Кампаний:** 2")
        st.write("**Последняя активность:** 02.08.2025 15:45")
        st.write("**Последнее сообщение:** Новая версия Python 3.12 выпущена...")
        st.write("**Статус:** 🟢 Подключен")


if __name__ == "__main__":
    main()