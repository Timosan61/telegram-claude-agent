#!/usr/bin/env python3
"""
✅ Тест после переавторизации Telegram агента

Этот скрипт проверяет что переавторизация прошла успешно
и агент может видеть сообщения в Telegram.
"""
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerChat, PeerUser

async def test_reauth_success():
    """Проверка успешности переавторизации"""
    print("✅ ТЕСТ ПОСЛЕ ПЕРЕАВТОРИЗАЦИИ")
    print("=" * 40)
    
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    
    client = TelegramClient("telegram_agent", api_id, api_hash)
    
    try:
        await client.connect()
        
        # Проверка авторизации
        if not await client.is_user_authorized():
            print("❌ АВТОРИЗАЦИЯ НЕ РАБОТАЕТ")
            print("💡 Выполните: python reauth_telegram.py")
            return False
        
        print("✅ Авторизация работает!")
        
        # Информация о пользователе
        me = await client.get_me()
        print(f"👤 Пользователь: {me.first_name} (ID: {me.id})")
        
        # Проверка доступа к диалогам
        print(f"\\n📋 Доступные чаты:")
        
        dialogs_count = 0
        target_channels = []
        
        async for dialog in client.iter_dialogs(limit=20):
            dialogs_count += 1
            
            # Определяем тип
            if dialog.is_channel:
                if dialog.entity.megagroup:
                    chat_type = "👥"
                else:
                    chat_type = "📺"
            elif dialog.is_group:
                chat_type = "👥"
            else:
                chat_type = "👤"
            
            print(f"  {dialogs_count:2d}. {chat_type} {dialog.name}")
            
            # Ищем целевые каналы
            name_lower = dialog.name.lower()
            if any(target in name_lower for target in ['eslitotoeto', 'если это']):
                target_channels.append({
                    'name': dialog.name,
                    'id': dialog.id,
                    'type': chat_type
                })
        
        print(f"\\n📊 Найдено {dialogs_count} диалогов")
        
        if target_channels:
            print(f"\\n🎯 ЦЕЛЕВЫЕ КАНАЛЫ НАЙДЕНЫ:")
            for channel in target_channels:
                print(f"   {channel['type']} {channel['name']} (ID: {channel['id']})")
        else:
            print(f"\\n⚠️  Целевой канал @eslitotoeto не найден")
            print(f"   Возможно нужно присоединиться к каналу")
        
        # Краткий тест мониторинга
        print(f"\\n🔍 Тест мониторинга сообщений (5 секунд)...")
        print("💡 Напишите что-нибудь в любом чате для проверки")
        
        messages_received = 0
        
        @client.on(events.NewMessage())
        async def handler(event):
            nonlocal messages_received
            messages_received += 1
            
            # Получаем информацию о чате
            try:
                chat_entity = await client.get_entity(event.message.peer_id)
                chat_name = getattr(chat_entity, 'title', 
                                 getattr(chat_entity, 'username', 
                                        getattr(chat_entity, 'first_name', 'Неизвестно')))
            except:
                chat_name = "Неизвестно"
            
            text = event.message.text[:40] + "..." if event.message.text and len(event.message.text) > 40 else event.message.text or "[Медиа]"
            now = datetime.now().strftime("%H:%M:%S")
            
            print(f"📨 [{now}] {chat_name}: {text}")
        
        # Ждем сообщения
        await asyncio.sleep(5)
        
        print(f"\\n📊 РЕЗУЛЬТАТ ТЕСТА:")
        print(f"   Получено сообщений: {messages_received}")
        
        if messages_received > 0:
            print("   🎉 АГЕНТ ВИДИТ СООБЩЕНИЯ!")
            print("   ✅ Переавторизация успешна")
        else:
            print("   ⚠️  Новых сообщений не получено")
            print("   💡 Это нормально если нет активности в чатах")
            print("   ✅ Авторизация работает, агент готов к мониторингу")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        await client.disconnect()

async def main():
    success = await test_reauth_success()
    
    print("\\n" + "=" * 40)
    if success:
        print("🎉 ПЕРЕАВТОРИЗАЦИЯ ПОДТВЕРЖДЕНА!")
        print("🔧 Backend может использовать Telegram агент")
        print("🌐 Проверьте API: /health должен показать telegram_connected: true")
    else:
        print("❌ ПЕРЕАВТОРИЗАЦИЯ ТРЕБУЕТСЯ")
        print("💡 Выполните: python reauth_telegram.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n🛑 Тест прерван")
    except Exception as e:
        print(f"\\n❌ Ошибка: {e}")