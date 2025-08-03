#!/usr/bin/env python3
"""
Скрипт для исправления проблемы с дублирующимися сообщениями бота
"""
import requests
import json
import asyncio

async def fix_campaign_issue():
    """Исправляем проблему с кампанией"""
    
    print("🔍 Анализ проблемы с дублирующимися сообщениями...")
    
    # 1. Получаем текущие кампании
    print("\n1. Получение текущих кампаний...")
    try:
        response = requests.get("https://answerbot-magph.ondigitalocean.app/campaigns/", timeout=10)
        if response.status_code == 200:
            campaigns = response.json()
            print(f"📋 Найдено кампаний: {len(campaigns)}")
            
            for campaign in campaigns:
                print(f"   ID: {campaign['id']}, Name: {campaign['name']}")
                print(f"   Keywords: {campaign['keywords']}")
                print(f"   Instruction: {campaign['system_instruction'][:50]}...")
                print(f"   AI Provider: {campaign['ai_provider']}")
        else:
            print(f"❌ Ошибка получения кампаний: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    # 2. Исправляем кампанию ТИМ
    print("\n2. Исправление кампании ТИМ...")
    if campaigns:
        team_campaign = campaigns[0]  # Кампания ТИМ
        campaign_id = team_campaign['id']
        
        # Правильная конфигурация
        updated_campaign = {
            "name": "Team Support Bot",
            "active": True,
            "telegram_chats": ["@eslitotoeto"],
            "keywords": ["тест", "ии", "чат бот", "помощь", "вопрос"],
            "telegram_account": "@myassyst",
            "ai_provider": "openai",
            "openai_model": "gpt-4",
            "context_messages_count": 3,
            "system_instruction": "Ты - ассистент команды с именем Сметанка. Отвечай кратко, по-дружески на русском языке. На слово 'тест' всегда отвечай одним словом: 'КРУТО'. На другие вопросы помогай полезными советами. Используй эмодзи.",
            "example_replies": {
                "тест": "КРУТО",
                "помощь": "Чем могу помочь? 🤔",
                "спасибо": "Пожалуйста! 😊"
            }
        }
        
        try:
            response = requests.put(
                f"https://answerbot-magph.ondigitalocean.app/campaigns/{campaign_id}",
                json=updated_campaign,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Кампания успешно обновлена")
            else:
                print(f"❌ Ошибка обновления: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Ошибка обновления: {e}")
            return False
    
    # 3. Очистка кэша и перезапуск агента
    print("\n3. Перезапуск агента для очистки кэша...")
    try:
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/telegram/restart",
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Агент перезапущен")
            
            # Ждем перезапуска
            print("⏳ Ожидание перезапуска (10 секунд)...")
            await asyncio.sleep(10)
            
        else:
            print(f"❌ Ошибка перезапуска: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка перезапуска: {e}")
        return False
    
    # 4. Проверка статуса после исправления
    print("\n4. Проверка статуса после исправления...")
    try:
        response = requests.get("https://answerbot-magph.ondigitalocean.app/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Статус: {health['status']}")
            print(f"📡 Telegram: {health['telegram_connected']}")
            print(f"🧠 AI клиенты: {health['ai_providers']}")
            print(f"📋 Активных кампаний: {health['telegram_status']['active_campaigns']}")
            
            if health['telegram_status']['active_campaigns'] == 1:
                print("✅ Количество кампаний исправлено!")
            else:
                print(f"⚠️ Все еще {health['telegram_status']['active_campaigns']} кампаний")
                
        else:
            print(f"❌ Ошибка проверки здоровья: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
    
    print("\n🎯 Рекомендации для тестирования:")
    print("1. Напишите 'тест' в канал @eslitotoeto")
    print("2. Бот должен ответить только одним сообщением: 'КРУТО'")
    print("3. Если бот все еще дублирует ответы, нужен полный рестарт backend")
    
    return True

async def main():
    """Главная функция"""
    print("🚀 Исправление проблемы с дублирующимися сообщениями бота")
    print("=" * 60)
    
    success = await fix_campaign_issue()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Исправление завершено!")
        print("\n📝 Что было исправлено:")
        print("- Очищена конфигурация кампании")
        print("- Исправлена системная инструкция")
        print("- Добавлены правильные примеры ответов")
        print("- Перезапущен агент для очистки кэша")
        print("\n🧪 Теперь протестируйте бота командой 'тест'")
    else:
        print("❌ Возникли ошибки при исправлении")
        print("🔧 Может потребоваться ручное вмешательство")

if __name__ == "__main__":
    asyncio.run(main())