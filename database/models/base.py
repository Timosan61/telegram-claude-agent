from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# База данных - Supabase PostgreSQL или локальный SQLite для разработки
def get_database_url():
    # Проверяем есть ли прямой DATABASE_URL
    direct_db_url = os.getenv("DATABASE_URL")
    if direct_db_url:
        print(f"🔗 Используем прямой DATABASE_URL")
        return direct_db_url
    
    # Fallback к SQLite для локальной разработки
    print("🔄 Fallback к SQLite для локальной разработки")
    return "sqlite:///./campaigns.db"

DATABASE_URL = get_database_url()

# Создаем engine с правильными параметрами
if "postgresql" in DATABASE_URL:
    # PostgreSQL/Supabase настройки
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
else:
    # SQLite настройки для локальной разработки
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Создание всех таблиц в базе данных"""
    Base.metadata.create_all(bind=engine)