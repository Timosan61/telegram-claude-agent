import os
import asyncio
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile
import json

from anthropic import Anthropic


class ClaudeClient:
    """
    Клиент для работы с Claude Code SDK и Anthropic API
    """
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY не найден в переменных окружения")
        
        # Инициализация Anthropic клиента
        self.anthropic = Anthropic(api_key=self.api_key)
        
        # Путь к Claude Code CLI (если установлен)
        self.claude_code_path = self._find_claude_code_cli()
        
        print("🧠 Claude Client инициализирован")
    
    def _find_claude_code_cli(self) -> Optional[str]:
        """Поиск Claude Code CLI в системе"""
        try:
            result = subprocess.run(["which", "claude"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        # Проверка стандартных путей
        possible_paths = [
            "/usr/local/bin/claude",
            "/usr/bin/claude",
            "~/.local/bin/claude",
            "claude"  # В PATH
        ]
        
        for path in possible_paths:
            expanded_path = Path(path).expanduser()
            if expanded_path.exists():
                return str(expanded_path)
        
        return None
    
    async def generate_response(
        self,
        prompt: str,
        agent_id: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Генерация ответа через Claude Code SDK или Anthropic API
        """
        try:
            # Попытка использовать Claude Code CLI
            if self.claude_code_path and agent_id:
                return await self._generate_with_claude_code(prompt, agent_id)
            
            # Fallback на прямой API Anthropic
            return await self._generate_with_anthropic_api(
                prompt, model, max_tokens, temperature
            )
            
        except Exception as e:
            print(f"❌ Ошибка генерации ответа: {e}")
            # Резервный простой ответ
            return "Извините, произошла ошибка при генерации ответа."
    
    async def _generate_with_claude_code(self, prompt: str, agent_id: str) -> str:
        """Генерация через Claude Code CLI"""
        try:
            # Создание временного файла с промптом
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_file = f.name
            
            # Команда Claude Code
            cmd = [
                self.claude_code_path,
                "--agent", agent_id,
                "--file", temp_file,
                "--output", "text"
            ]
            
            # Выполнение команды
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Удаление временного файла
            os.unlink(temp_file)
            
            if process.returncode == 0:
                return stdout.decode().strip()
            else:
                print(f"❌ Ошибка Claude Code CLI: {stderr.decode()}")
                raise Exception(f"Claude Code CLI error: {stderr.decode()}")
                
        except Exception as e:
            print(f"❌ Ошибка выполнения Claude Code CLI: {e}")
            raise
    
    async def _generate_with_anthropic_api(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Генерация через прямой API Anthropic"""
        try:
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
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
            
            return response.content[0].text
            
        except Exception as e:
            print(f"❌ Ошибка Anthropic API: {e}")
            raise
    
    async def chat_completion(
        self,
        messages: list,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Завершение чата с историей сообщений"""
        try:
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"❌ Ошибка chat completion: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Тестирование соединения с Claude"""
        try:
            # Простой тест через Anthropic API
            response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=10,
                messages=[
                    {
                        "role": "user",
                        "content": "Hi"
                    }
                ]
            )
            
            return len(response.content) > 0
            
        except Exception as e:
            print(f"❌ Ошибка тестирования соединения: {e}")
            return False
    
    def get_available_models(self) -> list:
        """Получение списка доступных моделей"""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    async def create_agent_session(self, session_id: str, system_prompt: str) -> Dict[str, Any]:
        """Создание сессии агента для контекстного общения"""
        return {
            "session_id": session_id,
            "system_prompt": system_prompt,
            "messages": [],
            "created_at": asyncio.get_event_loop().time()
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
        model: str = "claude-3-sonnet-20240229"
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