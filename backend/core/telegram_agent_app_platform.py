import asyncio
import os
import time
import base64
import logging
from typing import List, Dict, Optional
from datetime import datetime

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Message, User, Chat, Channel
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest
from sqlalchemy.orm import Session

from database.models.base import SessionLocal
from database.models.campaign import Campaign
from database.models.log import ActivityLog

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Встроенные AI клиенты (заменяют utils.*)
class SimpleClaudeClient:
    """Простой Claude клиент"""
    def __init__(self):
        try:
            import anthropic
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if self.api_key:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Claude клиент инициализирован")
            else:
                self.client = None
        except ImportError:
            self.client = None
            
    async def generate_response(self, prompt: str, **kwargs) -> str:
        if not self.client:
            return "Claude недоступен - проверьте ANTHROPIC_API_KEY и установку anthropic"
        try:
            import asyncio
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Ошибка Claude: {e}"

class SimpleOpenAIClient:
    """Простой OpenAI клиент"""
    def __init__(self):
        try:
            import openai
            self.api_key = os.getenv("OPENAI_API_KEY")
            if self.api_key:
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI клиент инициализирован")
            else:
                self.client = None
        except ImportError:
            self.client = None
            
    async def generate_response(self, prompt: str, **kwargs) -> str:
        if not self.client:
            return "OpenAI недоступен - проверьте OPENAI_API_KEY и установку openai"
        try:
            import asyncio
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка OpenAI: {e}"

# Проверка доступности AI провайдеров
try:
    ClaudeClient = SimpleClaudeClient
    CLAUDE_AVAILABLE = True
except:
    CLAUDE_AVAILABLE = False
    logger.warning("ClaudeClient недоступен")

try:
    OpenAIClient = SimpleOpenAIClient
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAIClient недоступен")

