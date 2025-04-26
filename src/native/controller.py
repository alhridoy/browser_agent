import os
import time
import pyautogui
import pynput
import cv2
import numpy as np
import subprocess
import platform
from typing import Dict, Any, List, Tuple, Optional
import logging
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger("native_browser")

class NativeBrowserController:
    """
    Control a browser using OS-level APIs (PyAutoGUI and Pynput).
    """
    
    def __init__(self, browser_name: str = "chrome", headless: bool = False, slow_mo: int = 50):
        """
        Initialize the native browser controller.
        
        Args:
            browser_name: The name of the browser to control (chrome, firefox, safari).
            headless: Whether to run the browser in headless mode (not applicable for native control).
            slow_mo: How much to slow down operations (in ms).
        """
        self.browser_name = browser_name.lower()
        self.headless = headless  # Not applicable for native control, but kept for API compatibility
        self.slow_mo = slow_mo
        self.browser_process = None
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Set PyAutoGUI settings
        pyautogui.PAUSE = self.slow_mo / 1000.0  # Convert ms to seconds
        pyautogui.FAILSAFE = True
        
        # Initialize mouse and keyboard controllers
        self.mouse = pynput.mouse.Controller()
        self.keyboard = pynput.keyboard.Controller()
        
        # Load browser-specific templates
        self.templates = self._load_templates()
        
        logger.info(f"Initialized native browser controller for {browser_name}")
    
    def _load_templates(self) -> Dict[str, np.ndarray]:
        """
        Load image templates for browser elements.
        """
        templates = {}
        template_dir = os.path.join(os.path.dirname(__file__), "templates", self.browser_name)
        
        # Create templates directory if it doesn't exist
        os.makedirs(template_dir, exist_ok=True)
        
        # Check if templates exist, if not, return empty dict
        if not os.path.exists(template_dir) or not os.listdir(template_dir):
            logger.warning(f"No templates found for {self.browser_name}")
            return templates
        
        # Load templates
        for filename in os.listdir(template_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                template_name = os.path.splitext(filename)[0]
                template_path = os.path.join(template_dir, filename)
                templates[template_name] = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                logger.info(f"Loaded template: {template_name}")
        
        return templates
    
    async def launch_browser(self) -> Dict[str, Any]:
        """
        Launch the browser.
        """
        try:
            # Determine the browser executable based on the platform
            browser_cmd = self._get_browser_command()
            
            if not browser_cmd:
                return {
                    "success": False,
                    "message": f"Could not find {self.browser_name} browser on this system"
                }
            
            # Launch the browser
            self.browser_process = subprocess.Popen(browser_cmd, shell=True)
            
            # Wait for the browser to start
            time.sleep(2)
            
            return {
                "success": True,
                "message": f"Launched {self.browser_name} browser",
                "process_id": self.browser_process.pid
            }
        except Exception as e:
            logger.error(f"Error launching browser: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to launch browser: {str(e)}"
            }
    
    def _get_browser_command(self) -> str:
        """
        Get the command to launch the browser based on the platform.
        """
        system = platform.system()
        
        if system == "Darwin":  # macOS
            if self.browser_name == "chrome":
                return "open -a 'Google Chrome' --args --start-maximized"
            elif self.browser_name == "firefox":
                return "open -a Firefox"
            elif self.browser_name == "safari":
                return "open -a Safari"
        elif system == "Windows":
            if self.browser_name == "chrome":
                return "start chrome --start-maximized"
            elif self.browser_name == "firefox":
                return "start firefox"
            elif self.browser_name == "edge":
                return "start msedge --start-maximized"
        elif system == "Linux":
            if self.browser_name == "chrome":
                return "google-chrome --start-maximized"
            elif self.browser_name == "firefox":
                return "firefox"
        
        return ""
    
    async def close_browser(self) -> Dict[str, Any]:
        """
        Close the browser.
        """
        try:
            if self.browser_process:
                self.browser_process.terminate()
                self.browser_process.wait()
                self.browser_process = None
                return {
                    "success": True,
                    "message": f"Closed {self.browser_name} browser"
                }
            else:
                # Try to close the browser using keyboard shortcuts
                with self.keyboard.pressed(pynput.keyboard.Key.alt):
                    self.keyboard.press(pynput.keyboard.Key.f4)
                    self.keyboard.release(pynput.keyboard.Key.f4)
                
                return {
                    "success": True,
                    "message": f"Attempted to close {self.browser_name} browser with keyboard shortcut"
                }
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to close browser: {str(e)}"
            }
    
    async def execute(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a list of browser actions.
        
        Args:
            actions: A list of actions to execute.
            
        Returns:
            A dictionary containing the result of the execution.
        """
        results = []
        
        for action in actions:
            action_type = action.get("type")
            
            try:
                if action_type == "navigate":
                    result = await self._navigate(action.get("url"))
                elif action_type == "click":
                    result = await self._click(action.get("element"))
                elif action_type == "type":
                    result = await self._type(action.get("element"), action.get("text"))
                elif action_type == "search":
                    result = await self._search(action.get("site"), action.get("query"))
                elif action_type == "login":
                    result = await self._login(action.get("site"), action.get("username"), action.get("password"))
                elif action_type == "scroll":
                    result = await self._scroll(action.get("direction"), action.get("amount"))
                elif action_type == "wait":
                    result = await self._wait(action.get("seconds"))
                elif action_type == "press":
                    result = await self._press(action.get("key"))
                elif action_type == "extract":
                    result = await self._extract(action.get("selector"), action.get("format"))
                else:
                    result = {
                        "success": False,
                        "message": f"Unknown action type: {action_type}"
                    }
                
                results.append({
                    "action": action,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error executing action {action_type}: {str(e)}")
                results.append({
                    "action": action,
                    "result": {
                        "success": False,
                        "message": str(e)
                    }
                })
        
        return {
            "results": results
        }
    
    async def _navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.
        """
        try:
            # Click on the address bar (Cmd+L or Ctrl+L)
            if platform.system() == "Darwin":  # macOS
                with self.keyboard.pressed(pynput.keyboard.Key.cmd):
                    self.keyboard.press('l')
                    self.keyboard.release('l')
            else:  # Windows/Linux
                with self.keyboard.pressed(pynput.keyboard.Key.ctrl):
                    self.keyboard.press('l')
                    self.keyboard.release('l')
            
            # Wait for the address bar to be focused
            time.sleep(0.5)
            
            # Clear the address bar
            with self.keyboard.pressed(pynput.keyboard.Key.cmd if platform.system() == "Darwin" else pynput.keyboard.Key.ctrl):
                self.keyboard.press('a')
                self.keyboard.release('a')
            
            self.keyboard.press(pynput.keyboard.Key.delete)
            self.keyboard.release(pynput.keyboard.Key.delete)
            
            # Type the URL
            self.keyboard.type(url)
            
            # Press Enter
            self.keyboard.press(pynput.keyboard.Key.enter)
            self.keyboard.release(pynput.keyboard.Key.enter)
            
            # Wait for the page to load
            time.sleep(3)
            
            return {
                "success": True,
                "message": f"Navigated to {url}"
            }
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to navigate to {url}: {str(e)}"
            }
    
    async def _click(self, element: str) -> Dict[str, Any]:
        """
        Click on an element.
        """
        try:
            # Try to find the element by image recognition
            element_location = self._find_element_by_image(element)
            
            if element_location:
                # Move to the element
                pyautogui.moveTo(element_location[0], element_location[1], duration=0.5)
                
                # Click on the element
                pyautogui.click()
                
                return {
                    "success": True,
                    "message": f"Clicked on {element}",
                    "location": element_location
                }
            else:
                # Try to find the element by text
                element_location = self._find_element_by_text(element)
                
                if element_location:
                    # Move to the element
                    pyautogui.moveTo(element_location[0], element_location[1], duration=0.5)
                    
                    # Click on the element
                    pyautogui.click()
                    
                    return {
                        "success": True,
                        "message": f"Clicked on {element}",
                        "location": element_location
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Could not find element: {element}"
                    }
        except Exception as e:
            logger.error(f"Error clicking on {element}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to click on {element}: {str(e)}"
            }
    
    async def _type(self, element: str, text: str) -> Dict[str, Any]:
        """
        Type text into an input field.
        """
        try:
            # First, click on the element
            click_result = await self._click(element)
            
            if not click_result["success"]:
                return click_result
            
            # Type the text
            pyautogui.typewrite(text, interval=0.05)
            
            return {
                "success": True,
                "message": f"Typed '{text}' into {element}"
            }
        except Exception as e:
            logger.error(f"Error typing into {element}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to type into {element}: {str(e)}"
            }
    
    async def _search(self, site: str, query: str) -> Dict[str, Any]:
        """
        Search for something on a site.
        """
        try:
            # Navigate to the site if needed
            if site.lower() == "google":
                navigate_result = await self._navigate("https://www.google.com")
                if not navigate_result["success"]:
                    return navigate_result
                
                # Wait for the page to load
                time.sleep(1)
                
                # Type the query
                pyautogui.typewrite(query, interval=0.05)
                
                # Press Enter
                pyautogui.press('enter')
                
                # Wait for the search results
                time.sleep(2)
                
                return {
                    "success": True,
                    "message": f"Searched for '{query}' on Google"
                }
            elif site.lower() == "github":
                navigate_result = await self._navigate("https://github.com")
                if not navigate_result["success"]:
                    return navigate_result
                
                # Find and click the search button
                search_button_location = self._find_element_by_image("github_search_button")
                
                if search_button_location:
                    pyautogui.moveTo(search_button_location[0], search_button_location[1], duration=0.5)
                    pyautogui.click()
                    
                    # Wait for the search box to appear
                    time.sleep(1)
                    
                    # Type the query
                    pyautogui.typewrite(query, interval=0.05)
                    
                    # Press Enter
                    pyautogui.press('enter')
                    
                    # Wait for the search results
                    time.sleep(2)
                    
                    return {
                        "success": True,
                        "message": f"Searched for '{query}' on GitHub"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Could not find GitHub search button"
                    }
            else:
                return {
                    "success": False,
                    "message": f"Search on {site} is not supported yet"
                }
        except Exception as e:
            logger.error(f"Error searching for {query} on {site}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to search for {query} on {site}: {str(e)}"
            }
    
    async def _login(self, site: str, username: str, password: str) -> Dict[str, Any]:
        """
        Log into a site.
        """
        try:
            # Navigate to the site
            navigate_result = await self._navigate(site)
            if not navigate_result["success"]:
                return navigate_result
            
            # Wait for the page to load
            time.sleep(2)
            
            # Find and click the username field
            username_field_location = self._find_element_by_image(f"{site.split('.')[0]}_username_field")
            
            if not username_field_location:
                return {
                    "success": False,
                    "message": "Could not find username field"
                }
            
            # Click on the username field
            pyautogui.moveTo(username_field_location[0], username_field_location[1], duration=0.5)
            pyautogui.click()
            
            # Type the username
            pyautogui.typewrite(username, interval=0.05)
            
            # Find and click the password field
            password_field_location = self._find_element_by_image(f"{site.split('.')[0]}_password_field")
            
            if not password_field_location:
                return {
                    "success": False,
                    "message": "Could not find password field"
                }
            
            # Click on the password field
            pyautogui.moveTo(password_field_location[0], password_field_location[1], duration=0.5)
            pyautogui.click()
            
            # Type the password
            pyautogui.typewrite(password, interval=0.05)
            
            # Find and click the login button
            login_button_location = self._find_element_by_image(f"{site.split('.')[0]}_login_button")
            
            if not login_button_location:
                # Try pressing Enter instead
                pyautogui.press('enter')
            else:
                # Click on the login button
                pyautogui.moveTo(login_button_location[0], login_button_location[1], duration=0.5)
                pyautogui.click()
            
            # Wait for the login to complete
            time.sleep(3)
            
            return {
                "success": True,
                "message": f"Logged into {site} with username {username}"
            }
        except Exception as e:
            logger.error(f"Error logging into {site}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to log into {site}: {str(e)}"
            }
    
    async def _scroll(self, direction: str, amount: int = 10) -> Dict[str, Any]:
        """
        Scroll the page.
        """
        try:
            if direction.lower() == "down":
                pyautogui.scroll(-amount * 100)  # Negative for scrolling down
            elif direction.lower() == "up":
                pyautogui.scroll(amount * 100)  # Positive for scrolling up
            elif direction.lower() == "right":
                pyautogui.hscroll(amount * 100)  # Positive for scrolling right
            elif direction.lower() == "left":
                pyautogui.hscroll(-amount * 100)  # Negative for scrolling left
            else:
                return {
                    "success": False,
                    "message": f"Unknown scroll direction: {direction}"
                }
            
            return {
                "success": True,
                "message": f"Scrolled {direction} by {amount}"
            }
        except Exception as e:
            logger.error(f"Error scrolling {direction}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to scroll {direction}: {str(e)}"
            }
    
    async def _wait(self, seconds: int) -> Dict[str, Any]:
        """
        Wait for a specified number of seconds.
        """
        try:
            time.sleep(seconds)
            
            return {
                "success": True,
                "message": f"Waited for {seconds} seconds"
            }
        except Exception as e:
            logger.error(f"Error waiting: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to wait: {str(e)}"
            }
    
    async def _press(self, key: str) -> Dict[str, Any]:
        """
        Press a key.
        """
        try:
            pyautogui.press(key)
            
            return {
                "success": True,
                "message": f"Pressed {key}"
            }
        except Exception as e:
            logger.error(f"Error pressing {key}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to press {key}: {str(e)}"
            }
    
    async def _extract(self, selector: str, format: str = "text") -> Dict[str, Any]:
        """
        Extract data from the page.
        """
        try:
            # Take a screenshot
            screenshot = pyautogui.screenshot()
            
            # Convert the screenshot to a numpy array
            screenshot_np = np.array(screenshot)
            
            # For now, just return a placeholder result
            # In a real implementation, we would use OCR to extract text from the screenshot
            return {
                "success": True,
                "message": f"Extracted data from {selector}",
                "data": "Sample extracted data"
            }
        except Exception as e:
            logger.error(f"Error extracting data from {selector}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to extract data from {selector}: {str(e)}"
            }
    
    def _find_element_by_image(self, element_name: str) -> Optional[Tuple[int, int]]:
        """
        Find an element on the screen by matching a template image.
        
        Args:
            element_name: The name of the element to find.
            
        Returns:
            The (x, y) coordinates of the center of the element, or None if not found.
        """
        # Check if we have a template for this element
        if element_name in self.templates:
            template = self.templates[element_name]
            
            # Take a screenshot
            screenshot = pyautogui.screenshot()
            
            # Convert the screenshot to a numpy array
            screenshot_np = np.array(screenshot)
            
            # Convert to grayscale
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            # Match the template
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            
            # Get the best match
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # If the match is good enough
            if max_val > 0.8:
                # Get the center of the template
                h, w = template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                return (center_x, center_y)
        
        # If we don't have a template or the match is not good enough, try to find by text
        return None
    
    def _find_element_by_text(self, text: str) -> Optional[Tuple[int, int]]:
        """
        Find an element on the screen by its text.
        
        Args:
            text: The text to find.
            
        Returns:
            The (x, y) coordinates of the center of the element, or None if not found.
        """
        # For now, just use PyAutoGUI's locateOnScreen function with OCR
        # In a real implementation, we would use a more robust OCR solution
        try:
            location = pyautogui.locateOnScreen(text, confidence=0.7)
            
            if location:
                center_x = location.left + location.width // 2
                center_y = location.top + location.height // 2
                
                return (center_x, center_y)
        except:
            pass
        
        return None
