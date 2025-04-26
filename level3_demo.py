import os
import asyncio
import json
import time
import datetime
import uuid
import argparse
from src.level3.agent import BrowserAgent
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

async def run_demo():
    """
    Run a comprehensive demo of the Level 3 browser automation agent.
    """
    try:
        print("\n=== Level 3 Browser Automation Agent Demo ===")
        
        # Initialize the browser agent
        agent = BrowserAgent()
        
        # Generate a unique user ID for this demo
        user_id = str(uuid.uuid4())
        print(f"User ID: {user_id}")
        
        # Step 1: Demonstrate conversational interface
        print("\n1. Demonstrating conversational interface")
        
        # First message
        print("\nUser: Hello, can you help me search for something on Google?")
        response = await agent.process_message(user_id, "Hello, can you help me search for something on Google?")
        print(f"Agent: {response['response']}")
        
        # Second message with context from the first
        print("\nUser: Yes, please search for 'browser automation' on Google")
        response = await agent.process_message(user_id, "Yes, please search for 'browser automation' on Google")
        print(f"Agent: {response['response']}")
        
        # Wait for the search to complete
        await asyncio.sleep(5)
        
        # Third message with memory
        print("\nUser: Remember this search query for later")
        response = await agent.process_message(user_id, "Remember this search query for later")
        print(f"Agent: {response['response']}")
        
        # Fourth message referencing memory
        print("\nUser: What was the search query I asked you to remember?")
        response = await agent.process_message(user_id, "What was the search query I asked you to remember?")
        print(f"Agent: {response['response']}")
        
        # Step 2: Demonstrate scheduled tasks
        print("\n2. Demonstrating scheduled tasks")
        
        # Schedule a task to run every minute
        task_id = str(uuid.uuid4())
        task_name = "Demo Task"
        
        print(f"\nScheduling a task to navigate to GitHub every minute (Task ID: {task_id})")
        
        success = agent.schedule_task(
            task_id=task_id,
            name=task_name,
            actions=[
                {
                    "type": "navigate",
                    "url": "https://github.com"
                }
            ],
            schedule_type="interval",
            interval=60,  # 1 minute
            max_runs=2  # Run at most twice
        )
        
        if success:
            print(f"✓ Successfully scheduled task: {task_name}")
        else:
            print(f"✗ Failed to schedule task: {task_name}")
        
        # Get all scheduled tasks
        tasks = agent.get_scheduled_tasks()
        print(f"\nScheduled tasks: {len(tasks)}")
        
        for task in tasks:
            print(f"- {task['name']} (ID: {task['task_id']})")
            print(f"  Schedule: {task['schedule_type']}, Interval: {task['interval']} seconds")
            print(f"  Next run: {task['next_run']}")
        
        # Run the task immediately
        print(f"\nRunning task immediately: {task_name}")
        result = agent.run_task(task_id)
        
        if result:
            print(f"✓ Task executed successfully")
        else:
            print(f"✗ Failed to execute task")
        
        # Step 3: Demonstrate cross-platform compatibility
        print("\n3. Demonstrating cross-platform compatibility")
        
        # Get platform information
        platform_adapter = agent.platform_adapter
        system_info = platform_adapter.get_system_info()
        
        print(f"\nRunning on: {system_info['system']} {system_info['release']} ({system_info['machine']})")
        print(f"Python version: {system_info['python_version']}")
        
        if 'screen_width' in system_info and 'screen_height' in system_info:
            print(f"Screen resolution: {system_info['screen_width']}x{system_info['screen_height']}")
        
        # Step 4: Demonstrate contextual intelligence
        print("\n4. Demonstrating contextual intelligence")
        
        # First command
        print("\nUser: Go to Google")
        response = await agent.process_message(user_id, "Go to Google")
        print(f"Agent: {response['response']}")
        
        # Wait for navigation to complete
        await asyncio.sleep(3)
        
        # Second command with implicit context
        print("\nUser: Now search for Python programming")
        response = await agent.process_message(user_id, "Now search for Python programming")
        print(f"Agent: {response['response']}")
        
        # Wait for the search to complete
        await asyncio.sleep(3)
        
        # Third command with implicit context
        print("\nUser: Scroll down to see more results")
        response = await agent.process_message(user_id, "Scroll down to see more results")
        print(f"Agent: {response['response']}")
        
        # Wait for scrolling to complete
        await asyncio.sleep(3)
        
        # Get conversation history
        conversation = agent.dialog_manager.get_conversation_history(user_id)
        print(f"\nConversation history: {len(conversation)} messages")
        
        # Get user memory
        memory = agent.dialog_manager.get_user_memory(user_id)
        print(f"\nUser memory: {memory}")
        
        print("\n=== Demo completed successfully ===")
        print("\nLevel 3 capabilities demonstrated:")
        print("✓ Conversational interface with context maintenance")
        print("✓ Scheduled tasks and automated workflows")
        print("✓ Cross-platform compatibility")
        print("✓ Contextual intelligence for multi-turn interactions")
        
        # Clean up
        agent.stop()
        
    except Exception as e:
        logger.error(f"Error running demo: {str(e)}")
        print(f"Error running demo: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Level 3 Browser Automation Agent Demo")
    
    args = parser.parse_args()
    
    # Install required packages if they're not already installed
    try:
        import schedule
    except ImportError:
        print("Installing required packages...")
        os.system("pip install schedule")
    
    # Run the demo
    asyncio.run(run_demo())