# ZepMemoryManager заменяем на заглушку
ZEP_AVAILABLE = False
ZepMemoryManager = None
logger.info("ZepMemoryManager отключен (не требуется для базовой функциональности)")


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
            logger.info("TelegramClient инициализован с StringSession")
        else:
            # Fallback к файловой сессии для локальной разработки
            self.client = TelegramClient("telegram_agent", self.api_id, self.api_hash)
            logger.warning("Используется файловая сессия (локальная разработка)")
        
        # AI клиенты - инициализируем с обработкой ошибок
        if CLAUDE_AVAILABLE:
            try:
                self.claude_client = ClaudeClient()
                logger.info("Claude Client доступен")
            except Exception as e:
                logger.warning(f"Claude Client недоступен: {e}")
                self.claude_client = None
        else:
            self.claude_client = None
            logger.warning("Claude Client отключен - используем только OpenAI")
        
        try:
            logger.info("Инициализация OpenAI клиента...")
            self.openai_client = OpenAIClient()
            logger.info("OpenAI Client успешно инициализирован")
        except Exception as e:
            logger.error(f"OpenAI Client недоступен: {type(e).__name__}: {str(e)}")
            self.openai_client = None
        
        # Инициализация менеджера памяти (опционально)
        if ZEP_AVAILABLE:
            self.memory_manager = ZepMemoryManager()
            logger.info("ZepMemoryManager инициализирован")
        else:
            self.memory_manager = None
            logger.warning("Работаем без менеджера памяти")
        
        # Кэш активных кампаний
        self.active_campaigns: List[Campaign] = []
        self.last_campaign_update = 0
        self.campaign_cache_ttl = int(os.getenv("CACHE_TTL", "60"))
        
        # Кэш групп обсуждений каналов
        self.channel_discussion_groups: Dict[str, int] = {}
        
        # Статус подключения
        self.is_connected = False
        self.is_authorized = False
    
    def _get_session_from_env(self) -> Optional[str]:
        """Получение сессии из переменных окружения"""
        # Попробуем получить прямую строку сессии
        session_string = os.getenv("TELEGRAM_SESSION_STRING")
        if session_string:
            logger.info("Найдена TELEGRAM_SESSION_STRING")
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
        
        logger.warning("Сессия в переменных окружения не найдена")
        return None
    
    async def get_channel_discussion_group(self, channel_identifier: str) -> Optional[int]:
        """Получение ID группы обсуждений канала"""
        try:
            # Проверяем кэш
            if channel_identifier in self.channel_discussion_groups:
                return self.channel_discussion_groups[channel_identifier]
            
            
            # Получаем объект канала
            channel = await self.client.get_entity(channel_identifier)
            
            # Получаем полную информацию о канале
            full_channel = await self.client(GetFullChannelRequest(channel))
            
            # Проверяем наличие linked_chat_id (группа обсуждений)
            if hasattr(full_channel.full_chat, 'linked_chat_id') and full_channel.full_chat.linked_chat_id:
                discussion_group_id = full_channel.full_chat.linked_chat_id
                
                # Кэшируем результат
                self.channel_discussion_groups[channel_identifier] = discussion_group_id
                
                print(f"✅ Найдена группа обсуждений для {channel_identifier}: {discussion_group_id}")
                
                # Дополнительная диагностика доступа к группе обсуждений
                try:
                    discussion_entity = await self.client.get_entity(discussion_group_id)
                    print(f"   📋 Название: {getattr(discussion_entity, 'title', 'None')}")
                    print(f"   🔒 Тип: {type(discussion_entity)}")
                    print(f"   👥 Участников: {getattr(discussion_entity, 'participants_count', 'Unknown')}")
                    
                    # Попробуем получить последние сообщения
                    messages_count = 0
                    async for message in self.client.iter_messages(discussion_entity, limit=5):
                        messages_count += 1
                    
                    if messages_count == 0:
                        logger.warning("   Нет доступных сообщений в группе обсуждений")
                    else:
                        logger.info(f"   Найдено {messages_count} сообщений в группе обсуждений")
                    
                    # Попробуем активировать участие в группе обсуждений
                    try:
                        print(f"   🔧 Попытка активации участия в группе обсуждений...")
                        activation_message = "🤖 Bot activation - starting to monitor comments"
                        await self.client.send_message(discussion_entity, activation_message)
                        print(f"   ✅ Активационное сообщение отправлено в группу обсуждений")
                    except Exception as activation_error:
                        print(f"   ⚠️ Не удалось отправить активационное сообщение: {activation_error}")
                        print(f"   💡 Это нормально - бот будет работать после первого сообщения пользователя")
                        
                except Exception as diag_error:
                    print(f"   ❌ Ошибка диагностики группы обсуждений: {diag_error}")
                
                return discussion_group_id
            else:
                print(f"⚠️ У канала {channel_identifier} нет группы обсуждений")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка получения группы обсуждений для {channel_identifier}: {e}")
            return None
    
    async def start(self):
        """Запуск агента"""
        try:
            logger.info("Подключение к Telegram...")
            await self.client.connect()
            self.is_connected = True
            
            # Проверка авторизации
            self.is_authorized = await self.client.is_user_authorized()
            
            if self.is_authorized:
                logger.info("Telegram авторизация активна")
                
                # Получение информации о пользователе
                me = await self.client.get_me()
                logger.info(f"Пользователь: {me.first_name} {me.last_name or ''}, телефон: {me.phone}")
                
                # Настройка обработчиков событий
                await self._setup_event_handlers()
                
                # Загрузка активных кампаний
                await self.update_campaigns()
                
                # Определение групп обсуждений для каналов в кампаниях
                await self.discover_discussion_groups()
                
                # Принудительное подключение к группам обсуждений
                await self.join_discussion_groups()
                
                logger.info("Telegram Agent запущен и готов к работе!")
                return True
            else:
                logger.error("Telegram не авторизован. Требуется настройка TELEGRAM_SESSION_STRING")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка запуска Telegram Agent: {e}")
            self.is_connected = False
            self.is_authorized = False
            return False
    
    async def _setup_event_handlers(self):
        """Настройка обработчиков событий"""
        # Собираем все ID групп обсуждений для мониторинга
        discussion_group_ids = []
        
        # Получаем группы обсуждений из кампаний
        for campaign in self.active_campaigns:
            if campaign.telegram_chats:
                for chat in campaign.telegram_chats:
                    # Если это число, считаем что это ID группы обсуждений
                    if isinstance(chat, str) and chat.isdigit():
                        discussion_group_ids.append(int(chat))
                    elif isinstance(chat, int):
                        discussion_group_ids.append(chat)
        
        # Добавляем известную группу обсуждений
        if 2532661483 not in discussion_group_ids:
            discussion_group_ids.append(2532661483)
        
        logger.info(f"Настройка мониторинга для групп обсуждений: {discussion_group_ids}")
        
        # Обработчик СПЕЦИАЛЬНО для групп обсуждений
        @self.client.on(events.NewMessage(chats=discussion_group_ids, incoming=True))
        async def handle_discussion_message(event):
            await self._handle_message(event)
        
        # Обработчик для редактирования сообщений в группах обсуждений
        @self.client.on(events.MessageEdited(chats=discussion_group_ids, incoming=True))
        async def handle_discussion_edited(event):
            await self._handle_message(event)
        
        # Общий обработчик как fallback (но с меньшим приоритетом)
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_general_message(event):
            # Проверяем, не из группы обсуждений ли это (чтобы избежать дублирования)
            chat = await event.get_chat()
            chat_id = getattr(chat, 'id', None)
            if chat_id not in discussion_group_ids:
                await self._handle_message(event)
        
        # Дополнительный debug обработчик для ВСЕХ событий
        @self.client.on(events.Raw)
        async def handle_raw_event(event):
            # Логируем только значимые события
            event_type = type(event).__name__
            if event_type not in ['UpdateUserStatus', 'UpdateReadHistoryInbox', 'UpdateReadHistoryOutbox']:
                logger.debug(f"Raw event: {event_type}")
        
        logger.info(f"Обработчики событий настроены (специально для {len(discussion_group_ids)} групп обсуждений + общий fallback)")
    
    async def _handle_message(self, event):
        """Обработка нового сообщения"""
        try:
            message = event.message
            chat = await event.get_chat()
            
            # Проверка является ли это комментарием
            is_comment = hasattr(message, 'reply_to_msg_id') and message.reply_to_msg_id is not None
            
            logger.debug(f"Получено сообщение: текст='{message.text[:50] if message.text else 'None'}...', " +
                        f"чат={getattr(chat, 'title', getattr(chat, 'username', 'Unknown'))}, " +
                        f"от={message.sender_id}, комментарий={is_comment}")
            
            if is_comment:
                logger.info(f"Обнаружен комментарий к сообщению ID: {message.reply_to_msg_id}")
            
            # Проверяем, есть ли активные кампании для этого чата
            relevant_campaigns = []
            for campaign in self.active_campaigns:
                if self._is_message_relevant(message, chat, campaign, is_comment):
                    relevant_campaigns.append(campaign)
                    logger.debug(f"Кампания {campaign.name} релевантна для сообщения")
            
            if not relevant_campaigns:
                return
            
            # Обработка сообщения для каждой релевантной кампании
            for campaign in relevant_campaigns:
                await self._process_message_for_campaign(message, chat, campaign, is_comment, event)
                
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    def _is_message_relevant(self, message: Message, chat, campaign: Campaign, is_comment: bool = False) -> bool:
        """Проверка релевантности сообщения для кампании"""
        try:
            # DEBUG: Подробное логирование проверки релевантности
            logger.debug(f"Проверка релевантности для кампании '{campaign.name}': " +
                        f"чат_ID={getattr(chat, 'id', 'None')}, " +
                        f"username={getattr(chat, 'username', 'None')}, " +
                        f"комментарий={is_comment}")
            
            # Логика проверки чата
            chat_matches = False
            
            # Получаем target_chats
            target_chats = campaign.telegram_chats if isinstance(campaign.telegram_chats, list) else campaign.telegram_chats.split(',')
            # Проверка по ID чата/канала и username
            if hasattr(chat, 'id') or (hasattr(chat, 'username') and chat.username):
                # Проверка по ID чата
                if hasattr(chat, 'id') and str(chat.id) in target_chats:
                    chat_matches = True
                    
                # Проверка по username чата (с @ и без @)
                if hasattr(chat, 'username') and chat.username:
                    username_variants = [chat.username.lower(), f"@{chat.username.lower()}"]
                    for target in target_chats:
                        if target.lower() in username_variants:
                            chat_matches = True
                            break
            
            # Дополнительная проверка для групп обсуждений
            if not chat_matches and hasattr(chat, 'id'):
                chat_id = getattr(chat, 'id', None)
                # Проверяем, является ли этот чат группой обсуждений одного из каналов
                for target_chat in target_chats:
                    if target_chat.startswith('@'):
                        discussion_group_id = self.channel_discussion_groups.get(target_chat)
                        if discussion_group_id and chat_id == discussion_group_id:
                            chat_matches = True
                            break
            
            # Если чат не подходит, сразу отклоняем
            if not chat_matches:
                print(f"         ❌ Чат не соответствует кампании")
                return False
            
            # Проверка по ключевым словам
            if campaign.keywords and message.text:
                # campaign.keywords уже список (JSON), не строка
                if isinstance(campaign.keywords, list):
                    keywords = [kw.strip().lower() for kw in campaign.keywords]
                else:
                    # Поддержка старого формата (строка с запятыми)
                    keywords = [kw.strip().lower() for kw in campaign.keywords.split(',')]
                    
                message_text = message.text.lower()
                print(f"            📝 Текст сообщения (lower): '{message_text}'")
                print(f"            🔑 Keywords для поиска: {keywords}")
                
                for keyword in keywords:
                    if keyword in message_text:
                        print(f"         ✅ Найдено ключевое слово: '{keyword}' в '{message_text}'")
                        return True
                    else:
                        logger.debug(f"         Ключевое слово '{keyword}' не найдено")
            else:
                print(f"         ⚠️ Пропускаем проверку keywords: keywords={bool(campaign.keywords)}, message.text={bool(message.text)}")
            
            print(f"         ❌ Сообщение не релевантно для кампании '{campaign.name}'")
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка проверки релевантности: {e}")
            return False
    
    async def _process_message_for_campaign(self, message: Message, chat, campaign: Campaign, is_comment: bool = False, event=None):
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
                'campaign': campaign.name,
                'is_comment': is_comment,
                'reply_to_msg_id': getattr(message, 'reply_to_msg_id', None) if is_comment else None
            }
            
            # Генерация ответа через AI
            response = await self._generate_ai_response(context, campaign)
            
            if response:
                # Отправка автоответа с передачей event для правильного ответа на комментарии
                await self._send_response(message, response, campaign, is_comment, event)
            
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
    
    async def _send_response(self, original_message: Message, response: str, campaign: Campaign, is_comment: bool = False, event=None):
        """Отправка ответа"""
        try:
            if is_comment and event:
                # Для комментариев используем event.respond() с comment_to (правильный метод по документации)
                await event.respond(response, comment_to=original_message.id)
            elif is_comment:
                # Fallback для комментариев, если нет event
                print(f"💬 Отправка ответа на комментарий через reply (fallback)")
                await original_message.reply(response)
            else:
                # Для обычных сообщений используем reply
                await original_message.reply(response)
                print(f"✅ Обычный ответ отправлен для кампании: {campaign.name}")
            
        except Exception as e:
            print(f"❌ Ошибка отправки ответа (is_comment={is_comment}): {e}")
            
            # Fallback: попробуем альтернативный способ отправки
            try:
                if is_comment:
                    # Альтернативный способ для комментариев - обычный reply
                    print(f"🔄 Попытка альтернативной отправки комментария через reply")
                    await original_message.reply(response)
                    print(f"✅ Альтернативная отправка ответа на комментарий успешна")
                else:
                    # Альтернативный способ для обычных сообщений
                    print(f"🔄 Попытка альтернативной отправки через send_message")
                    await self.client.send_message(
                        entity=original_message.chat_id,
                        message=response
                    )
                    print(f"✅ Альтернативная отправка обычного ответа успешна")
            except Exception as fallback_error:
                print(f"❌ Альтернативная отправка также не удалась: {fallback_error}")
    
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
            
            # Определяем тип сообщения для логирования
            message_type = "comment" if context.get('is_comment') else "message"
            chat_title = context.get('chat_name', 'Unknown')
            if context.get('is_comment'):
                chat_title += " (Discussion Group)"
            
            log_entry = ActivityLog(
                campaign_id=campaign.id,
                chat_id=str(context['chat_id']),
                chat_title=chat_title,
                message_id=getattr(context.get('message_obj'), 'id', 0),
                trigger_keyword=f"{trigger_keyword} ({message_type})",
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
    
    async def discover_discussion_groups(self):
        """Обнаружение групп обсуждений для всех каналов в кампаниях"""
        try:
            print("🔍 Обнаружение групп обсуждений для каналов...")
            
            # Собираем все уникальные каналы из кампаний
            all_channels = set()
            for campaign in self.active_campaigns:
                if campaign.telegram_chats:
                    for chat in campaign.telegram_chats:
                        # Проверяем, является ли это каналом (начинается с @)
                        if isinstance(chat, str) and chat.startswith('@'):
                            all_channels.add(chat)
            
            print(f"📋 Найдено каналов для проверки: {list(all_channels)}")
            
            # Получаем группы обсуждений для каждого канала
            for channel in all_channels:
                discussion_group_id = await self.get_channel_discussion_group(channel)
                if discussion_group_id:
                    print(f"✅ Канал {channel} → Группа обсуждений: {discussion_group_id}")
                else:
                    print(f"⚠️ Канал {channel} не имеет группы обсуждений")
            
            print(f"📊 Всего найдено групп обсуждений: {len(self.channel_discussion_groups)}")
            
        except Exception as e:
            print(f"❌ Ошибка обнаружения групп обсуждений: {e}")
    
    async def join_discussion_groups(self):
        """Принудительное подключение к группам обсуждений для получения обновлений"""
        try:
            print("🔗 Принудительное подключение к группам обсуждений...")
            
            joined_count = 0
            
            # Подключаемся ко всем известным группам обсуждений
            for channel_identifier, discussion_group_id in self.channel_discussion_groups.items():
                try:
                    print(f"🔗 Подключение к группе обсуждений {discussion_group_id} для канала {channel_identifier}...")
                    
                    # Получаем entity группы обсуждений
                    discussion_entity = await self.client.get_entity(discussion_group_id)
                    
                    # Пытаемся присоединиться
                    try:
                        await self.client(JoinChannelRequest(discussion_entity))
                        print(f"   ✅ Присоединились к группе обсуждений {discussion_group_id}")
                        joined_count += 1
                    except Exception as join_error:
                        # Если не можем присоединиться (например, уже участник), это нормально
                        if "already" in str(join_error).lower() or "participant" in str(join_error).lower():
                            print(f"   ✅ Уже участник группы обсуждений {discussion_group_id}")
                            joined_count += 1
                        else:
                            print(f"   ⚠️ Не удалось присоединиться к группе {discussion_group_id}: {join_error}")
                    
                    # Дополнительно: отправляем silent ping для активации
                    try:
                        await self.client.send_message(
                            discussion_entity, 
                            "🔔 Активация мониторинга комментариев",
                            silent=True  # Без уведомлений
                        )
                        print(f"   📡 Активационное сообщение отправлено в группу {discussion_group_id}")
                    except Exception as ping_error:
                        print(f"   ⚠️ Не удалось отправить активационное сообщение: {ping_error}")
                        
                except Exception as entity_error:
                    print(f"   ❌ Ошибка получения entity группы {discussion_group_id}: {entity_error}")
            
            print(f"📊 Результат подключения к группам обсуждений: {joined_count}/{len(self.channel_discussion_groups)}")
            
            # Дополнительно: попробуем подключиться к основной группе обсуждений, если её нет в списке
            main_discussion_id = 2532661483
            if main_discussion_id not in [group_id for group_id in self.channel_discussion_groups.values()]:
                try:
                    print(f"🔗 Дополнительное подключение к основной группе обсуждений {main_discussion_id}...")
                    main_entity = await self.client.get_entity(main_discussion_id)
                    
                    try:
                        await self.client(JoinChannelRequest(main_entity))
                        print(f"   ✅ Присоединились к основной группе обсуждений")
                    except Exception as main_join_error:
                        if "already" in str(main_join_error).lower():
                            print(f"   ✅ Уже участник основной группы обсуждений")
                        else:
                            print(f"   ⚠️ Не удалось присоединиться к основной группе: {main_join_error}")
                            
                except Exception as main_error:
                    print(f"   ❌ Ошибка подключения к основной группе: {main_error}")
            
        except Exception as e:
            print(f"❌ Ошибка принудительного подключения к группам обсуждений: {e}")
    
    async def get_status(self) -> Dict:
        """Получение статуса агента"""
        # Test OpenAI client if it exists
        openai_working = False
        if self.openai_client:
            try:
                # Simple test
                openai_working = self.openai_client.test_connection()
            except:
                openai_working = False
        
        return {
            "connected": self.is_connected,
            "authorized": self.is_authorized,
            "active_campaigns": len(self.active_campaigns),
            "session_type": "StringSession" if self.session_string else "FileSession",
            "ai_clients": {
                "openai": self.openai_client is not None,
                "openai_working": openai_working,
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