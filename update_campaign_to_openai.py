#!/usr/bin/env python3
"""
Обновление кампании для использования OpenAI
"""
import requests
import json

def update_campaign_to_openai(campaign_id=1):
    """Обновить кампанию для использования OpenAI"""
    
    # Получить текущие данные кампании
    try:
        response = requests.get(f"https://answerbot-magph.ondigitalocean.app/campaigns/{campaign_id}")
        if response.status_code != 200:
            print(f"❌ Ошибка получения кампании: {response.status_code}")
            return False
            
        campaign_data = response.json()
        print(f"📋 Текущая кампания: {campaign_data['name']}")
        print(f"🤖 Текущий AI provider: {campaign_data.get('ai_provider', 'unknown')}")
        
        # Обновить AI провайдер на OpenAI
        campaign_data['ai_provider'] = 'openai'
        campaign_data['openai_model'] = 'gpt-4o'
        
        print(f"\n🔄 Обновление на OpenAI...")
        
        # Отправить обновленные данные
        update_response = requests.put(
            f"https://answerbot-magph.ondigitalocean.app/campaigns/{campaign_id}",
            json=campaign_data,
            timeout=30
        )
        
        if update_response.status_code == 200:
            updated_data = update_response.json()
            print(f"✅ Кампания обновлена!")
            print(f"🤖 Новый AI provider: {updated_data.get('ai_provider')}")
            print(f"🧠 Модель: {updated_data.get('openai_model')}")
            return True
        else:
            print(f"❌ Ошибка обновления: {update_response.status_code}")
            print(f"📋 Ответ: {update_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def restart_agent():
    """Перезапустить агента"""
    try:
        print("\n🔄 Перезапуск агента для применения изменений...")
        response = requests.post("https://answerbot-magph.ondigitalocean.app/telegram/restart", timeout=30)
        
        if response.status_code == 200:
            print("✅ Агент перезапущен")
            return True
        else:
            print(f"❌ Ошибка перезапуска: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка перезапуска: {e}")
        return False

def check_openai_status():
    """Проверить статус OpenAI"""
    try:
        print("\n📊 Проверка статуса OpenAI...")
        
        import time
        time.sleep(3)  # Ждем инициализацию
        
        response = requests.get("https://answerbot-magph.ondigitalocean.app/telegram/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            details = status.get('details', {})
            ai_clients = details.get('ai_clients', {})
            
            print(f"🤖 OpenAI доступен: {ai_clients.get('openai', False)}")
            print(f"🤖 OpenAI работает: {ai_clients.get('openai_working', False)}")
            print(f"📊 Активных кампаний: {details.get('active_campaigns', 0)}")
            
            if ai_clients.get('openai_working'):
                print("\n🎉 OPENAI АКТИВЕН! Бот готов к интеллектуальным ответам!")
                return True
            else:
                print("\n⚠️ OpenAI пока не активен. Возможные причины:")
                print("   1. Нет OPENAI_API_KEY в переменных окружения")
                print("   2. Неправильный API ключ")
                print("   3. Ошибка инициализации")
                return False
        else:
            print(f"❌ Ошибка получения статуса: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def main():
    """Основная функция"""
    print("🔄 ПЕРЕКЛЮЧЕНИЕ КАМПАНИИ НА OPENAI")
    print("=" * 40)
    
    # Обновить кампанию
    if update_campaign_to_openai():
        # Перезапустить агента
        if restart_agent():
            # Проверить статус OpenAI
            openai_working = check_openai_status()
            
            if openai_working:
                print("\n🚀 ГОТОВО К РАБОТЕ!")
                print("💡 Попробуйте написать комментарий:")
                print("   'тест бот' или 'помощь' в канале @eslitotoeto")
                print("🧠 Ответы будут генерироваться GPT-4o!")
            else:
                print("\n⚠️ Требуется настройка OPENAI_API_KEY")
                print("💡 Бот будет использовать fallback ответы")
        else:
            print("❌ Ошибка перезапуска агента")
    else:
        print("❌ Ошибка обновления кампании")

if __name__ == "__main__":
    main()