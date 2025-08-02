#!/usr/bin/env python3
"""
🔍 Поиск DigitalOcean дроплета с Telegram Agent
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def get_droplets():
    """Получить список всех дроплетов"""
    token = os.getenv('DIGITALOCEAN_TOKEN')
    if not token:
        print("❌ DIGITALOCEAN_TOKEN не найден в переменных окружения")
        return None
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('https://api.digitalocean.com/v2/droplets', headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Ошибка запроса к DigitalOcean API: {e}")
        return None

def analyze_droplet(droplet):
    """Анализ дроплета для поиска Telegram Agent"""
    score = 0
    reasons = []
    
    # Проверка имени
    name = droplet.get('name', '').lower()
    if any(keyword in name for keyword in ['telegram', 'agent', 'bot']):
        score += 3
        reasons.append(f"📛 Имя содержит ключевые слова: {droplet['name']}")
    
    # Проверка размера (типичный для небольших приложений)
    size_slug = droplet.get('size_slug', '')
    if size_slug in ['s-1vcpu-2gb', 's-2vcpu-4gb', 's-1vcpu-1gb']:
        score += 2
        reasons.append(f"💾 Подходящий размер: {size_slug}")
    
    # Проверка образа Ubuntu (типичный для Python приложений)
    image = droplet.get('image', {})
    if image.get('distribution') == 'Ubuntu':
        score += 1
        reasons.append(f"🐧 Ubuntu: {image.get('name', 'Unknown')}")
    
    # Проверка статуса (должен быть активным)
    if droplet.get('status') == 'active':
        score += 1
        reasons.append("✅ Статус: активный")
    
    # Проверка возраста (недавно созданный)
    created_at = droplet.get('created_at', '')
    if '2025' in created_at:
        score += 1
        reasons.append(f"📅 Создан в 2025: {created_at[:10]}")
    
    return score, reasons

def main():
    print("🔍 ПОИСК DITALOCEAN ДРОПЛЕТА С TELEGRAM AGENT")
    print("=" * 55)
    
    # Получение списка дроплетов
    data = get_droplets()
    if not data:
        return
    
    droplets = data.get('droplets', [])
    if not droplets:
        print("❌ Дроплеты не найдены")
        return
    
    print(f"📋 Найдено дроплетов: {len(droplets)}")
    print()
    
    # Анализ каждого дроплета
    candidates = []
    
    for droplet in droplets:
        score, reasons = analyze_droplet(droplet)
        candidates.append((score, droplet, reasons))
    
    # Сортировка по релевантности
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Отображение результатов
    for i, (score, droplet, reasons) in enumerate(candidates, 1):
        print(f"🏆 ДРОПЛЕТ #{i} (Релевантность: {score}/8)")
        print("─" * 50)
        
        # Основная информация
        print(f"📛 Имя: {droplet['name']}")
        print(f"🆔 ID: {droplet['id']}")
        print(f"🌐 IP адреса:")
        
        # IP адреса
        networks = droplet.get('networks', {})
        v4_networks = networks.get('v4', [])
        
        public_ips = []
        private_ips = []
        
        for network in v4_networks:
            ip = network.get('ip_address')
            net_type = network.get('type')
            if net_type == 'public':
                public_ips.append(ip)
            elif net_type == 'private':
                private_ips.append(ip)
        
        for ip in public_ips:
            print(f"   🌍 Публичный: {ip}")
        for ip in private_ips:
            print(f"   🏠 Приватный: {ip}")
        
        # Характеристики
        print(f"💻 Размер: {droplet.get('size_slug', 'Unknown')}")
        print(f"💾 RAM: {droplet.get('memory', 0)} MB")
        print(f"🖥️  CPU: {droplet.get('vcpus', 0)} vCPU")
        print(f"💽 Диск: {droplet.get('disk', 0)} GB")
        print(f"📍 Регион: {droplet.get('region', {}).get('name', 'Unknown')}")
        print(f"🐧 ОС: {droplet.get('image', {}).get('name', 'Unknown')}")
        print(f"📊 Статус: {droplet.get('status', 'Unknown')}")
        print(f"📅 Создан: {droplet.get('created_at', 'Unknown')[:19]}")
        
        # Причины релевантности
        if reasons:
            print(f"🎯 Причины релевантности:")
            for reason in reasons:
                print(f"   {reason}")
        
        print()
        
        # Команды SSH для лучшего кандидата
        if i == 1 and public_ips:
            print("🚀 КОМАНДЫ ДЛЯ ПОДКЛЮЧЕНИЯ (лучший кандидат):")
            print("─" * 50)
            for ip in public_ips:
                print(f"🔑 SSH root: ssh root@{ip}")
                print(f"🔑 SSH ubuntu: ssh ubuntu@{ip}")
            print()
            print("📋 Команды после подключения:")
            print("   docker ps                                    # найти контейнер")
            print("   docker exec -it CONTAINER_ID /bin/bash      # войти в контейнер")
            print("   python reauth_telegram.py                   # авторизация")
            print()
        
        if i < len(candidates):
            print("─" * 55)
    
    # Итоговые рекомендации
    if candidates:
        best_droplet = candidates[0][1]
        best_public_ips = []
        
        for network in best_droplet.get('networks', {}).get('v4', []):
            if network.get('type') == 'public':
                best_public_ips.append(network.get('ip_address'))
        
        print("🎯 РЕКОМЕНДАЦИИ:")
        print("=" * 55)
        print(f"✅ Лучший кандидат: {best_droplet['name']}")
        
        if best_public_ips:
            print(f"🌐 IP для подключения: {best_public_ips[0]}")
            print()
            print("🚀 БЫСТРЫЙ СТАРТ:")
            print(f"   1. ssh root@{best_public_ips[0]}")
            print("   2. Выполните: ./docker_connect.sh")
            print("   3. В контейнере: ./container_auth.sh")
            print("   4. Проверка: ./verify_auth_results.sh")
        else:
            print("⚠️  Публичный IP не найден")

if __name__ == "__main__":
    main()