"""
Главный файл FastAPI сервера для DigitalOcean App Platform
Адаптирован для работы с переменными окружения и StringSession
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import asyncio
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models.base import get_db, create_tables
from backend.api.campaigns import router as campaigns_router
from backend.api.logs import router as logs_router
from backend.api.chats import router as chats_router, set_telegram_agent
from backend.api.company import router as company_router
from backend.core.telegram_agent_app_platform import get_telegram_agent, stop_telegram_agent

# Загрузка переменных окружения
load_dotenv()

# Создание приложения FastAPI
app = FastAPI(
    title="Telegram Claude Agent API (App Platform)",
    description="API для управления ИИ-агентом в Telegram с поддержкой DigitalOcean App Platform",
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

# Глобальная переменная для хранения агента
telegram_agent = None

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    global telegram_agent
    
    # Создание таблиц БД
    create_tables()
    print("✅ База данных инициализирована")
    
    # Инициализация Telegram агента
    try:
        telegram_agent = await get_telegram_agent()
        
        # Передаем агента в роутер чатов
        if telegram_agent:
            set_telegram_agent(telegram_agent)
        
        if telegram_agent and telegram_agent.is_authorized:
            print("🚀 Telegram Claude Agent запущен в App Platform режиме!")
        else:
            print("⚠️ Telegram Agent запущен, но не авторизован")
            print("💡 Проверьте переменную TELEGRAM_SESSION_STRING")
    except Exception as e:
        print(f"❌ Ошибка инициализации Telegram Agent: {e}")
        telegram_agent = None

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении приложения"""
    global telegram_agent
    
    if telegram_agent:
        await stop_telegram_agent()
        print("✅ Telegram Agent остановлен")

@app.get("/")
async def root():
    """Корневая страница"""
    return {
        "message": "Telegram Claude Agent API",
        "version": "1.0.2",
        "platform": "DigitalOcean App Platform",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Проверка состояния приложения"""
    global telegram_agent
    
    # Базовый статус
    health_status = {
        "status": "healthy",
        "database": "connected",
        "platform": "app_platform"
    }
    
    # Статус Telegram подключения
    if telegram_agent:
        agent_status = await telegram_agent.get_status()
        health_status.update({
            "telegram_connected": agent_status.get("authorized", False),
            "telegram_status": agent_status,
            "session_type": agent_status.get("session_type", "unknown")
        })
    else:
        health_status.update({
            "telegram_connected": False,
            "telegram_status": "not_initialized",
            "session_type": "none"
        })
    
    # Статус AI провайдеров
    ai_providers = {}
    
    # Проверка OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    ai_providers["openai"] = bool(openai_key and len(openai_key) > 20)
    
    # Проверка Claude (опционально)
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    ai_providers["claude"] = bool(claude_key and len(claude_key) > 20)
    
    health_status["ai_providers"] = ai_providers
    
    # Проверка переменных окружения
    env_status = {}
    required_vars = [
        "TELEGRAM_API_ID",
        "TELEGRAM_API_HASH", 
        "TELEGRAM_PHONE"
    ]
    
    for var in required_vars:
        env_status[var] = bool(os.getenv(var))
    
    # Проверка сессии
    session_vars = [
        "TELEGRAM_SESSION_STRING",
        "TELEGRAM_SESSION_B64",
        "TELEGRAM_SESSION"
    ]
    
    env_status["session_available"] = any(os.getenv(var) for var in session_vars)
    health_status["environment"] = env_status
    
    return health_status

@app.get("/telegram/status")
async def telegram_status():
    """Детальный статус Telegram агента"""
    global telegram_agent
    
    if not telegram_agent:
        return {
            "status": "not_initialized",
            "message": "Telegram Agent не инициализирован"
        }
    
    status = await telegram_agent.get_status()
    
    return {
        "status": "initialized",
        "details": status,
        "message": "Telegram Agent статус получен"
    }

@app.post("/telegram/restart")
async def restart_telegram_agent():
    """Перезапуск Telegram агента"""
    global telegram_agent
    
    try:
        # Остановка текущего агента
        if telegram_agent:
            await stop_telegram_agent()
        
        # Запуск нового агента
        telegram_agent = await get_telegram_agent()
        
        if telegram_agent and telegram_agent.is_authorized:
            return {
                "status": "success",
                "message": "Telegram Agent перезапущен успешно"
            }
        else:
            return {
                "status": "warning",
                "message": "Telegram Agent перезапущен, но не авторизован"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка перезапуска: {str(e)}"
        }

@app.get("/environment/check")
async def check_environment():
    """Проверка переменных окружения"""
    env_info = {}
    
    # Telegram переменные
    telegram_vars = {
        "TELEGRAM_API_ID": os.getenv("TELEGRAM_API_ID"),
        "TELEGRAM_API_HASH": bool(os.getenv("TELEGRAM_API_HASH")),
        "TELEGRAM_PHONE": os.getenv("TELEGRAM_PHONE"),
    }
    
    # Сессионные переменные
    session_vars = {
        "TELEGRAM_SESSION_STRING": bool(os.getenv("TELEGRAM_SESSION_STRING")),
        "TELEGRAM_SESSION_B64": bool(os.getenv("TELEGRAM_SESSION_B64")),
        "TELEGRAM_SESSION": bool(os.getenv("TELEGRAM_SESSION")),
    }
    
    # AI провайдеры
    ai_vars = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
    }
    
    env_info.update({
        "telegram": telegram_vars,
        "session": session_vars,
        "ai_providers": ai_vars,
        "platform": "DigitalOcean App Platform"
    })
    
    return env_info

# Подключение роутеров API
app.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
app.include_router(logs_router, prefix="/logs", tags=["logs"])
app.include_router(chats_router, prefix="/chats", tags=["chats"])
app.include_router(company_router, prefix="/company", tags=["company"])

if __name__ == "__main__":
    import uvicorn
    
    # Получение настроек из переменных окружения
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    
    print(f"🚀 Запуск Telegram Claude Agent для App Platform на {host}:{port}")
    
    uvicorn.run(
        "backend.main_app_platform:app",
        host=host,
        port=port,
        reload=False,  # Отключаем reload в продакшене
        log_level="info"
    )