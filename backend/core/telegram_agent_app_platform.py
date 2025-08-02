import asyncio
import os
import time
import base64
from typing import List, Dict, Optional
from datetime import datetime

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Message, User, Chat, Channel
from sqlalchemy.orm import Session

from database.models.base import SessionLocal
from database.models.campaign import Campaign
from database.models.log import ActivityLog

# Опциональный импорт Claude Client
try:
    from utils.claude.client import ClaudeClient
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    print("⚠️ ClaudeClient недоступен - отключен anthropic")

from utils.openai.client import OpenAIClient

# Опциональный импорт ZepMemoryManager
try:
    from utils.zep.memory import ZepMemoryManager
    ZEP_AVAILABLE = True
except ImportError:
    ZEP_AVAILABLE = False
    print("⚠️ ZepMemoryManager недоступен - работаем без управления памятью")


class TelegramAgentAppPlatform:
    """
    Telegram-агент для DigitalOcean App Platform
    Использует StringSession из переменных окружения
    """
    
    def __init__(self):
        self.api_id = int(os.getenv("TELEGRAM_API_ID"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        
        # Получение сессии из переменных окружения
        self.session_string = self._get_session_from_env()
        
        # Инициализация клиента с StringSession
        if self.session_string:
            session = StringSession(self.session_string)
            self.client = TelegramClient(session, self.api_id, self.api_hash)
            print("✅ TelegramClient инициализован с StringSession")
        else:
            # Fallback к файловой сессии для локальной разработки
            self.client = TelegramClient("telegram_agent", self.api_id, self.api_hash)
            print("⚠️ Используется файловая сессия (локальная разработка)")
        
        # AI клиенты - инициализируем с обработкой ошибок
        if CLAUDE_AVAILABLE:
            try:
                self.claude_client = ClaudeClient()
                print("✅ Claude Client доступен")
            except Exception as e:
                print(f"⚠️ Claude Client недоступен: {e}")
                self.claude_client = None
        else:
            self.claude_client = None
            print("⚠️ Claude Client отключен - используем только OpenAI")
        
        try:
            self.openai_client = OpenAIClient()
            print("✅ OpenAI Client доступен")
        except Exception as e:
            print(f"⚠️ OpenAI Client недоступен: {e}")
            self.openai_client = None
        
        # Инициализация менеджера памяти (опционально)
        if ZEP_AVAILABLE:
            self.memory_manager = ZepMemoryManager()
            print("✅ ZepMemoryManager инициализирован")
        else:
            self.memory_manager = None
            print("⚠️ Работаем без менеджера памяти")
        
        # Кэш активных кампаний
        self.active_campaigns: List[Campaign] = []
        self.last_campaign_update = 0
        self.campaign_cache_ttl = int(os.getenv("CACHE_TTL", "60"))
        
        # Статус подключения
        self.is_connected = False
        self.is_authorized = False
    
    def _get_session_from_env(self) -> Optional[str]:
        """Получение сессии из переменных окружения"""
        # Попробуем получить прямую строку сессии
        session_string = os.getenv("TELEGRAM_SESSION_STRING")
        if session_string:
            print("✅ Найдена TELEGRAM_SESSION_STRING")
            return session_string
        
        # Попробуем получить base64 версию
        session_b64 = os.getenv("TELEGRAM_SESSION_B64")
        if session_b64:
            try:
                session_string = base64.b64decode(session_b64).decode()
                print("✅ Найдена TELEGRAM_SESSION_B64, декодирована")
                return session_string
            except Exception as e:
                print(f"❌ Ошибка декодирования TELEGRAM_SESSION_B64: {e}")
        
        # Попробуем получить из других возможных переменных
        for var_name in ["TELEGRAM_SESSION", "SESSION_STRING", "TG_SESSION"]:
            session = os.getenv(var_name)
            if session:
                print(f"✅ Найдена сессия в {var_name}")
                return session
        
        print("⚠️ Сессия в переменных окружения не найдена")
        return None
    
    async def start(self):
        """Запуск агента"""
        try:
            print("🔗 Подключение к Telegram...")
            await self.client.connect()
            self.is_connected = True
            
            # Проверка авторизации
            self.is_authorized = await self.client.is_user_authorized()
            
            if self.is_authorized:
                print("✅ Telegram авторизация активна")
                
                # Получение информации о пользователе
                me = await self.client.get_me()
                print(f"👤 Пользователь: {me.first_name} {me.last_name or ''}")
                print(f"📱 Телефон: {me.phone}")
                
                # Настройка обработчиков событий
                await self._setup_event_handlers()
                
                # Загрузка активных кампаний
                await self.update_campaigns()
                
                print("🚀 Telegram Agent запущен и готов к работе!")
                return True
            else:
                print("❌ Telegram не авторизован")
                print("💡 Требуется настройка переменной TELEGRAM_SESSION_STRING")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запуска Telegram Agent: {e}")
            self.is_connected = False
            self.is_authorized = False
            return False
    
    async def _setup_event_handlers(self):
        """Настройка обработчиков событий"""
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            await self._handle_message(event)
        
        print("✅ Обработчики событий настроены")
    
    async def _handle_message(self, event):
        """Обработка нового сообщения"""
        try:
            message = event.message
            chat = await event.get_chat()
            
            # DEBUG: Логируем все входящие сообщения
            print(f"🔍 DEBUG: Получено сообщение!")
            print(f"   📝 Текст: '{message.text or 'None'}'")
            print(f"   💬 Чат: {getattr(chat, 'title', getattr(chat, 'username', 'Unknown'))} (ID: {getattr(chat, 'id', 'Unknown')})")
            print(f"   👤 От: {message.sender_id}")
            print(f"   📊 Активных кампаний: {len(self.active_campaigns)}")
            
            # Проверяем, есть ли активные кампании для этого чата
            relevant_campaigns = []
            for campaign in self.active_campaigns:
                print(f"   🎯 Проверяем кампанию: {campaign.name}")
                if self._is_message_relevant(message, chat, campaign):
                    relevant_campaigns.append(campaign)
                    print(f"   ✅ Кампания {campaign.name} релевантна!")
                else:
                    print(f"   ❌ Кампания {campaign.name} не релевантна")
            
            if not relevant_campaigns:
                return
            
            # Обработка сообщения для каждой релевантной кампании
            for campaign in relevant_campaigns:
                await self._process_message_for_campaign(message, chat, campaign)
                
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    def _is_message_relevant(self, message: Message, chat, campaign: Campaign) -> bool:
        """Проверка релевантности сообщения для кампании"""
        try:
            # DEBUG: Подробное логирование проверки релевантности
            print(f"      🔍 DEBUG: Проверка релевантности для кампании '{campaign.name}'")
            print(f"         📋 Target chats: {campaign.telegram_chats}")
            print(f"         🔑 Keywords: {campaign.keywords}")
            print(f"         💬 Chat ID: {getattr(chat, 'id', 'None')}")
            print(f"         🏷️ Chat username: {getattr(chat, 'username', 'None')}")
            print(f"         📝 Message text: '{message.text or 'None'}'")
            
            # Проверка по ID чата/канала и username
            if hasattr(chat, 'id') or (hasattr(chat, 'username') and chat.username):
                # campaign.telegram_chats уже список (JSON), не строка
                target_chats = campaign.telegram_chats if isinstance(campaign.telegram_chats, list) else campaign.telegram_chats.split(',')
                print(f"         🎯 Обработанные target_chats: {target_chats}")
                
                # Проверка по ID чата
                if hasattr(chat, 'id') and str(chat.id) in target_chats:
                    print(f"         ✅ Совпадение по Chat ID: {chat.id}")
                    return True
                    
                # Проверка по username чата (с @ и без @)
                if hasattr(chat, 'username') and chat.username:
                    username_variants = [chat.username.lower(), f"@{chat.username.lower()}"]
                    print(f"         🔍 Проверяем username варианты: {username_variants}")
                    for target in target_chats:
                        if target.lower() in username_variants:
                            print(f"         ✅ Совпадение по username: {target} in {username_variants}")
                            return True
            
            # Проверка по ключевым словам
            if campaign.keywords and message.text:
                # campaign.keywords уже список (JSON), не строка
                if isinstance(campaign.keywords, list):
                    keywords = [kw.strip().lower() for kw in campaign.keywords]
                else:
                    # Поддержка старого формата (строка с запятыми)
                    keywords = [kw.strip().lower() for kw in campaign.keywords.split(',')]
                    
                message_text = message.text.lower()
                print(f"         🔍 Проверяем ключевые слова:")
                print(f"            📝 Текст сообщения (lower): '{message_text}'")
                print(f"            🔑 Keywords для поиска: {keywords}")
                
                for keyword in keywords:
                    if keyword in message_text:
                        print(f"         ✅ Найдено ключевое слово: '{keyword}' в '{message_text}'")
                        return True
                    else:
                        print(f"         ❌ Ключевое слово '{keyword}' не найдено")
            else:
                print(f"         ⚠️ Пропускаем проверку keywords: keywords={bool(campaign.keywords)}, message.text={bool(message.text)}")
            
            print(f"         ❌ Сообщение не релевантно для кампании '{campaign.name}'")
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка проверки релевантности: {e}")
            return False
    
    async def _process_message_for_campaign(self, message: Message, chat, campaign: Campaign):
        """Обработка сообщения для конкретной кампании"""
        try:
            # Подготовка контекста
            context = {
                'message': message.text or '',
                'message_obj': message,  # Добавляем объект сообщения для логирования
                'chat_name': getattr(chat, 'title', getattr(chat, 'username', 'Unknown')),
                'chat_id': getattr(chat, 'id', 'Unknown'),
                'sender_id': message.sender_id,
                'date': message.date,
                'campaign': campaign.name
            }
            
            # Генерация ответа через AI
            response = await self._generate_ai_response(context, campaign)
            
            if response:
                # Отправка автоответа
                await self._send_response(message, response, campaign)
            
            # Логирование активности
            await self._log_activity(context, response, campaign)
            
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения для кампании {campaign.name}: {e}")
    
    async def _generate_ai_response(self, context: Dict, campaign: Campaign) -> Optional[str]:
        """Генерация ответа через AI"""
        try:
            # Формирование промпта
            prompt = f"""
            Контекст: {context['message']}
            Чат: {context['chat_name']}
            Кампания: {campaign.name}
            Инструкции: {campaign.system_instruction}
            
            Сгенерируй подходящий ответ согласно инструкциям кампании.
            """
            
            # Использование доступного AI клиента
            if self.openai_client:
                response = await self.openai_client.generate_response(prompt)
                return response
            elif self.claude_client:
                response = await self.claude_client.generate_response(prompt)
                return response
            else:
                print("⚠️ AI клиенты недоступны, используем фоллбэк ответы")
                # Фоллбэк на статичные ответы из кампании
                if campaign.example_replies:
                    message_lower = context.get('message', '').lower()
                    
                    # Простой выбор ответа на основе содержания сообщения
                    if any(word in message_lower for word in ['привет', 'hello', 'hi']):
                        return campaign.example_replies.get('greeting', 'Привет! 👋')
                    elif any(word in message_lower for word in ['спасибо', 'thanks', 'благодарю']):
                        return campaign.example_replies.get('thanks', 'Пожалуйста! 😊')
                    elif any(word in message_lower for word in ['помощь', 'help', 'вопрос', 'задача']):
                        return campaign.example_replies.get('help', 'Конечно, помогу! 🤔')
                    else:
                        # Возвращаем базовый ответ
                        return "Привет! Я получил ваше сообщение. В данный момент AI временно недоступен, но я все равно здесь! 🤖"
                else:
                    return "Привет! Я вижу ваше сообщение. Спасибо за обращение! 👋"
                
        except Exception as e:
            print(f"❌ Ошибка генерации AI ответа: {e}")
            return None
    
    async def _send_response(self, original_message: Message, response: str, campaign: Campaign):
        """Отправка ответа"""
        try:
            # Отправляем ответ на сообщение (самый простой способ)
            await original_message.reply(response)
            print(f"✅ Ответ отправлен для кампании: {campaign.name}")
            
        except Exception as e:
            print(f"❌ Ошибка отправки ответа: {e}")
    
    async def _log_activity(self, context: Dict, response: Optional[str], campaign: Campaign):
        """Логирование активности"""
        try:
            db = SessionLocal()
            
            # Находим какое ключевое слово сработало
            trigger_keyword = "unknown"
            if campaign.keywords and context.get('message'):
                message_lower = context['message'].lower()
                keywords = campaign.keywords if isinstance(campaign.keywords, list) else campaign.keywords.split(',')
                for keyword in keywords:
                    if keyword.strip().lower() in message_lower:
                        trigger_keyword = keyword.strip()
                        break
            
            log_entry = ActivityLog(
                campaign_id=campaign.id,
                chat_id=str(context['chat_id']),
                chat_title=context.get('chat_name', 'Unknown'),
                message_id=getattr(context.get('message_obj'), 'id', 0),
                trigger_keyword=trigger_keyword,
                original_message=context['message'][:1000] if context.get('message') else '',
                agent_response=response[:1000] if response else 'No response',
                status='sent' if response else 'failed'
            )
            
            db.add(log_entry)
            db.commit()
            db.close()
            
        except Exception as e:
            print(f"❌ Ошибка логирования: {e}")
    
    async def update_campaigns(self):
        """Обновление списка активных кампаний"""
        try:
            current_time = time.time()
            
            # Проверяем, нужно ли обновлять кэш
            if current_time - self.last_campaign_update < self.campaign_cache_ttl:
                return
            
            db = SessionLocal()
            campaigns = db.query(Campaign).filter(Campaign.active == True).all()
            
            self.active_campaigns = campaigns
            self.last_campaign_update = current_time
            
            print(f"✅ Загружено активных кампаний: {len(campaigns)}")
            
            db.close()
            
        except Exception as e:
            print(f"❌ Ошибка обновления кампаний: {e}")
    
    async def get_status(self) -> Dict:
        """Получение статуса агента"""
        return {
            "connected": self.is_connected,
            "authorized": self.is_authorized,
            "active_campaigns": len(self.active_campaigns),
            "session_type": "StringSession" if self.session_string else "FileSession",
            "ai_clients": {
                "openai": self.openai_client is not None,
                "claude": self.claude_client is not None
            }
        }
    
    async def stop(self):
        """Остановка агента"""
        try:
            if self.is_connected:
                await self.client.disconnect()
                self.is_connected = False
                self.is_authorized = False
                print("✅ Telegram Agent остановлен")
        except Exception as e:
            print(f"❌ Ошибка остановки агента: {e}")


# Глобальная переменная для хранения экземпляра агента
telegram_agent_instance = None

async def get_telegram_agent():
    """Получение экземпляра агента (Singleton)"""
    global telegram_agent_instance
    
    if telegram_agent_instance is None:
        telegram_agent_instance = TelegramAgentAppPlatform()
        await telegram_agent_instance.start()
    
    return telegram_agent_instance

async def stop_telegram_agent():
    """Остановка агента"""
    global telegram_agent_instance
    
    if telegram_agent_instance:
        await telegram_agent_instance.stop()
        telegram_agent_instance = None