from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from database.models.base import get_db
from database.models.company import CompanySettings

router = APIRouter()


# Pydantic модели для API
class CompanySettingsCreate(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    timezone: str = "UTC"
    telegram_accounts: Optional[list] = []
    ai_providers: Optional[dict] = {}
    default_settings: Optional[dict] = {}


class CompanySettingsUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    timezone: Optional[str] = None
    telegram_accounts: Optional[list] = None
    ai_providers: Optional[dict] = None
    default_settings: Optional[dict] = None


class TelegramAccountCreate(BaseModel):
    name: str
    phone: str
    api_id: str
    api_hash: str


class AIProviderUpdate(BaseModel):
    enabled: bool
    api_key: Optional[str] = None
    default_model: Optional[str] = None
    default_agent: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


@router.get("/settings", response_model=dict)
async def get_company_settings(db: Session = Depends(get_db)):
    """Получить настройки компании"""
    # Получаем первую запись (предполагаем одну компанию)
    settings = db.query(CompanySettings).first()
    
    if not settings:
        # Возвращаем дефолтные настройки если их нет
        return {
            "name": "",
            "description": "",
            "website": "",
            "email": "",
            "timezone": "UTC",
            "telegram_accounts": [],
            "ai_providers": {
                "openai": {"enabled": False, "default_model": "gpt-4"},
                "claude": {"enabled": False, "default_agent": ""}
            },
            "default_settings": {
                "context_messages_count": 3,
                "response_delay": 1.0,
                "auto_reply": True,
                "work_hours_enabled": False,
                "work_start": "09:00",
                "work_end": "18:00"
            }
        }
    
    return settings.to_dict()


@router.put("/settings", response_model=dict)
async def update_company_settings(
    settings_data: CompanySettingsUpdate,
    db: Session = Depends(get_db)
):
    """Обновить настройки компании"""
    # Получаем существующие настройки или создаем новые
    settings = db.query(CompanySettings).first()
    
    if not settings:
        # Создаем новые настройки
        settings = CompanySettings()
        db.add(settings)
    
    # Обновление полей
    update_data = settings_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return settings.to_dict()


@router.post("/telegram-accounts", response_model=dict)
async def add_telegram_account(
    account_data: TelegramAccountCreate,
    db: Session = Depends(get_db)
):
    """Добавить новый Telegram аккаунт"""
    settings = db.query(CompanySettings).first()
    
    if not settings:
        # Создаем настройки если их нет
        settings = CompanySettings(
            name="Default Company",
            telegram_accounts=[]
        )
        db.add(settings)
        db.flush()  # Получаем ID без коммита
    
    # Добавляем новый аккаунт
    new_account = {
        "id": len(settings.telegram_accounts or []) + 1,
        "name": account_data.name,
        "phone": account_data.phone,
        "api_id": account_data.api_id,
        "api_hash": account_data.api_hash,  # В реальном приложении нужно шифровать
        "is_active": False,
        "campaigns_count": 0,
        "last_used": None
    }
    
    if not settings.telegram_accounts:
        settings.telegram_accounts = []
    
    settings.telegram_accounts.append(new_account)
    
    db.commit()
    db.refresh(settings)
    
    return {"message": "Telegram аккаунт добавлен", "account": new_account}


@router.delete("/telegram-accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_telegram_account(account_id: int, db: Session = Depends(get_db)):
    """Удалить Telegram аккаунт"""
    settings = db.query(CompanySettings).first()
    
    if not settings or not settings.telegram_accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аккаунт не найден"
        )
    
    # Находим и удаляем аккаунт
    updated_accounts = [
        acc for acc in settings.telegram_accounts 
        if acc.get("id") != account_id
    ]
    
    if len(updated_accounts) == len(settings.telegram_accounts):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аккаунт не найден"
        )
    
    settings.telegram_accounts = updated_accounts
    db.commit()


@router.put("/ai-providers/{provider}", response_model=dict)
async def update_ai_provider(
    provider: str,
    provider_data: AIProviderUpdate,
    db: Session = Depends(get_db)
):
    """Обновить настройки AI провайдера"""
    if provider not in ["openai", "claude"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неподдерживаемый провайдер"
        )
    
    settings = db.query(CompanySettings).first()
    
    if not settings:
        settings = CompanySettings(
            name="Default Company",
            ai_providers={}
        )
        db.add(settings)
        db.flush()
    
    # Обновляем настройки провайдера
    if not settings.ai_providers:
        settings.ai_providers = {}
    
    if provider not in settings.ai_providers:
        settings.ai_providers[provider] = {}
    
    # Обновление полей провайдера
    provider_update = provider_data.dict(exclude_unset=True)
    settings.ai_providers[provider].update(provider_update)
    
    db.commit()
    db.refresh(settings)
    
    return {
        "message": f"Настройки {provider} обновлены",
        "provider": provider,
        "settings": settings.ai_providers[provider]
    }


@router.put("/default-settings", response_model=dict)
async def update_default_settings(
    default_data: dict,
    db: Session = Depends(get_db)
):
    """Обновить настройки по умолчанию"""
    settings = db.query(CompanySettings).first()
    
    if not settings:
        settings = CompanySettings(
            name="Default Company",
            default_settings=default_data
        )
        db.add(settings)
    else:
        settings.default_settings = default_data
    
    db.commit()
    db.refresh(settings)
    
    return {"message": "Настройки по умолчанию обновлены", "settings": settings.default_settings}