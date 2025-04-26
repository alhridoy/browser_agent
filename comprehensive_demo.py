import asyncio
import argparse
import json
import time
from src.nlp.parser import CommandParser
from src.browser.controller import BrowserController
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

async def run_demo(headless: bool = False, slow_mo: int = 50):
    """
    Run a comprehensive demo of the browser automation agent.

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

        # Demo 1: Search on Google
        print("\n=== Demo 1: Search on Google ===")
        print("Command: Go to Google and search for 'browser automation'")

        actions = [
            {
                "type": "search",
                "site": "Google",
                "query": "browser automation"
            }
        ]

        print(f"Actions: {json.dumps(actions, indent=2)}")

        result = await browser_controller.execute(actions)
        print(f"Result: {json.dumps(result, indent=2)}")

        # Wait a bit to see the results
        time.sleep(3)

        # Demo 2: Click on a search result
        print("\n=== Demo 2: Click on a search result ===")
        print("Command: Click on the first search result")

        actions = [
            {
                "type": "click",
                "element": "a h3"
            }
        ]

        print(f"Actions: {json.dumps(actions, indent=2)}")

        result = await browser_controller.execute(actions)
        print(f"Result: {json.dumps(result, indent=2)}")

        # Wait a bit to see the results
        time.sleep(3)

        # Demo 3: Navigate to GitHub
        print("\n=== Demo 3: Navigate to GitHub ===")
        print("Command: Go to github.com")

        actions = [
            {
                "type": "navigate",
                "url": "https://github.com"
            }
        ]

        print(f"Actions: {json.dumps(actions, indent=2)}")

        result = await browser_controller.execute(actions)
        print(f"Result: {json.dumps(result, indent=2)}")

        # Wait a bit to see the results
        time.sleep(3)

        # Demo 4: Search on GitHub
        print("\n=== Demo 4: Search on GitHub ===")
        print("Command: Search for 'browser automation' on GitHub")

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

        print(f"Actions: {json.dumps(actions, indent=2)}")

        result = await browser_controller.execute(actions)
        print(f"Result: {json.dumps(result, indent=2)}")

        # Wait a bit to see the results
        time.sleep(3)

        # Close the browser
        await browser_controller.close()

        print("\n=== Demo completed successfully ===")
    except Exception as e:
        logger.error(f"Error running demo: {str(e)}")
        print(f"Error running demo: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Browser Automation Agent Comprehensive Demo")
    parser.add_argument("--headless", action="store_true", help="Run the browser in headless mode")
    parser.add_argument("--slow-mo", type=int, default=50, help="Slow down browser operations by the specified amount (in ms)")

    args = parser.parse_args()

    asyncio.run(run_demo(headless=args.headless, slow_mo=args.slow_mo))
