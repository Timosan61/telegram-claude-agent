from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database.models.base import Base
from datetime import datetime


class CampaignStatistics(Base):
    """Статистика по кампаниям"""
    __tablename__ = "campaign_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Основные метрики
    messages_processed = Column(Integer, default=0)  # Обработано сообщений
    responses_sent = Column(Integer, default=0)      # Отправлено ответов
    responses_failed = Column(Integer, default=0)    # Неудачных ответов
    
    # Производительность
    avg_response_time_ms = Column(Float, default=0.0)  # Среднее время ответа
    max_response_time_ms = Column(Float, default=0.0)  # Максимальное время ответа
    min_response_time_ms = Column(Float, default=0.0)  # Минимальное время ответа
    
    # Дополнительные метрики
    unique_chats_active = Column(Integer, default=0)    # Активных чатов
    unique_users_interacted = Column(Integer, default=0) # Уникальных пользователей
    keywords_triggered = Column(JSON)  # Сработавшие ключевые слова {"keyword": count}
    
    # Связи
    campaign = relationship("Campaign", back_populates="statistics")
    
    def to_dict(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "date": self.date.isoformat() if self.date else None,
            "messages_processed": self.messages_processed,
            "responses_sent": self.responses_sent,
            "responses_failed": self.responses_failed,
            "success_rate": round((self.responses_sent / max(1, self.messages_processed)) * 100, 2),
            "avg_response_time_ms": self.avg_response_time_ms,
            "max_response_time_ms": self.max_response_time_ms,
            "min_response_time_ms": self.min_response_time_ms,
            "unique_chats_active": self.unique_chats_active,
            "unique_users_interacted": self.unique_users_interacted,
            "keywords_triggered": self.keywords_triggered or {}
        }


class SystemStatistics(Base):
    """Общая статистика системы"""
    __tablename__ = "system_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Общие метрики системы
    total_campaigns = Column(Integer, default=0)
    active_campaigns = Column(Integer, default=0)
    total_messages_processed = Column(Integer, default=0)
    total_responses_sent = Column(Integer, default=0)
    
    # Производительность системы
    system_uptime_hours = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_mb = Column(Float, default=0.0)
    
    # API статистика
    api_requests_count = Column(Integer, default=0)
    api_errors_count = Column(Integer, default=0)
    avg_api_response_time_ms = Column(Float, default=0.0)
    
    # Telegram статистика
    telegram_connected = Column(Boolean, default=False)
    telegram_connection_uptime_hours = Column(Float, default=0.0)
    telegram_api_calls = Column(Integer, default=0)
    telegram_rate_limit_hits = Column(Integer, default=0)
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "total_campaigns": self.total_campaigns,
            "active_campaigns": self.active_campaigns,
            "total_messages_processed": self.total_messages_processed,
            "total_responses_sent": self.total_responses_sent,
            "success_rate": round((self.total_responses_sent / max(1, self.total_messages_processed)) * 100, 2),
            "system_uptime_hours": self.system_uptime_hours,
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "api_requests_count": self.api_requests_count,
            "api_errors_count": self.api_errors_count,
            "avg_api_response_time_ms": self.avg_api_response_time_ms,
            "telegram_connected": self.telegram_connected,
            "telegram_connection_uptime_hours": self.telegram_connection_uptime_hours,
            "telegram_api_calls": self.telegram_api_calls,
            "telegram_rate_limit_hits": self.telegram_rate_limit_hits
        }


class ChatStatistics(Base):
    """Статистика по чатам"""
    __tablename__ = "chat_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(255), nullable=False)
    chat_title = Column(String(500))
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Активность в чате
    messages_count = Column(Integer, default=0)        # Всего сообщений
    bot_responses_count = Column(Integer, default=0)   # Ответов бота
    unique_users_count = Column(Integer, default=0)    # Уникальных пользователей
    
    # Статистика по времени
    peak_hour = Column(Integer)  # Час максимальной активности (0-23)
    messages_per_hour = Column(JSON)  # {"0": count, "1": count, ...}
    
    # Популярные слова и темы
    top_keywords = Column(JSON)  # [{"word": "keyword", "count": 123}, ...]
    hashtags_used = Column(JSON)  # [{"tag": "#hashtag", "count": 10}, ...]
    
    # Метрики вовлеченности
    avg_message_length = Column(Float, default=0.0)
    media_messages_count = Column(Integer, default=0)
    reply_messages_count = Column(Integer, default=0)
    
    def to_dict(self):
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "chat_title": self.chat_title,
            "date": self.date.isoformat() if self.date else None,
            "messages_count": self.messages_count,
            "bot_responses_count": self.bot_responses_count,
            "unique_users_count": self.unique_users_count,
            "response_rate": round((self.bot_responses_count / max(1, self.messages_count)) * 100, 2),
            "peak_hour": self.peak_hour,
            "messages_per_hour": self.messages_per_hour or {},
            "top_keywords": self.top_keywords or [],
            "hashtags_used": self.hashtags_used or [],
            "avg_message_length": self.avg_message_length,
            "media_messages_count": self.media_messages_count,
            "reply_messages_count": self.reply_messages_count
        }


class UserStatistics(Base):
    """Статистика по пользователям"""
    __tablename__ = "user_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Активность пользователя
    messages_sent = Column(Integer, default=0)
    bot_interactions = Column(Integer, default=0)  # Сколько раз бот отвечал пользователю
    chats_active_in = Column(Integer, default=0)   # В скольких чатах активен
    
    # Поведенческие метрики
    avg_message_length = Column(Float, default=0.0)
    most_active_hour = Column(Integer)  # Час наибольшей активности
    favorite_words = Column(JSON)  # Часто используемые слова
    
    # Временные паттерны
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    total_active_days = Column(Integer, default=0)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "date": self.date.isoformat() if self.date else None,
            "messages_sent": self.messages_sent,
            "bot_interactions": self.bot_interactions,
            "chats_active_in": self.chats_active_in,
            "avg_message_length": self.avg_message_length,
            "most_active_hour": self.most_active_hour,
            "favorite_words": self.favorite_words or [],
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "total_active_days": self.total_active_days
        }


class PerformanceMetrics(Base):
    """Метрики производительности"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metric_type = Column(String(100), nullable=False)  # 'response_time', 'memory', 'cpu', etc.
    
    # Значения метрик
    value = Column(Float, nullable=False)
    unit = Column(String(50))  # 'ms', 'mb', '%', etc.
    
    # Контекст
    source = Column(String(100))  # 'telegram_agent', 'api', 'analytics', etc.
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    chat_id = Column(String(255), nullable=True)
    
    # Дополнительные данные
    extra_data = Column(JSON)  # Дополнительная информация
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metric_type": self.metric_type,
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "campaign_id": self.campaign_id,
            "chat_id": self.chat_id,
            "extra_data": self.extra_data or {}
        }