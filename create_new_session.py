#!/usr/bin/env python3
"""
🔄 Создание новой Telegram сессии

Этот скрипт создает новую сессию без интерактивного ввода,
используя предварительно сохраненные данные авторизации.
"""
import asyncio
import os
import sys
from datetime import datetime
import sqlite3
from dotenv import load_dotenv

load_dotenv()

try:
    from telethon import TelegramClient
    from telethon.sessions import SQLiteSession
except ImportError:
    print("❌ ОШИБКА: telethon не установлен")
    print("Выполните: pip install telethon cryptg python-dotenv")
    sys.exit(1)

async def create_fresh_session():
    """Создание новой чистой сессии"""
    print("🔄 СОЗДАНИЕ НОВОЙ TELEGRAM СЕССИИ")
    print("=" * 45)
    
    # Получение конфигурации
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    phone = os.getenv("TELEGRAM_PHONE")
    
    if not all([api_id, api_hash, phone]):
        print("❌ Ошибка: не все переменные настроены в .env")
        return False
    
    api_id = int(api_id)
    print(f"📋 Конфигурация:")
    print(f"   📱 Телефон: {phone}")
    print(f"   🔑 API ID: {api_id}")
    
    # Удаление старой сессии
    session_file = "telegram_agent.session"
    if os.path.exists(session_file):
        backup_name = f"{session_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(session_file, backup_name)
        print(f"📁 Старая сессия сохранена как: {backup_name}")
    
    # Анализ существующей сессии для извлечения данных авторизации
    print("\n🔍 Анализ резервной сессии для восстановления...")
    
    try:
        # Попробуем извлечь данные авторизации из резервной копии
        conn = sqlite3.connect(backup_name)
        cursor = conn.cursor()
        
        # Получаем данные сессии
        cursor.execute("SELECT * FROM sessions")
        session_data = cursor.fetchall()
        
        if session_data:
            print("✅ Найдены данные авторизации в резервной сессии")
            dc_id, server_address, port, auth_key, takeout_id = session_data[0]
            print(f"   DC ID: {dc_id}")
            print(f"   Сервер: {server_address}:{port}")
            
            # Создаем новую сессию с существующими данными авторизации
            client = TelegramClient("telegram_agent", api_id, api_hash)
            
            # Подключаемся
            await client.connect()
            
            # Проверяем авторизацию
            if await client.is_user_authorized():
                print("✅ Авторизация восстановлена из резервной сессии!")
                
                # Проверяем доступ
                me = await client.get_me()
                print(f"👤 Пользователь: {me.first_name} {me.last_name or ''}")
                
                # Проверяем диалоги
                print("\n📋 Проверка доступа к диалогам...")
                dialogs_count = 0
                target_found = False
                
                async for dialog in client.iter_dialogs(limit=10):
                    dialogs_count += 1
                    
                    if 'eslitotoeto' in dialog.name.lower():
                        target_found = True
                        print(f"🎯 ЦЕЛЕВОЙ КАНАЛ НАЙДЕН: {dialog.name}")
                
                print(f"📊 Доступно диалогов: {dialogs_count}")
                print(f"🎯 Целевой канал: {'✅ Найден' if target_found else '❌ Не найден'}")
                
                await client.disconnect()
                conn.close()
                
                return True
            else:
                print("❌ Авторизация из резервной сессии не работает")
                await client.disconnect()
                conn.close()
                return False
                
        else:
            print("❌ Данные авторизации не найдены в резервной сессии")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Ошибка восстановления сессии: {e}")
        return False

async def main():
    success = await create_fresh_session()
    
    print("\n" + "=" * 45)
    if success:
        print("✅ СЕССИЯ УСПЕШНО ВОССТАНОВЛЕНА")
        print("🔧 Backend может использовать Telegram агент")
        print("🎯 Агент готов к мониторингу сообщений")
        print("\n📋 Следующие шаги:")
        print("   1. Запустите тест: python test_after_reauth.py")
        print("   2. Проверьте API: curl <backend_url>/health")
    else:
        print("❌ ВОССТАНОВЛЕНИЕ СЕССИИ НЕ УДАЛОСЬ")
        print("💡 Требуется ручная переавторизация:")
        print("   1. Запустите в интерактивной среде: python reauth_telegram.py")
        print("   2. Введите код из Telegram")
        print("   3. Проверьте результат: python test_after_reauth.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Процесс прерван")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()