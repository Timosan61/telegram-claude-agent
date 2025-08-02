#!/usr/bin/env python3
"""
🔑 Добавление OpenAI API ключа в DigitalOcean App Platform
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class DOOpenAIUpdater:
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
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.openai_key:
            print("❌ OPENAI_API_KEY не найден в переменных окружения")
            exit(1)
        
        print(f"🎯 Целевое приложение: {self.app_id}")
        print(f"🔑 OpenAI ключ найден: {self.openai_key[:20]}...")
    
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
    
    def add_openai_key(self):
        """Добавление OpenAI ключа в переменные окружения"""
        try:
            # Получение текущей спецификации
            app = self.get_app_spec()
            if not app:
                return False
            
            spec = app['spec'].copy()
            
            # Обновление переменных окружения
            if 'envs' not in spec:
                spec['envs'] = []
            
            # Добавление OpenAI ключа
            openai_var = {
                "key": "OPENAI_API_KEY",
                "value": self.openai_key,
                "scope": "RUN_AND_BUILD_TIME"
            }
            
            # Проверяем, есть ли уже такая переменная
            existing_var_index = None
            for i, env_var in enumerate(spec['envs']):
                if env_var['key'] == 'OPENAI_API_KEY':
                    existing_var_index = i
                    break
            
            if existing_var_index is not None:
                # Обновляем существующую переменную
                spec['envs'][existing_var_index] = openai_var
                print("✅ Переменная OPENAI_API_KEY обновлена")
            else:
                # Добавляем новую переменную
                spec['envs'].append(openai_var)
                print("✅ Переменная OPENAI_API_KEY добавлена")
            
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
            print(f"❌ Ошибка добавления OpenAI ключа: {e}")
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
                    
                    # Проверяем environment endpoint
                    try:
                        import time
                        time.sleep(5)  # Ждем обновления
                        env_response = requests.get(f"{live_url}/environment/check", timeout=10)
                        if env_response.status_code == 200:
                            env_data = env_response.json()
                            openai_available = env_data.get('ai_providers', {}).get('openai', False)
                            if openai_available:
                                print("🎉 OPENAI API КЛЮЧ АКТИВИРОВАН УСПЕШНО!")
                            else:
                                print("⚠️ OpenAI ключ не обнаружен, проверьте логи")
                    except:
                        print("⚠️ Не удалось проверить environment endpoint")
            
            elif phase in ['BUILDING', 'DEPLOYING']:
                print("⏳ Деплой в процессе, подождите...")
            elif phase == 'ERROR':
                print("❌ Ошибка деплоя, проверьте логи в Dashboard")
            
        except Exception as e:
            print(f"❌ Ошибка проверки статуса: {e}")

def main():
    print("🔑 ДОБАВЛЕНИЕ OPENAI API КЛЮЧА В APP PLATFORM")
    print("=" * 60)
    
    updater = DOOpenAIUpdater()
    
    print("🔄 Добавление OpenAI ключа...")
    success = updater.add_openai_key()
    
    if success:
        print("\n✅ OpenAI ключ добавлен успешно!")
        print("⏳ Ожидание завершения автодеплоя (это может занять 2-3 минуты)...")
        
        # Ожидание и проверка статуса
        import time
        for i in range(4):  # Проверяем 4 раза с интервалом 30 секунд
            time.sleep(30)
            print(f"\n📊 Проверка #{i+1}/4...")
            updater.check_deployment_status()
            
            # Проверяем, завершился ли деплой
            app = updater.get_app_spec()
            if app and app.get('active_deployment', {}).get('phase') == 'ACTIVE':
                break
        
        print("\n🎯 ФИНАЛЬНАЯ ПРОВЕРКА:")
        print("=" * 30)
        updater.check_deployment_status()
        
    else:
        print("\n❌ Ошибка добавления OpenAI ключа")

if __name__ == "__main__":
    main()