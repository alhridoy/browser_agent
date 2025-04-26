import os
import time
import subprocess
import platform
import pyautogui
import sys

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
        return True
    except Exception as e:
        print(f"Error taking screenshot: {str(e)}")
        return False

def run_demo():
    """
    Run the PyAutoGUI demo.
    """
    print("\n=== Level 2 PyAutoGUI Demo: Direct Browser Control ===")
    
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
        
        # Take a screenshot of Google homepage
        take_screenshot("google_homepage.png")
        
        # Search for "browser automation"
        if not search_on_google("browser automation"):
            return False
        
        # Take a screenshot of search results
        take_screenshot("search_results.png")
        
        # Scroll down to see more results
        if not scroll_down():
            return False
        
        # Take a screenshot after scrolling
        take_screenshot("scrolled_results.png")
        
        # Navigate to GitHub
        if not navigate_to_url("https://github.com"):
            return False
        
        # Take a screenshot of GitHub homepage
        take_screenshot("github_homepage.png")
        
        print("\n=== Demo completed successfully ===")
        print("\nLevel 2 capabilities demonstrated:")
        print("✓ OS-level browser control using PyAutoGUI")
        print("✓ Direct keyboard and mouse simulation")
        print("✓ Complete automation flow (navigate, search, scroll)")
        print("✓ Screenshot capture")
        
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
    # Check if PyAutoGUI is installed
    try:
        import pyautogui
    except ImportError:
        print("PyAutoGUI is not installed. Please install it with: pip install pyautogui")
        sys.exit(1)
    
    # Run the demo
    success = run_demo()
    
    if not success:
        print("\n=== Demo failed ===")
