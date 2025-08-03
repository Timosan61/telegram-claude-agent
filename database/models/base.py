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
    
    # Проверяем наличие обеих переменных и что service key отличается от anon key
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    # Простая проверка что это JWT токен (3 части разделённые точками)
    is_valid_jwt = len(supabase_service_key.split('.')) == 3 if supabase_service_key else False
    
    if (supabase_url and supabase_service_key and 
        anon_key and supabase_service_key != anon_key and
        is_valid_jwt):
        
        # Формируем PostgreSQL connection string для Supabase
        # Извлекаем project_id из URL вида https://project_id.supabase.co
        project_id = supabase_url.replace("https://", "").replace(".supabase.co", "")
        postgres_url = f"postgresql://postgres.{project_id}:{supabase_service_key}@aws-0-eu-north-1.pooler.supabase.com:6543/postgres"
        print(f"🔗 Подключение к Supabase: postgresql://postgres.{project_id}:***@aws-0-eu-north-1.pooler.supabase.com:6543/postgres")
        return postgres_url
    else:
        # Отладочная информация
        print(f"🔍 Debug info:")
        print(f"  SUPABASE_URL: {'✅' if supabase_url else '❌'}")
        print(f"  SUPABASE_SERVICE_ROLE_KEY: {'✅' if supabase_service_key else '❌'}")
        print(f"  SUPABASE_ANON_KEY: {'✅' if anon_key else '❌'}")
        if supabase_service_key and anon_key:
            print(f"  Keys different: {'✅' if supabase_service_key != anon_key else '❌'}")
            is_valid_jwt = len(supabase_service_key.split('.')) == 3 if supabase_service_key else False
            print(f"  Valid JWT format: {'✅' if is_valid_jwt else '❌'}")
    
    # Fallback к DATABASE_URL или SQLite для локальной разработки
    print("🔄 Fallback к SQLite для локальной разработки")
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