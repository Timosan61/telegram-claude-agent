#!/usr/bin/env python3
"""
Отключение старых кампаний
"""
import requests
import time

def get_campaigns():
    """Получить все кампании"""
    try:
        response = requests.get("https://answerbot-magph.ondigitalocean.app/campaigns", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def update_campaign(campaign_id, active=False):
    """Обновить статус кампании"""
    try:
        # Получить текущие данные кампании
        response = requests.get(f"https://answerbot-magph.ondigitalocean.app/campaigns/{campaign_id}", timeout=10)
        if response.status_code != 200:
            print(f"❌ Не удалось получить кампанию {campaign_id}")
            return False
        
        campaign_data = response.json()
        campaign_data['active'] = active
        
        # Обновить кампанию
        update_response = requests.put(
            f"https://answerbot-magph.ondigitalocean.app/campaigns/{campaign_id}",
            json=campaign_data,
            timeout=10
        )
        
        return update_response.status_code == 200
        
    except Exception as e:
        print(f"❌ Ошибка обновления кампании {campaign_id}: {e}")
        return False

def main():
    """Основная функция"""
    print("🔧 ОТКЛЮЧЕНИЕ СТАРЫХ КАМПАНИЙ")
    print("=" * 40)
    
    campaigns = get_campaigns()
    print(f"📊 Всего кампаний: {len(campaigns)}")
    
    # Найти и отключить старые кампании (1 и 2)
    target_campaigns = []
    keep_campaign = None
    
    for campaign in campaigns:
        campaign_id = campaign.get('id')
        name = campaign.get('name', 'Unknown')
        
        print(f"\n📋 Кампания {campaign_id}: {name}")
        print(f"   Активна: {campaign.get('active')}")
        print(f"   Чаты: {campaign.get('telegram_chats')}")
        
        if campaign_id in [1, 2]:
            print(f"   ⚠️ Старая кампания - будет отключена")
            target_campaigns.append(campaign_id)
        elif campaign_id == 3:
            print(f"   ✅ Новая кампания - оставляем активной")
            keep_campaign = campaign_id
    
    # Отключить старые кампании
    print(f"\n🔄 Отключение старых кампаний...")
    disabled_count = 0
    
    for campaign_id in target_campaigns:
        if update_campaign(campaign_id, active=False):
            print(f"   ✅ Кампания {campaign_id} отключена")
            disabled_count += 1
        else:
            print(f"   ❌ Не удалось отключить кампанию {campaign_id}")
    
    print(f"📊 Отключено кампаний: {disabled_count}")
    
    # Перезапустить агента
    if disabled_count > 0:
        print(f"\n🔄 Перезапуск агента...")
        try:
            response = requests.post("https://answerbot-magph.ondigitalocean.app/telegram/restart", timeout=30)
            if response.status_code == 200:
                print(f"✅ Агент перезапущен")
                
                # Проверить результат
                time.sleep(3)
                final_campaigns = get_campaigns()
                active_campaigns = [c for c in final_campaigns if c.get('active')]
                
                print(f"\n📊 Финальный результат:")
                print(f"   Всего кампаний: {len(final_campaigns)}")
                print(f"   Активных кампаний: {len(active_campaigns)}")
                
                for campaign in active_campaigns:
                    print(f"   ✅ АКТИВНА: {campaign.get('name')} (ID: {campaign.get('id')})")
                
                if len(active_campaigns) == 1:
                    print(f"\n🎯 ОТЛИЧНО! Теперь только 1 активная кампания")
                    print(f"💡 Попробуйте написать 'тест' - должно быть только 1 ответ")
                else:
                    print(f"\n⚠️ Все еще {len(active_campaigns)} активных кампаний")
            else:
                print(f"❌ Ошибка перезапуска агента")
        except Exception as e:
            print(f"❌ Ошибка перезапуска: {e}")

if __name__ == "__main__":
    main()