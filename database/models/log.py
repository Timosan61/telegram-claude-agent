from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class ActivityLog(Base):
    """
    Модель логов активности агента - история всех действий
    """
    __tablename__ = "activity_logs"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Telegram данные
    chat_id = Column(String(255), nullable=False, index=True)
    chat_title = Column(String(255), nullable=True)
    message_id = Column(Integer, nullable=False)
    trigger_keyword = Column(String(255), nullable=False, index=True)
    
    # Контекст и ответ
    context_messages = Column(JSON, nullable=True)  # Сообщения до триггера
    original_message = Column(Text, nullable=False)  # Сообщение-триггер
    agent_response = Column(Text, nullable=False)    # Ответ агента
    
    # Статус и результат
    status = Column(String(50), default="sent", index=True)  # sent, failed, pending
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)  # Время обработки в мс
    
    # Метаданные
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    campaign = relationship("Campaign", backref="activity_logs")
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, campaign_id={self.campaign_id}, status='{self.status}')>"
    
    def to_dict(self):
        """Преобразование объекта в словарь для API"""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "chat_id": self.chat_id,
            "chat_title": self.chat_title,
            "message_id": self.message_id,
            "trigger_keyword": self.trigger_keyword,
            "context_messages": self.context_messages,
            "original_message": self.original_message,
            "agent_response": self.agent_response,
            "status": self.status,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }