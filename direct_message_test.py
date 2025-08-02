#!/usr/bin/env python3
"""
Прямой тест отправки сообщения в группу обсуждений
"""
import asyncio
import os
import sys
sys.path.append('.')

from backend.core.telegram_agent_app_platform import get_telegram_agent

async def send_direct_test():
    """Отправить тестовое сообщение напрямую в группу обсуждений"""
    print("🔄 Подключение к агенту...")
    
    try:
        agent = await get_telegram_agent()
        
        if not agent or not agent.is_authorized:
            print("❌ Агент не авторизован")
            return False
        
        print("✅ Агент подключен")
        
        # ID группы обсуждений
        discussion_group_id = 2532661483
        
        # Получаем информацию о группе
        try:
            discussion_entity = await agent.client.get_entity(discussion_group_id)
            print(f"📋 Группа: {getattr(discussion_entity, 'title', 'Unknown')}")
            print(f"🔒 Тип: {type(discussion_entity)}")
            
            # Пробуем отправить тестовое сообщение
            test_message = "🤖 ПРЯМОЙ ТЕСТ: Это сообщение отправлено для проверки работы бота"
            
            print(f"📝 Отправка тестового сообщения...")
            
            result = await agent.client.send_message(
                entity=discussion_entity,
                message=test_message
            )
            
            print(f"✅ Сообщение отправлено! ID: {result.id}")
            print(f"📊 Дата: {result.date}")
            
            return True
            
        except Exception as send_error:
            print(f"❌ Ошибка отправки: {send_error}")
            print(f"📋 Тип ошибки: {type(send_error).__name__}")
            
            # Попробуем проверить права в группе
            try:
                # Получаем последние сообщения для проверки доступа
                messages_count = 0
                async for message in agent.client.iter_messages(discussion_entity, limit=3):
                    messages_count += 1
                    print(f"   📝 Сообщение {messages_count}: {message.text[:50] if message.text else 'No text'}")
                
                print(f"📊 Доступ к чтению: ✅ ({messages_count} сообщений)")
                print(f"📊 Доступ к отправке: ❌ (ошибка выше)")
                
            except Exception as read_error:
                print(f"❌ Нет доступа к чтению: {read_error}")
            
            return False
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

async def check_comment_format():
    """Проверить формат последних сообщений в группе"""
    print("\n🔍 Анализ формата сообщений в группе...")
    
    try:
        agent = await get_telegram_agent()
        discussion_group_id = 2532661483
        discussion_entity = await agent.client.get_entity(discussion_group_id)
        
        print("📊 Последние 5 сообщений:")
        message_count = 0
        
        async for message in agent.client.iter_messages(discussion_entity, limit=5):
            message_count += 1
            is_reply = hasattr(message, 'reply_to_msg_id') and message.reply_to_msg_id is not None
            
            print(f"\n💬 Сообщение {message_count}:")
            print(f"   📝 Текст: '{message.text[:100] if message.text else 'None'}'")
            print(f"   👤 От: {message.sender_id}")
            print(f"   🔗 Reply to: {getattr(message, 'reply_to_msg_id', None)}")
            print(f"   💬 Это комментарий: {is_reply}")
            print(f"   📅 Дата: {message.date}")
            
            # Проверим, есть ли ключевые слова
            if message.text:
                keywords = ["тест", "задача", "вопрос", "помощь", "claude"]
                found_keywords = [kw for kw in keywords if kw.lower() in message.text.lower()]
                if found_keywords:
                    print(f"   🔑 Найдены ключевые слова: {found_keywords}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return False

async def main():
    """Основная функция теста"""
    print("🧪 ПРЯМОЙ ТЕСТ ОТПРАВКИ СООБЩЕНИЙ")
    print("=" * 50)
    
    # Установка переменных окружения
    os.environ['TELEGRAM_API_ID'] = '29071357'
    os.environ['TELEGRAM_API_HASH'] = 'e5bb33acb28c91b50e63d86a3c3b8c1f'
    os.environ['TELEGRAM_SESSION_STRING'] = '1BVtsOKIBu0YAdpG6lpPEYFaYt4K5ZUBn1N05dOcJIwZLApCJZ8PLyE1tXFcg90LQO51vyuQ94KgTfxKzCZj6PawgQT4_LLGOhiJhiGaWyN9jZ_x1WP2M7YNyoGcJLY3B9dP_kWm9_T1K_xT0A9FQ2SnLzVZZq9MhQQ5EJo_yJ9H9J_N8KfOzzCdyYW0mOjEo5VjLVR85T3N5J9OzJ1D9b_Oj5hJIaYE9_7KY9oyDYX0vJ05Z0K2n_Yh4yTfkNZKyDHyyYJ0dN5jOQ8f9FGyJ-Z1T9oJKIzXo0VJqYJyJTzLn3Q8iHKLY0j9YRGDDzYj1yJ-Q9YmKHh8Y3Yo_o-V8n2T-JKYn3Q2_nJiY9nQo1lnYxXl2QZEk9HJKyKGJJx_8F2LoDxOcT9xYmJ1hJOzOGhK9iVJ8Y9hYGJQJKOH9K9j8Y2XYznIJhJJ5xhJqJJJl2TYqHI3YqAJ9mOJJ0z9o9FKyEY3hXJ0mIn9Q4Y9D8QmKjY0o1z5OcGYTJqJoJlJK2K-JJ30o-1Y1JOhYo_JJ='
    
    # Тест 1: Прямая отправка
    print("\n=== ТЕСТ 1: ПРЯМАЯ ОТПРАВКА ===")
    success = await send_direct_test()
    
    # Тест 2: Анализ формата сообщений
    print("\n=== ТЕСТ 2: АНАЛИЗ СООБЩЕНИЙ ===")
    await check_comment_format()
    
    print("\n🎯 РЕЗУЛЬТАТ:")
    if success:
        print("✅ Бот МОЖЕТ отправлять сообщения в группу")
        print("💡 Если вы не видите ответов, возможно:")
        print("   1. Комментарии приходят в другом формате")
        print("   2. События комментариев не регистрируются")
        print("   3. Проблема с timing - ответы приходят с задержкой")
    else:
        print("❌ Бот НЕ МОЖЕТ отправлять сообщения в группу")
        print("💡 Нужно проверить права доступа")

if __name__ == "__main__":
    asyncio.run(main())