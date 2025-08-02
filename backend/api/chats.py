from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
import json

from database.models.base import get_db
from database.models.campaign import Campaign
from database.models.log import ActivityLog

router = APIRouter()

# Глобальная переменная для доступа к telegram_agent
telegram_agent = None

def set_telegram_agent(agent):
    """Установка глобального экземпляра telegram агента"""
    global telegram_agent
    telegram_agent = agent


@router.get("/active")
async def get_active_chats(db: Session = Depends(get_db)):
    """Получение списка активных чатов из кампаний"""
    try:
        # Получаем все активные кампании
        campaigns = db.query(Campaign).filter(Campaign.active == True).all()
        
        active_chats = []
        chat_set = set()  # Для избежания дублирования
        
        for campaign in campaigns:
            for chat_id in campaign.telegram_chats:
                if chat_id not in chat_set:
                    chat_set.add(chat_id)
                    
                    # Получаем информацию о чате из логов
                    latest_log = db.query(ActivityLog).filter(
                        ActivityLog.chat_id == chat_id
                    ).order_by(ActivityLog.timestamp.desc()).first()
                    
                    chat_info = {
                        "chat_id": chat_id,
                        "chat_title": latest_log.chat_title if latest_log else chat_id,
                        "campaign_count": sum(1 for c in campaigns if chat_id in c.telegram_chats),
                        "last_activity": latest_log.timestamp.isoformat() if latest_log else None,
                        "last_message": latest_log.original_message[:100] + "..." if latest_log and latest_log.original_message and len(latest_log.original_message) > 100 else (latest_log.original_message if latest_log else None),
                        "is_connected": (telegram_agent.is_connected() if hasattr(telegram_agent, 'is_connected') and callable(telegram_agent.is_connected) else telegram_agent.is_connected) if telegram_agent else False
                    }
                    active_chats.append(chat_info)
        
        return active_chats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения активных чатов: {str(e)}")


