from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# База данных - Supabase PostgreSQL или локальный SQLite для разработки
def get_database_url():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") 
    
    if supabase_url and supabase_service_key:
        # Формируем PostgreSQL connection string для Supabase
        # Извлекаем project_id из URL вида https://project_id.supabase.co
        project_id = supabase_url.replace("https://", "").replace(".supabase.co", "")
        postgres_url = f"postgresql://postgres.{project_id}:{supabase_service_key}@aws-0-eu-north-1.pooler.supabase.com:6543/postgres"
        return postgres_url
    
    # Fallback к DATABASE_URL или SQLite для локальной разработки
    return os.getenv("DATABASE_URL", "sqlite:///./campaigns.db")

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