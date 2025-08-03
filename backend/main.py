from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models.base import get_db, create_tables
from backend.api.campaigns import router as campaigns_router
from backend.api.logs import router as logs_router
from backend.api.chats import router as chats_router, set_telegram_agent
from backend.api.campaigns import set_telegram_agent as set_campaigns_agent
from backend.api.company import router as company_router
from backend.core.telegram_agent import TelegramAgent

# Загрузка переменных окружения
load_dotenv()

# Создание приложения FastAPI
app = FastAPI(
    title="Telegram Claude Agent API",
    description="API для управления ИИ-агентом в Telegram с Claude Code SDK",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware для работы со Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный экземпляр Telegram агента
telegram_agent = None


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    # Создание таблиц БД
    create_tables()
    
    # Инициализация Telegram агента
    global telegram_agent
    telegram_agent = TelegramAgent()
    await telegram_agent.initialize()
    
    # Передаем агента в роутеры
    set_telegram_agent(telegram_agent)
    set_campaigns_agent(telegram_agent)
    
    print("🚀 Telegram Claude Agent запущен!")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка ресурсов при завершении"""
    global telegram_agent
    if telegram_agent:
        await telegram_agent.disconnect()
    print("👋 Telegram Claude Agent остановлен!")


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Telegram Claude Agent API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Проверка состояния системы"""
    global telegram_agent
    
    return {
        "status": "healthy",
        "telegram_connected": (telegram_agent.is_connected() if hasattr(telegram_agent, 'is_connected') and callable(telegram_agent.is_connected) else telegram_agent.is_connected) if telegram_agent else False,
        "database": "connected"
    }


# Подключение роутеров
app.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
app.include_router(logs_router, prefix="/logs", tags=["logs"])
app.include_router(chats_router, prefix="/chats", tags=["chats"])
app.include_router(company_router, prefix="/company", tags=["company"])


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )