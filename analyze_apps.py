#!/usr/bin/env python3
"""
🔍 Анализ DigitalOcean Apps для поиска Telegram Agent
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def get_apps():
    """Получить список всех приложений"""
    token = os.getenv('DIGITALOCEAN_TOKEN')
    if not token:
        print("❌ DIGITALOCEAN_TOKEN не найден в переменных окружения")
        return None
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('https://api.digitalocean.com/v2/apps', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Ошибка запроса к DigitalOcean API: {e}")
        return None

def analyze_app_for_telegram(app):
    """Анализ приложения для поиска Telegram Agent"""
    score = 0
    reasons = []
    
    # Проверка имени приложения
    name = app.get('spec', {}).get('name', '').lower()
    if any(keyword in name for keyword in ['telegram', 'agent', 'bot', 'answer']):
        score += 5
        reasons.append(f"📛 Имя содержит ключевые слова: {name}")
    
    # Проверка репозитория GitHub
    services = app.get('spec', {}).get('services', [])
    for service in services:
        github = service.get('github', {})
        repo = github.get('repo', '').lower()
        if 'telegram' in repo or 'agent' in repo or 'claude' in repo:
            score += 5
            reasons.append(f"📦 Репозиторий: {repo}")
    
    # Проверка переменных окружения
    envs = app.get('spec', {}).get('envs', [])
    telegram_env_found = False
    for env in envs:
        key = env.get('key', '').upper()
        if any(keyword in key for keyword in ['TELEGRAM', 'ANTHROPIC', 'CLAUDE']):
            if not telegram_env_found:
                score += 3
                reasons.append(f"🔑 Telegram/AI переменные найдены")
                telegram_env_found = True
    
    # Проверка URL (live_url)
    live_url = app.get('live_url', '')
    if live_url:
        if 'answerbot' in live_url or 'telegram' in live_url or 'agent' in live_url:
            score += 2
            reasons.append(f"🌐 URL указывает на агента: {live_url}")
    
    # Проверка статуса активности
    if app.get('last_deployment_active_at'):
        score += 1
        reasons.append("✅ Активное развертывание")
    
    return score, reasons

def main():
    print("🔍 АНАЛИЗ DIGITALOCEAN APP PLATFORM ПРИЛОЖЕНИЙ")
    print("=" * 60)
    
    # Получение списка приложений
    data = get_apps()
    if not data:
        return
    
    apps = data.get('apps', [])
    if not apps:
        print("❌ Приложения не найдены")
        return
    
    print(f"📋 Найдено приложений: {len(apps)}")
    print()
    
    # Анализ каждого приложения
    candidates = []
    
    for app in apps:
        score, reasons = analyze_app_for_telegram(app)
        candidates.append((score, app, reasons))
    
    # Сортировка по релевантности
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Отображение результатов
    for i, (score, app, reasons) in enumerate(candidates, 1):
        print(f"🏆 ПРИЛОЖЕНИЕ #{i} (Релевантность: {score}/16)")
        print("─" * 50)
        
        # Основная информация
        spec = app.get('spec', {})
        print(f"📛 Имя: {spec.get('name', 'Unknown')}")
        print(f"🆔 ID: {app.get('id', 'Unknown')}")
        print(f"🌐 URL: {app.get('live_url', 'Not available')}")
        print(f"📍 Регион: {app.get('region', {}).get('label', 'Unknown')}")
        print(f"📅 Создано: {app.get('created_at', 'Unknown')[:19]}")
        print(f"🚀 Последний деплой: {app.get('last_deployment_active_at', 'Unknown')[:19]}")
        
        # Информация о сервисах
        services = spec.get('services', [])
        if services:
            print(f"🔧 Сервисы:")
            for service in services:
                service_name = service.get('name', 'Unknown')
                github = service.get('github', {})
                repo = github.get('repo', 'No repo')
                branch = github.get('branch', 'main')
                print(f"   📦 {service_name}: {repo} ({branch})")
        
        # Переменные окружения (только Telegram-связанные)
        print(f"🔑 Telegram/AI переменные:")
        envs = spec.get('envs', [])
        telegram_vars = []
        for env in envs:
            key = env.get('key', '')
            if any(keyword in key.upper() for keyword in ['TELEGRAM', 'ANTHROPIC', 'CLAUDE', 'OPENAI', 'API_ID', 'API_HASH', 'PHONE']):
                value = env.get('value', '')
                if len(value) > 20:
                    value = value[:10] + "..." + value[-5:]
                telegram_vars.append(f"   {key}: {value}")
        
        if telegram_vars:
            for var in telegram_vars[:5]:  # Показываем первые 5
                print(var)
            if len(telegram_vars) > 5:
                print(f"   ... и еще {len(telegram_vars) - 5} переменных")
        else:
            print("   Telegram переменные не найдены в spec.envs")
        
        # Причины релевантности
        if reasons:
            print(f"🎯 Причины релевантности:")
            for reason in reasons:
                print(f"   {reason}")
        
        print()
        
        # Подробная информация для лучшего кандидата
        if i == 1 and score > 5:
            print("🎯 TELEGRAM AGENT НАЙДЕН!")
            print("─" * 50)
            print(f"✅ Приложение: {spec.get('name')}")
            print(f"🌐 URL: {app.get('live_url')}")
            
            # Проверка доступности
            live_url = app.get('live_url', '')
            if live_url:
                print(f"🔍 Проверка доступности...")
                try:
                    import requests
                    response = requests.get(f"{live_url}/health", timeout=10)
                    if response.status_code == 200:
                        health_data = response.json()
                        print(f"✅ API доступен: {health_data}")
                    else:
                        print(f"⚠️  API отвечает с кодом: {response.status_code}")
                except:
                    print("❌ API недоступен или не отвечает")
            
            print()
            
            # Инструкции для App Platform
            print("📋 ОСОБЕННОСТИ APP PLATFORM:")
            print("   🚫 НЕТ SSH доступа к контейнерам")
            print("   🔧 Управление через Dashboard/API")
            print("   📝 Логи через веб-интерфейс")
            print("   🔄 Переменные через Settings")
            print("")
            
            print("💡 ВАРИАНТЫ АВТОРИЗАЦИИ:")
            print("   1. Переменные окружения с готовой сессией")
            print("   2. GitHub Actions для автоавторизации")
            print("   3. Модификация кода для автоматической авторизации")
            print("   4. Deploy hooks с предварительной авторизацией")
            print()
        
        if i < len(candidates):
            print("─" * 60)
    
    # Итоговые рекомендации
    if candidates:
        best_app = candidates[0][1]
        best_score = candidates[0][0]
        
        print("🎯 ИТОГОВЫЕ РЕКОМЕНДАЦИИ:")
        print("=" * 60)
        
        if best_score > 5:
            print(f"✅ Telegram Agent найден: {best_app.get('spec', {}).get('name')}")
            print(f"🌐 URL: {best_app.get('live_url')}")
            print()
            print("🚀 СЛЕДУЮЩИЕ ШАГИ:")
            print("   1. App Platform НЕ поддерживает SSH доступ")
            print("   2. Нужен альтернативный подход к авторизации")
            print("   3. Рассмотрите варианты:")
            print("      - Переменные окружения с токенами")
            print("      - GitHub Actions авторизация")
            print("      - Модификация кода для автоавторизации")
        else:
            print("⚠️  Telegram Agent не найден с высокой точностью")
            print("💡 Проверьте настройки вручную в DigitalOcean Dashboard")

if __name__ == "__main__":
    main()