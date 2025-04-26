import os
import asyncio
import datetime
import uuid
from typing import Dict, Any, List, Optional, Union, Callable
import logging
from src.utils.logger import setup_logger
from src.native.platform_adapter import PlatformAdapter
from src.native.controller import NativeBrowserController
from src.native.extractor import DataExtractor
from src.native.config import BrowserConfig
from src.conversation.memory import MemoryManager
from src.conversation.dialog_manager import DialogManager
from src.scheduler.task_scheduler import TaskScheduler, Task
from src.nlp.parser import CommandParser

# Setup logger
logger = setup_logger("agent")

class BrowserAgent:
    """
    Level 3 browser automation agent with contextual intelligence and advanced workflows.
    """
    
    def __init__(self, agent_id: str = None, config_dir: str = None, data_dir: str = None):
        """
        Initialize the browser agent.
        
        Args:
            agent_id: The unique ID of the agent.
            config_dir: The directory to store configuration files.
            data_dir: The directory to store data files.
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        
        # Initialize platform adapter
        self.platform_adapter = PlatformAdapter()
        
        # Set up directories
        self.config_dir = config_dir or self.platform_adapter.get_config_directory("browser_agent")
        self.data_dir = data_dir or self.platform_adapter.get_data_directory("browser_agent")
        
        # Initialize components
        self.memory_manager = MemoryManager(data_dir=os.path.join(self.data_dir, "memory"))
        self.command_parser = CommandParser()
        self.dialog_manager = DialogManager(memory_manager=self.memory_manager, command_parser=self.command_parser)
        self.task_scheduler = TaskScheduler(config_dir=os.path.join(self.config_dir, "scheduler"))
        
        # Initialize browser components
        self.browser_config = BrowserConfig("chrome")
        self.browser_controller = None
        self.data_extractor = DataExtractor()
        
        # Register action handlers
        self._register_action_handlers()
        
        # Start the scheduler
        self.task_scheduler.start()
        
        logger.info(f"Initialized browser agent with ID: {self.agent_id}")
    
    def _register_action_handlers(self):
        """
        Register handlers for different action types.
        """
        self.dialog_manager.register_action_handler("navigate", self._handle_navigate)
        self.dialog_manager.register_action_handler("click", self._handle_click)
        self.dialog_manager.register_action_handler("type", self._handle_type)
        self.dialog_manager.register_action_handler("search", self._handle_search)
        self.dialog_manager.register_action_handler("login", self._handle_login)
        self.dialog_manager.register_action_handler("scroll", self._handle_scroll)
        self.dialog_manager.register_action_handler("wait", self._handle_wait)
        self.dialog_manager.register_action_handler("press", self._handle_press)
        self.dialog_manager.register_action_handler("extract", self._handle_extract)
        self.dialog_manager.register_action_handler("schedule", self._handle_schedule)
        self.dialog_manager.register_action_handler("remember", self._handle_remember)
        self.dialog_manager.register_action_handler("recall", self._handle_recall)
        self.dialog_manager.register_action_handler("forget", self._handle_forget)
    
    async def _get_browser_controller(self) -> NativeBrowserController:
        """
        Get or create a browser controller.
        
        Returns:
            A NativeBrowserController instance.
        """
        if not self.browser_controller:
            self.browser_controller = NativeBrowserController(
                browser_name=self.browser_config.browser_name,
                headless=False,
                slow_mo=50
            )
            
            # Launch the browser
            await self.browser_controller.launch_browser()
        
        return self.browser_controller
    
    async def _handle_navigate(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a navigate action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        browser_controller = await self._get_browser_controller()
        
        result = await browser_controller.execute([action])
        
        return result["results"][0]["result"]
    
    async def _handle_click(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a click action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        browser_controller = await self._get_browser_controller()
        
        result = await browser_controller.execute([action])
        
        return result["results"][0]["result"]
    
    async def _handle_type(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a type action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        browser_controller = await self._get_browser_controller()
        
        result = await browser_controller.execute([action])
        
        return result["results"][0]["result"]
    
    async def _handle_search(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a search action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        browser_controller = await self._get_browser_controller()
        
        result = await browser_controller.execute([action])
        
        return result["results"][0]["result"]
    
    async def _handle_login(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a login action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        browser_controller = await self._get_browser_controller()
        
        result = await browser_controller.execute([action])
        
        return result["results"][0]["result"]
    
    async def _handle_scroll(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a scroll action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        browser_controller = await self._get_browser_controller()
        
        result = await browser_controller.execute([action])
        
        return result["results"][0]["result"]
    
    async def _handle_wait(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a wait action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        browser_controller = await self._get_browser_controller()
        
        result = await browser_controller.execute([action])
        
        return result["results"][0]["result"]
    
    async def _handle_press(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a press action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        browser_controller = await self._get_browser_controller()
        
        result = await browser_controller.execute([action])
        
        return result["results"][0]["result"]
    
    async def _handle_extract(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle an extract action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        extraction_type = action.get("extraction_type", "ocr")
        params = action.get("params", {})
        
        result = await self.data_extractor.extract(extraction_type, params)
        
        return result
    
    async def _handle_schedule(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a schedule action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        task_id = action.get("task_id") or str(uuid.uuid4())
        name = action.get("name") or f"Task {task_id}"
        schedule_type = action.get("schedule_type", "interval")
        interval = action.get("interval", 3600)  # Default: 1 hour
        cron = action.get("cron")
        start_time_str = action.get("start_time")
        end_time_str = action.get("end_time")
        max_runs = action.get("max_runs")
        actions = action.get("actions", [])
        
        # Parse start and end times
        start_time = None
        if start_time_str:
            try:
                start_time = datetime.datetime.fromisoformat(start_time_str)
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid start time format: {start_time_str}"
                }
        
        end_time = None
        if end_time_str:
            try:
                end_time = datetime.datetime.fromisoformat(end_time_str)
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid end time format: {end_time_str}"
                }
        
        # Create a function to execute the actions
        async def execute_actions():
            browser_controller = await self._get_browser_controller()
            return await browser_controller.execute(actions)
        
        # Create the task
        task = Task(
            task_id=task_id,
            name=name,
            function=execute_actions,
            schedule_type=schedule_type,
            interval=interval,
            cron=cron,
            start_time=start_time,
            end_time=end_time,
            max_runs=max_runs,
            enabled=True
        )
        
        # Add the task to the scheduler
        success = self.task_scheduler.add_task(task)
        
        if success:
            return {
                "success": True,
                "message": f"Scheduled task {task_id} ({name})",
                "task_id": task_id
            }
        else:
            return {
                "success": False,
                "message": f"Failed to schedule task {task_id} ({name})"
            }
    
    async def _handle_remember(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a remember action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        key = action.get("key")
        value = action.get("value")
        
        if not key:
            return {
                "success": False,
                "message": "No key specified for remember action"
            }
        
        user_memory.set(key, value)
        
        return {
            "success": True,
            "message": f"Remembered {key}: {value}"
        }
    
    async def _handle_recall(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a recall action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        key = action.get("key")
        
        if not key:
            return {
                "success": False,
                "message": "No key specified for recall action"
            }
        
        value = user_memory.get(key)
        
        if value is None:
            return {
                "success": False,
                "message": f"No memory found for key: {key}"
            }
        
        return {
            "success": True,
            "message": f"Recalled {key}: {value}",
            "value": value
        }
    
    async def _handle_forget(self, action: Dict[str, Any], user_memory: Any, conversation_memory: Any) -> Dict[str, Any]:
        """
        Handle a forget action.
        
        Args:
            action: The action to handle.
            user_memory: The user's memory.
            conversation_memory: The conversation memory.
            
        Returns:
            The result of the action.
        """
        key = action.get("key")
        
        if not key:
            return {
                "success": False,
                "message": "No key specified for forget action"
            }
        
        user_memory.delete(key)
        
        return {
            "success": True,
            "message": f"Forgot {key}"
        }
    
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_id: The ID of the user.
            message: The message from the user.
            
        Returns:
            A dictionary containing the response and any actions performed.
        """
        return await self.dialog_manager.process_message(user_id, message)
    
    def schedule_task(self, task_id: str, name: str, actions: List[Dict[str, Any]], 
                     schedule_type: str = "interval", interval: int = 3600, cron: str = None, 
                     start_time: datetime.datetime = None, end_time: datetime.datetime = None,
                     max_runs: int = None) -> bool:
        """
        Schedule a task to be executed periodically.
        
        Args:
            task_id: The unique ID of the task.
            name: The name of the task.
            actions: The actions to execute.
            schedule_type: The type of schedule ("interval", "cron", "once").
            interval: The interval in seconds (for "interval" schedule type).
            cron: The cron expression (for "cron" schedule type).
            start_time: The start time (for "once" schedule type).
            end_time: The end time after which the task will be disabled.
            max_runs: The maximum number of times to run the task.
            
        Returns:
            True if the task was scheduled successfully, False otherwise.
        """
        # Create a function to execute the actions
        async def execute_actions():
            browser_controller = await self._get_browser_controller()
            return await browser_controller.execute(actions)
        
        # Create the task
        task = Task(
            task_id=task_id,
            name=name,
            function=execute_actions,
            schedule_type=schedule_type,
            interval=interval,
            cron=cron,
            start_time=start_time,
            end_time=end_time,
            max_runs=max_runs,
            enabled=True
        )
        
        # Add the task to the scheduler
        return self.task_scheduler.add_task(task)
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all scheduled tasks.
        
        Returns:
            A list of scheduled tasks.
        """
        tasks = self.task_scheduler.get_tasks()
        return [task.to_dict() for task in tasks]
    
    def run_task(self, task_id: str) -> Any:
        """
        Run a task immediately.
        
        Args:
            task_id: The ID of the task to run.
            
        Returns:
            The result of the task.
        """
        return self.task_scheduler.run_task(task_id)
    
    def stop(self):
        """
        Stop the agent and clean up resources.
        """
        # Stop the scheduler
        self.task_scheduler.stop()
        
        # Close the browser
        if self.browser_controller:
            asyncio.create_task(self.browser_controller.close_browser())
        
        logger.info("Stopped browser agent")