@router.get("/{chat_id}/messages")
async def get_chat_messages(
    chat_id: str, 
    limit: int = 50,
    before_message_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Получение сообщений из чата"""
    try:
        if not telegram_agent or not (telegram_agent.is_connected() if hasattr(telegram_agent, 'is_connected') and callable(telegram_agent.is_connected) else telegram_agent.is_connected):
            raise HTTPException(status_code=503, detail="Telegram агент не подключен")
        
        # Получаем сообщения через Telegram API
        chat_entity = await telegram_agent.client.get_entity(chat_id)
        
        messages = []
        async for message in telegram_agent.client.iter_messages(
            chat_entity, 
            limit=limit,
            max_id=before_message_id
        ):
            # Получаем информацию об отправителе
            sender_info = "Unknown"
            if message.sender:
                if hasattr(message.sender, 'username') and message.sender.username:
                    sender_info = f"@{message.sender.username}"
                elif hasattr(message.sender, 'first_name'):
                    sender_info = message.sender.first_name
                    if hasattr(message.sender, 'last_name') and message.sender.last_name:
                        sender_info += f" {message.sender.last_name}"
            
            # Проверяем, есть ли ответ бота на это сообщение
            bot_response = None
            log_entry = db.query(ActivityLog).filter(
                ActivityLog.chat_id == str(chat_id),
                ActivityLog.message_id == message.id
            ).first()
            
            if log_entry:
                bot_response = {
                    "response": log_entry.agent_response,
                    "status": log_entry.status,
                    "trigger_keyword": log_entry.trigger_keyword,
                    "processing_time_ms": log_entry.processing_time_ms
                }
            
            messages.append({
                "id": message.id,
                "text": message.text or "",
                "date": message.date.isoformat(),
                "sender": sender_info,
                "sender_id": str(message.sender_id) if message.sender_id else None,
                "is_bot": bool(message.via_bot_id) or (message.sender and getattr(message.sender, 'bot', False)),
                "bot_response": bot_response
            })
        
        return {
            "chat_id": chat_id,
            "chat_title": chat_entity.title if hasattr(chat_entity, 'title') else chat_id,
            "messages": messages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения сообщений: {str(e)}")


@router.post("/{chat_id}/send")
async def send_message_to_chat(
    chat_id: str,
    message_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Отправка сообщения в чат от имени бота"""
    try:
        if not telegram_agent or not (telegram_agent.is_connected() if hasattr(telegram_agent, 'is_connected') and callable(telegram_agent.is_connected) else telegram_agent.is_connected):
            raise HTTPException(status_code=503, detail="Telegram агент не подключен")
        
        text = message_data.get("text", "").strip()
        reply_to = message_data.get("reply_to")  # ID сообщения для ответа
        
        if not text:
            raise HTTPException(status_code=400, detail="Текст сообщения не может быть пустым")
        
        # Отправляем сообщение
        sent_message = await telegram_agent.client.send_message(
            chat_id,
            text,
            reply_to=reply_to
        )
        
        # Логируем отправку
        background_tasks.add_task(
            log_manual_message,
            db,
            chat_id,
            sent_message.id,
            text,
            "manual_send",
            reply_to
        )
        
        return {
            "success": True,
            "message_id": sent_message.id,
            "chat_id": chat_id,
            "text": text,
            "timestamp": sent_message.date.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка отправки сообщения: {str(e)}")


@router.get("/{chat_id}/info")
async def get_chat_info(chat_id: str):
    """Получение информации о чате"""
    try:
        if not telegram_agent or not (telegram_agent.is_connected() if hasattr(telegram_agent, 'is_connected') and callable(telegram_agent.is_connected) else telegram_agent.is_connected):
            raise HTTPException(status_code=503, detail="Telegram агент не подключен")
        
        chat_entity = await telegram_agent.client.get_entity(chat_id)
        
        info = {
            "id": str(chat_entity.id),
            "title": getattr(chat_entity, 'title', 'Private Chat'),
            "type": "channel" if hasattr(chat_entity, 'broadcast') else "group" if hasattr(chat_entity, 'megagroup') else "private",
            "username": f"@{chat_entity.username}" if getattr(chat_entity, 'username', None) else None,
            "participant_count": getattr(chat_entity, 'participants_count', None),
            "description": getattr(chat_entity, 'about', None)
        }
        
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения информации о чате: {str(e)}")


@router.get("/{chat_id}/campaigns")
async def get_chat_campaigns(chat_id: str, db: Session = Depends(get_db)):
    """Получение кампаний, которые мониторят данный чат"""
    try:
        campaigns = db.query(Campaign).filter(
            Campaign.telegram_chats.contains([chat_id])
        ).all()
        
        campaign_info = []
        for campaign in campaigns:
            campaign_info.append({
                "id": campaign.id,
                "name": campaign.name,
                "active": campaign.active,
                "keywords": campaign.keywords,
                "ai_provider": getattr(campaign, 'ai_provider', 'claude'),
                "context_messages_count": campaign.context_messages_count
            })
        
        return {
            "chat_id": chat_id,
            "campaigns": campaign_info,
            "total_campaigns": len(campaign_info)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения кампаний для чата: {str(e)}")


@router.post("/{chat_id}/trigger")
async def trigger_manual_response(
    chat_id: str,
    trigger_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Принудительная генерация ответа для сообщения"""
    try:
        if not telegram_agent or not (telegram_agent.is_connected() if hasattr(telegram_agent, 'is_connected') and callable(telegram_agent.is_connected) else telegram_agent.is_connected):
            raise HTTPException(status_code=503, detail="Telegram агент не подключен")
        
        message_id = trigger_data.get("message_id")
        campaign_id = trigger_data.get("campaign_id")
        
        if not message_id or not campaign_id:
            raise HTTPException(status_code=400, detail="Требуются message_id и campaign_id")
        
        # Получаем кампанию
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Кампания не найдена")
        
        # Получаем сообщение
        message = await telegram_agent.client.get_messages(chat_id, ids=[message_id])
        if not message or not message[0]:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")
        
        target_message = message[0]
        
        # Запускаем обработку в фоне
        background_tasks.add_task(
            process_manual_trigger,
            campaign,
            target_message
        )
        
        return {
            "success": True,
            "message": "Обработка запущена",
            "message_id": message_id,
            "campaign_id": campaign_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запуска принудительной обработки: {str(e)}")


async def log_manual_message(
    db: Session,
    chat_id: str,
    message_id: int,
    text: str,
    action: str,
    reply_to: Optional[int] = None
):
    """Логирование ручных действий"""
    try:
        # Получаем информацию о чате
        chat_title = "Unknown"
        if telegram_agent and (telegram_agent.is_connected() if hasattr(telegram_agent, 'is_connected') and callable(telegram_agent.is_connected) else telegram_agent.is_connected):
            try:
                entity = await telegram_agent.client.get_entity(chat_id)
                if hasattr(entity, 'title'):
                    chat_title = entity.title
                elif hasattr(entity, 'username'):
                    chat_title = f"@{entity.username}"
            except:
                pass
        
        # Создаем запись лога
        log_entry = ActivityLog(
            campaign_id=0,  # 0 для ручных действий
            chat_id=str(chat_id),
            chat_title=chat_title,
            message_id=message_id,
            trigger_keyword=action,
            context_messages=[],
            original_message=text,
            agent_response=f"Manual action: {action}",
            status="sent",
            processing_time_ms=0
        )
        
        db.add(log_entry)
        db.commit()
        
    except Exception as e:
        print(f"Ошибка логирования ручного действия: {e}")


async def process_manual_trigger(campaign: Campaign, message):
    """Обработка принудительного триггера"""
    try:
        if telegram_agent:
            await telegram_agent.process_campaign_trigger(campaign, message)
    except Exception as e:
        print(f"Ошибка принудительной обработки: {e}")