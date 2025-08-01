"""
Минимальная версия FastAPI сервера для тестирования без Telegram
"""

from fastapi import FastAPI, Depends
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

# Загрузка переменных окружения
load_dotenv()

# Создание приложения FastAPI
app = FastAPI(
    title="Telegram Claude Agent API (Minimal)",
    description="API для управления ИИ-агентом в Telegram с Claude Code SDK (без Telegram подключения)",
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


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    # Создание таблиц БД
    create_tables()
    print("🚀 Minimal Telegram Claude Agent API запущен!")


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Telegram Claude Agent API (Minimal Mode)",
        "version": "1.0.0-minimal",
        "status": "active",
        "note": "Запущен без Telegram соединения для тестирования API"
    }


@app.get("/health")
async def health_check():
    """Проверка состояния системы"""
    return {
        "status": "healthy",
        "telegram_connected": False,  # В минимальном режиме всегда False
        "database": "connected",
        "mode": "minimal"
    }


# Подключение роутеров
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(logs_router, prefix="/api/logs", tags=["logs"])


if __name__ == "__main__":
    import uvicorn
    
    # Поддержка как локального так и облачного развертывания
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🚀 Запуск сервера на {host}:{port}")
    print(f"🔧 Режим отладки: {debug}")
    print(f"📂 Рабочая директория: {os.getcwd()}")
    
    uvicorn.run(
        "backend.main_minimal:app",
        host=host, 
        port=port,
        reload=debug,
        log_level="info"
    )