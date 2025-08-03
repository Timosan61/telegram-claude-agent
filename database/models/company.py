from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from .base import Base


class CompanySettings(Base):
    """
    Модель настроек компании
    """
    __tablename__ = "company_settings"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    email = Column(String(255), nullable=True)
    timezone = Column(String(50), default="UTC")
    
    # Telegram аккаунты
    telegram_accounts = Column(JSON, nullable=True, default=list)
    
    # AI провайдеры настройки
    ai_providers = Column(JSON, nullable=True, default=dict)
    
    # Настройки по умолчанию
    default_settings = Column(JSON, nullable=True, default=dict)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CompanySettings(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Преобразование объекта в словарь для API"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "website": self.website,
            "email": self.email,
            "timezone": self.timezone,
            "telegram_accounts": self.telegram_accounts or [],
            "ai_providers": self.ai_providers or {},
            "default_settings": self.default_settings or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }