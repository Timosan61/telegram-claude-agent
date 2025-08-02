#!/usr/bin/env python3
"""
🔐 Создание Telegram сессии для DigitalOcean App Platform
Этот скрипт создает авторизованную сессию локально и конвертирует её в base64 для переменных окружения
"""
import asyncio
import os
import base64
import json
from dotenv import load_dotenv

load_dotenv()

try:
    from telethon import TelegramClient
    from telethon.errors import PhoneCodeInvalidError, PhoneNumberInvalidError, SessionPasswordNeededError
    from telethon.sessions import StringSession
except ImportError:
    print("❌ ОШИБКА: telethon не установлен")
    print("Выполните: pip install telethon cryptg python-dotenv")
    exit(1)

class AppPlatformSessionCreator:
    def __init__(self):
        # Получение данных из .env
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        
        # Проверка конфигурации
        if not all([self.api_id, self.api_hash, self.phone]):
            print("❌ ОШИБКА: Не все переменные настроены в .env")
            print("Требуются: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
            exit(1)
        
        self.api_id = int(self.api_id)
        print(f"📋 Конфигурация:")
        print(f"   📱 Телефон: {self.phone}")
        print(f"   🔑 API ID: {self.api_id}")
        print()
    
    async def create_session(self):
        """Создание новой авторизованной сессии"""
        print("🔐 СОЗДАНИЕ TELEGRAM СЕССИИ ДЛЯ APP PLATFORM")
        print("=" * 60)
        
        # Создание клиента с StringSession (для переносимости)
        string_session = StringSession()
        client = TelegramClient(string_session, self.api_id, self.api_hash)
        
        try:
            print("🔗 Подключение к Telegram...")
            await client.connect()
            
            # Проверяем текущий статус
            if await client.is_user_authorized():
                print("✅ Уже авторизован! Получаем данные...")
                await self.export_session_data(client)
                return True
            
            print("📞 Отправка кода авторизации...")
            print(f"📱 Код будет отправлен на: {self.phone}")
            
            # Отправка кода
            await client.send_code_request(self.phone)
            print("✅ Код отправлен!")
            
            # Получение кода от пользователя
            while True:
                try:
                    code = input("\n🔢 Введите 5-значный код из Telegram: ").strip()
                    
                    if not code or len(code) != 5 or not code.isdigit():
                        print("❌ Неверный формат. Введите ровно 5 цифр.")
                        continue
                    
                    print("🔐 Авторизация...")
                    await client.sign_in(self.phone, code)
                    break
                    
                except PhoneCodeInvalidError:
                    print("❌ Неверный код. Попробуйте еще раз.")
                    continue
                    
                except SessionPasswordNeededError:
                    # Требуется пароль двухфакторной авторизации
                    print("🔑 Требуется пароль двухфакторной авторизации")
                    while True:
                        password = input("Введите пароль: ").strip()
                        if password:
                            try:
                                await client.sign_in(password=password)
                                break
                            except Exception as e:
                                print(f"❌ Неверный пароль: {e}")
                                continue
                        else:
                            print("❌ Пароль не может быть пустым")
            
            print("✅ АВТОРИЗАЦИЯ УСПЕШНА!")
            
            # Экспорт данных сессии
            await self.export_session_data(client)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка во время авторизации: {e}")
            return False
            
        finally:
            await client.disconnect()
    
    async def export_session_data(self, client):
        """Экспорт данных сессии для App Platform"""
        try:
            # Получение информации о пользователе
            me = await client.get_me()
            print(f"👤 Пользователь: {me.first_name} {me.last_name or ''}")
            print(f"📱 Телефон: {me.phone}")
            print(f"🆔 ID: {me.id}")
            if me.username:
                print(f"📧 Username: @{me.username}")
            print()
            
            # Получение строки сессии
            session_string = client.session.save()
            print("🔑 ДАННЫЕ ДЛЯ APP PLATFORM:")
            print("=" * 50)
            
            # Конвертация в base64 для переменных окружения
            session_b64 = base64.b64encode(session_string.encode()).decode()
            
            print("📋 ПЕРЕМЕННАЯ ОКРУЖЕНИЯ:")
            print(f"TELEGRAM_SESSION_STRING={session_string}")
            print()
            print("📋 ПЕРЕМЕННАЯ ОКРУЖЕНИЯ (BASE64):")
            print(f"TELEGRAM_SESSION_B64={session_b64}")
            print()
            
            # Создание файла с данными
            session_data = {
                "session_string": session_string,
                "session_base64": session_b64,
                "user_info": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone": me.phone
                },
                "api_credentials": {
                    "api_id": self.api_id,
                    "api_hash": self.api_hash,
                    "phone": self.phone
                },
                "instructions": {
                    "app_platform": "Добавьте TELEGRAM_SESSION_STRING в переменные окружения DigitalOcean App",
                    "format": "Environment Variables → TELEGRAM_SESSION_STRING = {session_string}"
                }
            }
            
            # Сохранение в файл
            with open("telegram_session_for_app_platform.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print("💾 Данные сохранены в: telegram_session_for_app_platform.json")
            print()
            
            # Проверка доступа к каналу
            print("📺 Проверка доступа к целевому каналу...")
            try:
                channel = await client.get_entity("@eslitotoeto")
                print(f"✅ Канал найден: {channel.title}")
                print(f"   ID: {channel.id}")
                print(f"   Участников: {channel.participants_count}")
            except Exception as e:
                print(f"⚠️  Не удалось получить доступ к каналу @eslitotoeto: {e}")
            
            print()
            print("🚀 СЛЕДУЮЩИЕ ШАГИ:")
            print("1. Скопируйте TELEGRAM_SESSION_STRING")
            print("2. Добавьте в DigitalOcean App Settings → Environment Variables")
            print("3. Измените код для использования StringSession")
            print("4. Сделайте push в GitHub для автодеплоя")
            
        except Exception as e:
            print(f"❌ Ошибка экспорта данных: {e}")

async def main():
    creator = AppPlatformSessionCreator()
    success = await creator.create_session()
    
    if success:
        print("\n🎉 СЕССИЯ СОЗДАНА УСПЕШНО!")
        print("📋 Файл telegram_session_for_app_platform.json готов для использования")
    else:
        print("\n❌ ОШИБКА СОЗДАНИЯ СЕССИИ")
        print("💡 Проверьте настройки и попробуйте снова")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Создание сессии прервано")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()