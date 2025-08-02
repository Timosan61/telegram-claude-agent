#!/usr/bin/env python3
"""
🔧 Автоматическое обновление переменных окружения DigitalOcean App Platform
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class DOAppEnvironmentUpdater:
    def __init__(self):
        self.token = os.getenv('DIGITALOCEAN_TOKEN')
        if not self.token:
            print("❌ DIGITALOCEAN_TOKEN не найден в переменных окружения")
            exit(1)
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        self.app_id = "090c79a2-012d-41fa-a89f-fca3017701e2"  # ID вашего answerbot
        print(f"🎯 Целевое приложение: {self.app_id}")
    
    def get_app_spec(self):
        """Получение текущей спецификации приложения"""
        try:
            response = requests.get(
                f'https://api.digitalocean.com/v2/apps/{self.app_id}',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()['app']
        except requests.RequestException as e:
            print(f"❌ Ошибка получения спецификации приложения: {e}")
            return None
    
    def update_environment_variables(self, session_string):
        """Обновление переменных окружения приложения"""
        try:
            # Получение текущей спецификации
            app = self.get_app_spec()
            if not app:
                return False
            
            spec = app['spec'].copy()
            
            # Обновление переменных окружения
            if 'envs' not in spec:
                spec['envs'] = []
            
            # Добавление новой переменной TELEGRAM_SESSION_STRING
            session_var = {
                "key": "TELEGRAM_SESSION_STRING",
                "value": session_string,
                "scope": "RUN_AND_BUILD_TIME"
            }
            
            # Проверяем, есть ли уже такая переменная
            existing_var_index = None
            for i, env_var in enumerate(spec['envs']):
                if env_var['key'] == 'TELEGRAM_SESSION_STRING':
                    existing_var_index = i
                    break
            
            if existing_var_index is not None:
                # Обновляем существующую переменную
                spec['envs'][existing_var_index] = session_var
                print("✅ Переменная TELEGRAM_SESSION_STRING обновлена")
            else:
                # Добавляем новую переменную
                spec['envs'].append(session_var)
                print("✅ Переменная TELEGRAM_SESSION_STRING добавлена")
            
            # Также добавим переменные Telegram API если их нет
            telegram_vars = [
                {
                    "key": "TELEGRAM_API_ID",
                    "value": os.getenv("TELEGRAM_API_ID", "21220429"),
                    "scope": "RUN_AND_BUILD_TIME"
                },
                {
                    "key": "TELEGRAM_API_HASH", 
                    "value": os.getenv("TELEGRAM_API_HASH", "2f4d35cf3aa6bfcfae8f655547084a44"),
                    "scope": "RUN_AND_BUILD_TIME"
                },
                {
                    "key": "TELEGRAM_PHONE",
                    "value": os.getenv("TELEGRAM_PHONE", "+79885517453"),
                    "scope": "RUN_AND_BUILD_TIME"
                }
            ]
            
            for telegram_var in telegram_vars:
                # Проверяем, есть ли уже такая переменная
                existing = False
                for env_var in spec['envs']:
                    if env_var['key'] == telegram_var['key']:
                        existing = True
                        break
                
                if not existing:
                    spec['envs'].append(telegram_var)
                    print(f"✅ Добавлена переменная {telegram_var['key']}")
            
            # Обновление спецификации приложения
            update_payload = {"spec": spec}
            
            response = requests.put(
                f'https://api.digitalocean.com/v2/apps/{self.app_id}',
                headers=self.headers,
                json=update_payload
            )
            response.raise_for_status()
            
            print("🚀 Спецификация приложения обновлена!")
            print("⏳ Ожидается автоматический деплой...")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обновления переменных: {e}")
            return False
    
    def check_deployment_status(self):
        """Проверка статуса деплоя"""
        try:
            app = self.get_app_spec()
            if not app:
                return
            
            deployment = app.get('active_deployment', {})
            phase = deployment.get('phase', 'Unknown')
            
            print(f"📊 Статус деплоя: {phase}")
            
            if phase == 'ACTIVE':
                print("✅ Деплой завершен успешно!")
                live_url = app.get('live_url', '')
                if live_url:
                    print(f"🌐 Приложение доступно: {live_url}")
                    
                    # Проверяем health endpoint
                    try:
                        health_response = requests.get(f"{live_url}/health", timeout=10)
                        if health_response.status_code == 200:
                            health_data = health_response.json()
                            telegram_connected = health_data.get('telegram_connected', False)
                            if telegram_connected:
                                print("🎉 TELEGRAM AGENT АВТОРИЗОВАН УСПЕШНО!")
                            else:
                                print("⚠️ Telegram Agent не авторизован, проверьте логи")
                    except:
                        print("⚠️ Не удалось проверить health endpoint")
            
            elif phase in ['BUILDING', 'DEPLOYING']:
                print("⏳ Деплой в процессе, подождите...")
            elif phase == 'ERROR':
                print("❌ Ошибка деплоя, проверьте логи в Dashboard")
            
        except Exception as e:
            print(f"❌ Ошибка проверки статуса: {e}")

def main():
    print("🔧 ОБНОВЛЕНИЕ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ APP PLATFORM")
    print("=" * 60)
    
    # Проверяем, есть ли готовая сессия
    session_file = "telegram_session_for_app_platform.json"
    
    if os.path.exists(session_file):
        print(f"📁 Найден файл сессии: {session_file}")
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            session_string = session_data.get('session_string')
            if not session_string:
                print("❌ session_string не найдена в файле")
                return
            
            print(f"✅ Сессия загружена: {session_string[:20]}...")
            
        except Exception as e:
            print(f"❌ Ошибка чтения файла сессии: {e}")
            return
    else:
        print(f"❌ Файл сессии не найден: {session_file}")
        print("💡 Сначала запустите: python create_session_for_app_platform.py")
        return
    
    # Создание updater и обновление переменных
    updater = DOAppEnvironmentUpdater()
    
    print("\n🔄 Обновление переменных окружения...")
    success = updater.update_environment_variables(session_string)
    
    if success:
        print("\n✅ Переменные обновлены успешно!")
        print("⏳ Ожидание завершения автодеплоя (это может занять 2-3 минуты)...")
        
        # Ожидание и проверка статуса
        import time
        for i in range(6):  # Проверяем 6 раз с интервалом 30 секунд
            time.sleep(30)
            print(f"\n📊 Проверка #{i+1}/6...")
            updater.check_deployment_status()
            
            # Проверяем, завершился ли деплой
            app = updater.get_app_spec()
            if app and app.get('active_deployment', {}).get('phase') == 'ACTIVE':
                break
        
        print("\n🎯 ФИНАЛЬНАЯ ПРОВЕРКА:")
        print("=" * 30)
        updater.check_deployment_status()
        
    else:
        print("\n❌ Ошибка обновления переменных")

if __name__ == "__main__":
    main()