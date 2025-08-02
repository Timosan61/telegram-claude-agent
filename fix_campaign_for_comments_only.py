#!/usr/bin/env python3
"""
Исправление кампании для работы только с комментариями
"""
import requests
import json

def update_campaign():
    """Обновить кампанию для работы только с комментариями"""
    
    # ИСПРАВЛЕННАЯ конфигурация - ТОЛЬКО группа обсуждений
    campaign_data = {
        "name": "Comments Only Campaign @eslitotoeto",
        "active": True,
        "telegram_chats": ["2532661483"],  # ТОЛЬКО группа обсуждений, НЕ канал
        "keywords": ["задача", "вопрос", "помощь", "тест", "claude"],
        "telegram_account": "+79885517453",
        "ai_provider": "openai",
        "claude_agent_id": "telegram_claude_agent",
        "openai_model": "gpt-4o",
        "context_messages_count": 3,
        "system_instruction": "Ты - полезный ассистент с именем Claude Bot. Отвечай кратко и по существу на русском языке. Помогай пользователям с их вопросами. Используй эмодзи для дружелюбности.",
        "example_replies": {
            "greeting": "Привет! Как дела? 👋",
            "help": "Конечно, помогу! Что именно вас интересует? 🤔",
            "thanks": "Пожалуйста! Рад был помочь! 😊"
        }
    }
    
    print("🔄 Удаление старой кампании...")
    
    # Получить ID существующей кампании
    try:
        response = requests.get("https://answerbot-magph.ondigitalocean.app/campaigns", timeout=10)
        if response.status_code == 200:
            campaigns = response.json()
            for campaign in campaigns:
                campaign_id = campaign.get('id')
                print(f"🗑️ Удаление кампании ID: {campaign_id}")
                
                # Удалить кампанию
                delete_response = requests.delete(
                    f"https://answerbot-magph.ondigitalocean.app/campaigns/{campaign_id}",
                    timeout=10
                )
                if delete_response.status_code in [200, 204]:
                    print(f"✅ Кампания {campaign_id} удалена")
                else:
                    print(f"⚠️ Не удалось удалить кампанию {campaign_id}: {delete_response.status_code}")
    except Exception as e:
        print(f"⚠️ Ошибка при удалении: {e}")
    
    print("\n🎯 Создание новой кампании (только комментарии)...")
    
    try:
        # Создать новую кампанию
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/campaigns",
            json=campaign_data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Новая кампания создана: ID {result.get('id', 'Unknown')}")
            print(f"📋 Настройки:")
            print(f"   Название: {result.get('name', 'Unknown')}")
            print(f"   Чаты: {result.get('telegram_chats', [])}")
            print(f"   Ключевые слова: {result.get('keywords', [])}")
            return True
        else:
            print(f"❌ Ошибка создания кампании: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def restart_agent():
    """Перезапустить агента"""
    try:
        print(f"\n🔄 Перезапуск агента...")
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/telegram/restart",
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Агент перезапущен: {result['message']}")
            return True
        else:
            print(f"❌ Ошибка перезапуска: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_final_status():
    """Проверить финальный статус"""
    try:
        print(f"\n📊 Проверка финального статуса...")
        
        # Статус агента
        response = requests.get("https://answerbot-magph.ondigitalocean.app/telegram/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"🔍 Статус агента:")
            print(f"   Активных кампаний: {status['details']['active_campaigns']}")
        
        # Кампании
        response = requests.get("https://answerbot-magph.ondigitalocean.app/campaigns", timeout=10)
        if response.status_code == 200:
            campaigns = response.json()
            print(f"📋 Кампании ({len(campaigns)}):")
            for campaign in campaigns:
                print(f"   - {campaign['name']}: {campaign['telegram_chats']}")
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")

def main():
    """Основная функция"""
    print("🔧 Исправление кампании для работы ТОЛЬКО с комментариями...")
    print("⚠️ ВАЖНО: Теперь бот будет отвечать ТОЛЬКО на комментарии к постам, НЕ на сообщения в канале")
    
    if update_campaign():
        if restart_agent():
            import time
            time.sleep(3)
            check_final_status()
            
            print("\n🎯 ГОТОВО!")
            print("📝 Теперь попробуйте:")
            print("   1. Зайти в канал @eslitotoeto")
            print("   2. Найти любой пост с комментариями")
            print("   3. Написать комментарий с словом 'тест'")
            print("   4. Бот должен ответить на ваш комментарий")
    else:
        print("❌ Не удалось обновить кампанию")

if __name__ == "__main__":
    main()