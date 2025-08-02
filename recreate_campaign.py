#!/usr/bin/env python3
"""
Script to recreate campaign for comment monitoring
"""
import asyncio
import requests
import json

async def recreate_campaign():
    """Recreate the campaign for comment monitoring"""
    
    # Campaign data
    campaign_data = {
        "name": "Test Campaign @eslitotoeto Comments",
        "active": True,
        "telegram_chats": ["@eslitotoeto", "eslitotoeto", "1676879122", "2532661483", "8192524245"],
        "keywords": ["задача", "вопрос", "помощь", "тест", "claude"],
        "telegram_account": "+79885517453",
        "ai_provider": "openai",  # Changed to OpenAI since it's available
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
    
    print("🔄 Создание кампании...")
    
    try:
        # Create campaign
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/campaigns",
            json=campaign_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Кампания создана: {result}")
            return result
        else:
            print(f"❌ Ошибка создания кампании: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

async def check_campaign_status():
    """Check campaign status"""
    try:
        response = requests.get(
            "https://answerbot-magph.ondigitalocean.app/campaigns",
            timeout=10
        )
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"📋 Активные кампании: {len(campaigns)}")
            for campaign in campaigns:
                print(f"   - {campaign.get('name', 'Unknown')}: {campaign.get('active', 'Unknown')}")
            return campaigns
        else:
            print(f"❌ Ошибка получения кампаний: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

async def restart_agent():
    """Restart the telegram agent"""
    try:
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/telegram/restart",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Агент перезапущен: {result}")
            return True
        else:
            print(f"❌ Ошибка перезапуска агента: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Воссоздание кампании для комментариев...")
    
    # Check current status
    print("\n1. Проверка текущих кампаний...")
    campaigns = await check_campaign_status()
    
    if not campaigns:
        print("\n2. Создание новой кампании...")
        result = await recreate_campaign()
        
        if result:
            print("\n3. Перезапуск агента...")
            await restart_agent()
            
            print("\n4. Проверка финального статуса...")
            await asyncio.sleep(3)
            await check_campaign_status()
    else:
        print("✅ Кампания уже существует")

if __name__ == "__main__":
    asyncio.run(main())