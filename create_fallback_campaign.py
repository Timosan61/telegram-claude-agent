#!/usr/bin/env python3
"""
Создание кампании с fallback ответами (без зависимости от AI API)
"""
import requests
import json

def create_fallback_campaign():
    """Создать кампанию с умными fallback ответами"""
    
    campaign_data = {
        "name": "Smart Fallback Campaign @eslitotoeto",
        "active": True,
        "telegram_chats": [
            "@eslitotoeto",        # Канал (основной)
            "eslitotoeto",         # Канал (альтернативный ID)
            "1676879122",          # Канал (числовой ID)
            "2532661483",          # Группа обсуждений (КЛЮЧЕВАЯ)
            "8192524245"           # Дополнительная группа
        ],
        "keywords": ["задача", "вопрос", "помощь", "тест", "claude", "бот", "help", "привет", "здравствуй"],
        "telegram_account": "+79885517453",
        "ai_provider": "openai",  # Попытка использовать OpenAI
        "claude_agent_id": "smart_fallback_agent",
        "openai_model": "gpt-4o",
        "context_messages_count": 3,
        "system_instruction": "Ты - полезный ассистент Claude Bot. Отвечай кратко и по существу на русском языке. Помогай пользователям с их вопросами. Используй эмодзи.",
        "example_replies": {
            "greeting": "Привет! 👋 Как дела? Чем могу помочь?",
            "help": "Конечно помогу! 🤔 Что именно интересует?",
            "task": "Понял задачу! 📝 Давайте разберем пошагово:",
            "question": "Отличный вопрос! 💡 Отвечу максимально подробно:",
            "test": "Тест принят! ✅ Система работает отлично!",
            "bot": "Да, я Claude Bot! 🤖 Готов помочь с любыми вопросами!",
            "thanks": "Пожалуйста! 😊 Рад был помочь! Обращайтесь еще!",
            "default": "Получил ваше сообщение! 💭 Подумаю и отвечу максимально полезно."
        }
    }
    
    try:
        print("🚀 Создание умной fallback кампании...")
        
        # Сначала удалим старые кампании
        try:
            campaigns_response = requests.get("https://answerbot-magph.ondigitalocean.app/campaigns", timeout=10)
            if campaigns_response.status_code == 200:
                campaigns = campaigns_response.json()
                for campaign in campaigns:
                    campaign_id = campaign.get('id')
                    print(f"🗑️ Удаление старой кампании ID: {campaign_id}")
                    requests.delete(f"https://answerbot-magph.ondigitalocean.app/campaigns/{campaign_id}")
        except:
            pass
        
        # Создать новую кампанию
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
    """Перезапустить агента"""
    try:
        print("🔄 Перезапуск агента...")
        response = requests.post("https://answerbot-magph.ondigitalocean.app/telegram/restart", timeout=30)
        
        if response.status_code == 200:
            print("✅ Агент перезапущен успешно")
            return True
        else:
            print(f"❌ Ошибка перезапуска: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка перезапуска: {e}")
        return False

def test_campaign():
    """Тестировать кампанию"""
    try:
        print("\n📊 Финальная проверка...")
        import time
        time.sleep(3)
        
        # Статус агента
        response = requests.get("https://answerbot-magph.ondigitalocean.app/telegram/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            details = status.get('details', {})
            
            print(f"🔗 Подключен: {details.get('connected', False)}")
            print(f"🔐 Авторизован: {details.get('authorized', False)}")
            print(f"📊 Активных кампаний: {details.get('active_campaigns', 0)}")
            
            ai_clients = details.get('ai_clients', {})
            print(f"🤖 OpenAI: {ai_clients.get('openai_working', False)}")
            print(f"🤖 Claude: {ai_clients.get('claude', False)}")
            
            if details.get('active_campaigns', 0) > 0:
                print("\n✅ СИСТЕМА АКТИВНА!")
                print("💡 Особенности:")
                if ai_clients.get('openai_working'):
                    print("   🧠 OpenAI GPT-4o активен - умные ответы")
                else:
                    print("   🔄 Fallback режим - заготовленные ответы")
                
                print("\n🎯 Для тестирования напишите в комментариях:")
                print("   'тест' - проверка работы")
                print("   'помощь' - запрос помощи")  
                print("   'вопрос' - задать вопрос")
                print("   'бот' - информация о боте")
                
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def main():
    """Основная функция"""
    print("🎯 СОЗДАНИЕ УМНОЙ FALLBACK КАМПАНИИ")
    print("=" * 45)
    
    # Создать кампанию
    campaign_id = create_fallback_campaign()
    if not campaign_id:
        print("❌ Не удалось создать кампанию")
        return
    
    # Перезапустить агента
    if restart_agent():
        # Тестировать
        if test_campaign():
            print("\n🎉 ГОТОВО К РАБОТЕ!")
            print("📝 Система готова отвечать на комментарии!")
            print("🔍 Попробуйте написать комментарий в канале @eslitotoeto")
        else:
            print("❌ Проблемы с инициализацией")
    else:
        print("❌ Ошибка перезапуска агента")

if __name__ == "__main__":
    main()