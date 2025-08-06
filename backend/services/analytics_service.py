import os
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import csv
import io

from telethon import TelegramClient
from telethon.tl.types import Message, User, Chat, Channel
from telethon.errors import FloodWaitError, ChannelPrivateError
from sqlalchemy.orm import Session

from database.models.base import get_db
from database.models.campaign import Campaign


@dataclass
class AnalyticsConfig:
    """Конфигурация для анализа чата"""
    chat_id: str
    chat_username: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit_messages: int = 1000
    include_media: bool = False
    include_replies: bool = True
    analyze_participants: bool = True
    keywords_filter: Optional[List[str]] = None


@dataclass
class ChatAnalytics:
    """Результаты анализа чата"""
    chat_info: Dict[str, Any]
    message_stats: Dict[str, Any]
    participant_stats: Dict[str, Any]
    time_analysis: Dict[str, Any]
    keyword_analysis: Dict[str, Any]
    media_analysis: Dict[str, Any]
    export_data: List[Dict[str, Any]]


class AnalyticsService:
    """Сервис для аналитики Telegram чатов"""
    
    def __init__(self):
        # Безопасная инициализация с проверкой переменных окружения
        api_id_str = os.getenv("TELEGRAM_API_ID")
        self.api_id = int(api_id_str) if api_id_str else None
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        
        # Инициализация Telegram клиента только если есть все необходимые данные
        if self.api_id and self.api_hash:
            self.client = TelegramClient("analytics_session", self.api_id, self.api_hash)
        else:
            self.client = None
            print("⚠️ Analytics Service: Telegram API credentials не настроены")
        
        self.is_connected = False
    
    async def initialize(self) -> bool:
        """Инициализация соединения с Telegram"""
        if not self.client:
            print("⚠️ Analytics Service: Нет Telegram клиента для инициализации")
            return False
        
        try:
            await self.client.start(phone=self.phone)
            self.is_connected = True
            print("✅ Analytics Service подключен к Telegram")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения Analytics Service к Telegram: {e}")
            return False
    
    async def disconnect(self):
        """Отключение от Telegram"""
        if self.client and self.client.is_connected():
            await self.client.disconnect()
            self.is_connected = False
            print("👋 Analytics Service отключен от Telegram")
    
    async def get_available_chats(self) -> List[Dict[str, Any]]:
        """Получить список доступных чатов для анализа"""
        if not self.client:
            return []
        
        if not self.is_connected:
            await self.initialize()
        
        if not self.is_connected:
            return []
        
        try:
            chats = []
            
            # Получаем диалоги
            async for dialog in self.client.iter_dialogs():
                chat_info = {
                    "id": str(dialog.id),
                    "title": dialog.title,
                    "username": getattr(dialog.entity, 'username', None),
                    "type": "channel" if dialog.is_channel else "group" if dialog.is_group else "user",
                    "participant_count": getattr(dialog.entity, 'participants_count', None),
                    "is_private": getattr(dialog.entity, 'access_hash', None) is None
                }
                chats.append(chat_info)
            
            return chats
            
        except Exception as e:
            print(f"❌ Ошибка получения списка чатов: {e}")
            return []
    
    async def get_channel_info(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о канале/чате для предпросмотра
        
        Args:
            channel_name: Название канала (@channel, username, или ID)
        
        Returns:
            Словарь с информацией о канале или None если не найден
        """
        if not self.client:
            return None
        
        if not self.is_connected:
            await self.initialize()
            
        if not self.is_connected:
            return None
        
        try:
            # Нормализуем имя канала
            if channel_name.isdigit():
                # Если это число, используем как ID
                entity = await self.client.get_entity(int(channel_name))
            elif channel_name.startswith('@'):
                # Убираем @ если есть
                entity = await self.client.get_entity(channel_name)
            else:
                # Добавляем @ если нет
                entity = await self.client.get_entity(f"@{channel_name}")
            
            # Получаем детальную информацию
            channel_info = {
                "id": str(entity.id),
                "title": getattr(entity, 'title', 'Private Chat'),
                "username": getattr(entity, 'username', None),
                "type": type(entity).__name__,
                "participant_count": getattr(entity, 'participants_count', None),
                "description": getattr(entity, 'about', None),
                "created_date": getattr(entity, 'date', None),
                "access_hash": getattr(entity, 'access_hash', None) is not None,
                "verified": getattr(entity, 'verified', False),
                "restricted": getattr(entity, 'restricted', False),
                "scam": getattr(entity, 'scam', False)
            }
            
            # Получаем дополнительную информацию о канале
            try:
                # Пробуем получить последнее сообщение для проверки доступности
                async for message in self.client.iter_messages(entity, limit=1):
                    channel_info["last_message_date"] = message.date.isoformat() if message.date else None
                    channel_info["accessible"] = True
                    break
                else:
                    channel_info["accessible"] = False
            except Exception:
                channel_info["accessible"] = False
                
            return channel_info
            
        except ChannelPrivateError:
            return {
                "error": "Канал приватный или недоступен",
                "accessible": False
            }
        except Exception as e:
            print(f"❌ Ошибка получения информации о канале {channel_name}: {e}")
            return {
                "error": f"Канал не найден: {str(e)}",
                "accessible": False
            }
    
    async def analyze_chat(self, config: AnalyticsConfig) -> ChatAnalytics:
        """Выполнить анализ чата"""
        if not self.client:
            # Возвращаем пустой результат с ошибкой
            return ChatAnalytics(
                chat_info={"error": "Analytics Service не инициализирован - отсутствуют Telegram API credentials"},
                message_stats={},
                participant_stats={},
                time_analysis={},
                keyword_analysis={},
                media_analysis={},
                export_data=[]
            )
        
        if not self.is_connected:
            await self.initialize()
            
        if not self.is_connected:
            return ChatAnalytics(
                chat_info={"error": "Не удалось подключиться к Telegram API"},
                message_stats={},
                participant_stats={},
                time_analysis={},
                keyword_analysis={},
                media_analysis={},
                export_data=[]
            )
        
        try:
            # Получаем информацию о чате
            chat_entity = await self._get_chat_entity(config.chat_id, config.chat_username)
            chat_info = await self._get_chat_info(chat_entity)
            
            # Получаем сообщения
            messages = await self._get_messages(chat_entity, config)
            
            # Анализируем данные
            message_stats = self._analyze_messages(messages)
            participant_stats = await self._analyze_participants(messages, config.analyze_participants)
            time_analysis = self._analyze_time_patterns(messages)
            keyword_analysis = self._analyze_keywords(messages, config.keywords_filter)
            media_analysis = self._analyze_media(messages)
            
            # Подготавливаем данные для экспорта
            export_data = self._prepare_export_data(messages)
            
            return ChatAnalytics(
                chat_info=chat_info,
                message_stats=message_stats,
                participant_stats=participant_stats,
                time_analysis=time_analysis,
                keyword_analysis=keyword_analysis,
                media_analysis=media_analysis,
                export_data=export_data
            )
            
        except ChannelPrivateError:
            raise Exception("Нет доступа к приватному каналу")
        except FloodWaitError as e:
            raise Exception(f"Превышен лимит запросов. Подождите {e.seconds} секунд")
        except Exception as e:
            raise Exception(f"Ошибка анализа чата: {e}")
    
    async def _get_chat_entity(self, chat_id: str, chat_username: Optional[str]):
        """Получить сущность чата"""
        try:
            if chat_username:
                return await self.client.get_entity(chat_username)
            else:
                return await self.client.get_entity(int(chat_id))
        except Exception as e:
            raise Exception(f"Чат не найден: {e}")
    
    async def _get_chat_info(self, chat_entity) -> Dict[str, Any]:
        """Получить информацию о чате"""
        return {
            "id": str(chat_entity.id),
            "title": getattr(chat_entity, 'title', 'Private Chat'),
            "username": getattr(chat_entity, 'username', None),
            "type": type(chat_entity).__name__,
            "participant_count": getattr(chat_entity, 'participants_count', None),
            "description": getattr(chat_entity, 'about', None),
            "created_date": getattr(chat_entity, 'date', None)
        }
    
    async def _get_messages(self, chat_entity, config: AnalyticsConfig) -> List[Message]:
        """Получить сообщения чата"""
        messages = []
        
        try:
            async for message in self.client.iter_messages(
                chat_entity,
                limit=config.limit_messages,
                offset_date=config.end_date,
                reverse=False
            ):
                # Фильтр по дате
                if config.start_date and message.date < config.start_date:
                    break
                if config.end_date and message.date > config.end_date:
                    continue
                
                # Фильтр по ответам
                if not config.include_replies and message.reply_to:
                    continue
                
                messages.append(message)
            
            return messages
            
        except Exception as e:
            print(f"❌ Ошибка получения сообщений: {e}")
            return []
    
    def _analyze_messages(self, messages: List[Message]) -> Dict[str, Any]:
        """Анализ сообщений"""
        if not messages:
            return {"total": 0}
        
        total_messages = len(messages)
        text_messages = sum(1 for msg in messages if msg.text)
        media_messages = sum(1 for msg in messages if msg.media)
        forward_messages = sum(1 for msg in messages if msg.forward)
        reply_messages = sum(1 for msg in messages if msg.reply_to)
        
        # Анализ длины сообщений
        text_lengths = [len(msg.text or "") for msg in messages if msg.text]
        avg_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
        
        # Анализ периода
        dates = [msg.date for msg in messages if msg.date]
        date_range = {
            "start": min(dates).isoformat() if dates else None,
            "end": max(dates).isoformat() if dates else None,
            "days": (max(dates) - min(dates)).days + 1 if dates else 0
        }
        
        return {
            "total": total_messages,
            "text_messages": text_messages,
            "media_messages": media_messages,
            "forward_messages": forward_messages,
            "reply_messages": reply_messages,
            "avg_message_length": round(avg_length, 2),
            "date_range": date_range,
            "messages_per_day": round(total_messages / max(date_range["days"], 1), 2) if date_range["days"] else 0
        }
    
    async def _analyze_participants(self, messages: List[Message], analyze: bool) -> Dict[str, Any]:
        """Анализ участников"""
        if not analyze or not messages:
            return {"analyzed": False}
        
        # Подсчет сообщений по участникам
        participant_counts = {}
        participant_info = {}
        
        for message in messages:
            if message.from_id:
                user_id = str(message.from_id.user_id if hasattr(message.from_id, 'user_id') else message.from_id)
                participant_counts[user_id] = participant_counts.get(user_id, 0) + 1
                
                # Получаем информацию о пользователе
                if user_id not in participant_info:
                    try:
                        user = await self.client.get_entity(int(user_id))
                        participant_info[user_id] = {
                            "id": user_id,
                            "username": getattr(user, 'username', None),
                            "first_name": getattr(user, 'first_name', ''),
                            "last_name": getattr(user, 'last_name', ''),
                            "is_bot": getattr(user, 'bot', False)
                        }
                    except Exception:
                        participant_info[user_id] = {
                            "id": user_id,
                            "username": None,
                            "first_name": "Unknown",
                            "last_name": "",
                            "is_bot": False
                        }
        
        # Топ участников
        top_participants = sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "analyzed": True,
            "total_participants": len(participant_counts),
            "total_bots": sum(1 for info in participant_info.values() if info["is_bot"]),
            "participant_counts": participant_counts,
            "participant_info": participant_info,
            "top_participants": [
                {
                    "user_id": user_id,
                    "message_count": count,
                    "info": participant_info.get(user_id, {})
                }
                for user_id, count in top_participants
            ]
        }
    
    def _analyze_time_patterns(self, messages: List[Message]) -> Dict[str, Any]:
        """Анализ временных паттернов"""
        if not messages:
            return {}
        
        # Анализ по часам
        hourly_counts = {}
        daily_counts = {}
        monthly_counts = {}
        
        for message in messages:
            if message.date:
                hour = message.date.hour
                day = message.date.strftime('%Y-%m-%d')
                month = message.date.strftime('%Y-%m')
                
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
                daily_counts[day] = daily_counts.get(day, 0) + 1
                monthly_counts[month] = monthly_counts.get(month, 0) + 1
        
        # Определяем самые активные периоды
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else (0, 0)
        peak_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else ("", 0)
        
        return {
            "hourly_distribution": hourly_counts,
            "daily_distribution": daily_counts,
            "monthly_distribution": monthly_counts,
            "peak_hour": {"hour": peak_hour[0], "count": peak_hour[1]},
            "peak_day": {"date": peak_day[0], "count": peak_day[1]},
            "most_active_hours": sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _analyze_keywords(self, messages: List[Message], keywords_filter: Optional[List[str]]) -> Dict[str, Any]:
        """Анализ ключевых слов"""
        if not messages:
            return {}
        
        # Объединяем все тексты
        all_text = " ".join([msg.text.lower() for msg in messages if msg.text])
        words = all_text.split()
        
        # Подсчет частоты слов
        word_counts = {}
        for word in words:
            # Убираем знаки препинания
            clean_word = ''.join(c for c in word if c.isalnum() or c in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
            if len(clean_word) > 2:  # Игнорируем короткие слова
                word_counts[clean_word] = word_counts.get(clean_word, 0) + 1
        
        # Топ слов
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Анализ хештегов и упоминаний
        hashtags = []
        mentions = []
        
        for message in messages:
            if message.text:
                # Хештеги
                hashtags.extend([word for word in message.text.split() if word.startswith('#')])
                # Упоминания
                mentions.extend([word for word in message.text.split() if word.startswith('@')])
        
        hashtag_counts = {}
        for tag in hashtags:
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        
        mention_counts = {}
        for mention in mentions:
            mention_counts[mention] = mention_counts.get(mention, 0) + 1
        
        result = {
            "total_words": len(words),
            "unique_words": len(word_counts),
            "top_words": top_words,
            "hashtags": {
                "total": len(hashtags),
                "unique": len(hashtag_counts),
                "top": sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            },
            "mentions": {
                "total": len(mentions),
                "unique": len(mention_counts),
                "top": sorted(mention_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            }
        }
        
        # Фильтр по ключевым словам
        if keywords_filter:
            keyword_matches = {}
            for keyword in keywords_filter:
                count = sum(1 for msg in messages if msg.text and keyword.lower() in msg.text.lower())
                keyword_matches[keyword] = count
            result["filtered_keywords"] = keyword_matches
        
        return result
    
    def _analyze_media(self, messages: List[Message]) -> Dict[str, Any]:
        """Анализ медиафайлов"""
        if not messages:
            return {}
        
        media_types = {}
        media_count = 0
        
        for message in messages:
            if message.media:
                media_count += 1
                media_type = type(message.media).__name__
                media_types[media_type] = media_types.get(media_type, 0) + 1
        
        return {
            "total_media": media_count,
            "media_types": media_types,
            "media_percentage": round((media_count / len(messages)) * 100, 2) if messages else 0
        }
    
    def _prepare_export_data(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Подготовка данных для экспорта"""
        export_data = []
        
        for message in messages:
            try:
                data = {
                    "message_id": message.id,
                    "date": message.date.isoformat() if message.date else None,
                    "from_id": str(message.from_id.user_id) if hasattr(message.from_id, 'user_id') else str(message.from_id) if message.from_id else None,
                    "text": message.text or "",
                    "media_type": type(message.media).__name__ if message.media else None,
                    "is_reply": bool(message.reply_to),
                    "reply_to_msg_id": message.reply_to.reply_to_msg_id if message.reply_to else None,
                    "is_forward": bool(message.forward),
                    "views": getattr(message, 'views', None),
                    "edit_date": message.edit_date.isoformat() if message.edit_date else None
                }
                export_data.append(data)
            except Exception as e:
                print(f"Ошибка обработки сообщения {message.id}: {e}")
                continue
        
        return export_data
    
    def export_to_csv(self, analytics: ChatAnalytics) -> str:
        """Экспорт данных в CSV"""
        output = io.StringIO()
        if analytics.export_data:
            fieldnames = analytics.export_data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(analytics.export_data)
        
        return output.getvalue()
    
    def export_to_json(self, analytics: ChatAnalytics) -> str:
        """Экспорт данных в JSON"""
        return json.dumps({
            "chat_info": analytics.chat_info,
            "message_stats": analytics.message_stats,
            "participant_stats": analytics.participant_stats,
            "time_analysis": analytics.time_analysis,
            "keyword_analysis": analytics.keyword_analysis,
            "media_analysis": analytics.media_analysis,
            "export_data": analytics.export_data
        }, ensure_ascii=False, indent=2, default=str)


# Глобальный экземпляр сервиса
analytics_service = AnalyticsService()