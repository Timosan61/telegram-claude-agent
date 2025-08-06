#!/usr/bin/env python3
"""
Скрипт для авторизации Telegram Analytics Service.

Этот скрипт должен запускаться ЛОКАЛЬНО для первичной авторизации.
После успешной авторизации файл analytics_session.session нужно
скопировать на продакшн сервер.

Использование:
1. Установите переменные окружения TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
2. Запустите: python authorize_telegram.py
3. Введите код подтверждения из SMS
4. Скопируйте analytics_session.session на продакшн
"""

import os
import sys
import asyncio
from pathlib import Path

# Добавляем корневую директорию в путь для импорта модулей
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from backend.services.analytics_service import analytics_service


async def main():
    """Главная функция авторизации"""
    
    print("🔐 Telegram Analytics Service - Авторизация")
    print("=" * 50)
    
    # Проверяем переменные окружения
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH") 
    phone = os.getenv("TELEGRAM_PHONE")
    
    print(f"📋 Проверка переменных окружения:")
    print(f"   TELEGRAM_API_ID: {'✅' if api_id else '❌ Отсутствует'}")
    print(f"   TELEGRAM_API_HASH: {'✅' if api_hash else '❌ Отсутствует'}")
    print(f"   TELEGRAM_PHONE: {'✅' if phone else '❌ Отсутствует'}")
    print()
    
    if not all([api_id, api_hash, phone]):
        print("❌ Не все переменные окружения установлены!")
        print("💡 Установите переменные и запустите снова:")
        print("   export TELEGRAM_API_ID=your_api_id")
        print("   export TELEGRAM_API_HASH=your_api_hash")  
        print("   export TELEGRAM_PHONE=your_phone")
        return False
    
    # Проверяем существующую сессию
    session_path = Path("analytics_session.session")
    if session_path.exists():
        print(f"📁 Найден файл сессии: {session_path}")
        choice = input("Переавторизоваться? [y/N]: ").lower().strip()
        if choice != 'y':
            print("👋 Авторизация отменена")
            return True
    
    print("🔄 Начинаем авторизацию...")
    print("📱 На ваш номер телефона придет SMS с кодом подтверждения")
    print()
    
    # Выполняем авторизацию
    try:
        success = await analytics_service.authorize()
        
        if success:
            print()
            print("🎉 Авторизация успешна!")
            print(f"✅ Файл сессии создан: {session_path.absolute()}")
            print()
            print("📤 Следующие шаги:")
            print("1. Скопируйте файл analytics_session.session на продакшн сервер")
            print("2. Убедитесь что файл доступен в рабочей директории приложения")
            print("3. Перезапустите приложение на продакшн")
            print()
            print("🔧 Для DigitalOcean App Platform:")
            print("   - Загрузите файл через Git или Volume Mount")
            print("   - Убедитесь что путь к файлу корректен в приложении")
            
            return True
        else:
            print("❌ Авторизация не удалась")
            return False
            
    except KeyboardInterrupt:
        print("\n👋 Авторизация прервана пользователем")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False
    finally:
        # Отключаемся от клиента
        try:
            await analytics_service.disconnect()
        except:
            pass


if __name__ == "__main__":
    # Запускаем авторизацию
    success = asyncio.run(main())
    
    if success:
        print("✅ Готово!")
        sys.exit(0)
    else:
        print("❌ Ошибка авторизации")
        sys.exit(1)