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
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
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
        st.error("❌ Сервер недоступен")
        return
    
    # Боковая панель навигации
    st.sidebar.title("Навигация")
    page = st.sidebar.selectbox(
        "Выберите страницу",
        ["📋 Кампании", "📊 Статистика", "📝 Логи активности", "⚙️ Настройки"]
    )
    
    # Отображение выбранной страницы
    if page == "📋 Кампании":
        show_campaigns_page()
    elif page == "📊 Статистика":
        show_statistics_page()
    elif page == "📝 Логи активности":
        show_logs_page()
    elif page == "⚙️ Настройки":
        show_settings_page()


def show_campaigns_page():
    """Страница управления кампаниями"""
    st.header("📋 Управление кампаниями")
    
    # Получение списка кампаний
    campaigns_data = make_api_request("/api/campaigns/")
    
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
                    st.write(f"**Claude агент:** {campaign['claude_agent_id']}")
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
        
        # Claude настройки
        st.subheader("🧠 Настройки Claude")
        
        claude_agent_id = st.text_input(
            "ID Claude агента*",
            value=edit_data.get('claude_agent_id', '') if is_edit else '',
            help="Идентификатор или alias Claude Code агента"
        )
        
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
            if not all([name, telegram_account, telegram_chats_text, keywords_text, claude_agent_id, system_instruction]):
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
                "claude_agent_id": claude_agent_id,
                "context_messages_count": context_messages_count,
                "system_instruction": system_instruction,
                "example_replies": example_replies,
                "active": active
            }
            
            # Отправка данных
            if is_edit:
                response = make_api_request(
                    f"/api/campaigns/{edit_data['id']}",
                    method="PUT",
                    data=campaign_data
                )
            else:
                response = make_api_request(
                    "/api/campaigns/",
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
    response = make_api_request(f"/api/campaigns/{campaign_id}/toggle", method="POST")
    if response:
        st.success(f"✅ {response['message']}")


def delete_campaign(campaign_id):
    """Удаление кампании"""
    response = make_api_request(f"/api/campaigns/{campaign_id}", method="DELETE")
    if response is not None:  # 204 статус не возвращает JSON
        st.success("✅ Кампания удалена!")


def show_statistics_page():
    """Страница статистики"""
    st.header("📊 Статистика системы")
    
    # Общая статистика
    overview_data = make_api_request("/api/logs/stats/overview")
    
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
    campaigns_data = make_api_request("/api/campaigns/")
    if campaigns_data:
        st.subheader("📋 Статистика по кампаниям")
        
        campaign_stats = []
        for campaign in campaigns_data:
            stats = make_api_request(f"/api/logs/campaign/{campaign['id']}/stats")
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
        campaigns_data = make_api_request("/api/campaigns/")
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
    endpoint = f"/api/logs/{'?' + query_string if query_string else ''}"
    
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
    if server_status:
        st.subheader("🔧 Статус системы")
        
        status_data = {
            "Компонент": ["API Сервер", "База данных", "Telegram", "Claude"],
            "Статус": [
                "🟢 Работает",
                "🟢 Подключена" if server_status.get("database") == "connected" else "🔴 Отключена",
                "🟢 Подключен" if server_status.get("telegram_connected") else "🔴 Отключен",
                "🟢 Доступен"  # Предполагаем, что Claude доступен если API работает
            ]
        }
        
        df_status = pd.DataFrame(status_data)
        st.table(df_status)
    
    # Настройки конфигурации
    st.subheader("🔧 Конфигурация")
    
    with st.expander("API Настройки"):
        st.code(f"""
        API_BASE_URL = "{API_BASE_URL}"
        Документация API: {API_BASE_URL}/docs
        Redoc: {API_BASE_URL}/redoc
        """, language="python")
    
    with st.expander("Переменные окружения"):
        st.info("""
        Убедитесь, что следующие переменные настроены в .env файле:
        - ANTHROPIC_API_KEY
        - TELEGRAM_API_ID
        - TELEGRAM_API_HASH
        - TELEGRAM_PHONE
        - ZEP_API_KEY (опционально)
        """)
    
    # Действия системы
    st.subheader("🔄 Действия")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Обновить статус"):
            st.rerun()
    
    with col2:
        if st.button("📊 Экспорт данных"):
            st.info("Функция экспорта будет добавлена в следующих версиях")


if __name__ == "__main__":
    main()