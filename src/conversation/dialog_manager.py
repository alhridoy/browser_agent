import os
import json
import time
import datetime
import re
from typing import Dict, Any, List, Optional, Union, Callable
import logging
from src.utils.logger import setup_logger
from src.conversation.memory import MemoryManager, Memory, ConversationMemory
from src.nlp.parser import CommandParser

# Setup logger
logger = setup_logger("dialog_manager")

class DialogManager:
    """
    Manager for handling conversational dialogs.
    """
    
    def __init__(self, memory_manager: MemoryManager = None, command_parser: CommandParser = None):
        """
        Initialize the dialog manager.
        
        Args:
            memory_manager: The memory manager to use.
            command_parser: The command parser to use.
        """
        self.memory_manager = memory_manager or MemoryManager()
        self.command_parser = command_parser or CommandParser()
        self.action_handlers = {}
        
        logger.info("Initialized dialog manager")
    
    def register_action_handler(self, action_type: str, handler: Callable) -> None:
        """
        Register a handler for a specific action type.
        
        Args:
            action_type: The type of action to handle.
            handler: The function to call when the action is triggered.
        """
        self.action_handlers[action_type] = handler
        logger.info(f"Registered handler for action type: {action_type}")
    
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_id: The ID of the user.
            message: The message from the user.
            
        Returns:
            A dictionary containing the response and any actions to perform.
        """
        try:
            logger.info(f"Processing message from user {user_id}: {message}")
            
            # Get or create the conversation memory for the user
            conversation_memory = self.memory_manager.get_conversation_memory(user_id)
            
            if not conversation_memory:
                conversation_memory = self.memory_manager.create_conversation_memory(user_id)
            
            # Add the user message to the conversation
            self.memory_manager.add_message_to_conversation(user_id, "user", message)
            
            # Get or create the user memory
            user_memory = self.memory_manager.get_memory(user_id)
            
            if not user_memory:
                user_memory = self.memory_manager.create_memory(user_id)
            
            # Parse the message to extract actions
            actions = self.command_parser.parse(message)
            
            # Execute the actions
            results = []
            
            for action in actions:
                action_type = action.get("type")
                
                if action_type in self.action_handlers:
                    try:
                        result = await self.action_handlers[action_type](action, user_memory, conversation_memory)
                        results.append({
                            "action": action,
                            "result": result
                        })
                    except Exception as e:
                        logger.error(f"Error executing action {action_type}: {str(e)}")
                        results.append({
                            "action": action,
                            "error": str(e)
                        })
                else:
                    logger.warning(f"No handler registered for action type: {action_type}")
                    results.append({
                        "action": action,
                        "error": f"No handler registered for action type: {action_type}"
                    })
            
            # Generate a response based on the results
            response = self._generate_response(results, user_memory, conversation_memory)
            
            # Add the assistant response to the conversation
            self.memory_manager.add_message_to_conversation(user_id, "assistant", response)
            
            return {
                "user_id": user_id,
                "message": message,
                "response": response,
                "actions": actions,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            
            # Add an error response to the conversation
            error_response = f"I'm sorry, but I encountered an error while processing your message: {str(e)}"
            self.memory_manager.add_message_to_conversation(user_id, "assistant", error_response)
            
            return {
                "user_id": user_id,
                "message": message,
                "response": error_response,
                "error": str(e)
            }
    
    def _generate_response(self, results: List[Dict[str, Any]], user_memory: Memory, conversation_memory: ConversationMemory) -> str:
        """
        Generate a response based on the results of executing actions.
        
        Args:
            results: The results of executing actions.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The generated response.
        """
        # Check if all actions were successful
        all_successful = all(result.get("result", {}).get("success", False) for result in results if "error" not in result)
        
        if not results:
            # No actions were executed
            return "I'm not sure what you want me to do. Could you please be more specific?"
        elif all_successful:
            # All actions were successful
            response = "I've completed the tasks you requested."
            
            # Add details about each action
            for result in results:
                action = result.get("action", {})
                action_result = result.get("result", {})
                
                if action.get("type") == "navigate":
                    response += f"\n- Navigated to {action.get('url')}"
                elif action.get("type") == "click":
                    response += f"\n- Clicked on {action.get('element')}"
                elif action.get("type") == "type":
                    response += f"\n- Typed '{action.get('text')}' into {action.get('element')}"
                elif action.get("type") == "search":
                    response += f"\n- Searched for '{action.get('query')}' on {action.get('site')}"
                elif action.get("type") == "extract":
                    response += f"\n- Extracted data from {action.get('selector')}"
                    
                    # Add a sample of the extracted data
                    data = action_result.get("data")
                    if data:
                        if isinstance(data, str):
                            sample = data[:100] + "..." if len(data) > 100 else data
                            response += f"\n  Sample: {sample}"
                        elif isinstance(data, list):
                            sample = data[:3]
                            response += f"\n  Sample: {sample}"
                        elif isinstance(data, dict):
                            sample = list(data.items())[:3]
                            response += f"\n  Sample: {sample}"
        else:
            # Some actions failed
            response = "I encountered some issues while trying to complete your requests."
            
            # Add details about each action
            for result in results:
                action = result.get("action", {})
                action_result = result.get("result", {})
                error = result.get("error")
                
                if error:
                    response += f"\n- Failed to {action.get('type')}: {error}"
                elif not action_result.get("success", False):
                    response += f"\n- Failed to {action.get('type')}: {action_result.get('message', 'Unknown error')}"
                else:
                    if action.get("type") == "navigate":
                        response += f"\n- Successfully navigated to {action.get('url')}"
                    elif action.get("type") == "click":
                        response += f"\n- Successfully clicked on {action.get('element')}"
                    elif action.get("type") == "type":
                        response += f"\n- Successfully typed '{action.get('text')}' into {action.get('element')}"
                    elif action.get("type") == "search":
                        response += f"\n- Successfully searched for '{action.get('query')}' on {action.get('site')}"
                    elif action.get("type") == "extract":
                        response += f"\n- Successfully extracted data from {action.get('selector')}"
        
        return response
    
    def get_conversation_history(self, user_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a user.
        
        Args:
            user_id: The ID of the user.
            limit: The maximum number of messages to return.
            
        Returns:
            A list of messages in the conversation.
        """
        conversation_memory = self.memory_manager.get_conversation_memory(user_id)
        
        if conversation_memory:
            return conversation_memory.get_messages(limit=limit)
        
        return []
    
    def clear_conversation_history(self, user_id: str) -> bool:
        """
        Clear the conversation history for a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            True if the conversation history was cleared, False otherwise.
        """
        conversation_memory = self.memory_manager.get_conversation_memory(user_id)
        
        if conversation_memory:
            conversation_memory.clear()
            return True
        
        return False
    
    def get_user_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the memory for a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            The user's memory, or None if it doesn't exist.
        """
        memory = self.memory_manager.get_memory(user_id)
        
        if memory:
            return memory.data
        
        return None
    
    def update_user_memory(self, user_id: str, key: str, value: Any) -> bool:
        """
        Update the memory for a user.
        
        Args:
            user_id: The ID of the user.
            key: The key to update.
            value: The value to set.
            
        Returns:
            True if the memory was updated, False otherwise.
        """
        memory = self.memory_manager.get_memory(user_id)
        
        if memory:
            memory.set(key, value)
            return True
        
        return False
    
    def clear_user_memory(self, user_id: str) -> bool:
        """
        Clear the memory for a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            True if the memory was cleared, False otherwise.
        """
        memory = self.memory_manager.get_memory(user_id)
        
        if memory:
            memory.clear()
            return True
        
        return False
