#!/usr/bin/env python3
"""
🔐 Простой тест авторизации для проверки действительности сессии
"""
import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def test_auth():
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    phone = os.getenv("TELEGRAM_PHONE")
    
    print(f"🔐 Тестирование авторизации...")
    print(f"📱 Номер: {phone}")
    print(f"🔑 API ID: {api_id}")
    
    # Используем отдельное имя сессии для теста
    client = TelegramClient("auth_test", api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        me = await client.get_me()
        
        print(f"✅ АВТОРИЗАЦИЯ УСПЕШНА!")
        print(f"👤 Пользователь: {me.first_name}")
        print(f"📞 Телефон: {me.phone}")
        print(f"🆔 ID: {me.id}")
        
        # Теперь скопируем эту авторизацию в основную сессию
        await client.disconnect()
        
        # Копируем файл
        import shutil
        shutil.copy("auth_test.session", "telegram_agent.session")
        print(f"✅ Сессия скопирована в telegram_agent.session")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return False
    finally:
        if client.is_connected():
            await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_auth())