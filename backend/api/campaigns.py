from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database.models.base import get_db
from database.models.campaign import Campaign

# Глобальная переменная для доступа к telegram_agent
telegram_agent = None

def set_telegram_agent(agent):
    """Установка глобального экземпляра telegram агента"""
    global telegram_agent
    telegram_agent = agent

router = APIRouter()


# Pydantic модели для API
class CampaignCreate(BaseModel):
    name: str
    telegram_chats: List[str]
    keywords: List[str]
    telegram_account: str
    ai_provider: str = "claude"
    claude_agent_id: Optional[str] = None
    openai_model: str = "gpt-4"
    context_messages_count: int = 3
    system_instruction: str
    example_replies: Optional[dict] = None
    active: bool = False


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    telegram_chats: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    telegram_account: Optional[str] = None
    ai_provider: Optional[str] = None
    claude_agent_id: Optional[str] = None
    openai_model: Optional[str] = None
    context_messages_count: Optional[int] = None
    system_instruction: Optional[str] = None
    example_replies: Optional[dict] = None
    active: Optional[bool] = None


@router.get("/", response_model=List[dict])
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """Получить список всех кампаний"""
    query = db.query(Campaign)
    
    if active_only:
        query = query.filter(Campaign.active == True)
    
    campaigns = query.offset(skip).limit(limit).all()
    return [campaign.to_dict() for campaign in campaigns]


@router.get("/{campaign_id}", response_model=dict)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Получить кампанию по ID"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кампания не найдена"
        )
    
    return campaign.to_dict()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_campaign(campaign_data: CampaignCreate, db: Session = Depends(get_db)):
    """Создать новую кампанию"""
    # Проверка на дублирование имени
    existing = db.query(Campaign).filter(Campaign.name == campaign_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Кампания с таким именем уже существует"
        )
    
    # Создание кампании
    campaign = Campaign(
        name=campaign_data.name,
        telegram_chats=campaign_data.telegram_chats,
        keywords=campaign_data.keywords,
        telegram_account=campaign_data.telegram_account,
        ai_provider=campaign_data.ai_provider,
        claude_agent_id=campaign_data.claude_agent_id,
        openai_model=campaign_data.openai_model,
        context_messages_count=campaign_data.context_messages_count,
        system_instruction=campaign_data.system_instruction,
        example_replies=campaign_data.example_replies,
        active=campaign_data.active
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # Принудительное обновление кэша
    if telegram_agent:
        telegram_agent.force_campaigns_refresh()
    
    return campaign.to_dict()


@router.put("/{campaign_id}", response_model=dict)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: Session = Depends(get_db)
):
    """Обновить кампанию"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кампания не найдена"
        )
    
    # Обновление полей
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    
    # Принудительное обновление кэша
    if telegram_agent:
        telegram_agent.force_campaigns_refresh()
    
    return campaign.to_dict()


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Удалить кампанию"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кампания не найдена"
        )
    
    db.delete(campaign)
    db.commit()
    
    # Принудительное обновление кэша
    if telegram_agent:
        telegram_agent.force_campaigns_refresh()


@router.post("/{campaign_id}/toggle", response_model=dict)
async def toggle_campaign_status(campaign_id: int, db: Session = Depends(get_db)):
    """Переключить статус активности кампании"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кампания не найдена"
        )
    
    campaign.active = not campaign.active
    db.commit()
    db.refresh(campaign)
    
    # Принудительное обновление кэша
    if telegram_agent:
        telegram_agent.force_campaigns_refresh()
    
    return {
        "id": campaign.id,
        "name": campaign.name,
        "active": campaign.active,
        "message": f"Кампания {'активирована' if campaign.active else 'деактивирована'}"
    }


@router.post("/refresh-cache", response_model=dict)
async def refresh_campaigns_cache():
    """Принудительное обновление кэша кампаний"""
    if telegram_agent:
        telegram_agent.force_campaigns_refresh()
        return {"message": "Кэш кампаний будет обновлен при следующем запросе"}
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram агент недоступен"
        )