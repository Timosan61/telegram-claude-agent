from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from database.models.base import get_db
from database.models.log import ActivityLog
from database.models.campaign import Campaign

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_activity_logs(
    skip: int = 0,
    limit: int = 100,
    campaign_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    hours_back: Optional[int] = Query(None, description="Показать логи за последние N часов"),
    db: Session = Depends(get_db)
):
    """Получить логи активности агента"""
    query = db.query(ActivityLog).join(Campaign)
    
    # Фильтр по кампании
    if campaign_id:
        query = query.filter(ActivityLog.campaign_id == campaign_id)
    
    # Фильтр по статусу
    if status_filter:
        query = query.filter(ActivityLog.status == status_filter)
    
    # Фильтр по времени
    if hours_back:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        query = query.filter(ActivityLog.timestamp >= cutoff_time)
    
    # Сортировка по времени (новые сначала)
    query = query.order_by(desc(ActivityLog.timestamp))
    
    logs = query.offset(skip).limit(limit).all()
    return [log.to_dict() for log in logs]


@router.get("/{log_id}", response_model=dict)
async def get_activity_log(log_id: int, db: Session = Depends(get_db)):
    """Получить детали конкретного лога"""
    log = db.query(ActivityLog).filter(ActivityLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Лог не найден"
        )
    
    return log.to_dict()


@router.get("/campaign/{campaign_id}/stats")
async def get_campaign_stats(campaign_id: int, db: Session = Depends(get_db)):
    """Получить статистику по кампании"""
    # Проверка существования кампании
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кампания не найдена"
        )
    
    # Общее количество логов
    total_logs = db.query(ActivityLog).filter(ActivityLog.campaign_id == campaign_id).count()
    
    # Статистика по статусам
    status_stats = {}
    for status_val in ["sent", "failed", "pending"]:
        count = db.query(ActivityLog).filter(
            ActivityLog.campaign_id == campaign_id,
            ActivityLog.status == status_val
        ).count()
        status_stats[status_val] = count
    
    # Статистика за последние 24 часа
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    recent_logs = db.query(ActivityLog).filter(
        ActivityLog.campaign_id == campaign_id,
        ActivityLog.timestamp >= cutoff_time
    ).count()
    
    # Среднее время обработки
    avg_processing_time = db.query(ActivityLog.processing_time_ms).filter(
        ActivityLog.campaign_id == campaign_id,
        ActivityLog.processing_time_ms.isnot(None)
    ).all()
    
    avg_time = None
    if avg_processing_time:
        times = [t[0] for t in avg_processing_time if t[0] is not None]
        if times:
            avg_time = sum(times) / len(times)
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "total_responses": total_logs,
        "status_breakdown": status_stats,
        "responses_24h": recent_logs,
        "avg_processing_time_ms": round(avg_time) if avg_time else None,
        "success_rate": round((status_stats.get("sent", 0) / max(total_logs, 1)) * 100, 2)
    }


@router.delete("/campaign/{campaign_id}")
async def clear_campaign_logs(campaign_id: int, db: Session = Depends(get_db)):
    """Очистить все логи кампании"""
    # Проверка существования кампании
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кампания не найдена"
        )
    
    # Удаление логов
    deleted_count = db.query(ActivityLog).filter(
        ActivityLog.campaign_id == campaign_id
    ).delete()
    
    db.commit()
    
    return {
        "message": f"Удалено {deleted_count} записей логов для кампании '{campaign.name}'"
    }


@router.get("/stats/overview")
async def get_system_overview(db: Session = Depends(get_db)):
    """Общая статистика системы"""
    # Общее количество кампаний
    total_campaigns = db.query(Campaign).count()
    active_campaigns = db.query(Campaign).filter(Campaign.active == True).count()
    
    # Общее количество ответов
    total_responses = db.query(ActivityLog).count()
    
    # Ответы за последние 24 часа
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    responses_24h = db.query(ActivityLog).filter(
        ActivityLog.timestamp >= cutoff_time
    ).count()
    
    # Статистика по статусам за 24 часа
    status_stats_24h = {}
    for status_val in ["sent", "failed", "pending"]:
        count = db.query(ActivityLog).filter(
            ActivityLog.timestamp >= cutoff_time,
            ActivityLog.status == status_val
        ).count()
        status_stats_24h[status_val] = count
    
    return {
        "campaigns": {
            "total": total_campaigns,
            "active": active_campaigns,
            "inactive": total_campaigns - active_campaigns
        },
        "responses": {
            "total": total_responses,
            "last_24h": responses_24h,
            "status_24h": status_stats_24h
        },
        "success_rate_24h": round(
            (status_stats_24h.get("sent", 0) / max(responses_24h, 1)) * 100, 2
        )
    }