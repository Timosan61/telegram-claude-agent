#!/usr/bin/env python3
"""
🔐 Авторизация Telegram агента
Интерактивный скрипт для авторизации в Telegram
ЗАПУСКАЙТЕ ТОЛЬКО В РЕАЛЬНОМ ТЕРМИНАЛЕ (не в Claude Code)
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Добавляем текущую директорию в PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from telethon import TelegramClient

async def authorize_telegram():
    """Авторизация в Telegram"""
    print("🔐 Авторизация Telegram Claude Agent")
    print("=" * 50)
    
    # Получаем данные из .env
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    
    print(f"📱 Номер телефона: {phone}")
    print(f"🔑 API ID: {api_id}")
    print()
    
    # Создаем клиент
    client = TelegramClient("telegram_agent", api_id, api_hash)
    
    try:
        await client.connect()
        print("✅ Подключение к Telegram API успешно")
        
        # Проверяем, авторизованы ли мы уже
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ Уже авторизован как: {me.first_name}")
            print(f"📞 Телефон: {me.phone}")
            print(f"🆔 ID: {me.id}")
            
            # Тестируем доступ к каналу
            await test_channel_access(client)
            return True
        
        # Запрашиваем код авторизации
        print(f"📱 Отправляю код авторизации на {phone}...")
        sent_code = await client.send_code_request(phone)
        print("✅ Код отправлен!")
        print()
        
        # Запрашиваем код у пользователя
        print("💡 Проверьте SMS или уведомления в Telegram")
        code = input("🔢 Введите код авторизации: ").strip()
        
        if not code:
            print("❌ Код не введен")
            return False
        
        try:
            # Авторизуемся
            await client.sign_in(phone, code)
            
        except Exception as sign_in_error:
            # Если нужен пароль двухфакторной аутентификации
            if "Two-step verification" in str(sign_in_error) or "password" in str(sign_in_error).lower():
                print("🔒 Требуется пароль двухфакторной аутентификации")
                password = input("🔒 Введите пароль 2FA: ").strip()
                
                if not password:
                    print("❌ Пароль не введен")
                    return False
                
                await client.sign_in(password=password)
            else:
                raise sign_in_error
        
        # Проверяем успешность авторизации
        me = await client.get_me()
        print(f"\n🎉 АВТОРИЗАЦИЯ УСПЕШНА!")
        print(f"👤 Авторизован как: {me.first_name}")
        print(f"📞 Телефон: {me.phone}")
        print(f"🆔 ID: {me.id}")
        print()
        
        # Тестируем доступ к каналу
        await test_channel_access(client)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return False
        
    finally:
        await client.disconnect()

async def test_channel_access(client):
    """Тестирование доступа к каналу @eslitotoeto"""
    print("📺 Тестирование доступа к каналу...")
    print("-" * 30)
    
    try:
        channel = await client.get_entity("@eslitotoeto")
        print(f"✅ Канал найден: {channel.title}")
        print(f"🆔 ID канала: {channel.id}")
        
        # Получаем последние сообщения
        messages = await client.get_messages(channel, limit=3)
        print(f"📝 Последних сообщений: {len(messages)}")
        
        # Проверяем на ключевые слова
        keywords = ["ии", "бот", "искусственный интеллект", "помощь"]
        for i, msg in enumerate(messages, 1):
            if msg.text:
                text_preview = msg.text[:50] + "..." if len(msg.text) > 50 else msg.text
                print(f"   {i}. {text_preview}")
                
                # Ищем ключевые слова
                found_keywords = [kw for kw in keywords if kw.lower() in msg.text.lower()]
                if found_keywords:
                    print(f"      🔥 Ключевые слова: {', '.join(found_keywords)}")
        
        print("\n🎯 РЕЗУЛЬТАТ:")
        print("✅ Агент может читать сообщения из канала @eslitotoeto")
        print("✅ Готов к мониторингу и ответам")
        
    except Exception as e:
        print(f"⚠️ Проблема с каналом @eslitotoeto: {e}")
        print("💡 Убедитесь что:")
        print("   - Подписаны на канал @eslitotoeto")
        print("   - Канал существует и доступен")

async def main():
    """Главная функция"""
    print("🔐 Telegram Authorization Script")
    print("ВАЖНО: Запускайте только в реальном терминале!")
    print()
    
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден")
        print("💡 Убедитесь что находитесь в папке проекта")
        return
    
    # Проверяем переменные окружения
    required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Отсутствуют переменные окружения:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Проверьте файл .env")
        return
    
    try:
        success = await authorize_telegram()
        
        if success:
            print("\n" + "=" * 50)
            print("🚀 ГОТОВО К ЗАПУСКУ!")
            print("Теперь можно запустить:")
            print("1. python run.py                    # Backend сервер")
            print("2. streamlit run streamlit_app.py   # Веб-интерфейс")
            print()
            print("🤖 Создайте кампанию и агент начнет работать!")
        else:
            print("\n❌ Авторизация не удалась")
            print("💡 Проверьте номер телефона и код")
            
    except KeyboardInterrupt:
        print("\n\n👋 Авторизация прервана")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())