"""
Seed данные для инициализации базы данных
Создает демонстрационные данные для тестирования
"""

from sqlalchemy.orm import Session
from database.models.base import SessionLocal, create_tables
from database.models.campaign import Campaign
from database.models.company import CompanySettings
import json


def create_demo_company():
    """Создание демонстрационной компании для тестирования"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже демо компания
        existing_company = db.query(CompanySettings).filter(
            CompanySettings.name == "ТИМ"
        ).first()
        
        if existing_company:
            print("✅ Демо компания 'ТИМ' уже существует")
            return existing_company
        
        # Создаем демо компанию
        demo_company = CompanySettings(
            name="ТИМ",
            telegram_accounts=["+1234567890"],
            ai_providers={
                "claude": {
                    "enabled": True,
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1000
                },
                "openai": {
                    "enabled": True,
                    "model": "gpt-4",
                    "max_tokens": 1000
                }
            },
            default_settings={
                "context_messages_count": 5,
                "ai_provider": "claude",
                "auto_reply": True,
                "language": "ru"
            }
        )
        
        db.add(demo_company)
        db.commit()
        db.refresh(demo_company)
        
        print("✅ Демо компания 'ТИМ' создана успешно")
        return demo_company
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания демо компании: {e}")
        return None
    finally:
        db.close()


def create_demo_campaigns():
    """Создание демонстрационных кампаний"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже демо кампания
        existing_campaign = db.query(Campaign).filter(
            Campaign.name == "Демо кампания - Поддержка"
        ).first()
        
        if existing_campaign:
            print("✅ Демо кампания уже существует")
            return existing_campaign
        
        # Создаем демо кампанию
        demo_campaign = Campaign(
            name="Демо кампания - Поддержка",
            active=True,
            telegram_chats=["@demo_channel", "2532661483"],  # Включаем тестовую группу
            keywords=["помощь", "поддержка", "вопрос", "проблема", "help"],
            telegram_account="+1234567890",
            ai_provider="claude",
            system_instruction="""Ты - дружелюбный помощник службы поддержки компании ТИМ.

Твоя задача:
- Отвечать вежливо и профессионально
- Помогать пользователям с их вопросами
- Предоставлять полезную информацию о наших услугах
- При необходимости направлять к специалистам

Стиль общения:
- Дружелюбный, но профессиональный
- Используй эмодзи для создания теплой атмосферы
- Отвечай кратко и по существу
- Всегда предлагай дальнейшую помощь""",
            context_messages_count=3,
            example_replies=[
                "Привет! 👋 Как дела? Чем могу помочь?",
                "Конечно, помогу! 😊 Расскажи подробнее о твоем вопросе.",
                "Отличный вопрос! 🤔 Давай разберемся вместе.",
                "Спасибо за обращение! 🙏 Я передам твой вопрос специалистам.",
                "Всегда рад помочь! 💪 Есть ещё вопросы?"
            ]
        )
        
        db.add(demo_campaign)
        db.commit()
        db.refresh(demo_campaign)
        
        print("✅ Демо кампания создана успешно")
        return demo_campaign
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка создания демо кампании: {e}")
        return None
    finally:
        db.close()


def initialize_demo_data():
    """Инициализация всех демонстрационных данных"""
    print("🌱 Инициализация демонстрационных данных...")
    
    # Убеждаемся что таблицы созданы (на случай если этот скрипт вызывается отдельно)
    try:
        create_tables()
    except Exception as e:
        print(f"⚠️ Таблицы уже существуют или ошибка создания: {e}")
    
    # Создаем демо компанию
    company = create_demo_company()
    
    # Создаем демо кампанию
    campaign = create_demo_campaigns()
    
    if company and campaign:
        print("✅ Все демонстрационные данные созданы успешно")
        return True
    else:
        print("⚠️ Не все демонстрационные данные созданы")
        return False


if __name__ == "__main__":
    initialize_demo_data()