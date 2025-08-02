#!/usr/bin/env python3
"""
Создание production кампании с активным OpenAI
"""
import requests
import json

def create_openai_campaign():
    """Создать кампанию с активным OpenAI для реальных ответов"""
    
    campaign_data = {
        "name": "Production Campaign @eslitotoeto with OpenAI",
        "active": True,
        "telegram_chats": [
            "@eslitotoeto",        # Канал (основной)
            "eslitotoeto",         # Канал (альтернативный ID)
            "1676879122",          # Канал (числовой ID)
            "2532661483",          # Группа обсуждений (КЛЮЧЕВАЯ)
            "8192524245"           # Дополнительная группа
        ],
        "keywords": ["задача", "вопрос", "помощь", "тест", "claude", "бот", "help"],
        "telegram_account": "+79885517453",
        "ai_provider": "openai",  # АКТИВНЫЙ OpenAI
        "claude_agent_id": "production_telegram_agent",
        "openai_model": "gpt-4o",
        "context_messages_count": 5,
        "system_instruction": "Ты - полезный ассистент с именем Claude Bot. Отвечай кратко и по существу на русском языке. Помогай пользователям с их вопросами и задачами. Используй эмодзи для дружелюбности. Если вопрос касается технических тем, предоставляй практические советы.",
        "example_replies": {
            "greeting": "Привет! Как дела? 👋 Чем могу помочь?",
            "help": "Конечно, помогу! Что именно вас интересует? 🤔",
            "task": "Понял задачу! Давайте разберем по шагам 📝",
            "question": "Хороший вопрос! Отвечу максимально подробно 💡",
            "thanks": "Пожалуйста! Рад был помочь! 😊 Обращайтесь еще!"
        }
    }
    
    try:
        print("🚀 Создание production кампании с OpenAI...")
        
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/campaigns",
            json=campaign_data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            campaign_id = result.get('id')
            print(f"✅ Кампания успешно создана!")
            print(f"   📋 ID: {campaign_id}")
            print(f"   📝 Название: {result.get('name')}")
            print(f"   🤖 AI Provider: {result.get('ai_provider')}")
            print(f"   🔑 Keywords: {result.get('keywords')}")
            
            return campaign_id
        else:
            print(f"❌ Ошибка создания кампании: {response.status_code}")
            print(f"📋 Ответ: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def restart_agent():
    """Перезапустить агента для загрузки новой кампании"""
    try:
        print("🔄 Перезапуск агента...")
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/telegram/restart", 
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Агент перезапущен успешно")
            return True
        else:
            print(f"❌ Ошибка перезапуска: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка перезапуска: {e}")
        return False

def check_final_status():
    """Проверить финальный статус агента"""
    try:
        print("\n📊 Проверка финального статуса...")
        
        # Статус агента
        response = requests.get("https://answerbot-magph.ondigitalocean.app/telegram/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            details = status.get('details', {})
            
            print(f"🔗 Подключен: {details.get('connected', False)}")
            print(f"🔐 Авторизован: {details.get('authorized', False)}")
            print(f"📊 Активных кампаний: {details.get('active_campaigns', 0)}")
            print(f"🤖 OpenAI: {details.get('ai_clients', {}).get('openai_working', False)}")
        
        # Список кампаний
        campaigns_response = requests.get("https://answerbot-magph.ondigitalocean.app/campaigns", timeout=10)
        if campaigns_response.status_code == 200:
            campaigns = campaigns_response.json()
            print(f"\n📋 Всего кампаний: {len(campaigns)}")
            
            for campaign in campaigns:
                if campaign.get('active'):
                    print(f"   ✅ АКТИВНА: {campaign.get('name')} (ID: {campaign.get('id')})")
                    print(f"      🤖 AI: {campaign.get('ai_provider')}")
                    print(f"      💬 Чаты: {len(campaign.get('telegram_chats', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")
        return False

def main():
    """Основная функция"""
    print("🎯 СОЗДАНИЕ PRODUCTION КАМПАНИИ С OPENAI")
    print("=" * 50)
    
    # Создать кампанию
    campaign_id = create_openai_campaign()
    if not campaign_id:
        print("❌ Не удалось создать кампанию")
        return
    
    # Перезапустить агента
    if restart_agent():
        print("⏱️ Ожидание 5 секунд...")
        import time
        time.sleep(5)
        
        # Проверить результат
        check_final_status()
        
        print("\n🎉 ГОТОВО!")
        print("💡 Теперь бот будет отвечать через OpenAI GPT-4o")
        print("📝 Напишите комментарий с любым из ключевых слов:")
        print("   'задача', 'вопрос', 'помощь', 'тест', 'claude', 'бот', 'help'")
        print("🔍 Ответы будут генерироваться искусственным интеллектом!")
    else:
        print("❌ Ошибка перезапуска агента")

if __name__ == "__main__":
    main()