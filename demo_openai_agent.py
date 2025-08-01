#!/usr/bin/env python3
"""
🎯 Демонстрация работы Telegram агента с OpenAI
Показывает полный цикл обработки сообщений без необходимости Telegram авторизации
"""
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from utils.openai.client import OpenAIClient

class OpenAIAgentDemo:
    def __init__(self):
        self.openai_client = None
        
    async def run_demo(self):
        """Запуск демонстрации работы агента"""
        print("🎯 Демонстрация Telegram агента с OpenAI")
        print("=" * 60)
        
        # Инициализация OpenAI клиента
        if not await self.init_openai_client():
            return
        
        # Демо-кампания для тестирования
        demo_campaign = self.create_demo_campaign()
        print(f"📋 Создана демо-кампания: {demo_campaign.name}")
        print(f"🤖 AI провайдер: {demo_campaign.ai_provider}")
        print(f"🧠 Модель: {demo_campaign.openai_model}")
        print()
        
        # Симуляция различных сценариев
        await self.test_scenario_1(demo_campaign)
        await self.test_scenario_2(demo_campaign)
        await self.test_scenario_3(demo_campaign)
        
        print("\n" + "=" * 60)
        print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print("✅ OpenAI успешно интегрирован в Telegram агента")
        print("💡 Агент может обрабатывать сообщения и генерировать ответы через OpenAI")
    
    async def init_openai_client(self):
        """Инициализация OpenAI клиента"""
        try:
            self.openai_client = OpenAIClient()
            print("✅ OpenAI клиент инициализирован")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации OpenAI: {e}")
            return False
    
    def create_demo_campaign(self):
        """Создание демо-кампании"""
        # Имитируем объект Campaign
        class DemoCampaign:
            def __init__(self):
                self.id = 1
                self.name = "Демо: OpenAI помощник"
                self.ai_provider = "openai"
                self.openai_model = "gpt-3.5-turbo"  # Используем более дешевую модель
                self.claude_agent_id = None
                self.system_instruction = """
Ты полезный AI ассистент в Telegram канале о программировании.
Твоя задача - помогать пользователям с вопросами по Python, JavaScript и веб-разработке.
Отвечай кратко, но информативно. Используй примеры кода когда это уместно.
Будь дружелюбным и профессиональным.
                """.strip()
                self.example_replies = {
                    "python": "Вот пример кода на Python:",
                    "ошибка": "Давайте разберем эту ошибку:",
                    "помощь": "Конечно, помогу разобраться!"
                }
                self.keywords = ["ии", "бот", "помощь", "python", "javascript", "ошибка"]
                self.context_messages_count = 3
        
        return DemoCampaign()
    
    async def test_scenario_1(self, campaign):
        """Сценарий 1: Простой вопрос о Python"""
        print("🧪 СЦЕНАРИЙ 1: Простой вопрос о Python")
        print("-" * 40)
        
        # Имитируем контекст предыдущих сообщений
        context_messages = [
            {"date": "2024-08-01 14:30:00", "text": "Привет всем!"},
            {"date": "2024-08-01 14:31:00", "text": "Изучаю программирование"},
            {"date": "2024-08-01 14:32:00", "text": "Python кажется интересным языком"}
        ]
        
        trigger_message = "ии помоги с изучением Python для начинающих"
        
        print(f"💬 Триггерное сообщение: {trigger_message}")
        print(f"📝 Контекст: {len(context_messages)} предыдущих сообщений")
        
        # Генерируем ответ
        response = await self.generate_response_for_campaign(
            campaign, trigger_message, context_messages
        )
        
        print(f"🤖 Ответ OpenAI:")
        print(f"   {response}")
        print()
    
    async def test_scenario_2(self, campaign):
        """Сценарий 2: Вопрос об ошибке в коде"""
        print("🧪 СЦЕНАРИЙ 2: Вопрос об ошибке в коде")
        print("-" * 40)
        
        context_messages = [
            {"date": "2024-08-01 14:35:00", "text": "Пишу свой первый скрипт"},
            {"date": "2024-08-01 14:36:00", "text": "print('Hello World)"},
            {"date": "2024-08-01 14:37:00", "text": "Выдает какую-то ошибку"}
        ]
        
        trigger_message = "бот помоги, ошибка SyntaxError: unterminated string literal"
        
        print(f"💬 Триггерное сообщение: {trigger_message}")
        
        response = await self.generate_response_for_campaign(
            campaign, trigger_message, context_messages
        )
        
        print(f"🤖 Ответ OpenAI:")
        print(f"   {response}")
        print()
    
    async def test_scenario_3(self, campaign):
        """Сценарий 3: Запрос примера кода"""
        print("🧪 СЦЕНАРИЙ 3: Запрос примера кода")
        print("-" * 40)
        
        context_messages = [
            {"date": "2024-08-01 14:40:00", "text": "Хочу изучить работу с файлами"},
            {"date": "2024-08-01 14:41:00", "text": "Нужно читать CSV файлы"},
            {"date": "2024-08-01 14:42:00", "text": "И обрабатывать данные"}
        ]
        
        trigger_message = "ии покажи пример кода для чтения CSV файла на Python"
        
        print(f"💬 Триггерное сообщение: {trigger_message}")
        
        response = await self.generate_response_for_campaign(
            campaign, trigger_message, context_messages
        )
        
        print(f"🤖 Ответ OpenAI:")
        print(f"   {response}")
        print()
    
    async def generate_response_for_campaign(self, campaign, trigger_message, context_messages):
        """Генерация ответа для кампании (имитация работы агента)"""
        
        # Используем тот же подход что и в реальном агенте
        prompt = self.openai_client.format_telegram_context(
            system_instruction=campaign.system_instruction,
            context_messages=context_messages,
            trigger_message=trigger_message,
            example_replies=campaign.example_replies
        )
        
        # Генерируем ответ
        response = await self.openai_client.generate_response(
            prompt=prompt,
            model=campaign.openai_model,
            max_tokens=300,
            temperature=0.7
        )
        
        return response

async def main():
    """Главная функция"""
    print("🎯 OpenAI Agent Demo")
    print("Демонстрация работы Telegram агента с OpenAI без авторизации")
    print()
    
    # Проверка API ключа
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY не найден в переменных окружения")
        print("💡 Добавьте ключ в .env файл для тестирования")
        return
    
    demo = OpenAIAgentDemo()
    await demo.run_demo()
    
    print("\n🚀 ЧТО ДАЛЬШЕ?")
    print("1. Выполните Telegram авторизацию: python complete_setup.py")
    print("2. Создайте кампанию с ai_provider='openai' в веб-интерфейсе")
    print("3. Запустите backend сервер: python run.py")
    print("4. Агент будет использовать OpenAI для генерации ответов!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Демонстрация прервана")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()