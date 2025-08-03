#!/usr/bin/env python3
"""
🔐 Создание Telegram сессии для DigitalOcean App Platform с альтернативным номером
Этот скрипт создает авторизованную сессию с другим номером телефона
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

class AlternativeSessionCreator:
    def __init__(self, phone_number=None):
        # Получение данных из .env
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        
        # Использовать переданный номер или запросить ввод
        if phone_number:
            self.phone = phone_number
        else:
            print("📱 Введите альтернативный номер телефона (с кодом страны, например +79123456789):")
            self.phone = input("Номер: ").strip()
        
        # Проверка конфигурации
        if not all([self.api_id, self.api_hash, self.phone]):
            print("❌ ОШИБКА: Не все данные предоставлены")
            print("Требуются: TELEGRAM_API_ID, TELEGRAM_API_HASH, номер телефона")
            exit(1)
        
        self.api_id = int(self.api_id)
        print(f"📋 Конфигурация:")
        print(f"   📱 Телефон: {self.phone}")
        print(f"   🔑 API ID: {self.api_id}")
        print()
    
    async def create_session(self):
        """Создание новой авторизованной сессии с альтернативным номером"""
        print("🔐 СОЗДАНИЕ TELEGRAM СЕССИИ С АЛЬТЕРНАТИВНЫМ НОМЕРОМ")
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
                "creation_method": "alternative_phone",
                "instructions": {
                    "app_platform": "Добавьте TELEGRAM_SESSION_STRING в переменные окружения DigitalOcean App",
                    "format": "Environment Variables → TELEGRAM_SESSION_STRING = {session_string}"
                }
            }
            
            # Сохранение в файл с уникальным именем
            filename = f"telegram_session_alternative_{me.phone}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Данные сохранены в: {filename}")
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
                print("💡 Возможно нужно сначала присоединиться к каналу вручную")
            
            print()
            print("🚀 СЛЕДУЮЩИЕ ШАГИ:")
            print("1. Скопируйте TELEGRAM_SESSION_STRING")
            print("2. Замените в переменных окружения DigitalOcean App Platform")
            print("3. Обновите TELEGRAM_PHONE в .env на новый номер")
            print("4. Сделайте push в GitHub для автодеплоя")
            
        except Exception as e:
            print(f"❌ Ошибка экспорта данных: {e}")

async def main():
    import sys
    
    # Проверяем аргументы командной строки
    phone = None
    if len(sys.argv) > 1:
        phone = sys.argv[1]
        print(f"📱 Используем номер из аргумента: {phone}")
    
    creator = AlternativeSessionCreator(phone)
    success = await creator.create_session()
    
    if success:
        print("\n🎉 СЕССИЯ С АЛЬТЕРНАТИВНЫМ НОМЕРОМ СОЗДАНА УСПЕШНО!")
        print("📋 Файл готов для использования")
    else:
        print("\n❌ ОШИБКА СОЗДАНИЯ СЕССИИ")
        print("💡 Проверьте номер телефона и попробуйте снова")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Создание сессии прервано")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()