#!/usr/bin/env python3
"""
Создание Telegram сессии с ручным вводом кода
"""
import os
import base64
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

async def create_session_with_code(code=None):
    """Создание сессии с предоставленным кодом"""
    try:
        api_id = int(os.getenv("TELEGRAM_API_ID"))
        api_hash = os.getenv("TELEGRAM_API_HASH")
        phone = os.getenv("TELEGRAM_PHONE")
        
        print(f"📱 Создание сессии для {phone}")
        print(f"🔑 API ID: {api_id}")
        
        # Создаем StringSession для портативности
        string_session = StringSession()
        client = TelegramClient(string_session, api_id, api_hash)
        
        await client.connect()
        
        # Проверяем, авторизованы ли мы уже
        if await client.is_user_authorized():
            print("✅ Уже авторизованы!")
        else:
            print("📞 Отправляем код авторизации...")
            
            # Отправляем код
            await client.send_code_request(phone)
            print(f"✅ Код отправлен на {phone}")
            
            if code:
                print(f"🔐 Используем предоставленный код: {code}")
                await client.sign_in(phone, code)
            else:
                print("⚠️ Код не предоставлен. Необходимо получить код из Telegram и запустить с параметром.")
                print("Пример: python create_session_manual.py 12345")
                await client.disconnect()
                return None
        
        # Получаем информацию о пользователе
        me = await client.get_me()
        print(f"✅ Авторизация успешна!")
        print(f"👤 Пользователь: {me.first_name} {me.last_name or ''}")
        print(f"📱 Телефон: {me.phone}")
        print(f"🆔 ID: {me.id}")
        
        # Получаем строку сессии
        session_string = client.session.save()
        session_b64 = base64.b64encode(session_string.encode()).decode()
        
        print("\n🔑 ДАННЫЕ ДЛЯ APP PLATFORM:")
        print("=" * 50)
        print(f"TELEGRAM_SESSION_STRING={session_string}")
        print()
        print(f"TELEGRAM_SESSION_B64={session_b64}")
        print("=" * 50)
        
        # Сохраняем в файл
        with open("session_credentials.txt", "w") as f:
            f.write(f"TELEGRAM_SESSION_STRING={session_string}\n")
            f.write(f"TELEGRAM_SESSION_B64={session_b64}\n")
        
        print("💾 Данные сохранены в: session_credentials.txt")
        
        # Проверяем доступ к каналу
        print("\n📺 Проверка доступа к каналу...")
        try:
            channel = await client.get_entity("@eslitotoeto")
            print(f"✅ Канал найден: {channel.title}")
        except Exception as e:
            print(f"⚠️ Ошибка доступа к каналу: {e}")
        
        await client.disconnect()
        return session_string
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    import sys
    
    # Получаем код из аргументов командной строки
    code = None
    if len(sys.argv) > 1:
        code = sys.argv[1]
        print(f"📩 Используем код: {code}")
    
    session_string = await create_session_with_code(code)
    
    if session_string:
        print("\n🎉 СЕССИЯ СОЗДАНА УСПЕШНО!")
        print("📋 Скопируйте TELEGRAM_SESSION_STRING из session_credentials.txt")
        print("🚀 Добавьте её в DigitalOcean App Platform переменные окружения")
    else:
        print("\n❌ СОЗДАНИЕ СЕССИИ НЕ УДАЛОСЬ")
        if not code:
            print("💡 Запустите: python create_session_manual.py XXXXX (где XXXXX - код из Telegram)")

if __name__ == "__main__":
    asyncio.run(main())