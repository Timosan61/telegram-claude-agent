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
from utils.claude.client import ClaudeClient
from utils.zep.memory import ZepMemoryManager


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
        self.claude_client = ClaudeClient()
        self.memory_manager = ZepMemoryManager()
        
        # Кэш активных кампаний
        self.active_campaigns: List[Campaign] = []
        self.last_cache_update = 0
        self.cache_ttl = 60  # 60 секунд
        
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
    
    async def refresh_campaigns_cache(self):
        """Обновление кэша активных кампаний"""
        current_time = time.time()
        
        # Проверка TTL кэша
        if current_time - self.last_cache_update < self.cache_ttl:
            return
        
        try:
            db = SessionLocal()
            campaigns = db.query(Campaign).filter(Campaign.active == True).all()
            self.active_campaigns = campaigns
            self.last_cache_update = current_time
            
            print(f"🔄 Кэш кампаний обновлен: {len(campaigns)} активных кампаний")
            
        except Exception as e:
            print(f"❌ Ошибка обновления кэша кампаний: {e}")
        finally:
            db.close()
    
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
        """Генерация ответа через Claude Code SDK"""
        
        # Формирование промпта
        context_text = "\n".join([f"[{msg['date']}] {msg['text']}" for msg in context_messages])
        
        prompt = f"""
Системная инструкция: {campaign.system_instruction}

Контекст предыдущих сообщений:
{context_text}

Сообщение-триггер: {trigger_message.text}

Примеры ответов: {campaign.example_replies if campaign.example_replies else 'Нет примеров'}

Сгенерируй подходящий ответ на основе контекста и системной инструкции.
"""
        
        # Получение ответа от Claude
        response = await self.claude_client.generate_response(
            prompt,
            campaign.claude_agent_id
        )
        
        # Сохранение в память Zep
        await self.memory_manager.add_interaction(
            session_id=f"campaign_{campaign.id}_chat_{trigger_message.peer_id}",
            message=trigger_message.text,
            response=response
        )
        
        return response
    
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