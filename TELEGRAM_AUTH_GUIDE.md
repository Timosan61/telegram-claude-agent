# 📱 Руководство по авторизации Telegram агента

## ⚠️ Текущее состояние

**Статус**: ❌ Telegram агент НЕ авторизован  
**Проблема**: Все сессионные файлы потеряли авторизацию  
**Решение**: Требуется интерактивная авторизация

## 🔧 Как авторизовать агента

### Шаг 1: Локальная авторизация

```bash
# На локальной машине или в интерактивной среде
cd telegram_claude_agent
python3 -m venv venv
source venv/bin/activate
pip install telethon cryptg python-dotenv

# Запустить интерактивную авторизацию
python telegram_auth_setup.py
```

### Шаг 2: Процесс авторизации

1. **Введите номер телефона**: +79885517453
2. **Получите код из Telegram**: Telegram отправит 5-значный код
3. **Введите код**: Введите полученный код
4. **Возможно потребуется пароль**: Если включена двухфакторная авторизация

### Шаг 3: Проверка авторизации

После успешной авторизации создастся файл `telegram_agent.session` с действительной авторизацией.

## 🚀 Создание скрипта авторизации

Создам интерактивный скрипт для авторизации:

```python
#!/usr/bin/env python3
"""
Интерактивная авторизация Telegram агента
Запускайте в локальной интерактивной среде
"""
import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def authorize():
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH") 
    phone = os.getenv("TELEGRAM_PHONE")
    
    print("🔐 Авторизация Telegram агента")
    print(f"📱 Телефон: {phone}")
    
    client = TelegramClient("telegram_agent", api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        
        me = await client.get_me()
        print(f"✅ Успешно авторизован: {me.first_name}")
        
        # Проверяем доступ к чатам
        count = 0
        async for dialog in client.iter_dialogs(limit=5):
            count += 1
            print(f"  {count}. {dialog.name}")
        
        print(f"📊 Доступно {count} диалогов")
        print("✅ Авторизация завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(authorize())
```

## 🔄 После авторизации

1. **Скопируйте файл сессии** `telegram_agent.session` в рабочую директорию
2. **Перезапустите backend** для подключения к Telegram
3. **Проверьте статус** через API: `/health`

## 🎯 Ожидаемый результат

После успешной авторизации:

```json
{
  "status": "healthy",
  "telegram_connected": true,  // ← Изменится на true
  "database": "connected",
  "mode": "full"
}
```

## 📝 Важные замечания

- **Безопасность**: Не делитесь файлами .session - они содержат авторизационные данные
- **Срок действия**: Сессии Telegram имеют длительный срок, но могут истекать
- **Двухфакторная авторизация**: Если включена, потребуется пароль cloud password
- **Интерактивность**: Авторизация возможна только в интерактивной среде

## 🆘 Устранение проблем

**Код не приходит:**
- Проверьте правильность номера телефона
- Убедитесь что Telegram установлен на устройстве
- Попробуйте через несколько минут

**Ошибка авторизации:**
- Проверьте API_ID и API_HASH в .env
- Убедитесь в стабильности интернет-соединения
- Попробуйте удалить старые .session файлы

**Сессия не работает:**
- Возможно сессия устарела
- Повторите процесс авторизации
- Проверьте права доступа к файлу .session