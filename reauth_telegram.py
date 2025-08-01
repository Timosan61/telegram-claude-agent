#!/usr/bin/env python3
"""
🔐 БЫСТРАЯ ПЕРЕАВТОРИЗАЦИЯ Telegram агента

Этот скрипт восстанавливает авторизацию для существующей сессии.
Использует уже настроенные API данные из .env файла.

ЗАПУСК: python reauth_telegram.py
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

try:
    from telethon import TelegramClient
    from telethon.errors import PhoneCodeInvalidError, PhoneNumberInvalidError, SessionPasswordNeededError
except ImportError:
    print("❌ ОШИБКА: telethon не установлен")
    print("Выполните: pip install telethon cryptg python-dotenv")
    sys.exit(1)

class TelegramReauth:
    def __init__(self):
        # Получение данных из .env
        self.api_id = os.getenv("TELEGRAM_API_ID")
        self.api_hash = os.getenv("TELEGRAM_API_HASH")
        self.phone = os.getenv("TELEGRAM_PHONE")
        
        # Проверка конфигурации
        if not all([self.api_id, self.api_hash, self.phone]):
            print("❌ ОШИБКА: Не все переменные настроены в .env")
            print("Требуются: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
            sys.exit(1)
        
        self.api_id = int(self.api_id)
        print(f"📋 Конфигурация:")
        print(f"   📱 Телефон: {self.phone}")
        print(f"   🔑 API ID: {self.api_id}")
        print()
    
    async def reauthorize(self):
        """Основной процесс переавторизации"""
        print("🔐 ПЕРЕАВТОРИЗАЦИЯ TELEGRAM АГЕНТА")
        print("=" * 50)
        
        # Создание клиента (перезапишет существующую сессию)
        client = TelegramClient("telegram_agent", self.api_id, self.api_hash)
        
        try:
            print("🔗 Подключение к Telegram...")
            await client.connect()
            
            # Проверяем текущий статус
            if await client.is_user_authorized():
                print("✅ Уже авторизован! Проверяем доступ...")
                await self.verify_access(client)
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
                    break
                    
                except Exception as e:
                    print(f"❌ Ошибка авторизации: {e}")
                    return False
            
            print("🎉 АВТОРИЗАЦИЯ УСПЕШНА!")
            await self.verify_access(client)
            return True
            
        except PhoneNumberInvalidError:
            print(f"❌ Неверный номер телефона: {self.phone}")
            return False
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return False
            
        finally:
            await client.disconnect()
    
    async def verify_access(self, client):
        """Проверка доступа после авторизации"""
        try:
            # Информация о пользователе
            me = await client.get_me()
            print(f"\n✅ Авторизован как: {me.first_name} {me.last_name or ''}")
            print(f"📱 Телефон: {me.phone}")
            print(f"🆔 ID: {me.id}")
            
            # Проверка доступа к диалогам
            print(f"\n📋 Проверка доступа к чатам...")
            
            dialogs = []
            target_found = False
            
            async for dialog in client.iter_dialogs(limit=15):
                dialog_info = {
                    'name': dialog.name,
                    'id': dialog.id,
                    'type': 'канал' if dialog.is_channel else ('группа' if dialog.is_group else 'личный')
                }
                dialogs.append(dialog_info)
                
                # Проверяем целевой канал
                if 'eslitotoeto' in dialog.name.lower():
                    target_found = True
                    print(f"🎯 ЦЕЛЕВОЙ КАНАЛ НАЙДЕН: {dialog.name} (ID: {dialog.id})")
            
            print(f"\n📊 Доступно диалогов: {len(dialogs)}")
            
            # Показываем первые 5 диалогов
            for i, dialog in enumerate(dialogs[:5], 1):
                print(f"  {i}. {dialog['type']}: {dialog['name']}")
            
            if len(dialogs) > 5:
                print(f"  ... и еще {len(dialogs) - 5} диалогов")
            
            if target_found:
                print(f"\n🎉 ЦЕЛЕВОЙ КАНАЛ @eslitotoeto ДОСТУПЕН!")
            else:
                print(f"\n⚠️  Целевой канал @eslitotoeto не найден в первых 15 диалогах")
                print(f"   Возможно нужно присоединиться к каналу")
            
        except Exception as e:
            print(f"❌ Ошибка проверки доступа: {e}")

async def main():
    """Главная функция"""
    reauth = TelegramReauth()
    success = await reauth.reauthorize()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ПЕРЕАВТОРИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print(f"📁 Обновлен файл: telegram_agent.session")
        print(f"🔧 Теперь backend сможет подключиться к Telegram")
        print(f"📊 Проверьте API: curl https://answerbot-magph.ondigitalocean.app/health")
    else:
        print("❌ ПЕРЕАВТОРИЗАЦИЯ НЕ УДАЛАСЬ")
        print("💡 Проверьте данные в .env и попробуйте еще раз")

if __name__ == "__main__":
    print("🤖 Telegram Claude Agent - Переавторизация")
    print("Восстановление доступа к Telegram для агента\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Переавторизация прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()