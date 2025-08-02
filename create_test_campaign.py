#!/usr/bin/env python3
"""
📋 Создание тестовой кампании для мониторинга Telegram канала
"""
import requests
import json

def create_test_campaign():
    """Создание тестовой кампании"""
    
    url = "https://answerbot-magph.ondigitalocean.app/campaigns"
    
    campaign_data = {
        "name": "Test Campaign @eslitotoeto v2",
        "telegram_chats": ["@eslitotoeto", "eslitotoeto", "1676879122"],
        "keywords": ["задача", "вопрос", "помощь", "тест", "claude"],
        "telegram_account": "+79885517453",
        "claude_agent_id": "telegram_claude_agent",
        "context_messages_count": 3,
        "system_instruction": "Ты - полезный ассистент с именем Claude Bot. Отвечай кратко и по существу на русском языке. Помогай пользователям с их вопросами. Используй эмодзи для дружелюбности.",
        "example_replies": {
            "greeting": "Привет! Как дела? 👋",
            "help": "Конечно, помогу! Что именно вас интересует? 🤔",
            "thanks": "Пожалуйста! Рад был помочь! 😊"
        },
        "active": True
    }
    
    try:
        print("📋 Создание тестовой кампании...")
        print(f"🎯 Целевой канал: @eslitotoeto (ID: 1676879122)")
        print(f"🔑 Ключевые слова: {campaign_data['keywords']}")
        print(f"🤖 Автоответы: {'Включены' if campaign_data['active'] else 'Отключены'}")
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=campaign_data,
            timeout=10
        )
        
        print(f"📊 HTTP Status: {response.status_code}")
        
        if response.status_code == 201:
            campaign = response.json()
            print("✅ Кампания создана успешно!")
            print(f"📋 ID кампании: {campaign.get('id')}")
            print(f"📝 Название: {campaign.get('name')}")
            print(f"🎯 Цели: {campaign.get('target_chats')}")
            print(f"🔄 Статус: {'Активна' if campaign.get('is_active') else 'Неактивна'}")
            return campaign
        else:
            print(f"❌ Ошибка создания кампании: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def check_campaigns():
    """Проверка списка кампаний"""
    try:
        print("\n📂 Проверка существующих кампаний...")
        
        response = requests.get(
            "https://answerbot-magph.ondigitalocean.app/campaigns",
            timeout=10
        )
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"📊 Найдено кампаний: {len(campaigns)}")
            
            for campaign in campaigns:
                status = "🟢 Активна" if campaign.get('is_active') else "🔴 Неактивна"
                print(f"  📋 {campaign.get('name')} - {status}")
                print(f"     🎯 Цели: {campaign.get('target_chats')}")
                print(f"     🔑 Ключевые слова: {campaign.get('keywords')}")
                print()
        else:
            print(f"❌ Ошибка получения кампаний: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    print("🧪 СОЗДАНИЕ ТЕСТОВОЙ КАМПАНИИ")
    print("=" * 50)
    
    # Проверяем существующие кампании
    check_campaigns()
    
    # Создаем новую кампанию
    campaign = create_test_campaign()
    
    if campaign:
        print("\n🎉 ТЕСТОВАЯ КАМПАНИЯ ГОТОВА!")
        print("📱 Теперь можно отправить сообщение в канал @eslitotoeto")
        print("🔑 Используйте ключевые слова: задача, вопрос, помощь, тест, claude")
        print("🤖 Бот должен автоматически ответить используя gpt-4o")
    else:
        print("\n❌ Не удалось создать кампанию")

if __name__ == "__main__":
    main()