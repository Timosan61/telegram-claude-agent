#!/usr/bin/env python3
"""
Скрипт для генерации TELEGRAM_SESSION_STRING для production развертывания
Использует локальные переменные окружения для создания строки сессии
"""

import asyncio
import os
import base64
from dotenv import load_dotenv

try:
    from telethon import TelegramClient
except ImportError:
    print("❌ Ошибка: telethon не установлен")
    print("Установите: pip install telethon")
    exit(1)

# Загрузка переменных окружения
load_dotenv()

# Получение переменных
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH') 
PHONE = os.getenv('TELEGRAM_PHONE')

# Валидация переменных
if not API_ID:
    print("❌ Ошибка: TELEGRAM_API_ID не найден в .env файле")
    exit(1)

if not API_HASH:
    print("❌ Ошибка: TELEGRAM_API_HASH не найден в .env файле")
    exit(1)

if not PHONE:
    print("❌ Ошибка: TELEGRAM_PHONE не найден в .env файле")
    exit(1)

try:
    API_ID = int(API_ID)
except ValueError:
    print("❌ Ошибка: TELEGRAM_API_ID должен быть числом")
    exit(1)

async def generate_session():
    """Генерация строки сессии Telegram"""
    
    print("🚀 Запуск генерации сессии Telegram...")
    print(f"📱 Телефон: {PHONE}")
    print(f"🔑 API ID: {API_ID}")
    
    # Создание клиента
    client = TelegramClient('temp_session', API_ID, API_HASH)
    
    try:
        print("\n📞 Подключение к Telegram...")
        
        # Начало авторизации
        await client.start(phone=PHONE)
        
        print("✅ Успешная авторизация!")
        
        # Получение строки сессии
        session_string = client.session.save()
        
        # Кодирование в base64 для удобства
        session_b64 = base64.b64encode(session_string).decode()
        
        # Вывод результатов
        print("\n🎉 Сессия успешно сгенерирована!")
        print("="*60)
        print("📋 Скопируйте эти переменные в ваш деплой:")
        print("="*60)
        print()
        print(f"TELEGRAM_SESSION_STRING={session_string}")
        print()
        print(f"TELEGRAM_SESSION_B64={session_b64}")
        print()
        print("="*60)
        print("💡 Используйте TELEGRAM_SESSION_STRING для Heroku/Railway")
        print("💡 Используйте TELEGRAM_SESSION_B64 для DigitalOcean если возникают проблемы")
        print("="*60)
        
        # Сохранение в файл
        with open('.session_backup.txt', 'w') as f:
            f.write(f"TELEGRAM_SESSION_STRING={session_string}\n")
            f.write(f"TELEGRAM_SESSION_B64={session_b64}\n")
        
        print("💾 Результат также сохранен в .session_backup.txt")
        
        # Проверка информации об аккаунте
        me = await client.get_me()
        print(f"👤 Аккаунт: {me.first_name} {me.last_name or ''}")
        print(f"📱 Username: @{me.username or 'Не установлен'}")
        print(f"🆔 ID: {me.id}")
        
    except Exception as e:
        print(f"❌ Ошибка при генерации сессии: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Проверьте правильность API_ID и API_HASH")
        print("2. Убедитесь, что номер телефона корректный")
        print("3. Проверьте интернет соединение")
        print("4. Убедитесь, что приложение создано на https://my.telegram.org/apps")
        
    finally:
        # Отключение от Telegram
        await client.disconnect()
        
        # Удаление временного файла сессии
        try:
            os.remove('temp_session.session')
        except:
            pass
        
        print("\n🔒 Соединение закрыто")

def main():
    """Главная функция"""
    print("🤖 Telegram Claude Agent - Генератор Сессии")
    print("="*50)
    print()
    
    # Проверка .env файла
    if os.path.exists('.env'):
        print("✅ .env файл найден")
    else:
        print("⚠️  .env файл не найден, использую переменные окружения")
    
    # Запуск генерации
    try:
        asyncio.run(generate_session())
    except KeyboardInterrupt:
        print("\n❌ Операция отменена пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    main()