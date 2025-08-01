#!/usr/bin/env python3
"""
🎮 Интерактивный тестер для Telegram агента с отладочным режимом

Позволяет:
- Включить отладочный режим в агенте
- Отправлять тестовые сообщения
- Видеть полный путь обработки сообщения
- Проверять реакцию агента в реальном времени
"""
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from telethon import TelegramClient, events
from telethon.tl.types import Message

class InteractiveAgentTester:
    def __init__(self):
        self.api_id = int(os.getenv("TELEGRAM_API_ID"))
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        
        self.client = TelegramClient("telegram_agent", self.api_id, self.api_hash)
        self.debug_mode = True
        self.test_keywords = ["ии", "бот", "искусственный интеллект", "помощь"]
        
        # Счетчики для статистики
        self.total_messages = 0
        self.matching_messages = 0
        self.responses_sent = 0
        
    async def start_interactive_testing(self):
        """Запуск интерактивного тестирования"""
        print("🎮 Интерактивный тестер Telegram агента")
        print("=" * 60)
        
        await self.client.start(phone=self.phone)
        me = await self.client.get_me()
        print(f"✅ Подключен как: {me.first_name}")
        
        # Регистрируем обработчик с отладкой
        self.client.add_event_handler(self.debug_message_handler, events.NewMessage())
        
        print(f"🔧 Отладочный режим: {'✅ ВКЛЮЧЕН' if self.debug_mode else '❌ ВЫКЛЮЧЕН'}")
        print(f"🎯 Тестовые ключевые слова: {', '.join(self.test_keywords)}")
        print()
        
        # Показываем меню команд
        self.show_commands()
        
        # Запускаем интерактивный режим
        await self.run_interactive_mode()
    
    def show_commands(self):
        """Показать доступные команды"""
        print("🎮 ДОСТУПНЫЕ КОМАНДЫ:")
        print("─" * 30)
        print("help     - Показать эту справку")
        print("status   - Показать статистику")
        print("debug    - Переключить отладочный режим")
        print("test     - Отправить тестовое сообщение")
        print("monitor  - Начать мониторинг (Ctrl+C для остановки)")
        print("channel  - Проверить доступ к каналу @eslitotoeto")
        print("keywords - Изменить тестовые ключевые слова")
        print("quit     - Выйти из программы")
        print("─" * 30)
        print()
    
    async def run_interactive_mode(self):
        """Интерактивный режим с командами"""
        print("💡 Введите команду или 'help' для справки:")
        
        while True:
            try:
                command = input("🎮 > ").strip().lower()
                
                if command == "help":
                    self.show_commands()
                    
                elif command == "status":
                    await self.show_status()
                    
                elif command == "debug":
                    self.debug_mode = not self.debug_mode
                    print(f"🔧 Отладочный режим: {'✅ ВКЛЮЧЕН' if self.debug_mode else '❌ ВЫКЛЮЧЕН'}")
                    
                elif command == "test":
                    await self.send_test_message()
                    
                elif command == "monitor":
                    await self.start_monitoring()
                    
                elif command == "channel":
                    await self.check_channel_access()
                    
                elif command == "keywords":
                    await self.change_keywords()
                    
                elif command in ["quit", "exit", "q"]:
                    print("👋 До свидания!")
                    break
                    
                else:
                    print(f"❌ Неизвестная команда: '{command}'. Введите 'help' для справки.")
                    
            except KeyboardInterrupt:
                print("\\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка выполнения команды: {e}")
        
        await self.client.disconnect()
    
    async def debug_message_handler(self, event):
        """Обработчик сообщений с отладочной информацией (имитация агента)"""
        if not self.debug_mode:
            return
            
        try:
            message: Message = event.message
            self.total_messages += 1
            
            now = datetime.now().strftime("%H:%M:%S")
            print(f"\\n🔍 DEBUG [{now}] - Обработка сообщения #{self.total_messages}")
            print("─" * 50)
            
            # Шаг 1: Определение типа чата
            chat_info = await self.get_chat_info(message.peer_id)
            print(f"1️⃣ Чат: {chat_info['type']} '{chat_info['title']}' (ID: {chat_info['id']})")
            
            # Шаг 2: Проверка текста сообщения
            if message.text:
                text_preview = message.text[:80] + "..." if len(message.text) > 80 else message.text
                print(f"2️⃣ Текст: {text_preview}")
            else:
                print(f"2️⃣ Текст: [Нет текста или медиа]")
                print("❌ ФИЛЬТР: Сообщение без текста - игнорируется")
                return
            
            # Шаг 3: Проверка кампаний (имитация)
            is_monitored_chat = self.is_chat_monitored(chat_info)
            print(f"3️⃣ Мониторинг чата: {'✅ ДА' if is_monitored_chat else '❌ НЕТ'}")
            
            if not is_monitored_chat:
                print("❌ ФИЛЬТР: Чат не отслеживается - игнорируется")
                return
            
            # Шаг 4: Проверка ключевых слов
            found_keywords = self.find_keywords(message.text)
            print(f"4️⃣ Ключевые слова: {', '.join(found_keywords) if found_keywords else 'не найдены'}")
            
            if not found_keywords:
                print("❌ ФИЛЬТР: Ключевые слова не найдены - игнорируется")
                return
            
            # Шаг 5: Сообщение соответствует критериям!
            self.matching_messages += 1
            print("✅ СОВПАДЕНИЕ: Сообщение соответствует всем критериям!")
            
            # Шаг 6: Имитация генерации ответа
            print("5️⃣ Генерация ответа через Claude AI...")
            test_response = f"Привет! Я нашел ключевые слова: {', '.join(found_keywords)}"
            print(f"6️⃣ Сгенерированный ответ: {test_response}")
            
            # Шаг 7: Имитация отправки (без реальной отправки)
            print("7️⃣ [ТЕСТ] Ответ НЕ отправлен (тестовый режим)")
            self.responses_sent += 1
            
            print(f"📊 Статистика: {self.matching_messages}/{self.total_messages} совпадений")
            print("─" * 50)
            
        except Exception as e:
            print(f"❌ Ошибка в отладчике: {e}")
            import traceback
            traceback.print_exc()
    
    async def get_chat_info(self, peer_id):
        """Получить информацию о чате"""
        try:
            entity = await self.client.get_entity(peer_id)
            
            if hasattr(entity, 'title'):
                return {
                    'type': '📺 Канал' if hasattr(entity, 'broadcast') else '👥 Группа',
                    'title': entity.title,
                    'id': entity.id,
                    'username': getattr(entity, 'username', None)
                }
            elif hasattr(entity, 'first_name'):
                return {
                    'type': '👤 Личный чат',
                    'title': entity.first_name,
                    'id': entity.id,
                    'username': getattr(entity, 'username', None)
                }
        except:
            pass
        
        return {
            'type': '❓ Неизвестно',
            'title': 'Неизвестно',
            'id': str(peer_id),
            'username': None
        }
    
    def is_chat_monitored(self, chat_info):
        """Проверка, отслеживается ли чат (имитация кампании)"""
        # Имитируем кампанию для канала eslitotoeto
        monitored_chats = ["@eslitotoeto", "1676879122"]
        
        return (
            str(chat_info['id']) in monitored_chats or
            (chat_info['username'] and f"@{chat_info['username']}" in monitored_chats) or
            "eslitotoeto" in chat_info['title'].lower()
        )
    
    def find_keywords(self, text):
        """Поиск ключевых слов в тексте"""
        if not text:
            return []
        
        text_lower = text.lower()
        return [kw for kw in self.test_keywords if kw.lower() in text_lower]
    
    async def show_status(self):
        """Показать статистику"""
        print("📊 СТАТИСТИКА ТЕСТИРОВАНИЯ:")
        print("─" * 30)
        print(f"📨 Всего сообщений: {self.total_messages}")
        print(f"🎯 Совпадений: {self.matching_messages}")
        print(f"🤖 Ответов: {self.responses_sent}")
        if self.total_messages > 0:
            success_rate = (self.matching_messages / self.total_messages) * 100
            print(f"📈 Процент совпадений: {success_rate:.1f}%")
        print(f"🔧 Отладочный режим: {'✅ ВКЛЮЧЕН' if self.debug_mode else '❌ ВЫКЛЮЧЕН'}")
        print(f"🎯 Ключевые слова: {', '.join(self.test_keywords)}")
        print()
    
    async def send_test_message(self):
        """Отправить тестовое сообщение в канал"""
        try:
            print("📝 Отправка тестового сообщения в @eslitotoeto...")
            
            channel = await self.client.get_entity("@eslitotoeto")
            test_message = f"🧪 Тест: ии бот - {datetime.now().strftime('%H:%M:%S')}"
            
            await self.client.send_message(channel, test_message)
            print(f"✅ Тестовое сообщение отправлено: {test_message}")
            
        except Exception as e:
            print(f"❌ Ошибка отправки тестового сообщения: {e}")
    
    async def start_monitoring(self):
        """Начать мониторинг сообщений"""
        print("🔍 Начинаю мониторинг сообщений...")
        print("💡 Напишите что-нибудь в Telegram чтобы увидеть отладку")
        print("⏹️  Нажмите Ctrl+C для возврата в меню")
        print()
        
        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            print("\\n⏹️  Мониторинг остановлен")
            print()
    
    async def check_channel_access(self):
        """Проверить доступ к каналу @eslitotoeto"""
        try:
            print("🔍 Проверяю доступ к каналу @eslitotoeto...")
            
            channel = await self.client.get_entity("@eslitotoeto")
            print(f"✅ Канал найден: {channel.title}")
            print(f"   ID: {channel.id}")
            print(f"   Тип: {type(channel).__name__}")
            
            # Получаем последние сообщения
            print(f"\\n📝 Последние 3 сообщения:")
            messages = await self.client.get_messages(channel, limit=3)
            
            for i, msg in enumerate(messages, 1):
                text = msg.text[:50] + "..." if msg.text and len(msg.text) > 50 else msg.text or "[Медиа]"
                print(f"   {i}. [{msg.id}] {text}")
                
                # Проверяем ключевые слова
                if msg.text:
                    keywords = self.find_keywords(msg.text)
                    if keywords:
                        print(f"      🔥 Ключевые слова: {', '.join(keywords)}")
            
        except Exception as e:
            print(f"❌ Ошибка доступа к каналу: {e}")
        
        print()
    
    async def change_keywords(self):
        """Изменить тестовые ключевые слова"""
        print(f"Текущие ключевые слова: {', '.join(self.test_keywords)}")
        new_keywords = input("Введите новые ключевые слова через запятую: ").strip()
        
        if new_keywords:
            self.test_keywords = [kw.strip() for kw in new_keywords.split(",") if kw.strip()]
            print(f"✅ Ключевые слова обновлены: {', '.join(self.test_keywords)}")
        else:
            print("❌ Ключевые слова не изменены")
        print()

async def main():
    """Главная функция"""
    tester = InteractiveAgentTester()
    await tester.start_interactive_testing()

if __name__ == "__main__":
    print("🎮 Интерактивный тестер Telegram агента")
    print("Этот инструмент поможет протестировать и отладить работу агента")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()