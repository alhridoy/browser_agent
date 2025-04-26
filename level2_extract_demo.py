import os
import time
import subprocess
import platform
import pyautogui
import sys
import pytesseract
from PIL import Image
import json

def launch_browser():
    """
    Launch a browser using OS-level commands.
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        cmd = "open -a 'Google Chrome' --args --start-maximized"
    elif system == "Windows":
        cmd = "start chrome --start-maximized"
    elif system == "Linux":
        cmd = "google-chrome --start-maximized"
    else:
        print(f"Unsupported platform: {system}")
        return None
    
    try:
        print(f"Launching browser with command: {cmd}")
        process = subprocess.Popen(cmd, shell=True)
        
        # Wait for the browser to start
        time.sleep(2)
        
        print(f"Browser launched successfully with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"Error launching browser: {str(e)}")
        return None

def navigate_to_url(url):
    """
    Navigate to a URL using PyAutoGUI.
    """
    try:
        print(f"Navigating to {url}")
        
        # Press Cmd+L (macOS) or Ctrl+L (Windows/Linux) to focus the address bar
        if platform.system() == "Darwin":  # macOS
            pyautogui.hotkey('command', 'l')
        else:
            pyautogui.hotkey('ctrl', 'l')
        
        # Wait for the address bar to be focused
        time.sleep(0.5)
        
        # Clear the address bar
        pyautogui.hotkey('command' if platform.system() == "Darwin" else 'ctrl', 'a')
        pyautogui.press('delete')
        
        # Type the URL
        pyautogui.write(url)
        
        # Press Enter
        pyautogui.press('enter')
        
        # Wait for the page to load
        time.sleep(3)
        
        print(f"Successfully navigated to {url}")
        return True
    except Exception as e:
        print(f"Error navigating to {url}: {str(e)}")
        return False

def search_on_google(query):
    """
    Search for a query on Google.
    """
    try:
        print(f"Searching for '{query}' on Google")
        
        # Type the query
        pyautogui.write(query)
        
        # Press Enter
        pyautogui.press('enter')
        
        # Wait for the search results to load
        time.sleep(3)
        
        print(f"Successfully searched for '{query}' on Google")
        return True
    except Exception as e:
        print(f"Error searching for '{query}' on Google: {str(e)}")
        return False

def scroll_down():
    """
    Scroll down the page.
    """
    try:
        print("Scrolling down")
        
        # Scroll down 5 times
        for i in range(5):
            pyautogui.scroll(-300)  # Negative value scrolls down
            time.sleep(0.5)
        
        print("Successfully scrolled down")
        return True
    except Exception as e:
        print(f"Error scrolling down: {str(e)}")
        return False

def take_screenshot(filename):
    """
    Take a screenshot.
    """
    try:
        print(f"Taking screenshot: {filename}")
        
        # Create the output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # Take the screenshot
        screenshot = pyautogui.screenshot()
        
        # Save the screenshot
        screenshot_path = os.path.join("output", filename)
        screenshot.save(screenshot_path)
        
        print(f"Screenshot saved to {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Error taking screenshot: {str(e)}")
        return None

def extract_text_from_screenshot(screenshot_path):
    """
    Extract text from a screenshot using OCR.
    """
    try:
        print(f"Extracting text from {screenshot_path}")
        
        # Open the image
        image = Image.open(screenshot_path)
        
        # Extract text using Tesseract OCR
        text = pytesseract.image_to_string(image)
        
        # Save the extracted text
        text_path = os.path.splitext(screenshot_path)[0] + ".txt"
        with open(text_path, "w") as f:
            f.write(text)
        
        print(f"Extracted text saved to {text_path}")
        
        # Print a sample of the extracted text
        text_sample = text[:200] + "..." if len(text) > 200 else text
        print(f"\nSample of extracted text:\n{text_sample}")
        
        return text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return None

def extract_search_results(text):
    """
    Extract search results from the OCR text.
    """
    try:
        print("Extracting search results")
        
        # Split the text into lines
        lines = text.split("\n")
        
        # Filter out empty lines
        lines = [line.strip() for line in lines if line.strip()]
        
        # Extract search results (this is a simple heuristic)
        results = []
        for i, line in enumerate(lines):
            if len(line) > 20 and "..." not in line and "http" not in line.lower():
                results.append(line)
        
        # Save the search results
        results_path = os.path.join("output", "search_results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Search results saved to {results_path}")
        
        # Print the search results
        print("\nExtracted search results:")
        for i, result in enumerate(results[:5]):
            print(f"{i+1}. {result}")
        
        if len(results) > 5:
            print(f"... and {len(results) - 5} more results")
        
        return results
    except Exception as e:
        print(f"Error extracting search results: {str(e)}")
        return None

def run_demo():
    """
    Run the Extract API demo.
    """
    print("\n=== Level 2 Extract API Demo: Data Extraction from Browser ===")
    
    # Set PyAutoGUI settings
    pyautogui.PAUSE = 1  # 1 second pause between PyAutoGUI commands
    pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort
    
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    print(f"Screen size: {screen_width}x{screen_height}")
    
    # Launch the browser
    browser_process = launch_browser()
    
    if not browser_process:
        print("Failed to launch browser")
        return False
    
    try:
        # Navigate to Google
        if not navigate_to_url("https://www.google.com"):
            return False
        
        # Search for "browser automation"
        if not search_on_google("browser automation"):
            return False
        
        # Take a screenshot of search results
        screenshot_path = take_screenshot("search_results.png")
        
        if not screenshot_path:
            return False
        
        # Extract text from the screenshot
        text = extract_text_from_screenshot(screenshot_path)
        
        if not text:
            return False
        
        # Extract search results from the text
        results = extract_search_results(text)
        
        if not results:
            return False
        
        print("\n=== Demo completed successfully ===")
        print("\nLevel 2 capabilities demonstrated:")
        print("✓ OS-level browser control using PyAutoGUI")
        print("✓ Direct keyboard and mouse simulation")
        print("✓ Extract API for retrieving structured data")
        print("✓ OCR-based text extraction")
        print("✓ Complete automation flow (navigate, search, extract)")
        
        # Wait a bit before closing
        print("\nBrowser will close in 5 seconds...")
        time.sleep(5)
        
        return True
    except Exception as e:
        print(f"Error running demo: {str(e)}")
        return False
    finally:
        # Close the browser
        browser_process.terminate()
        browser_process.wait()
        print("Browser closed")

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import pyautogui
        import pytesseract
        from PIL import Image
    except ImportError as e:
        print(f"Required package not installed: {str(e)}")
        print("Please install the required packages with: pip install pyautogui pytesseract pillow")
        sys.exit(1)
    
    # Run the demo
    success = run_demo()
    
    if not success:
        print("\n=== Demo failed ===")
