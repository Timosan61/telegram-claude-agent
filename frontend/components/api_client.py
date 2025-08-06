import streamlit as st
import requests
from typing import Optional, Dict, Any
import time


class APIClient:
    """Унифицированный клиент для работы с backend API"""
    
    def __init__(self):
        # Проверяем запуск в Streamlit Cloud или локально
        try:
            import streamlit as st
            self.base_url = st.secrets.get("BACKEND_API_URL", "http://127.0.0.1:8000")
        except:
            self.base_url = "http://127.0.0.1:8000"
    
    def make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict[Any, Any]] = None, 
                    timeout: int = 30) -> Optional[Dict[Any, Any]]:
        """Выполнение запроса к API"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, timeout=timeout)
            else:
                raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
            
            if response.status_code in [200, 201]:
                return response.json() if response.content else {}
            elif response.status_code == 204:
                return {}  # Для DELETE запросов
            else:
                # Улучшенная обработка ошибок
                error_text = response.text[:500]  # Ограничиваем длину для читаемости
                
                if response.status_code == 404:
                    st.error(f"❌ Endpoint не найден: {endpoint}")
                elif response.status_code == 500:
                    st.error(f"❌ Внутренняя ошибка сервера")
                elif response.status_code == 504:
                    st.error(f"❌ Gateway Timeout (504)")
                    st.info("💡 Сервер не отвечает. Возможные причины:")
                    st.write("• DigitalOcean App Platform перезагружается")
                    st.write("• Telegram API подключение заблокировано")
                    st.write("• Превышен лимит запросов к Telegram")
                    st.write("• Временные проблемы с сетью")
                    st.info("🔄 Подождите 2-3 минуты и попробуйте снова")
                else:
                    st.error(f"❌ Ошибка API: {response.status_code}")
                    
                # Показываем подробности только если это JSON ошибка
                try:
                    error_json = response.json()
                    if "detail" in error_json:
                        st.error(f"Детали: {error_json['detail']}")
                except:
                    # Не JSON ответ, показываем HTML или текст только если это не 504
                    if response.status_code != 504 and len(error_text) < 200:
                        st.text(f"Ответ сервера: {error_text}")
                
                return None
        
        except requests.exceptions.ConnectionError:
            if "127.0.0.1" in self.base_url or "localhost" in self.base_url:
                st.error("❌ Не удается подключиться к локальному серверу. Убедитесь, что FastAPI сервер запущен на http://127.0.0.1:8000")
            else:
                st.error(f"❌ Не удается подключиться к backend серверу: `{self.base_url}`")
            return None
        except requests.exceptions.Timeout:
            st.error(f"⏰ Превышено время ожидания запроса ({timeout}s)")
            return None
        except Exception as e:
            st.error(f"❌ Ошибка запроса: {e}")
            return None
    
    def check_server_status(self) -> Optional[Dict[str, Any]]:
        """Проверка статуса сервера"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=3)
            if response.status_code == 200:
                return response.json()
        except Exception:
            return None
        return None
    
    # Методы для кампаний
    def get_campaigns(self, active_only: bool = False) -> Optional[list]:
        """Получить список кампаний"""
        endpoint = "/campaigns/" + ("?active_only=true" if active_only else "")
        return self.make_request(endpoint)
    
    def get_campaign(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """Получить кампанию по ID"""
        return self.make_request(f"/campaigns/{campaign_id}")
    
    def create_campaign(self, campaign_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создать новую кампанию"""
        return self.make_request("/campaigns/", method="POST", data=campaign_data)
    
    def update_campaign(self, campaign_id: int, campaign_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить кампанию"""
        return self.make_request(f"/campaigns/{campaign_id}", method="PUT", data=campaign_data)
    
    def delete_campaign(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """Удалить кампанию"""
        return self.make_request(f"/campaigns/{campaign_id}", method="DELETE")
    
    def toggle_campaign_status(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """Переключить статус кампании"""
        return self.make_request(f"/campaigns/{campaign_id}/toggle", method="POST")
    
    def refresh_campaigns_cache(self) -> Optional[Dict[str, Any]]:
        """Принудительное обновление кэша кампаний"""
        return self.make_request("/campaigns/refresh-cache", method="POST")
    
    # Методы для чатов
    def get_active_chats(self) -> Optional[list]:
        """Получить активные чаты"""
        return self.make_request("/chats/active")
    
    def get_chat_messages(self, chat_id: str, limit: int = 30) -> Optional[Dict[str, Any]]:
        """Получить сообщения чата"""
        return self.make_request(f"/chats/{chat_id}/messages?limit={limit}")
    
    def send_message(self, chat_id: str, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Отправить сообщение в чат"""
        return self.make_request(f"/chats/{chat_id}/send", method="POST", data=message_data)
    
    def get_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о чате"""
        return self.make_request(f"/chats/{chat_id}/info")
    
    def trigger_manual_response(self, chat_id: str, trigger_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Запустить принудительный ответ бота"""
        return self.make_request(f"/chats/{chat_id}/trigger", method="POST", data=trigger_data)
    
    # Методы для логов
    def get_logs(self, **params) -> Optional[list]:
        """Получить логи активности"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
        endpoint = f"/logs/{'?' + query_string if query_string else ''}"
        return self.make_request(endpoint)
    
    def get_stats_overview(self) -> Optional[Dict[str, Any]]:
        """Получить общую статистику"""
        return self.make_request("/logs/stats/overview")
    
    def get_campaign_stats(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """Получить статистику кампании"""
        return self.make_request(f"/logs/campaign/{campaign_id}/stats")
    
    # Методы для компании
    def get_company_settings(self) -> Optional[Dict[str, Any]]:
        """Получить настройки компании"""
        return self.make_request("/company/settings")
    
    def update_company_settings(self, settings_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить настройки компании"""
        return self.make_request("/company/settings", method="PUT", data=settings_data)
    
    def add_telegram_account(self, account_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Добавить Telegram аккаунт"""
        return self.make_request("/company/telegram-accounts", method="POST", data=account_data)
    
    def delete_telegram_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """Удалить Telegram аккаунт"""
        return self.make_request(f"/company/telegram-accounts/{account_id}", method="DELETE")
    
    def update_ai_provider(self, provider: str, provider_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить настройки AI провайдера"""
        return self.make_request(f"/company/ai-providers/{provider}", method="PUT", data=provider_data)
    
    def update_default_settings(self, settings_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить настройки по умолчанию"""
        return self.make_request("/company/default-settings", method="PUT", data=settings_data)
    
    # Методы для аналитики
    def check_analytics_health(self) -> Optional[Dict[str, Any]]:
        """Проверить статус сервиса аналитики"""
        return self.make_request("/analytics/health")
    
    def get_channel_info(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о канале"""
        return self.make_request(f"/analytics/channel-info/{channel_name}")
    
    def start_channel_analysis(self, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Запустить прямой анализ канала"""
        return self.make_request("/analytics/analyze-channel", method="POST", data=analysis_data)
    
    def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Получить статус анализа"""
        return self.make_request(f"/analytics/analyze/{analysis_id}/status")
    
    def get_analysis_results(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Получить результаты анализа"""
        return self.make_request(f"/analytics/analyze/{analysis_id}/results")
    
    def list_analyses(self) -> Optional[Dict[str, Any]]:
        """Получить список всех анализов"""
        return self.make_request("/analytics/analyze")
    
    def delete_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Удалить анализ"""
        return self.make_request(f"/analytics/analyze/{analysis_id}", method="DELETE")


# Глобальный экземпляр для использования в приложении
api_client = APIClient()


def show_connection_status():
    """Показать статус подключения к API"""
    server_status = api_client.check_server_status()
    
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
        
        return True
    else:
        st.warning("⚠️ Backend сервер недоступен")
        st.info("В демо-режиме интерфейс доступен для просмотра, но функциональность ограничена")
        return False


def handle_api_error(response, success_message: str = "✅ Операция выполнена успешно!", 
                    error_message: str = "❌ Ошибка выполнения операции"):
    """Обработка ответа API с отображением сообщений"""
    if response is not None:
        st.success(success_message)
        return True
    else:
        st.error(error_message)
        return False


def auto_refresh_component(key: str, interval: int = 5):
    """Компонент автообновления"""
    col1, col2 = st.columns([1, 4])
    with col1:
        auto_refresh = st.checkbox(f"🔄 Автообновление", value=False, key=f"auto_refresh_{key}")
    with col2:
        if st.button("📥 Обновить сейчас", key=f"refresh_now_{key}"):
            st.rerun()
    
    if auto_refresh:
        time.sleep(interval)
        st.rerun()