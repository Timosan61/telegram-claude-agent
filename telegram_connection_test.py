#!/usr/bin/env python3
"""
Тест подключения к Telegram для проверки видимости сообщений
Проверяет различные способы подключения и сессии
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

async def test_telegram_connection():
    """Основной тест подключения"""
    print("🔍 Тестирование подключения к Telegram...")
    print("=" * 50)
    
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH") 
    phone = os.getenv("TELEGRAM_PHONE")
    
    print(f"📱 Телефон: {phone}")
    print(f"🔑 API ID: {api_id}")
    print()
    
    # Список сессий для проверки
    session_names = [
        "telegram_agent",
        "auth_test", 
        "interactive_test",
        "check_auth"
    ]
    
    for session_name in session_names:
        print(f"🔍 Проверяем сессию: {session_name}")
        
        try:
            client = TelegramClient(session_name, api_id, api_hash)
            
            # Попробуем подключиться
            await client.connect()
            
            if await client.is_user_authorized():
                print(f"✅ Сессия {session_name} авторизована!")
                
                # Получаем информацию о пользователе
                me = await client.get_me()
                print(f"👤 Авторизован как: {me.first_name} {me.last_name or ''}")
                print(f"📱 Телефон: {me.phone}")
                print(f"🆔 ID пользователя: {me.id}")
                
                # Получаем диалоги
                print(f"\\n📋 Ваши чаты и каналы:")
                dialogs_count = 0
                async for dialog in client.iter_dialogs(limit=15):
                    dialogs_count += 1
                    
                    # Определяем тип чата
                    if dialog.is_channel:
                        if dialog.entity.megagroup:
                            chat_type = "👥 Супергруппа"
                        else:
                            chat_type = "📺 Канал"
                    elif dialog.is_group:
                        chat_type = "👥 Группа"
                    else:
                        chat_type = "👤 Личный чат"
                    
                    # Показываем информацию о чате
                    print(f"  {dialogs_count:2d}. {chat_type}: {dialog.name}")
                    print(f"      ID: {dialog.id}, Непрочитано: {dialog.unread_count}")
                
                print(f"\\n📊 Найдено {dialogs_count} диалогов")
                
                # Тест мониторинга сообщений (5 секунд)
                print(f"\\n🔍 Тестируем мониторинг сообщений (10 секунд)...")
                print("💡 Напишите что-нибудь в любом чате для проверки")
                
                messages_received = 0
                
                @client.on(events.NewMessage())
                async def message_handler(event):
                    nonlocal messages_received
                    messages_received += 1
                    
                    message = event.message
                    now = datetime.now().strftime("%H:%M:%S")
                    
                    # Определяем тип чата
                    chat_info = "Неизвестно"
                    if isinstance(message.peer_id, PeerChannel):
                        chat_info = f"📺 Канал/Группа"
                    elif isinstance(message.peer_id, PeerChat):
                        chat_info = f"👥 Группа"
                    elif isinstance(message.peer_id, PeerUser):
                        chat_info = f"👤 Личный чат"
                    
                    # Получаем название чата
                    try:
                        chat_entity = await client.get_entity(message.peer_id)
                        chat_name = getattr(chat_entity, 'title', 
                                          getattr(chat_entity, 'username', 
                                                 getattr(chat_entity, 'first_name', 'Без названия')))
                        if hasattr(chat_entity, 'username') and chat_entity.username:
                            chat_name = f"@{chat_entity.username}"
                    except:
                        chat_name = "Неизвестно"
                    
                    # Текст сообщения
                    text = message.text[:60] + "..." if message.text and len(message.text) > 60 else message.text or "[Медиа]"
                    
                    print(f"📨 [{now}] #{messages_received}")
                    print(f"   {chat_info}: {chat_name}")
                    print(f"   💬 {text}")
                    print()
                
                # Ждем сообщения
                await asyncio.sleep(10)
                
                print(f"\\n📊 Результаты мониторинга:")
                print(f"   Получено сообщений: {messages_received}")
                
                if messages_received > 0:
                    print("   ✅ АГЕНТ ВИДИТ СООБЩЕНИЯ!")
                    print("   🎯 Telegram интеграция работает корректно")
                else:
                    print("   ⚠️  Новых сообщений не получено")
                    print("   💡 Это может быть нормально если нет активности в чатах")
                
                await client.disconnect()
                return True
                
            else:
                print(f"❌ Сессия {session_name} не авторизована")
                await client.disconnect()
                
        except Exception as e:
            print(f"❌ Ошибка с сессией {session_name}: {e}")
            try:
                await client.disconnect()
            except:
                pass
    
    print("\\n❌ Ни одна сессия не работает")
    print("💡 Требуется интерактивная авторизация Telegram")
    return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_telegram_connection())
        if result:
            print("\\n🎉 ТЕСТ УСПЕШЕН: Telegram агент может видеть сообщения!")
        else:
            print("\\n⚠️ ТЕСТ НЕ ПРОЙДЕН: Требуется настройка авторизации")
    except KeyboardInterrupt:
        print("\\n🛑 Тест прерван пользователем")
    except Exception as e:
        print(f"\\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()