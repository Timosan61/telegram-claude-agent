#!/usr/bin/env python3
"""
Извлечение TELEGRAM_SESSION_STRING из существующего файла сессии
"""
import os
import base64
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

async def extract_session_string():
    """Извлекает строку сессии из существующего файла"""
    try:
        api_id = int(os.getenv("TELEGRAM_API_ID"))
        api_hash = os.getenv("TELEGRAM_API_HASH")
        
        print("🔗 Загрузка существующей сессии...")
        
        # Загружаем существующую сессию
        client = TelegramClient('telegram_agent', api_id, api_hash)
        
        # Подключаемся и проверяем авторизацию
        await client.connect()
        
        if await client.is_user_authorized():
            print("✅ Сессия найдена и авторизована!")
            
            # Получаем информацию о пользователе
            me = await client.get_me()
            print(f"👤 Пользователь: {me.first_name} {me.last_name or ''}")
            print(f"📱 Телефон: {me.phone}")
            print(f"🆔 ID: {me.id}")
            if me.username:
                print(f"📧 Username: @{me.username}")
            
            # Создаем новый StringSession с теми же данными
            string_session = StringSession()
            string_client = TelegramClient(string_session, api_id, api_hash)
            
            # Копируем авторизацию
            await string_client.connect()
            
            # Получаем строку сессии из оригинального клиента
            # Нам нужно получить raw данные сессии
            session_data = client.session.save()
            
            # Создаем StringSession и загружаем в него данные
            string_session_obj = StringSession()
            string_session_obj.load(session_data)
            
            # Получаем строку
            session_string = string_session_obj.save()
            
            print("\n🔑 ДАННЫЕ ДЛЯ APP PLATFORM:")
            print("=" * 50)
            print(f"TELEGRAM_SESSION_STRING={session_string}")
            
            # Также создаем base64 версию
            session_b64 = base64.b64encode(session_string.encode()).decode()
            print(f"TELEGRAM_SESSION_B64={session_b64}")
            
            # Сохраняем в файл
            with open("session_for_app_platform.txt", "w") as f:
                f.write(f"TELEGRAM_SESSION_STRING={session_string}\n")
                f.write(f"TELEGRAM_SESSION_B64={session_b64}\n")
            
            print("\n💾 Данные сохранены в: session_for_app_platform.txt")
            
            await string_client.disconnect()
            
        else:
            print("❌ Сессия не авторизована")
            return None
            
        await client.disconnect()
        return session_string
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    session_string = await extract_session_string()
    if session_string:
        print("\n🎉 СЕССИЯ УСПЕШНО ИЗВЛЕЧЕНА!")
        print("📋 Используйте данные из session_for_app_platform.txt")
    else:
        print("\n❌ НЕ УДАЛОСЬ ИЗВЛЕЧЬ СЕССИЮ")

if __name__ == "__main__":
    asyncio.run(main())