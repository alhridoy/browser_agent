import os
import time
import json
import threading
import schedule
import datetime
from typing import Dict, Any, List, Optional, Callable, Union
import logging
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("task_scheduler")

class Task:
    """
    Represents a scheduled task.
    """
    
    def __init__(self, task_id: str, name: str, function: Callable, args: List = None, kwargs: Dict = None, 
                 schedule_type: str = "interval", interval: int = 60, cron: str = None, 
                 start_time: datetime.datetime = None, end_time: datetime.datetime = None,
                 max_runs: int = None, enabled: bool = True):
        """
        Initialize a task.
        
        Args:
            task_id: The unique ID of the task.
            name: The name of the task.
            function: The function to execute.
            args: Positional arguments for the function.
            kwargs: Keyword arguments for the function.
            schedule_type: The type of schedule ("interval", "cron", "once").
            interval: The interval in seconds (for "interval" schedule type).
            cron: The cron expression (for "cron" schedule type).
            start_time: The start time (for "once" schedule type).
            end_time: The end time after which the task will be disabled.
            max_runs: The maximum number of times to run the task.
            enabled: Whether the task is enabled.
        """
        self.task_id = task_id
        self.name = name
        self.function = function
        self.args = args or []
        self.kwargs = kwargs or {}
        self.schedule_type = schedule_type
        self.interval = interval
        self.cron = cron
        self.start_time = start_time
        self.end_time = end_time
        self.max_runs = max_runs
        self.enabled = enabled
        self.run_count = 0
        self.last_run = None
        self.next_run = None
        self.job = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary.
        
        Returns:
            A dictionary representation of the task.
        """
        return {
            "task_id": self.task_id,
            "name": self.name,
            "schedule_type": self.schedule_type,
            "interval": self.interval,
            "cron": self.cron,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "max_runs": self.max_runs,
            "enabled": self.enabled,
            "run_count": self.run_count,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], function: Callable, args: List = None, kwargs: Dict = None) -> 'Task':
        """
        Create a task from a dictionary.
        
        Args:
            data: The dictionary representation of the task.
            function: The function to execute.
            args: Positional arguments for the function.
            kwargs: Keyword arguments for the function.
            
        Returns:
            A Task object.
        """
        task = cls(
            task_id=data["task_id"],
            name=data["name"],
            function=function,
            args=args or [],
            kwargs=kwargs or {},
            schedule_type=data["schedule_type"],
            interval=data["interval"],
            cron=data["cron"],
            start_time=datetime.datetime.fromisoformat(data["start_time"]) if data["start_time"] else None,
            end_time=datetime.datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            max_runs=data["max_runs"],
            enabled=data["enabled"]
        )
        
        task.run_count = data["run_count"]
        task.last_run = datetime.datetime.fromisoformat(data["last_run"]) if data["last_run"] else None
        task.next_run = datetime.datetime.fromisoformat(data["next_run"]) if data["next_run"] else None
        
        return task
    
    def run(self) -> Any:
        """
        Run the task.
        
        Returns:
            The result of the function.
        """
        if not self.enabled:
            logger.info(f"Task {self.task_id} ({self.name}) is disabled")
            return None
        
        # Check if the task has reached its maximum number of runs
        if self.max_runs is not None and self.run_count >= self.max_runs:
            logger.info(f"Task {self.task_id} ({self.name}) has reached its maximum number of runs")
            self.enabled = False
            return None
        
        # Check if the task has reached its end time
        if self.end_time is not None and datetime.datetime.now() > self.end_time:
            logger.info(f"Task {self.task_id} ({self.name}) has reached its end time")
            self.enabled = False
            return None
        
        logger.info(f"Running task {self.task_id} ({self.name})")
        
        try:
            result = self.function(*self.args, **self.kwargs)
            
            self.run_count += 1
            self.last_run = datetime.datetime.now()
            
            # Calculate the next run time
            if self.schedule_type == "interval":
                self.next_run = self.last_run + datetime.timedelta(seconds=self.interval)
            elif self.schedule_type == "cron":
                # For cron schedules, the next run time is calculated by the scheduler
                pass
            elif self.schedule_type == "once":
                self.next_run = None
                self.enabled = False
            
            logger.info(f"Task {self.task_id} ({self.name}) completed successfully")
            
            return result
        except Exception as e:
            logger.error(f"Error running task {self.task_id} ({self.name}): {str(e)}")
            return None

class TaskScheduler:
    """
    Scheduler for running tasks at specified intervals.
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the task scheduler.
        
        Args:
            config_dir: The directory to store the task configuration.
        """
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "config")
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.tasks = {}
        self.running = False
        self.thread = None
        
        # Load tasks from the configuration file
        self._load_tasks()
        
        logger.info("Initialized task scheduler")
    
    def _load_tasks(self):
        """
        Load tasks from the configuration file.
        """
        config_file = os.path.join(self.config_dir, "tasks.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    tasks_data = json.load(f)
                
                for task_data in tasks_data:
                    # Skip tasks that don't have a function registered
                    if task_data["task_id"] not in self.tasks:
                        continue
                    
                    # Update the task with the saved configuration
                    task = self.tasks[task_data["task_id"]]
                    task.enabled = task_data["enabled"]
                    task.run_count = task_data["run_count"]
                    task.last_run = datetime.datetime.fromisoformat(task_data["last_run"]) if task_data["last_run"] else None
                    task.next_run = datetime.datetime.fromisoformat(task_data["next_run"]) if task_data["next_run"] else None
                
                logger.info(f"Loaded {len(tasks_data)} tasks from configuration")
            except Exception as e:
                logger.error(f"Error loading tasks: {str(e)}")
    
    def _save_tasks(self):
        """
        Save tasks to the configuration file.
        """
        config_file = os.path.join(self.config_dir, "tasks.json")
        
        try:
            tasks_data = [task.to_dict() for task in self.tasks.values()]
            
            with open(config_file, "w") as f:
                json.dump(tasks_data, f, indent=2)
            
            logger.info(f"Saved {len(tasks_data)} tasks to configuration")
        except Exception as e:
            logger.error(f"Error saving tasks: {str(e)}")
    
    def add_task(self, task: Task) -> bool:
        """
        Add a task to the scheduler.
        
        Args:
            task: The task to add.
            
        Returns:
            True if the task was added successfully, False otherwise.
        """
        try:
            # Check if a task with the same ID already exists
            if task.task_id in self.tasks:
                logger.warning(f"Task {task.task_id} already exists")
                return False
            
            self.tasks[task.task_id] = task
            
            # Schedule the task
            self._schedule_task(task)
            
            # Save the tasks to the configuration file
            self._save_tasks()
            
            logger.info(f"Added task {task.task_id} ({task.name})")
            
            return True
        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from the scheduler.
        
        Args:
            task_id: The ID of the task to remove.
            
        Returns:
            True if the task was removed successfully, False otherwise.
        """
        try:
            # Check if the task exists
            if task_id not in self.tasks:
                logger.warning(f"Task {task_id} does not exist")
                return False
            
            # Get the task
            task = self.tasks[task_id]
            
            # Cancel the scheduled job
            if task.job:
                schedule.cancel_job(task.job)
            
            # Remove the task
            del self.tasks[task_id]
            
            # Save the tasks to the configuration file
            self._save_tasks()
            
            logger.info(f"Removed task {task_id} ({task.name})")
            
            return True
        except Exception as e:
            logger.error(f"Error removing task: {str(e)}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by its ID.
        
        Args:
            task_id: The ID of the task.
            
        Returns:
            The task, or None if it doesn't exist.
        """
        return self.tasks.get(task_id)
    
    def get_tasks(self) -> List[Task]:
        """
        Get all tasks.
        
        Returns:
            A list of all tasks.
        """
        return list(self.tasks.values())
    
    def enable_task(self, task_id: str) -> bool:
        """
        Enable a task.
        
        Args:
            task_id: The ID of the task to enable.
            
        Returns:
            True if the task was enabled successfully, False otherwise.
        """
        try:
            # Check if the task exists
            if task_id not in self.tasks:
                logger.warning(f"Task {task_id} does not exist")
                return False
            
            # Get the task
            task = self.tasks[task_id]
            
            # Enable the task
            task.enabled = True
            
            # Reschedule the task
            self._schedule_task(task)
            
            # Save the tasks to the configuration file
            self._save_tasks()
            
            logger.info(f"Enabled task {task_id} ({task.name})")
            
            return True
        except Exception as e:
            logger.error(f"Error enabling task: {str(e)}")
            return False
    
    def disable_task(self, task_id: str) -> bool:
        """
        Disable a task.
        
        Args:
            task_id: The ID of the task to disable.
            
        Returns:
            True if the task was disabled successfully, False otherwise.
        """
        try:
            # Check if the task exists
            if task_id not in self.tasks:
                logger.warning(f"Task {task_id} does not exist")
                return False
            
            # Get the task
            task = self.tasks[task_id]
            
            # Disable the task
            task.enabled = False
            
            # Cancel the scheduled job
            if task.job:
                schedule.cancel_job(task.job)
                task.job = None
            
            # Save the tasks to the configuration file
            self._save_tasks()
            
            logger.info(f"Disabled task {task_id} ({task.name})")
            
            return True
        except Exception as e:
            logger.error(f"Error disabling task: {str(e)}")
            return False
    
    def _schedule_task(self, task: Task) -> bool:
        """
        Schedule a task.
        
        Args:
            task: The task to schedule.
            
        Returns:
            True if the task was scheduled successfully, False otherwise.
        """
        try:
            # Cancel the existing job if it exists
            if task.job:
                schedule.cancel_job(task.job)
                task.job = None
            
            # Skip scheduling if the task is disabled
            if not task.enabled:
                logger.info(f"Task {task.task_id} ({task.name}) is disabled, skipping scheduling")
                return True
            
            # Schedule the task based on its type
            if task.schedule_type == "interval":
                task.job = schedule.every(task.interval).seconds.do(task.run)
                task.next_run = datetime.datetime.now() + datetime.timedelta(seconds=task.interval)
            elif task.schedule_type == "cron":
                # Parse the cron expression
                cron_parts = task.cron.split()
                
                if len(cron_parts) != 5:
                    logger.error(f"Invalid cron expression: {task.cron}")
                    return False
                
                minute, hour, day, month, day_of_week = cron_parts
                
                # Schedule the task
                job = schedule.every()
                
                if minute != "*":
                    job = job.at(f"{hour.zfill(2)}:{minute.zfill(2)}")
                else:
                    job = job.hour.at(f":{minute.zfill(2)}")
                
                if day != "*":
                    job = job.day.at(f"{hour.zfill(2)}:{minute.zfill(2)}")
                
                if month != "*":
                    # Not directly supported by schedule, would need custom logic
                    pass
                
                if day_of_week != "*":
                    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                    day_index = int(day_of_week) % 7  # 0 = Monday in cron
                    job = getattr(schedule.every(), days[day_index]).at(f"{hour.zfill(2)}:{minute.zfill(2)}")
                
                task.job = job.do(task.run)
                
                # Calculate the next run time
                # This is a simplified calculation and may not be accurate for all cron expressions
                now = datetime.datetime.now()
                next_run = now.replace(minute=int(minute) if minute != "*" else now.minute,
                                      hour=int(hour) if hour != "*" else now.hour,
                                      day=int(day) if day != "*" else now.day,
                                      month=int(month) if month != "*" else now.month)
                
                if next_run <= now:
                    next_run = next_run + datetime.timedelta(days=1)
                
                task.next_run = next_run
            elif task.schedule_type == "once":
                if task.start_time and task.start_time > datetime.datetime.now():
                    # Calculate the delay in seconds
                    delay = (task.start_time - datetime.datetime.now()).total_seconds()
                    
                    # Schedule the task to run once after the delay
                    task.job = schedule.every(delay).seconds.do(task.run)
                    task.next_run = task.start_time
                else:
                    # Run the task immediately
                    task.run()
                    task.next_run = None
                    task.enabled = False
            
            logger.info(f"Scheduled task {task.task_id} ({task.name})")
            
            return True
        except Exception as e:
            logger.error(f"Error scheduling task: {str(e)}")
            return False
    
    def start(self):
        """
        Start the scheduler.
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        
        # Schedule all tasks
        for task in self.tasks.values():
            self._schedule_task(task)
        
        # Start the scheduler thread
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Started scheduler")
    
    def stop(self):
        """
        Stop the scheduler.
        """
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        self.running = False
        
        # Wait for the scheduler thread to finish
        if self.thread:
            self.thread.join(timeout=1)
            self.thread = None
        
        # Save the tasks to the configuration file
        self._save_tasks()
        
        logger.info("Stopped scheduler")
    
    def _run_scheduler(self):
        """
        Run the scheduler loop.
        """
        while self.running:
            try:
                # Run pending tasks
                schedule.run_pending()
                
                # Sleep for a short time
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(5)  # Sleep for a longer time if there's an error
    
    def run_task(self, task_id: str) -> Any:
        """
        Run a task immediately.
        
        Args:
            task_id: The ID of the task to run.
            
        Returns:
            The result of the task, or None if the task doesn't exist or fails.
        """
        try:
            # Check if the task exists
            if task_id not in self.tasks:
                logger.warning(f"Task {task_id} does not exist")
                return None
            
            # Get the task
            task = self.tasks[task_id]
            
            # Run the task
            result = task.run()
            
            # Save the tasks to the configuration file
            self._save_tasks()
            
            return result
        except Exception as e:
            logger.error(f"Error running task: {str(e)}")
            return None
