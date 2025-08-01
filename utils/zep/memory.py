import os
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

try:
    from zep_python import ZepClient, Message, Memory
    ZEP_AVAILABLE = True
except ImportError:
    ZEP_AVAILABLE = False
    print("⚠️ Zep-python не установлен. Используется локальное хранение памяти.")


class ZepMemoryManager:
    """
    Менеджер долгосрочной памяти через Zep Cloud
    """
    
    def __init__(self):
        self.api_key = os.getenv("ZEP_API_KEY")
        self.api_url = os.getenv("ZEP_API_URL", "https://api.getzep.com")
        
        # Инициализация клиента
        if ZEP_AVAILABLE and self.api_key:
            try:
                self.client = ZepClient(
                    api_key=self.api_key,
                    api_url=self.api_url
                )
                self.enabled = True
                print("🧠 Zep Memory Manager инициализирован")
            except Exception as e:
                print(f"❌ Ошибка инициализации Zep: {e}")
                self.enabled = False
                self._init_local_storage()
        else:
            self.enabled = False
            self._init_local_storage()
    
    def _init_local_storage(self):
        """Инициализация локального хранения памяти"""
        self.local_memory = {}
        self.memory_file = "local_memory.json"
        self._load_local_memory()
        print("💾 Используется локальное хранение памяти")
    
    def _load_local_memory(self):
        """Загрузка локальной памяти из файла"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.local_memory = json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки локальной памяти: {e}")
            self.local_memory = {}
    
    def _save_local_memory(self):
        """Сохранение локальной памяти в файл"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.local_memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения локальной памяти: {e}")
    
    async def add_interaction(
        self,
        session_id: str,
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Добавление взаимодействия в память"""
        try:
            if self.enabled:
                return await self._add_interaction_zep(session_id, message, response, metadata)
            else:
                return await self._add_interaction_local(session_id, message, response, metadata)
        except Exception as e:
            print(f"❌ Ошибка добавления взаимодействия: {e}")
            return False
    
    async def _add_interaction_zep(
        self,
        session_id: str,
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Добавление взаимодействия через Zep"""
        try:
            messages = [
                Message(
                    role="user",
                    content=message,
                    metadata=metadata or {}
                ),
                Message(
                    role="assistant",
                    content=response,
                    metadata=metadata or {}
                )
            ]
            
            # Добавление в память
            await asyncio.to_thread(
                self.client.memory.add_memory,
                session_id=session_id,
                memory=Memory(messages=messages)
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка Zep add_memory: {e}")
            return False
    
    async def _add_interaction_local(
        self,
        session_id: str,
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Добавление взаимодействия в локальную память"""
        try:
            if session_id not in self.local_memory:
                self.local_memory[session_id] = {
                    "messages": [],
                    "created_at": datetime.utcnow().isoformat()
                }
            
            # Добавление сообщений
            timestamp = datetime.utcnow().isoformat()
            
            self.local_memory[session_id]["messages"].extend([
                {
                    "role": "user",
                    "content": message,
                    "timestamp": timestamp,
                    "metadata": metadata or {}
                },
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": timestamp,
                    "metadata": metadata or {}
                }
            ])
            
            # Ограничение размера истории (последние 100 сообщений)
            if len(self.local_memory[session_id]["messages"]) > 100:
                self.local_memory[session_id]["messages"] = \
                    self.local_memory[session_id]["messages"][-100:]
            
            # Сохранение в файл
            await asyncio.to_thread(self._save_local_memory)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка локального сохранения: {e}")
            return False
    
    async def get_memory(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Получение истории памяти"""
        try:
            if self.enabled:
                return await self._get_memory_zep(session_id, limit)
            else:
                return await self._get_memory_local(session_id, limit)
        except Exception as e:
            print(f"❌ Ошибка получения памяти: {e}")
            return []
    
    async def _get_memory_zep(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Получение памяти через Zep"""
        try:
            memory = await asyncio.to_thread(
                self.client.memory.get_memory,
                session_id=session_id
            )
            
            if memory and memory.messages:
                messages = []
                for msg in memory.messages[-limit:]:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content,
                        "metadata": msg.metadata,
                        "timestamp": msg.created_at.isoformat() if msg.created_at else None
                    })
                return messages
            
            return []
            
        except Exception as e:
            print(f"❌ Ошибка Zep get_memory: {e}")
            return []
    
    async def _get_memory_local(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Получение локальной памяти"""
        try:
            if session_id in self.local_memory:
                messages = self.local_memory[session_id]["messages"]
                return messages[-limit:] if messages else []
            
            return []
            
        except Exception as e:
            print(f"❌ Ошибка получения локальной памяти: {e}")
            return []
    
    async def get_session_summary(self, session_id: str) -> Optional[str]:
        """Получение сводки сессии"""
        try:
            if self.enabled:
                return await self._get_session_summary_zep(session_id)
            else:
                return await self._get_session_summary_local(session_id)
        except Exception as e:
            print(f"❌ Ошибка получения сводки: {e}")
            return None
    
    async def _get_session_summary_zep(self, session_id: str) -> Optional[str]:
        """Получение сводки через Zep"""
        try:
            memory = await asyncio.to_thread(
                self.client.memory.get_memory,
                session_id=session_id
            )
            
            if memory and memory.summary:
                return memory.summary.content
            
            return None
            
        except Exception as e:
            print(f"❌ Ошибка Zep get_summary: {e}")
            return None
    
    async def _get_session_summary_local(self, session_id: str) -> Optional[str]:
        """Получение локальной сводки"""
        try:
            if session_id in self.local_memory:
                messages = self.local_memory[session_id]["messages"]
                if len(messages) > 5:
                    # Простая сводка на основе количества сообщений
                    user_messages = len([m for m in messages if m["role"] == "user"])
                    assistant_messages = len([m for m in messages if m["role"] == "assistant"])
                    
                    return f"Сессия содержит {user_messages} сообщений пользователя и {assistant_messages} ответов ассистента."
            
            return None
            
        except Exception as e:
            print(f"❌ Ошибка локальной сводки: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Удаление сессии"""
        try:
            if self.enabled:
                return await self._delete_session_zep(session_id)
            else:
                return await self._delete_session_local(session_id)
        except Exception as e:
            print(f"❌ Ошибка удаления сессии: {e}")
            return False
    
    async def _delete_session_zep(self, session_id: str) -> bool:
        """Удаление сессии через Zep"""
        try:
            await asyncio.to_thread(
                self.client.memory.delete_memory,
                session_id=session_id
            )
            return True
            
        except Exception as e:
            print(f"❌ Ошибка Zep delete_memory: {e}")
            return False
    
    async def _delete_session_local(self, session_id: str) -> bool:
        """Удаление локальной сессии"""
        try:
            if session_id in self.local_memory:
                del self.local_memory[session_id]
                await asyncio.to_thread(self._save_local_memory)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка удаления локальной сессии: {e}")
            return False
    
    async def search_memory(
        self,
        session_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Поиск в памяти"""
        try:
            if self.enabled:
                return await self._search_memory_zep(session_id, query, limit)
            else:
                return await self._search_memory_local(session_id, query, limit)
        except Exception as e:
            print(f"❌ Ошибка поиска в памяти: {e}")
            return []
    
    async def _search_memory_zep(
        self,
        session_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Поиск через Zep"""
        try:
            results = await asyncio.to_thread(
                self.client.memory.search_memory,
                session_id=session_id,
                text=query,
                limit=limit
            )
            
            if results:
                messages = []
                for result in results:
                    if result.message:
                        messages.append({
                            "role": result.message.role,
                            "content": result.message.content,
                            "score": result.score,
                            "metadata": result.message.metadata
                        })
                return messages
            
            return []
            
        except Exception as e:
            print(f"❌ Ошибка Zep search: {e}")
            return []
    
    async def _search_memory_local(
        self,
        session_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Локальный поиск"""
        try:
            if session_id not in self.local_memory:
                return []
            
            messages = self.local_memory[session_id]["messages"]
            results = []
            
            query_lower = query.lower()
            
            for msg in messages:
                if query_lower in msg["content"].lower():
                    results.append({
                        "role": msg["role"],
                        "content": msg["content"],
                        "score": 1.0,  # Простая оценка
                        "metadata": msg.get("metadata", {}),
                        "timestamp": msg.get("timestamp")
                    })
            
            return results[-limit:]  # Последние совпадения
            
        except Exception as e:
            print(f"❌ Ошибка локального поиска: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера памяти"""
        status = {
            "enabled": self.enabled,
            "backend": "zep" if self.enabled else "local",
            "api_url": self.api_url if self.enabled else None
        }
        
        if not self.enabled:
            status["local_sessions"] = len(self.local_memory)
            total_messages = sum(
                len(session["messages"]) 
                for session in self.local_memory.values()
            )
            status["total_messages"] = total_messages
        
        return status