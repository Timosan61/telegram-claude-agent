#!/usr/bin/env python3
"""
🔐 Интерактивная авторизация Telegram агента

Этот скрипт нужно запускать в локальной интерактивной среде
для получения авторизационного кода и создания сессии.

ВАЖНО: Запускайте только на локальной машине с доступом к Telegram!
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

try:
    from telethon import TelegramClient
    from telethon.errors import PhoneCodeInvalidError, PhoneNumberInvalidError
except ImportError:
    print("❌ Ошибка: telethon не установлен")
    print("Установите зависимости:")
    print("pip install telethon cryptg python-dotenv")
    sys.exit(1)

class TelegramAuthenticator:
    def __init__(self):
        # Получение данных из .env
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        
        # Проверка конфигурации
        if not all([self.api_id, self.api_hash, self.phone]):
            print("❌ Ошибка конфигурации!")
            print("Проверьте файл .env и убедитесь что заполнены:")
            print("- TELEGRAM_API_ID")
            print("- TELEGRAM_API_HASH") 
            print("- TELEGRAM_PHONE")
            sys.exit(1)
        
        self.api_id = int(self.api_id)
        print(f"📋 Конфигурация загружена:")
        print(f"   📱 Телефон: {self.phone}")
        print(f"   🔑 API ID: {self.api_id}")
        print()
    
    async def authenticate(self):
        """Основной процесс авторизации"""
        print("🔐 Начинаем авторизацию Telegram агента")
        print("=" * 50)
        
        # Создание клиента
        client = TelegramClient("telegram_agent", self.api_id, self.api_hash)
        
        try:
            print("🔗 Подключение к Telegram...")
            await client.connect()
            
            # Проверка существующей авторизации
            if await client.is_user_authorized():
                print("✅ Пользователь уже авторизован!")
                await self.show_user_info(client)
                return True
            
            print("📞 Отправка кода авторизации...")
            print(f"📱 Код будет отправлен на номер: {self.phone}")
            
            # Отправка кода
            await client.send_code_request(self.phone)
            
            # Получение кода от пользователя
            while True:
                try:
                    code = input("🔢 Введите код из Telegram (5 цифр): ").strip()
                    
                    if not code or len(code) != 5 or not code.isdigit():
                        print("❌ Неверный формат кода. Введите 5 цифр.")
                        continue
                    
                    print("🔐 Авторизация с кодом...")
                    await client.sign_in(self.phone, code)
                    break
                    
                except PhoneCodeInvalidError:
                    print("❌ Неверный код. Попробуйте еще раз.")
                    continue
                except Exception as e:
                    if "password" in str(e).lower():
                        # Требуется пароль двухфакторной авторизации
                        password = input("🔑 Введите пароль двухфакторной авторизации: ")
                        await client.sign_in(password=password)
                        break
                    else:
                        print(f"❌ Ошибка авторизации: {e}")
                        return False
            
            print("✅ Авторизация успешна!")
            await self.show_user_info(client)
            
            # Проверка доступа к чатам
            await self.test_chat_access(client)
            
            return True
            
        except PhoneNumberInvalidError:
            print(f"❌ Неверный номер телефона: {self.phone}")
            print("Проверьте формат номера в файле .env")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка авторизации: {e}")
            return False
            
        finally:
            await client.disconnect()
    
    async def show_user_info(self, client):
        """Показать информацию о пользователе"""
        try:
            me = await client.get_me()
            print(f"👤 Авторизован как: {me.first_name} {me.last_name or ''}")
            print(f"📱 Телефон: {me.phone}")
            print(f"🆔 ID: {me.id}")
            if me.username:
                print(f"📧 Username: @{me.username}")
            print()
        except Exception as e:
            print(f"⚠️ Не удалось получить информацию о пользователе: {e}")
    
    async def test_chat_access(self, client):
        """Тестирование доступа к чатам"""
        print("📋 Проверка доступа к чатам...")
        
        try:
            count = 0
            async for dialog in client.iter_dialogs(limit=10):
                count += 1
                
                # Определение типа чата
                if dialog.is_channel:
                    if dialog.entity.megagroup:
                        chat_type = "👥 Супергруппа"
                    else:
                        chat_type = "📺 Канал"
                elif dialog.is_group:
                    chat_type = "👥 Группа"
                else:
                    chat_type = "👤 Личный"
                
                print(f"  {count:2d}. {chat_type}: {dialog.name}")
                print(f"      ID: {dialog.id}, Непрочитано: {dialog.unread_count}")
            
            print(f"\\n📊 Доступно {count} диалогов")
            
            if count > 0:
                print("✅ Доступ к чатам работает!")
                print("🎯 Агент сможет видеть сообщения в этих чатах")
            else:
                print("⚠️ Чаты не найдены или нет доступа")
                
        except Exception as e:
            print(f"❌ Ошибка проверки чатов: {e}")

async def main():
    """Главная функция"""
    print("🤖 Telegram Claude Agent - Авторизация")
    print("Этот скрипт авторизует агента для мониторинга Telegram чатов")
    print()
    
    authenticator = TelegramAuthenticator()
    success = await authenticator.authenticate()
    
    print("=" * 50)
    if success:
        print("🎉 АВТОРИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print()
        print("📁 Создан файл: telegram_agent.session")
        print("🔧 Теперь можно запускать backend с Telegram интеграцией")
        print("📊 Проверьте статус через: curl localhost:8000/health")
        print()
        print("⚠️ ВАЖНО:")
        print("- Не делитесь файлом .session - он содержит авторизационные данные")
        print("- Добавьте *.session в .gitignore")
        print("- В продакшене храните сессии в безопасном месте")
    else:
        print("❌ АВТОРИЗАЦИЯ НЕ УДАЛАСЬ")
        print("💡 Проверьте конфигурацию и попробуйте еще раз")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n🛑 Авторизация прервана пользователем")
    except Exception as e:
        print(f"\\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()