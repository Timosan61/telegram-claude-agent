from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.statistics_service import statistics_service

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_summary():
    """Получить сводку для главного дашборда"""
    try:
        summary = statistics_service.get_dashboard_summary()
        return JSONResponse(content=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения сводки: {str(e)}")


@router.get("/system")
async def get_system_statistics():
    """Получить системную статистику"""
    try:
        stats = statistics_service.collect_system_statistics()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сбора системной статистики: {str(e)}")


@router.get("/campaigns")
async def get_campaigns_statistics(
    campaign_id: Optional[int] = Query(None, description="ID конкретной кампании"),
    hours_back: int = Query(24, description="Период анализа в часах", ge=1, le=168)
):
    """Получить статистику по кампаниям"""
    try:
        stats = statistics_service.collect_campaign_statistics(campaign_id, hours_back)
        return JSONResponse(content={
            "campaigns": stats,
            "total": len(stats),
            "period_hours": hours_back
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сбора статистики кампаний: {str(e)}")


@router.get("/chats")
async def get_chats_statistics(
    hours_back: int = Query(24, description="Период анализа в часах", ge=1, le=168)
):
    """Получить статистику по чатам"""
    try:
        stats = statistics_service.collect_chat_statistics(hours_back)
        return JSONResponse(content={
            "chats": stats,
            "total": len(stats),
            "period_hours": hours_back
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сбора статистики чатов: {str(e)}")


@router.get("/performance/trends")
async def get_performance_trends(
    metric_type: str = Query(..., description="Тип метрики", 
                            regex="^(response_time|cpu_usage|memory_usage|api_calls)$"),
    hours_back: int = Query(24, description="Период анализа в часах", ge=1, le=168)
):
    """Получить тренды производительности"""
    try:
        trends = statistics_service.get_performance_trends(metric_type, hours_back)
        return JSONResponse(content={
            "metric_type": metric_type,
            "trends": trends,
            "total_points": len(trends),
            "period_hours": hours_back
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения трендов: {str(e)}")


@router.get("/historical")
async def get_historical_data(
    days_back: int = Query(7, description="Период анализа в днях", ge=1, le=30)
):
    """Получить исторические данные"""
    try:
        data = statistics_service.get_historical_data(days_back)
        return JSONResponse(content={
            "historical_data": data,
            "period_days": days_back
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения исторических данных: {str(e)}")


@router.post("/performance/record")
async def record_performance_metric(
    metric_type: str,
    value: float,
    unit: str,
    source: str = "api",
    campaign_id: Optional[int] = None,
    chat_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Записать метрику производительности"""
    try:
        statistics_service.record_performance_metric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            source=source,
            campaign_id=campaign_id,
            chat_id=chat_id,
            metadata=metadata
        )
        
        return JSONResponse(content={
            "message": "Метрика записана успешно",
            "metric_type": metric_type,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка записи метрики: {str(e)}")


@router.get("/health")
async def statistics_health():
    """Проверка статуса сервиса статистики"""
    try:
        # Попробуем получить базовые метрики
        summary = statistics_service.get_dashboard_summary()
        
        return JSONResponse(content={
            "status": "healthy",
            "service": "statistics",
            "uptime_hours": summary.get("system", {}).get("uptime_hours", 0),
            "total_campaigns": summary.get("campaigns", {}).get("total", 0),
            "api_requests": summary.get("system", {}).get("api_requests", 0)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Сервис статистики недоступен: {str(e)}")


@router.get("/realtime")
async def get_realtime_metrics():
    """Получить метрики в реальном времени"""
    try:
        import psutil
        import time
        
        # Системные метрики
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Метрики сервиса
        uptime = time.time() - statistics_service.start_time
        
        return JSONResponse(content={
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_available_mb": memory.available / 1024 / 1024
            },
            "service": {
                "uptime_seconds": uptime,
                "api_requests_total": statistics_service.api_requests_count,
                "api_errors_total": statistics_service.api_errors_count,
                "telegram_api_calls": statistics_service.telegram_api_calls,
                "telegram_rate_limits": statistics_service.telegram_rate_limit_hits
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения реальных метрик: {str(e)}")


@router.get("/export")
async def export_statistics(
    format: str = Query("json", regex="^(json|csv)$"),
    period_days: int = Query(7, ge=1, le=30),
    include_campaigns: bool = Query(True),
    include_chats: bool = Query(True),
    include_system: bool = Query(True)
):
    """Экспорт статистики в различных форматах"""
    try:
        export_data = {}
        
        if include_system:
            export_data["system"] = statistics_service.collect_system_statistics()
        
        if include_campaigns:
            export_data["campaigns"] = statistics_service.collect_campaign_statistics(
                hours_back=period_days * 24
            )
        
        if include_chats:
            export_data["chats"] = statistics_service.collect_chat_statistics(
                hours_back=period_days * 24
            )
        
        # Добавляем метаинформацию
        export_data["export_info"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "period_days": period_days,
            "format": format,
            "version": "1.2"
        }
        
        if format == "json":
            return JSONResponse(content=export_data)
        else:
            # Для CSV потребуется дополнительная обработка
            raise HTTPException(status_code=501, detail="CSV экспорт будет реализован в следующей версии")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта статистики: {str(e)}")


@router.post("/collect/all")
async def trigger_statistics_collection():
    """Принудительно запустить сбор всей статистики"""
    try:
        results = {}
        
        # Собираем системную статистику
        results["system"] = statistics_service.collect_system_statistics()
        
        # Собираем статистику кампаний
        results["campaigns"] = statistics_service.collect_campaign_statistics()
        
        # Собираем статистику чатов
        results["chats"] = statistics_service.collect_chat_statistics()
        
        return JSONResponse(content={
            "message": "Сбор статистики завершен",
            "timestamp": datetime.utcnow().isoformat(),
            "collected": {
                "system_metrics": 1 if results["system"] else 0,
                "campaign_stats": len(results["campaigns"]),
                "chat_stats": len(results["chats"])
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сбора статистики: {str(e)}")


@router.get("/campaigns/{campaign_id}")
async def get_campaign_detailed_statistics(
    campaign_id: int,
    hours_back: int = Query(24, ge=1, le=168)
):
    """Получить детальную статистику конкретной кампании"""
    try:
        stats = statistics_service.collect_campaign_statistics(campaign_id, hours_back)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Статистика для кампании не найдена")
        
        return JSONResponse(content={
            "campaign_statistics": stats[0],
            "period_hours": hours_back,
            "collected_at": datetime.utcnow().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики кампании: {str(e)}")


@router.delete("/cleanup")
async def cleanup_old_statistics(
    days_older_than: int = Query(30, description="Удалить статистику старше N дней", ge=7)
):
    """Очистка старой статистики"""
    try:
        from database.models.base import SessionLocal
        from database.models.statistics import (
            CampaignStatistics, SystemStatistics, ChatStatistics, 
            UserStatistics, PerformanceMetrics
        )
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_older_than)
        
        db = SessionLocal()
        
        # Счетчики удаленных записей
        deleted_counts = {}
        
        # Удаляем старые записи из каждой таблицы
        models = [
            ("campaign_statistics", CampaignStatistics),
            ("system_statistics", SystemStatistics),
            ("chat_statistics", ChatStatistics),
            ("user_statistics", UserStatistics),
            ("performance_metrics", PerformanceMetrics)
        ]
        
        for name, model in models:
            deleted = db.query(model).filter(model.date < cutoff_date).delete()
            deleted_counts[name] = deleted
        
        db.commit()
        
        return JSONResponse(content={
            "message": f"Очистка статистики старше {days_older_than} дней завершена",
            "cutoff_date": cutoff_date.isoformat(),
            "deleted_records": deleted_counts,
            "total_deleted": sum(deleted_counts.values())
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка очистки статистики: {str(e)}")
    finally:
        db.close()