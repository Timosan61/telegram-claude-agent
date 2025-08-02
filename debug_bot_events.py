#!/usr/bin/env python3
"""
Отладка событий бота через API
"""
import requests
import time
import json

def check_bot_status():
    """Проверить статус бота"""
    try:
        response = requests.get("https://answerbot-magph.ondigitalocean.app/telegram/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"🔍 Статус бота:")
            print(f"   Подключен: {status['details']['connected']}")
            print(f"   Авторизован: {status['details']['authorized']}")
            print(f"   Активных кампаний: {status['details']['active_campaigns']}")
            print(f"   OpenAI: {status['details']['ai_clients']['openai']}")
            print(f"   OpenAI работает: {status['details']['ai_clients']['openai_working']}")
            return status['details']['active_campaigns'] > 0
        else:
            print(f"❌ Ошибка получения статуса: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_campaigns():
    """Проверить кампании"""
    try:
        response = requests.get("https://answerbot-magph.ondigitalocean.app/campaigns", timeout=10)
        if response.status_code == 200:
            campaigns = response.json()
            print(f"\n📋 Кампании ({len(campaigns)}):")
            for campaign in campaigns:
                print(f"   - {campaign['name']}: активна={campaign['active']}")
                print(f"     Чаты: {campaign['telegram_chats']}")
                print(f"     Ключевые слова: {campaign['keywords']}")
            return len(campaigns) > 0
        else:
            print(f"❌ Ошибка получения кампаний: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_recent_logs():
    """Проверить последние логи"""
    try:
        print(f"\n📝 Попытка получения логов...")
        response = requests.get("https://answerbot-magph.ondigitalocean.app/logs", timeout=5)
        if response.status_code == 200:
            logs = response.json()
            print(f"📊 Найдено логов: {len(logs)}")
            for log in logs[-5:]:  # Последние 5
                print(f"   {log.get('timestamp', 'Unknown')}: {log.get('trigger_keyword', 'Unknown')} -> {log.get('status', 'Unknown')}")
        else:
            print(f"⚠️ Логи недоступны: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Логи недоступны: {e}")

def restart_bot():
    """Перезапустить бота"""
    try:
        print(f"\n🔄 Перезапуск бота...")
        response = requests.post("https://answerbot-magph.ondigitalocean.app/telegram/restart", timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Бот перезапущен: {result['message']}")
            return True
        else:
            print(f"❌ Ошибка перезапуска: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def force_create_campaign():
    """Принудительно создать кампанию"""
    campaign_data = {
        "name": "Test Campaign @eslitotoeto Comments",
        "active": True,
        "telegram_chats": ["@eslitotoeto", "eslitotoeto", "1676879122", "2532661483", "8192524245"],
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
        print(f"\n🎯 Создание кампании...")
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/campaigns",
            json=campaign_data,
            timeout=30
        )
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Кампания создана: ID {result.get('id', 'Unknown')}")
            return True
        else:
            print(f"❌ Ошибка создания кампании: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция диагностики"""
    print("🔍 Диагностика бота для комментариев...")
    
    print("\n=== ШАГ 1: ПРОВЕРКА СТАТУСА ===")
    bot_ok = check_bot_status()
    
    print("\n=== ШАГ 2: ПРОВЕРКА КАМПАНИЙ ===")
    campaigns_ok = check_campaigns()
    
    if not campaigns_ok:
        print("\n=== ШАГ 3: СОЗДАНИЕ КАМПАНИИ ===")
        if force_create_campaign():
            print("\n=== ШАГ 4: ПЕРЕЗАПУСК БОТА ===")
            if restart_bot():
                time.sleep(3)
                print("\n=== ШАГ 5: ПОВТОРНАЯ ПРОВЕРКА ===")
                check_bot_status()
                check_campaigns()
    
    print("\n=== ШАГ 6: ПРОВЕРКА ЛОГОВ ===")
    check_recent_logs()
    
    print("\n🎯 ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("📝 Теперь попробуйте написать комментарий с словом 'тест' в канале @eslitotoeto")
    print("⏰ Подождите 10-15 секунд и проверьте, ответил ли бот")

if __name__ == "__main__":
    main()