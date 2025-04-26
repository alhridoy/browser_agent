import os
import json
import time
import datetime
from typing import Dict, Any, List, Optional, Union
import logging
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("memory")

class Memory:
    """
    Memory for storing conversation history and context.
    """
    
    def __init__(self, memory_id: str, data: Dict[str, Any] = None):
        """
        Initialize a memory.
        
        Args:
            memory_id: The unique ID of the memory.
            data: The initial data for the memory.
        """
        self.memory_id = memory_id
        self.data = data or {}
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the memory.
        
        Args:
            key: The key to get.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The value for the key, or the default value if the key doesn't exist.
        """
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the memory.
        
        Args:
            key: The key to set.
            value: The value to set.
        """
        self.data[key] = value
        self.updated_at = datetime.datetime.now()
    
    def delete(self, key: str) -> None:
        """
        Delete a key from the memory.
        
        Args:
            key: The key to delete.
        """
        if key in self.data:
            del self.data[key]
            self.updated_at = datetime.datetime.now()
    
    def clear(self) -> None:
        """
        Clear the memory.
        """
        self.data = {}
        self.updated_at = datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory to a dictionary.
        
        Returns:
            A dictionary representation of the memory.
        """
        return {
            "memory_id": self.memory_id,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """
        Create a memory from a dictionary.
        
        Args:
            data: The dictionary representation of the memory.
            
        Returns:
            A Memory object.
        """
        memory = cls(memory_id=data["memory_id"], data=data["data"])
        memory.created_at = datetime.datetime.fromisoformat(data["created_at"])
        memory.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        
        return memory

class ConversationMemory:
    """
    Memory for storing conversation history.
    """
    
    def __init__(self, memory_id: str):
        """
        Initialize a conversation memory.
        
        Args:
            memory_id: The unique ID of the memory.
        """
        self.memory_id = memory_id
        self.messages = []
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None) -> None:
        """
        Add a message to the conversation.
        
        Args:
            role: The role of the message sender (user, assistant, system).
            content: The content of the message.
            metadata: Additional metadata for the message.
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        self.updated_at = datetime.datetime.now()
    
    def get_messages(self, limit: int = None, role: str = None) -> List[Dict[str, Any]]:
        """
        Get messages from the conversation.
        
        Args:
            limit: The maximum number of messages to return.
            role: Filter messages by role.
            
        Returns:
            A list of messages.
        """
        messages = self.messages
        
        if role:
            messages = [m for m in messages if m["role"] == role]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_last_message(self, role: str = None) -> Optional[Dict[str, Any]]:
        """
        Get the last message from the conversation.
        
        Args:
            role: Filter messages by role.
            
        Returns:
            The last message, or None if there are no messages.
        """
        messages = self.get_messages(role=role)
        
        if messages:
            return messages[-1]
        
        return None
    
    def clear(self) -> None:
        """
        Clear the conversation.
        """
        self.messages = []
        self.updated_at = datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the conversation memory to a dictionary.
        
        Returns:
            A dictionary representation of the conversation memory.
        """
        return {
            "memory_id": self.memory_id,
            "messages": self.messages,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMemory':
        """
        Create a conversation memory from a dictionary.
        
        Args:
            data: The dictionary representation of the conversation memory.
            
        Returns:
            A ConversationMemory object.
        """
        memory = cls(memory_id=data["memory_id"])
        memory.messages = data["messages"]
        memory.created_at = datetime.datetime.fromisoformat(data["created_at"])
        memory.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        
        return memory

class MemoryManager:
    """
    Manager for storing and retrieving memories.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the memory manager.
        
        Args:
            data_dir: The directory to store the memories.
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.memories = {}
        self.conversation_memories = {}
        
        # Load memories from disk
        self._load_memories()
        
        logger.info("Initialized memory manager")
    
    def _load_memories(self):
        """
        Load memories from disk.
        """
        # Load regular memories
        memories_dir = os.path.join(self.data_dir, "memories")
        os.makedirs(memories_dir, exist_ok=True)
        
        for filename in os.listdir(memories_dir):
            if filename.endswith(".json"):
                memory_id = os.path.splitext(filename)[0]
                
                try:
                    with open(os.path.join(memories_dir, filename), "r") as f:
                        memory_data = json.load(f)
                    
                    memory = Memory.from_dict(memory_data)
                    self.memories[memory_id] = memory
                except Exception as e:
                    logger.error(f"Error loading memory {memory_id}: {str(e)}")
        
        # Load conversation memories
        conversations_dir = os.path.join(self.data_dir, "conversations")
        os.makedirs(conversations_dir, exist_ok=True)
        
        for filename in os.listdir(conversations_dir):
            if filename.endswith(".json"):
                memory_id = os.path.splitext(filename)[0]
                
                try:
                    with open(os.path.join(conversations_dir, filename), "r") as f:
                        memory_data = json.load(f)
                    
                    memory = ConversationMemory.from_dict(memory_data)
                    self.conversation_memories[memory_id] = memory
                except Exception as e:
                    logger.error(f"Error loading conversation memory {memory_id}: {str(e)}")
        
        logger.info(f"Loaded {len(self.memories)} memories and {len(self.conversation_memories)} conversation memories")
    
    def _save_memory(self, memory: Memory):
        """
        Save a memory to disk.
        
        Args:
            memory: The memory to save.
        """
        memories_dir = os.path.join(self.data_dir, "memories")
        os.makedirs(memories_dir, exist_ok=True)
        
        try:
            with open(os.path.join(memories_dir, f"{memory.memory_id}.json"), "w") as f:
                json.dump(memory.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory {memory.memory_id}: {str(e)}")
    
    def _save_conversation_memory(self, memory: ConversationMemory):
        """
        Save a conversation memory to disk.
        
        Args:
            memory: The conversation memory to save.
        """
        conversations_dir = os.path.join(self.data_dir, "conversations")
        os.makedirs(conversations_dir, exist_ok=True)
        
        try:
            with open(os.path.join(conversations_dir, f"{memory.memory_id}.json"), "w") as f:
                json.dump(memory.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving conversation memory {memory.memory_id}: {str(e)}")
    
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """
        Get a memory by its ID.
        
        Args:
            memory_id: The ID of the memory.
            
        Returns:
            The memory, or None if it doesn't exist.
        """
        return self.memories.get(memory_id)
    
    def create_memory(self, memory_id: str, data: Dict[str, Any] = None) -> Memory:
        """
        Create a new memory.
        
        Args:
            memory_id: The ID of the memory.
            data: The initial data for the memory.
            
        Returns:
            The created memory.
        """
        memory = Memory(memory_id=memory_id, data=data)
        self.memories[memory_id] = memory
        self._save_memory(memory)
        
        return memory
    
    def update_memory(self, memory_id: str, key: str, value: Any) -> Optional[Memory]:
        """
        Update a memory.
        
        Args:
            memory_id: The ID of the memory.
            key: The key to update.
            value: The value to set.
            
        Returns:
            The updated memory, or None if it doesn't exist.
        """
        memory = self.get_memory(memory_id)
        
        if memory:
            memory.set(key, value)
            self._save_memory(memory)
        
        return memory
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: The ID of the memory.
            
        Returns:
            True if the memory was deleted, False otherwise.
        """
        if memory_id in self.memories:
            del self.memories[memory_id]
            
            try:
                os.remove(os.path.join(self.data_dir, "memories", f"{memory_id}.json"))
            except Exception as e:
                logger.error(f"Error deleting memory file for {memory_id}: {str(e)}")
            
            return True
        
        return False
    
    def get_conversation_memory(self, memory_id: str) -> Optional[ConversationMemory]:
        """
        Get a conversation memory by its ID.
        
        Args:
            memory_id: The ID of the conversation memory.
            
        Returns:
            The conversation memory, or None if it doesn't exist.
        """
        return self.conversation_memories.get(memory_id)
    
    def create_conversation_memory(self, memory_id: str) -> ConversationMemory:
        """
        Create a new conversation memory.
        
        Args:
            memory_id: The ID of the conversation memory.
            
        Returns:
            The created conversation memory.
        """
        memory = ConversationMemory(memory_id=memory_id)
        self.conversation_memories[memory_id] = memory
        self._save_conversation_memory(memory)
        
        return memory
    
    def add_message_to_conversation(self, memory_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> Optional[ConversationMemory]:
        """
        Add a message to a conversation memory.
        
        Args:
            memory_id: The ID of the conversation memory.
            role: The role of the message sender (user, assistant, system).
            content: The content of the message.
            metadata: Additional metadata for the message.
            
        Returns:
            The updated conversation memory, or None if it doesn't exist.
        """
        memory = self.get_conversation_memory(memory_id)
        
        if not memory:
            memory = self.create_conversation_memory(memory_id)
        
        memory.add_message(role=role, content=content, metadata=metadata)
        self._save_conversation_memory(memory)
        
        return memory
    
    def delete_conversation_memory(self, memory_id: str) -> bool:
        """
        Delete a conversation memory.
        
        Args:
            memory_id: The ID of the conversation memory.
            
        Returns:
            True if the conversation memory was deleted, False otherwise.
        """
        if memory_id in self.conversation_memories:
            del self.conversation_memories[memory_id]
            
            try:
                os.remove(os.path.join(self.data_dir, "conversations", f"{memory_id}.json"))
            except Exception as e:
                logger.error(f"Error deleting conversation memory file for {memory_id}: {str(e)}")
            
            return True
        
        return False
    
    def get_all_memories(self) -> List[Memory]:
        """
        Get all memories.
        
        Returns:
            A list of all memories.
        """
        return list(self.memories.values())
    
    def get_all_conversation_memories(self) -> List[ConversationMemory]:
        """
        Get all conversation memories.
        
        Returns:
            A list of all conversation memories.
        """
        return list(self.conversation_memories.values())
