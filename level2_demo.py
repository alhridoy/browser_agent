import asyncio
import argparse
import json
import time
import os
from src.native.controller import NativeBrowserController
from src.native.extractor import DataExtractor
from src.native.config import BrowserConfig
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

async def run_demo(headless: bool = False, slow_mo: int = 50):
    """
    Run a comprehensive demo of the Level 2 browser automation agent.
    
    Args:
        headless: Whether to run the browser in headless mode (not applicable for native control).
        slow_mo: How much to slow down operations (in ms).
    """
    try:
        print("\n=== Level 2 Browser Automation Agent Demo ===")
        
        # Initialize components
        browser_config = BrowserConfig("chrome")
        browser_controller = NativeBrowserController("chrome", headless=headless, slow_mo=slow_mo)
        data_extractor = DataExtractor()
        
        # Step 1: Configure the browser
        print("\n1. Configuring the browser")
        
        # Set window size
        window_size_result = browser_config.set_window_size(1280, 800)
        print(f"✓ Set window size: {window_size_result['message']}")
        
        # Set user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        user_agent_result = browser_config.set_user_agent(user_agent)
        print(f"✓ Set user agent: {user_agent_result['message']}")
        
        # Step 2: Launch the browser
        print("\n2. Launching the browser")
        launch_result = await browser_controller.launch_browser()
        
        if launch_result["success"]:
            print(f"✓ {launch_result['message']}")
        else:
            print(f"✗ {launch_result['message']}")
            return
        
        # Wait for the browser to initialize
        await asyncio.sleep(2)
        
        # Step 3: Navigate to Google
        print("\n3. Navigating to Google")
        navigate_result = await browser_controller.execute([
            {
                "type": "navigate",
                "url": "https://www.google.com"
            }
        ])
        
        if navigate_result["results"][0]["result"]["success"]:
            print(f"✓ {navigate_result['results'][0]['result']['message']}")
        else:
            print(f"✗ {navigate_result['results'][0]['result']['message']}")
        
        # Wait for the page to load
        await asyncio.sleep(2)
        
        # Step 4: Search for "browser automation"
        print("\n4. Searching for 'browser automation'")
        search_result = await browser_controller.execute([
            {
                "type": "search",
                "site": "Google",
                "query": "browser automation"
            }
        ])
        
        if search_result["results"][0]["result"]["success"]:
            print(f"✓ {search_result['results'][0]['result']['message']}")
        else:
            print(f"✗ {search_result['results'][0]['result']['message']}")
        
        # Wait for the search results to load
        await asyncio.sleep(3)
        
        # Step 5: Extract search results
        print("\n5. Extracting search results using OCR")
        
        # Take a screenshot of the search results
        os.makedirs("output", exist_ok=True)
        screenshot_path = os.path.join("output", "search_results.png")
        
        # Extract text from the screen
        extract_result = await data_extractor.extract("ocr", {
            "region": None,  # Extract from the entire screen
            "lang": "eng"
        })
        
        if extract_result["success"]:
            print(f"✓ {extract_result['message']}")
            
            # Save the extracted text
            text_path = os.path.join("output", "search_results.txt")
            with open(text_path, "w") as f:
                f.write(extract_result["data"])
            
            print(f"✓ Saved extracted text to {text_path}")
            
            # Print a sample of the extracted text
            text_sample = extract_result["data"][:200] + "..." if len(extract_result["data"]) > 200 else extract_result["data"]
            print(f"\nSample of extracted text:\n{text_sample}")
        else:
            print(f"✗ {extract_result['message']}")
        
        # Step 6: Navigate to GitHub
        print("\n6. Navigating to GitHub")
        navigate_result = await browser_controller.execute([
            {
                "type": "navigate",
                "url": "https://github.com"
            }
        ])
        
        if navigate_result["results"][0]["result"]["success"]:
            print(f"✓ {navigate_result['results'][0]['result']['message']}")
        else:
            print(f"✗ {navigate_result['results'][0]['result']['message']}")
        
        # Wait for the page to load
        await asyncio.sleep(3)
        
        # Step 7: Search on GitHub
        print("\n7. Searching for 'browser automation' on GitHub")
        github_search_result = await browser_controller.execute([
            {
                "type": "search",
                "site": "GitHub",
                "query": "browser automation"
            }
        ])
        
        if github_search_result["results"][0]["result"]["success"]:
            print(f"✓ {github_search_result['results'][0]['result']['message']}")
        else:
            print(f"✗ {github_search_result['results'][0]['result']['message']}")
        
        # Wait for the search results to load
        await asyncio.sleep(3)
        
        # Step 8: Scroll down to see more results
        print("\n8. Scrolling down to see more results")
        scroll_result = await browser_controller.execute([
            {
                "type": "scroll",
                "direction": "down",
                "amount": 5
            }
        ])
        
        if scroll_result["results"][0]["result"]["success"]:
            print(f"✓ {scroll_result['results'][0]['result']['message']}")
        else:
            print(f"✗ {scroll_result['results'][0]['result']['message']}")
        
        # Wait a bit to see the scrolled content
        await asyncio.sleep(2)
        
        # Step 9: Close the browser
        print("\n9. Closing the browser")
        close_result = await browser_controller.close_browser()
        
        if close_result["success"]:
            print(f"✓ {close_result['message']}")
        else:
            print(f"✗ {close_result['message']}")
        
        print("\n=== Demo completed successfully ===")
        print("\nLevel 2 capabilities demonstrated:")
        print("✓ OS-level browser control using PyAutoGUI and Pynput")
        print("✓ Data extraction using OCR")
        print("✓ Browser configuration (window size, user agent)")
        print("✓ Complete automation flow (search, extract, navigate)")
        
    except Exception as e:
        logger.error(f"Error running demo: {str(e)}")
        print(f"Error running demo: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Level 2 Browser Automation Agent Demo")
    parser.add_argument("--headless", action="store_true", help="Run the browser in headless mode (not applicable for native control)")
    parser.add_argument("--slow-mo", type=int, default=50, help="Slow down operations by the specified amount (in ms)")
    
    args = parser.parse_args()
    
    asyncio.run(run_demo(headless=args.headless, slow_mo=args.slow_mo))
