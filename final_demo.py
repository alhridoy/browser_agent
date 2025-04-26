import asyncio
import argparse
import json
import time
from src.browser.controller import BrowserController
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

async def run_demo(headless: bool = False, slow_mo: int = 50):
    """
    Run a final demo of the browser automation agent.
    
    Args:
        headless: Whether to run the browser in headless mode.
        slow_mo: How much to slow down browser operations (in ms).
    """
    try:
        # Initialize the browser controller
        browser_controller = BrowserController(
            headless=headless,
            slow_mo=slow_mo
        )
        
        print("\n=== Browser Automation Agent Demo ===")
        
        # Demo 1: Search on Google
        print("\n1. Searching on Google for 'browser automation'")
        actions = [
            {
                "type": "search",
                "site": "Google",
                "query": "browser automation"
            }
        ]
        
        result = await browser_controller.execute(actions)
        if result["results"][0]["result"]["success"]:
            print("✅ Successfully searched on Google")
        else:
            print("❌ Failed to search on Google")
        
        # Wait a bit to see the results
        time.sleep(3)
        
        # Demo 2: Navigate to GitHub
        print("\n2. Navigating to GitHub")
        actions = [
            {
                "type": "navigate",
                "url": "https://github.com"
            }
        ]
        
        result = await browser_controller.execute(actions)
        if result["results"][0]["result"]["success"]:
            print("✅ Successfully navigated to GitHub")
        else:
            print("❌ Failed to navigate to GitHub")
        
        # Wait a bit to see the results
        time.sleep(3)
        
        # Demo 3: Search on GitHub
        print("\n3. Searching on GitHub for 'browser automation'")
        actions = [
            {
                "type": "click",
                "element": "button[data-target='qbsearch-input.inputButton']"
            },
            {
                "type": "type",
                "element": "input[id='query-builder-test']",
                "text": "browser automation"
            },
            {
                "type": "press",
                "element": "input[id='query-builder-test']",
                "key": "Enter"
            }
        ]
        
        result = await browser_controller.execute(actions)
        if all(action["result"]["success"] for action in result["results"]):
            print("✅ Successfully searched on GitHub")
        else:
            print("❌ Failed to search on GitHub")
        
        # Wait a bit to see the results
        time.sleep(3)
        
        # Close the browser
        await browser_controller.close()
        
        print("\n=== Demo completed successfully ===")
    except Exception as e:
        logger.error(f"Error running demo: {str(e)}")
        print(f"Error running demo: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Browser Automation Agent Final Demo")
    parser.add_argument("--headless", action="store_true", help="Run the browser in headless mode")
    parser.add_argument("--slow-mo", type=int, default=50, help="Slow down browser operations by the specified amount (in ms)")
    
    args = parser.parse_args()
    
    asyncio.run(run_demo(headless=args.headless, slow_mo=args.slow_mo))
