import os
import asyncio
from typing import Optional, Dict, Any, List
import json

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIClient:
    """
    Клиент для работы с OpenAI API
    Альтернатива Claude для генерации ответов в Telegram агенте
    """
    
    def __init__(self):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library не установлена. Установите: pip install openai")
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY не найден в переменных окружения")
        
        # Инициализация OpenAI клиента
        self.client = OpenAI(api_key=self.api_key)
        
        # Настройки по умолчанию
        self.default_model = "gpt-4"
        self.fallback_model = "gpt-3.5-turbo"
        
        print("🤖 OpenAI Client инициализирован")
    
    async def generate_response(
        self,
        prompt: str,
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Генерация ответа через OpenAI API
        
        Args:
            prompt: Промпт для генерации
            agent_id: ID агента (игнорируется для OpenAI)
            model: Модель OpenAI (gpt-4, gpt-3.5-turbo)
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации (0.0-2.0)
        """
        try:
            # Определяем модель
            selected_model = model or self.default_model
            
            # Генерация ответа
            response = await self._generate_with_openai_api(
                prompt, selected_model, max_tokens, temperature
            )
            
            return response
            
        except Exception as e:
            print(f"❌ Ошибка генерации ответа OpenAI: {e}")
            
            # Попытка с резервной моделью
            if model != self.fallback_model:
                try:
                    print(f"🔄 Попытка с резервной моделью {self.fallback_model}")
                    return await self._generate_with_openai_api(
                        prompt, self.fallback_model, max_tokens, temperature
                    )
                except Exception as fallback_error:
                    print(f"❌ Ошибка резервной модели: {fallback_error}")
            
            # Возвращаем стандартный ответ об ошибке
            return "Извините, произошла ошибка при генерации ответа."
    
    async def _generate_with_openai_api(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Генерация через прямой API OpenAI"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Ошибка OpenAI API: {e}")
            raise
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Завершение чата с историей сообщений
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}]
            model: Модель OpenAI
            max_tokens: Максимальное количество токенов
            temperature: Температура генерации
        """
        try:
            selected_model = model or self.default_model
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=selected_model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Ошибка chat completion OpenAI: {e}")
            
            # Попробуем с резервной моделью
            if model != self.fallback_model:
                try:
                    response = await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.fallback_model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=messages
                    )
                    return response.choices[0].message.content.strip()
                except:
                    pass
            
            raise
    
    def test_connection(self) -> bool:
        """Тестирование соединения с OpenAI"""
        try:
            # Простой тест
            response = self.client.chat.completions.create(
                model=self.fallback_model,  # Используем более дешевую модель для теста
                max_tokens=5,
                messages=[
                    {
                        "role": "user",
                        "content": "Hi"
                    }
                ]
            )
            
            return len(response.choices) > 0 and response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Ошибка тестирования соединения OpenAI: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Получение списка доступных моделей"""
        return [
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
    
    async def create_agent_session(self, session_id: str, system_prompt: str) -> Dict[str, Any]:
        """Создание сессии агента для контекстного общения"""
        return {
            "session_id": session_id,
            "system_prompt": system_prompt,
            "messages": [],
            "created_at": asyncio.get_event_loop().time(),
            "provider": "openai"
        }
    
    async def add_message_to_session(
        self,
        session_id: str,
        role: str,
        content: str,
        sessions_storage: Dict[str, Dict]
    ):
        """Добавление сообщения в сессию"""
        if session_id in sessions_storage:
            sessions_storage[session_id]["messages"].append({
                "role": role,
                "content": content
            })
    
    async def generate_from_session(
        self,
        session_id: str,
        sessions_storage: Dict[str, Dict],
        model: Optional[str] = None
    ) -> str:
        """Генерация ответа из сессии с контекстом"""
        if session_id not in sessions_storage:
            raise ValueError(f"Сессия {session_id} не найдена")
        
        session = sessions_storage[session_id]
        
        # Формирование сообщений с системным промптом
        messages = []
        
        if session["system_prompt"]:
            messages.append({
                "role": "system",
                "content": session["system_prompt"]
            })
        
        messages.extend(session["messages"])
        
        # Генерация ответа
        response = await self.chat_completion(messages, model)
        
        # Добавление ответа в сессию
        await self.add_message_to_session(
            session_id, "assistant", response, sessions_storage
        )
        
        return response
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Получение информации о модели"""
        model_info = {
            "gpt-4": {
                "name": "GPT-4",
                "max_tokens": 8192,
                "cost_per_1k": 0.03,
                "description": "Самая мощная модель OpenAI"
            },
            "gpt-4-turbo-preview": {
                "name": "GPT-4 Turbo Preview",
                "max_tokens": 128000,
                "cost_per_1k": 0.01,
                "description": "Улучшенная версия GPT-4 с большим контекстом"
            },
            "gpt-3.5-turbo": {
                "name": "GPT-3.5 Turbo",
                "max_tokens": 4096,
                "cost_per_1k": 0.002,
                "description": "Быстрая и экономичная модель"
            },
            "gpt-3.5-turbo-16k": {
                "name": "GPT-3.5 Turbo 16K",
                "max_tokens": 16384,
                "cost_per_1k": 0.004,
                "description": "GPT-3.5 с расширенным контекстом"
            }
        }
        
        return model_info.get(model, {
            "name": model,
            "max_tokens": 4096,
            "cost_per_1k": 0.002,
            "description": "Неизвестная модель"
        })
    
    async def estimate_tokens(self, text: str) -> int:
        """Приблизительная оценка количества токенов"""
        # Простая оценка: ~4 символа = 1 токен для английского
        # Для русского текста коэффициент может быть выше
        return len(text) // 3  # Консервативная оценка для многоязычного текста
    
    def format_telegram_context(
        self,
        system_instruction: str,
        context_messages: List[Dict],
        trigger_message: str,
        example_replies: Optional[str] = None
    ) -> str:
        """
        Форматирование контекста для OpenAI в стиле Telegram агента
        Аналогично тому, как это делается для Claude
        """
        
        # Формирование контекста предыдущих сообщений
        context_text = ""
        if context_messages:
            context_text = "\n".join([
                f"[{msg.get('date', 'Unknown')}] {msg.get('text', '')}" 
                for msg in context_messages
            ])
        
        # Примеры ответов
        examples_text = ""
        if example_replies:
            examples_text = f"\n\nПримеры ответов: {example_replies}"
        
        # Итоговый промпт
        prompt = f"""Системная инструкция: {system_instruction}

Контекст предыдущих сообщений:
{context_text}

Сообщение-триггер: {trigger_message}{examples_text}

Сгенерируй подходящий ответ на основе контекста и системной инструкции. Ответ должен быть естественным и соответствовать тону беседы."""

        return prompt