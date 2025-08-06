from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import io

from services.analytics_service import analytics_service, AnalyticsConfig, ChatAnalytics

router = APIRouter()

# Хранилище результатов анализа (в продакшне лучше использовать Redis или БД)
analysis_results: Dict[str, ChatAnalytics] = {}


class AnalysisRequest(BaseModel):
    chat_id: str
    chat_username: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit_messages: int = 1000
    include_media: bool = False
    include_replies: bool = True
    analyze_participants: bool = True
    keywords_filter: Optional[List[str]] = None


class ExportRequest(BaseModel):
    analysis_id: str
    format: str = "csv"  # csv, json


class DirectChannelAnalysisRequest(BaseModel):
    channel_name: str  # @channel или ID или username
    limit_messages: int = 1000
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_media: bool = False
    include_replies: bool = True
    keywords_filter: Optional[List[str]] = None


@router.get("/health")
async def analytics_health():
    """Проверка статуса сервиса аналитики"""
    return {
        "status": "healthy",
        "telegram_connected": analytics_service.is_connected,
        "service": "analytics"
    }


@router.get("/chats/available")
async def get_available_chats():
    """Получить список доступных чатов для анализа"""
    try:
        chats = await analytics_service.get_available_chats()
        return {
            "chats": chats,
            "total": len(chats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка чатов: {str(e)}")


async def run_analysis_task(config: AnalyticsConfig, analysis_id: str):
    """Фоновая задача для выполнения анализа"""
    try:
        print(f"🔍 Начинаем анализ чата {config.chat_id} (ID: {analysis_id})")
        
        # Выполняем анализ
        result = await analytics_service.analyze_chat(config)
        
        # Сохраняем результат
        analysis_results[analysis_id] = result
        
        print(f"✅ Анализ завершен (ID: {analysis_id})")
        
    except Exception as e:
        print(f"❌ Ошибка анализа (ID: {analysis_id}): {e}")
        # Сохраняем ошибку
        error_result = ChatAnalytics(
            chat_info={"error": str(e)},
            message_stats={},
            participant_stats={},
            time_analysis={},
            keyword_analysis={},
            media_analysis={},
            export_data=[]
        )
        analysis_results[analysis_id] = error_result


@router.post("/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Запустить анализ чата"""
    try:
        # Генерируем уникальный ID для анализа
        analysis_id = str(uuid.uuid4())
        
        # Создаем конфигурацию
        config = AnalyticsConfig(
            chat_id=request.chat_id,
            chat_username=request.chat_username,
            start_date=request.start_date,
            end_date=request.end_date,
            limit_messages=request.limit_messages,
            include_media=request.include_media,
            include_replies=request.include_replies,
            analyze_participants=request.analyze_participants,
            keywords_filter=request.keywords_filter
        )
        
        # Запускаем анализ в фоне
        background_tasks.add_task(run_analysis_task, config, analysis_id)
        
        return {
            "analysis_id": analysis_id,
            "status": "started",
            "message": "Анализ запущен. Используйте analysis_id для получения результатов."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запуска анализа: {str(e)}")


@router.get("/analyze/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Получить статус анализа"""
    if analysis_id in analysis_results:
        result = analysis_results[analysis_id]
        
        # Проверяем на ошибку
        if "error" in result.chat_info:
            return {
                "analysis_id": analysis_id,
                "status": "error",
                "error": result.chat_info["error"]
            }
        else:
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "chat_title": result.chat_info.get("title", "Unknown"),
                "total_messages": result.message_stats.get("total", 0)
            }
    else:
        return {
            "analysis_id": analysis_id,
            "status": "in_progress"
        }


@router.get("/analyze/{analysis_id}/results")
async def get_analysis_results(analysis_id: str):
    """Получить результаты анализа"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Анализ не найден или еще выполняется")
    
    result = analysis_results[analysis_id]
    
    # Проверяем на ошибку
    if "error" in result.chat_info:
        raise HTTPException(status_code=500, detail=result.chat_info["error"])
    
    # Возвращаем результаты без экспортных данных (они могут быть большими)
    return {
        "analysis_id": analysis_id,
        "chat_info": result.chat_info,
        "message_stats": result.message_stats,
        "participant_stats": result.participant_stats,
        "time_analysis": result.time_analysis,
        "keyword_analysis": result.keyword_analysis,
        "media_analysis": result.media_analysis,
        "export_available": len(result.export_data) > 0
    }


@router.post("/export")
async def export_analysis(request: ExportRequest):
    """Экспорт результатов анализа"""
    if request.analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Анализ не найден")
    
    result = analysis_results[request.analysis_id]
    
    # Проверяем на ошибку
    if "error" in result.chat_info:
        raise HTTPException(status_code=500, detail=result.chat_info["error"])
    
    try:
        if request.format.lower() == "csv":
            # Экспорт в CSV
            csv_data = analytics_service.export_to_csv(result)
            
            # Создаем имя файла
            chat_title = result.chat_info.get("title", "chat").replace(" ", "_")
            filename = f"analytics_{chat_title}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            
            return StreamingResponse(
                io.StringIO(csv_data),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        elif request.format.lower() == "json":
            # Экспорт в JSON
            json_data = analytics_service.export_to_json(result)
            
            # Создаем имя файла
            chat_title = result.chat_info.get("title", "chat").replace(" ", "_")
            filename = f"analytics_{chat_title}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            
            return StreamingResponse(
                io.StringIO(json_data),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат экспорта")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта: {str(e)}")


@router.delete("/analyze/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Удалить результаты анализа"""
    if analysis_id in analysis_results:
        del analysis_results[analysis_id]
        return {"message": "Результаты анализа удалены"}
    else:
        raise HTTPException(status_code=404, detail="Анализ не найден")


@router.get("/analyze")
async def list_analyses():
    """Получить список всех анализов"""
    analyses = []
    
    for analysis_id, result in analysis_results.items():
        status = "error" if "error" in result.chat_info else "completed"
        
        analyses.append({
            "analysis_id": analysis_id,
            "status": status,
            "chat_title": result.chat_info.get("title", "Unknown"),
            "total_messages": result.message_stats.get("total", 0),
            "analyzed_participants": result.participant_stats.get("total_participants", 0)
        })
    
    return {
        "analyses": analyses,
        "total": len(analyses)
    }


@router.post("/initialize")
async def initialize_analytics_service():
    """Инициализация сервиса аналитики"""
    try:
        success = await analytics_service.initialize()
        if success:
            return {"message": "Сервис аналитики инициализирован", "status": "connected"}
        else:
            raise HTTPException(status_code=500, detail="Не удалось инициализировать сервис")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка инициализации: {str(e)}")


@router.post("/analyze-channel", response_model=dict)
async def analyze_channel_direct(request: DirectChannelAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Прямой анализ канала/чата по имени без привязки к кампаниям
    
    Новая логика:
    1. Принимаем название канала (@channel, username, или ID)
    2. Подключаемся к каналу напрямую через Telethon
    3. Загружаем указанное количество сообщений
    4. Анализируем и возвращаем результат
    """
    try:
        # Генерируем уникальный ID для анализа
        analysis_id = str(uuid.uuid4())
        
        # Создаем конфигурацию для прямого анализа
        config = AnalyticsConfig(
            chat_id=request.channel_name,  # Используем channel_name как chat_id
            chat_username=request.channel_name if request.channel_name.startswith('@') else None,
            start_date=request.start_date,
            end_date=request.end_date,
            limit_messages=request.limit_messages,
            include_media=request.include_media,
            include_replies=request.include_replies,
            analyze_participants=False,  # Отключаем анализ участников для каналов
            keywords_filter=request.keywords_filter
        )
        
        # Запускаем анализ в фоне
        background_tasks.add_task(run_analysis_task, config, analysis_id)
        
        return {
            "analysis_id": analysis_id,
            "status": "started",
            "channel": request.channel_name,
            "limit_messages": request.limit_messages,
            "message": "Анализ канала запущен. Используйте analysis_id для получения результатов.",
            "endpoints": {
                "status": f"/analytics/analyze/{analysis_id}/status",
                "results": f"/analytics/analyze/{analysis_id}/results"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запуска анализа канала: {str(e)}")


@router.get("/channel-info/{channel_name}")
async def get_channel_info(channel_name: str):
    """
    Получить информацию о канале/чате для предпросмотра перед анализом
    """
    try:
        # Получаем базовую информацию о канале
        channel_info = await analytics_service.get_channel_info(channel_name)
        
        if not channel_info:
            raise HTTPException(status_code=404, detail="Канал не найден или недоступен")
        
        return {
            "channel_name": channel_name,
            "info": channel_info,
            "accessible": True
        }
        
    except Exception as e:
        return {
            "channel_name": channel_name,
            "error": str(e),
            "accessible": False
        }