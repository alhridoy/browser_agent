import asyncio
import argparse
import json
from src.nlp.parser import CommandParser
from src.browser.controller import BrowserController
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

async def main():
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(description="Browser Automation Agent CLI")
    parser.add_argument("command", help="The natural language command to execute")
    parser.add_argument("--headless", action="store_true", help="Run the browser in headless mode")
    parser.add_argument("--slow-mo", type=int, default=50, help="Slow down browser operations by the specified amount (in ms)")
    
    args = parser.parse_args()
    
    try:
        # Parse the command
        command_parser = CommandParser()
        actions = command_parser.parse(args.command)
        
        logger.info(f"Parsed actions: {json.dumps(actions, indent=2)}")
        
        # Execute the actions
        browser_controller = BrowserController(
            headless=args.headless,
            slow_mo=args.slow_mo
        )
        
        result = await browser_controller.execute(actions)
        
        logger.info(f"Execution result: {json.dumps(result, indent=2)}")
        
        # Close the browser
        await browser_controller.close()
        
        return result
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return {
            "success": False,
            "message": f"Error executing command: {str(e)}"
        }

if __name__ == "__main__":
    asyncio.run(main())
