#!/usr/bin/env python3
"""
Исправление дублирующих кампаний
"""
import requests
import time

def get_all_campaigns():
    """Получить все кампании"""
    try:
        response = requests.get("https://answerbot-magph.ondigitalocean.app/campaigns", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка получения кампаний: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def delete_campaign(campaign_id):
    """Удалить кампанию"""
    try:
        response = requests.delete(f"https://answerbot-magph.ondigitalocean.app/campaigns/{campaign_id}", timeout=10)
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"❌ Ошибка удаления кампании {campaign_id}: {e}")
        return False

def create_single_campaign():
    """Создать единственную правильную кампанию"""
    campaign_data = {
        "name": "Single Comments Campaign @eslitotoeto",
        "active": True,
        "telegram_chats": ["2532661483"],  # ТОЛЬКО группа обсуждений
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
    
    try:
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/campaigns",
            json=campaign_data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Единственная кампания создана: ID {result.get('id')}")
            return True
        else:
            print(f"❌ Ошибка создания кампании: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def restart_agent():
    """Перезапустить агента"""
    try:
        response = requests.post("https://answerbot-magph.ondigitalocean.app/telegram/restart", timeout=30)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Ошибка перезапуска: {e}")
        return False

def main():
    """Основная функция"""
    print("🔧 ИСПРАВЛЕНИЕ ДУБЛИРУЮЩИХ КАМПАНИЙ")
    print("=" * 50)
    
    # Получить все кампании
    campaigns = get_all_campaigns()
    print(f"📊 Найдено кампаний: {len(campaigns)}")
    
    for campaign in campaigns:
        print(f"   - {campaign.get('name', 'Unknown')} (ID: {campaign.get('id')})")
    
    # Удалить ВСЕ кампании
    print(f"\n🗑️ Удаление всех кампаний...")
    deleted_count = 0
    for campaign in campaigns:
        campaign_id = campaign.get('id')
        if delete_campaign(campaign_id):
            print(f"   ✅ Удалена кампания ID: {campaign_id}")
            deleted_count += 1
        else:
            print(f"   ❌ Не удалось удалить кампанию ID: {campaign_id}")
    
    print(f"📊 Удалено кампаний: {deleted_count}")
    
    # Создать единственную кампанию
    print(f"\n🎯 Создание единственной кампании...")
    if create_single_campaign():
        print(f"\n🔄 Перезапуск агента...")
        if restart_agent():
            print(f"✅ Агент перезапущен")
            
            # Проверить результат
            time.sleep(3)
            new_campaigns = get_all_campaigns()
            print(f"\n📊 Финальный результат: {len(new_campaigns)} кампания")
            
            for campaign in new_campaigns:
                print(f"   ✅ {campaign.get('name')} - чаты: {campaign.get('telegram_chats')}")
            
            print(f"\n🎯 ГОТОВО!")
            print(f"💡 Теперь должно быть только 1 сообщение на каждый комментарий 'тест'")
            print(f"📝 Попробуйте написать комментарий с 'тест' снова")
        else:
            print(f"❌ Ошибка перезапуска агента")
    else:
        print(f"❌ Ошибка создания кампании")

if __name__ == "__main__":
    main()