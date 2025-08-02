#!/usr/bin/env python3
"""
Отладка комментариев в реальном времени
"""
import asyncio
import requests
import json

def check_recent_activity():
    """Проверить последнюю активность в логах"""
    try:
        print("📊 Проверка последних логов...")
        response = requests.get("https://answerbot-magph.ondigitalocean.app/logs", timeout=10)
        if response.status_code == 200:
            logs = response.json()
            print(f"📝 Всего логов: {len(logs)}")
            
            # Показать последние 10 логов
            recent_logs = logs[-10:] if logs else []
            for log in recent_logs:
                print(f"   {log.get('timestamp', 'Unknown')}: {log.get('original_message', 'No message')[:50]} -> {log.get('status', 'Unknown')}")
            
            return len(logs)
        else:
            print(f"❌ Не удалось получить логи: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Ошибка получения логов: {e}")
        return 0

def get_campaign_info():
    """Получить информацию о кампаниях"""
    try:
        print("\n📋 Информация о кампаниях...")
        response = requests.get("https://answerbot-magph.ondigitalocean.app/campaigns", timeout=10)
        if response.status_code == 200:
            campaigns = response.json()
            print(f"📊 Активных кампаний: {len(campaigns)}")
            
            for i, campaign in enumerate(campaigns, 1):
                print(f"\n🎯 Кампания {i}:")
                print(f"   📝 Название: {campaign.get('name', 'Unknown')}")
                print(f"   ✅ Активна: {campaign.get('active', False)}")
                print(f"   💬 Чаты: {campaign.get('telegram_chats', [])}")
                print(f"   🔑 Ключевые слова: {campaign.get('keywords', [])}")
                
                # Специальная проверка для группы обсуждений
                chats = campaign.get('telegram_chats', [])
                if '2532661483' in [str(chat) for chat in chats]:
                    print(f"   ✅ Группа обсуждений включена!")
                else:
                    print(f"   ❌ Группа обсуждений НЕ включена!")
                    
            return campaigns
        else:
            print(f"❌ Не удалось получить кампании: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Ошибка получения кампаний: {e}")
        return []

def check_agent_status():
    """Проверить статус агента"""
    try:
        print("\n🤖 Статус агента...")
        response = requests.get("https://answerbot-magph.ondigitalocean.app/telegram/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            details = status.get('details', {})
            
            print(f"🔗 Подключен: {details.get('connected', False)}")
            print(f"🔐 Авторизован: {details.get('authorized', False)}")
            print(f"📊 Активных кампаний: {details.get('active_campaigns', 0)}")
            print(f"💡 OpenAI: {details.get('ai_clients', {}).get('openai', False)}")
            
            return details.get('connected', False) and details.get('authorized', False)
        else:
            print(f"❌ Не удалось получить статус: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка получения статуса: {e}")
        return False

def test_manual_message():
    """Отправить тестовое сообщение в группу обсуждений через API"""
    print("\n🧪 Попытка отправки тестового сообщения...")
    
    # Создать временную кампанию для теста
    test_campaign = {
        "name": "Manual Test Campaign",
        "active": True,
        "telegram_chats": ["2532661483"],  # Группа обсуждений
        "keywords": ["мануальныйтест"],  # Уникальное слово
        "telegram_account": "+79885517453",
        "ai_provider": "openai",
        "system_instruction": "Тестовый ответ: Я получил ваше сообщение!"
    }
    
    try:
        # Создать тестовую кампанию
        response = requests.post(
            "https://answerbot-magph.ondigitalocean.app/campaigns",
            json=test_campaign,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Тестовая кампанию создана: ID {result.get('id')}")
            
            # Перезапустить агента
            restart_response = requests.post(
                "https://answerbot-magph.ondigitalocean.app/telegram/restart",
                timeout=30
            )
            
            if restart_response.status_code == 200:
                print("✅ Агент перезапущен для загрузки тестовой кампании")
                print("\n🎯 ИНСТРУКЦИЯ ДЛЯ РУЧНОГО ТЕСТА:")
                print("1. Зайдите в группу 'Если это, то сделай то Chat'")
                print("2. Напишите сообщение: мануальныйтест")
                print("3. Если бот работает, он должен ответить")
                print("4. Проверьте результат через 10 секунд")
                return True
            else:
                print(f"❌ Ошибка перезапуска агента: {restart_response.status_code}")
                return False
        else:
            print(f"❌ Ошибка создания тестовой кампании: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

def wait_and_check_results():
    """Подождать и проверить результаты"""
    print("\n⏰ Ожидание результатов теста (15 секунд)...")
    import time
    time.sleep(15)
    
    print("\n📊 Проверка результатов...")
    logs_before = check_recent_activity()
    
    if logs_before > 0:
        print("✅ Есть активность в логах!")
    else:
        print("❌ Нет активности в логах")

def main():
    """Основная функция диагностики"""
    print("🔍 ДИАГНОСТИКА КОММЕНТАРИЕВ В РЕАЛЬНОМ ВРЕМЕНИ")
    print("=" * 60)
    
    # Проверить статус
    if not check_agent_status():
        print("❌ Агент не работает - завершение диагностики")
        return
    
    # Проверить кампании
    campaigns = get_campaign_info()
    if not campaigns:
        print("❌ Нет активных кампаний")
        return
    
    # Проверить логи
    logs_count = check_recent_activity()
    
    # Сделать ручной тест
    if test_manual_message():
        wait_and_check_results()
    
    print("\n🎯 ЗАКЛЮЧЕНИЕ:")
    print("Если вы видели сообщение 'bot activation monitor', но бот не отвечает на 'тест',")
    print("возможные причины:")
    print("1. Комментарии приходят из другого чата (не группы обсуждений)")
    print("2. Событие комментария имеет другой формат")
    print("3. Нужно активировать подписку на события комментариев")

if __name__ == "__main__":
    main()