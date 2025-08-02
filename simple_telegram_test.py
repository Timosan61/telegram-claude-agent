#!/usr/bin/env python3
"""
Простой тест для проверки видимости сообщений в Telegram группах
Использует существующую сессию без интерактивного ввода
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

class SimpleTelegramTester:
    def __init__(self):
        self.api_id = int(os.getenv("TELEGRAM_API_ID"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        
        # Используем существующую сессию
        self.client = TelegramClient("telegram_agent", self.api_id, self.api_hash)
        self.message_count = 0
        self.test_duration = 20  # секунд
        
    async def test_connection(self):
        """Тест подключения и мониторинга"""
        print("🧪 Простой тест Telegram агента")
        print("=" * 50)
        
        try:
            # Подключение с существующей сессией
            await self.client.start()
            print("✅ Подключен к Telegram через существующую сессию")
            
            # Получение информации о себе
            me = await self.client.get_me()
            print(f"👤 Авторизован как: {me.first_name} ({me.username or 'без username'})")
            print(f"📱 Телефон: {me.phone}")
            print()
            
            # Получение списка диалогов (чатов)
            print("📋 Ваши чаты:")
            async for dialog in self.client.iter_dialogs(limit=10):
                chat_type = ""
                if dialog.is_channel:
                    chat_type = "📺 Канал"
                elif dialog.is_group:
                    chat_type = "👥 Группа" 
                else:
                    chat_type = "👤 Личный"
                print(f"  {chat_type}: {dialog.name} (ID: {dialog.id})")
            print()
            
            # Регистрация обработчика сообщений
            @self.client.on(events.NewMessage())
            async def handler(event):
                await self.handle_message(event)
            
            print(f"🔍 Начинаю мониторинг сообщений на {self.test_duration} секунд...")
            print("💡 Напишите что-нибудь в любом чате чтобы увидеть реакцию")
            print("=" * 50)
            
            # Ожидание сообщений
            await asyncio.sleep(self.test_duration)
            
            print(f"\n📊 Результат теста:")
            print(f"   Получено сообщений: {self.message_count}")
            if self.message_count == 0:
                print("   ⚠️  Сообщения не получены - возможно нет новых сообщений")
            else:
                print("   ✅ Агент видит сообщения!")
                
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
        finally:
            await self.client.disconnect()
            
        return True
    
    async def handle_message(self, event):
        """Обработчик входящих сообщений"""
        try:
            self.message_count += 1
            message = event.message
            
            # Определение типа чата
            chat_info = "Неизвестно"
            if isinstance(message.peer_id, PeerChannel):
                chat_info = f"📺 Канал ID: {message.peer_id.channel_id}"
            elif isinstance(message.peer_id, PeerChat):
                chat_info = f"👥 Группа ID: {message.peer_id.chat_id}"
            elif isinstance(message.peer_id, PeerUser):
                chat_info = f"👤 Личный ID: {message.peer_id.user_id}"
            
            # Получение названия чата
            try:
                chat_entity = await self.client.get_entity(message.peer_id)
                if hasattr(chat_entity, 'title'):
                    chat_name = chat_entity.title
                elif hasattr(chat_entity, 'username'):
                    chat_name = f"@{chat_entity.username}"
                elif hasattr(chat_entity, 'first_name'):
                    chat_name = chat_entity.first_name
                else:
                    chat_name = "Без названия"
            except:
                chat_name = "Неизвестно"
            
            # Краткий текст сообщения
            text_preview = "Пустое"
            if message.text:
                text_preview = message.text[:50] + "..." if len(message.text) > 50 else message.text
            
            # Время
            now = datetime.now().strftime("%H:%M:%S")
            
            print(f"📨 [{now}] #{self.message_count}")
            print(f"   {chat_info}")
            print(f"   📛 {chat_name}")
            print(f"   💬 {text_preview}")
            print()
            
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")

async def main():
    """Главная функция"""
    tester = SimpleTelegramTester()
    success = await tester.test_connection()
    
    if success:
        print("✅ Тест завершен успешно!")
    else:
        print("❌ Тест завершен с ошибками")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Тест прерван пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")