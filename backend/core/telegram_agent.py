import asyncio
import os
import time
from typing import List, Dict, Optional
from datetime import datetime

from telethon import TelegramClient, events
from telethon.tl.types import Message, User, Chat, Channel
from sqlalchemy.orm import Session

from database.models.base import SessionLocal
from database.models.campaign import Campaign
from database.models.log import ActivityLog

# Встроенные AI клиенты (заменяют utils.*)
class SimpleClaudeClient:
    """Простой Claude клиент"""
    def __init__(self):
        try:
            import anthropic
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if self.api_key:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                print("Claude клиент инициализирован")
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
                print("OpenAI клиент инициализирован")
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

# Алиасы для совместимости
ClaudeClient = SimpleClaudeClient
OpenAIClient = SimpleOpenAIClient
ZepMemoryManager = None  # Заглушка


class TelegramAgent:
    """
    Основной класс Telegram-агента для мониторинга чатов и генерации ответов
    """
    
    def __init__(self):
        self.api_id = int(os.getenv("TELEGRAM_API_ID"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        
        # Инициализация клиентов
        self.client = TelegramClient("telegram_agent", self.api_id, self.api_hash)
        
        # AI клиенты - инициализируем с обработкой ошибок
        try:
            self.claude_client = ClaudeClient()
            print("✅ Claude Client доступен")
        except Exception as e:
            print(f"⚠️ Claude Client недоступен: {e}")
            self.claude_client = None
        
        try:
            self.openai_client = OpenAIClient()
            print("✅ OpenAI Client доступен")
        except Exception as e:
            print(f"⚠️ OpenAI Client недоступен: {e}")
            self.openai_client = None
        
        # Memory manager временно отключен
        self.memory_manager = None
        
        # Кэш активных кампаний
        self.active_campaigns: List[Campaign] = []
        self.last_cache_update = 0
        self.cache_ttl = 10  # 10 секунд для быстрого отклика на изменения
        self.force_refresh = False  # Флаг принудительного обновления
        
        print("🤖 Telegram Agent инициализирован")
    
    async def initialize(self):
        """Инициализация соединения с Telegram"""
        try:
            await self.client.start(phone=self.phone)
            print(f"✅ Подключен к Telegram как {self.phone}")
            
            # Регистрация обработчиков событий
            self.client.add_event_handler(self.handle_new_message, events.NewMessage)
            
            # Загрузка активных кампаний
            await self.refresh_campaigns_cache()
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка подключения к Telegram: {e}")
            return False
    
    async def disconnect(self):
        """Отключение от Telegram"""
        if self.client.is_connected():
            await self.client.disconnect()
            print("👋 Отключен от Telegram")
    
    def is_connected(self) -> bool:
        """Проверка соединения с Telegram"""
        return self.client.is_connected()
    
    async def refresh_campaigns_cache(self, force: bool = False):
        """Обновление кэша активных кампаний"""
        current_time = time.time()
        
        # Проверка TTL кэша или принудительного обновления
        if not force and not self.force_refresh and current_time - self.last_cache_update < self.cache_ttl:
            return
        
        try:
            db = SessionLocal()
            campaigns = db.query(Campaign).filter(Campaign.active == True).all()
            self.active_campaigns = campaigns
            self.last_cache_update = current_time
            self.force_refresh = False  # Сбрасываем флаг
            
            print(f"🔄 Кэш кампаний обновлен: {len(campaigns)} активных кампаний")
            
        except Exception as e:
            print(f"❌ Ошибка обновления кэша кампаний: {e}")
        finally:
            db.close()
    
    def force_campaigns_refresh(self):
        """Установка флага принудительного обновления кэша"""
        self.force_refresh = True
        print("🔄 Запланировано принудительное обновление кэша кампаний")
    
    async def handle_new_message(self, event):
        """Обработчик новых сообщений"""
        try:
            message: Message = event.message
            
            # Обновление кэша при необходимости
            await self.refresh_campaigns_cache()
            
            # Поиск подходящих кампаний
            matching_campaigns = await self.find_matching_campaigns(message)
            
            # Обработка каждой подходящей кампании
            for campaign in matching_campaigns:
                await self.process_campaign_trigger(campaign, message)
                
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    async def find_matching_campaigns(self, message: Message) -> List[Campaign]:
        """Поиск кампаний, которые должны отреагировать на сообщение"""
        matching_campaigns = []
        
        # Получение ID чата
        chat_id = str(message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') 
                     else message.peer_id.chat_id if hasattr(message.peer_id, 'chat_id')
                     else message.peer_id.user_id)
        
        # Текст сообщения
        message_text = message.text.lower() if message.text else ""
        
        for campaign in self.active_campaigns:
            # Проверка чатов
            if not self.is_chat_monitored(chat_id, campaign.telegram_chats):
                continue
            
            # Проверка ключевых слов
            if not self.contains_keywords(message_text, campaign.keywords):
                continue
            
            matching_campaigns.append(campaign)
        
        return matching_campaigns
    
    def is_chat_monitored(self, chat_id: str, monitored_chats: List[str]) -> bool:
        """Проверка, отслеживается ли чат в кампании"""
        return chat_id in monitored_chats or any(
            chat.startswith('@') and chat[1:] in chat_id for chat in monitored_chats
        )
    
    def contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Проверка наличия ключевых слов в тексте"""
        return any(keyword.lower() in text for keyword in keywords)
    
    async def process_campaign_trigger(self, campaign: Campaign, trigger_message: Message):
        """Обработка триггера кампании"""
        start_time = time.time()
        
        try:
            # Получение контекста предыдущих сообщений
            context_messages = await self.get_context_messages(
                trigger_message,
                campaign.context_messages_count
            )
            
            # Генерация ответа через Claude
            response = await self.generate_response(
                campaign,
                trigger_message,
                context_messages
            )
            
            # Отправка ответа
            await self.send_response(trigger_message, response)
            
            # Логирование успешного ответа
            processing_time = int((time.time() - start_time) * 1000)
            await self.log_activity(
                campaign,
                trigger_message,
                context_messages,
                response,
                "sent",
                processing_time=processing_time
            )
            
            print(f"✅ Ответ отправлен для кампании '{campaign.name}'")
            
        except Exception as e:
            # Логирование ошибки
            processing_time = int((time.time() - start_time) * 1000)
            await self.log_activity(
                campaign,
                trigger_message,
                [],
                "",
                "failed",
                error_message=str(e),
                processing_time=processing_time
            )
            
            print(f"❌ Ошибка обработки кампании '{campaign.name}': {e}")
    
    async def get_context_messages(self, trigger_message: Message, count: int) -> List[Dict]:
        """Получение контекста предыдущих сообщений"""
        try:
            # Получение предыдущих сообщений
            messages = []
            async for message in self.client.iter_messages(
                trigger_message.peer_id,
                limit=count + 1,
                max_id=trigger_message.id
            ):
                if message.id != trigger_message.id:
                    messages.append({
                        "id": message.id,
                        "text": message.text or "",
                        "date": message.date.isoformat(),
                        "from_user": str(message.from_id) if message.from_id else "unknown"
                    })
            
            return messages[:count]  # Обрезаем до нужного количества
            
        except Exception as e:
            print(f"❌ Ошибка получения контекста: {e}")
            return []
    
    async def generate_response(
        self,
        campaign: Campaign,
        trigger_message: Message,
        context_messages: List[Dict]
    ) -> str:
        """Генерация ответа через выбранный AI провайдер"""
        
        # Определяем AI провайдера
        ai_provider = getattr(campaign, 'ai_provider', 'claude')
        
        try:
            if ai_provider == "openai" and self.openai_client:
                response = await self._generate_with_openai(campaign, trigger_message, context_messages)
            elif ai_provider == "claude" and self.claude_client:
                response = await self._generate_with_claude(campaign, trigger_message, context_messages)
            else:
                # Fallback на доступный провайдер
                if self.openai_client:
                    print(f"⚠️ Fallback на OpenAI (Claude недоступен)")
                    response = await self._generate_with_openai(campaign, trigger_message, context_messages)
                elif self.claude_client:
                    print(f"⚠️ Fallback на Claude (OpenAI недоступен)")
                    response = await self._generate_with_claude(campaign, trigger_message, context_messages)
                else:
                    raise Exception("Ни один AI провайдер не доступен")
            
            # Сохранение в память Zep
            await self.memory_manager.add_interaction(
                session_id=f"campaign_{campaign.id}_chat_{trigger_message.peer_id}",
                message=trigger_message.text,
                response=response
            )
            
            return response
            
        except Exception as e:
            print(f"❌ Ошибка генерации ответа: {e}")
            return "Извините, произошла ошибка при генерации ответа."
    
    async def _generate_with_claude(
        self,
        campaign: Campaign,
        trigger_message: Message,
        context_messages: List[Dict]
    ) -> str:
        """Генерация ответа через Claude"""
        
        # Формирование промпта для Claude
        context_text = "\n".join([f"[{msg['date']}] {msg['text']}" for msg in context_messages])
        
        prompt = f"""
Системная инструкция: {campaign.system_instruction}

Контекст предыдущих сообщений:
{context_text}

Сообщение-триггер: {trigger_message.text}

Примеры ответов: {campaign.example_replies if campaign.example_replies else 'Нет примеров'}

Сгенерируй подходящий ответ на основе контекста и системной инструкции.
"""
        
        return await self.claude_client.generate_response(
            prompt,
            campaign.claude_agent_id
        )
    
    async def _generate_with_openai(
        self,
        campaign: Campaign,
        trigger_message: Message,
        context_messages: List[Dict]
    ) -> str:
        """Генерация ответа через OpenAI"""
        
        # Используем специальный метод форматирования для OpenAI
        prompt = self.openai_client.format_telegram_context(
            system_instruction=campaign.system_instruction,
            context_messages=context_messages,
            trigger_message=trigger_message.text,
            example_replies=campaign.example_replies
        )
        
        # Получаем модель OpenAI из кампании
        openai_model = getattr(campaign, 'openai_model', 'gpt-4')
        
        return await self.openai_client.generate_response(
            prompt,
            model=openai_model
        )
    
    async def send_response(self, original_message: Message, response: str):
        """Отправка ответа в чат"""
        try:
            await self.client.send_message(
                original_message.peer_id,
                response,
                reply_to=original_message.id
            )
        except Exception as e:
            print(f"❌ Ошибка отправки ответа: {e}")
            raise
    
    async def log_activity(
        self,
        campaign: Campaign,
        trigger_message: Message,
        context_messages: List[Dict],
        response: str,
        status: str,
        error_message: Optional[str] = None,
        processing_time: Optional[int] = None
    ):
        """Логирование активности агента"""
        try:
            db = SessionLocal()
            
            # Получение информации о чате
            chat_title = "Unknown"
            try:
                entity = await self.client.get_entity(trigger_message.peer_id)
                if hasattr(entity, 'title'):
                    chat_title = entity.title
                elif hasattr(entity, 'username'):
                    chat_title = f"@{entity.username}"
            except:
                pass
            
            # Определение ключевого слова
            trigger_keyword = "unknown"
            if trigger_message.text:
                message_text = trigger_message.text.lower()
                for keyword in campaign.keywords:
                    if keyword.lower() in message_text:
                        trigger_keyword = keyword
                        break
            
            # Создание записи лога
            log_entry = ActivityLog(
                campaign_id=campaign.id,
                chat_id=str(trigger_message.peer_id),
                chat_title=chat_title,
                message_id=trigger_message.id,
                trigger_keyword=trigger_keyword,
                context_messages=context_messages,
                original_message=trigger_message.text or "",
                agent_response=response,
                status=status,
                error_message=error_message,
                processing_time_ms=processing_time
            )
            
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            print(f"❌ Ошибка логирования: {e}")
        finally:
            db.close()