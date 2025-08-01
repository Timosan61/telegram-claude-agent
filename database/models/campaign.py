from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from .base import Base


class Campaign(Base):
    """
    Модель кампании - основная сущность для управления Telegram-агентом
    """
    __tablename__ = "campaigns"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    active = Column(Boolean, default=False)
    
    # Telegram настройки
    telegram_chats = Column(JSON, nullable=False)  # Список ID или username чатов
    keywords = Column(JSON, nullable=False)        # Ключевые слова-триггеры
    telegram_account = Column(String(255), nullable=False)  # Аккаунт для ответов
    
    # Claude агент настройки
    claude_agent_id = Column(String(255), nullable=False)  # ID или alias Claude агента
    context_messages_count = Column(Integer, default=3)    # Кол-во сообщений до триггера
    
    # AI промпты и инструкции
    system_instruction = Column(Text, nullable=False)      # Системная подсказка
    example_replies = Column(JSON, nullable=True)          # Примеры ответов по ключевым словам
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', active={self.active})>"
    
    def to_dict(self):
        """Преобразование объекта в словарь для API"""
        return {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "telegram_chats": self.telegram_chats,
            "keywords": self.keywords,
            "telegram_account": self.telegram_account,
            "claude_agent_id": self.claude_agent_id,
            "context_messages_count": self.context_messages_count,
            "system_instruction": self.system_instruction,
            "example_replies": self.example_replies,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }