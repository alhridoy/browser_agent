import asyncio
import os
import re
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

class BrowserController:
    """
    Control a browser using Playwright.
    """

    def __init__(self, headless: bool = False, slow_mo: int = 50):
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.initialized = False

    async def initialize(self):
        """
        Initialize the browser if it's not already initialized.
        """
        if not self.initialized:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            self.initialized = True

    async def close(self):
        """
        Close the browser.
        """
        if self.initialized:
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()
            self.initialized = False

    async def execute(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a list of browser actions.

        Args:
            actions: A list of actions to execute.

        Returns:
            A dictionary containing the result of the execution.
        """
        await self.initialize()

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
                    result = await self._scroll(action.get("element"))
                elif action_type == "wait":
                    result = await self._wait(action.get("element"))
                elif action_type == "press":
                    result = await self._press(action.get("element"), action.get("key"))
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
            await self.page.goto(url)
            return {
                "success": True,
                "message": f"Navigated to {url}",
                "title": await self.page.title()
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
            # Try different selectors
            selectors = await self._get_selectors_for_element(element)

            for selector in selectors:
                try:
                    # Wait for the element to be visible
                    await self.page.wait_for_selector(selector, state="visible", timeout=5000)
                    await self.page.click(selector)
                    return {
                        "success": True,
                        "message": f"Clicked on {element}",
                        "selector": selector
                    }
                except Exception:
                    continue

            # If we get here, none of the selectors worked
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
            # Try different selectors
            selectors = await self._get_selectors_for_element(element)

            for selector in selectors:
                try:
                    # Wait for the element to be visible
                    await self.page.wait_for_selector(selector, state="visible", timeout=5000)
                    await self.page.fill(selector, text)
                    return {
                        "success": True,
                        "message": f"Typed '{text}' into {element}",
                        "selector": selector
                    }
                except Exception:
                    continue

            # If we get here, none of the selectors worked
            return {
                "success": False,
                "message": f"Could not find input field: {element}"
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
            # Handle different search sites
            if re.search(r'google', site, re.IGNORECASE):
                # Navigate to Google
                await self.page.goto("https://www.google.com")

                # Type the query into the search box
                await self.page.fill('textarea[name="q"]', query)

                # Press Enter
                await self.page.press('textarea[name="q"]', "Enter")

                # Wait for the search results
                await self.page.wait_for_selector('div#search')

                return {
                    "success": True,
                    "message": f"Searched for '{query}' on Google",
                    "title": await self.page.title()
                }
            elif re.search(r'bing', site, re.IGNORECASE):
                # Navigate to Bing
                await self.page.goto("https://www.bing.com")

                # Type the query into the search box
                await self.page.fill('input[name="q"]', query)

                # Press Enter
                await self.page.press('input[name="q"]', "Enter")

                # Wait for the search results
                await self.page.wait_for_selector('ol#b_results')

                return {
                    "success": True,
                    "message": f"Searched for '{query}' on Bing",
                    "title": await self.page.title()
                }
            elif re.search(r'yahoo', site, re.IGNORECASE):
                # Navigate to Yahoo
                await self.page.goto("https://search.yahoo.com")

                # Type the query into the search box
                await self.page.fill('input[name="p"]', query)

                # Press Enter
                await self.page.press('input[name="p"]', "Enter")

                # Wait for the search results
                await self.page.wait_for_selector('div#results')

                return {
                    "success": True,
                    "message": f"Searched for '{query}' on Yahoo",
                    "title": await self.page.title()
                }
            else:
                # Generic search
                # First navigate to the site if we're not already there
                current_url = self.page.url
                if not re.search(site, current_url, re.IGNORECASE):
                    if not site.startswith("http"):
                        site = "https://" + site
                    await self.page.goto(site)

                # Try to find a search box
                search_selectors = [
                    'input[type="search"]',
                    'input[name="q"]',
                    'input[name="query"]',
                    'input[name="search"]',
                    'input[placeholder*="search" i]',
                    'input[aria-label*="search" i]'
                ]

                for selector in search_selectors:
                    try:
                        if await self.page.query_selector(selector):
                            await self.page.fill(selector, query)
                            await self.page.press(selector, "Enter")
                            await asyncio.sleep(2)  # Wait for the search results to load
                            return {
                                "success": True,
                                "message": f"Searched for '{query}' on {site}",
                                "title": await self.page.title()
                            }
                    except Exception:
                        continue

                return {
                    "success": False,
                    "message": f"Could not find a search box on {site}"
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
            # Navigate to the site if needed
            current_url = self.page.url
            if site and not re.search(site, current_url, re.IGNORECASE):
                if not site.startswith("http"):
                    site = "https://" + site
                await self.page.goto(site)

            # Try to find username and password fields
            username_selectors = [
                'input[type="email"]',
                'input[type="text"][name*="email" i]',
                'input[type="text"][name*="user" i]',
                'input[type="text"][id*="email" i]',
                'input[type="text"][id*="user" i]',
                'input[type="text"][placeholder*="email" i]',
                'input[type="text"][placeholder*="user" i]',
                'input[name="username"]',
                'input[id="username"]'
            ]

            password_selectors = [
                'input[type="password"]'
            ]

            # Try to find and fill the username field
            username_filled = False
            for selector in username_selectors:
                try:
                    if await self.page.query_selector(selector):
                        await self.page.fill(selector, username)
                        username_filled = True
                        break
                except Exception:
                    continue

            if not username_filled:
                return {
                    "success": False,
                    "message": "Could not find username field"
                }

            # Try to find and fill the password field
            password_filled = False
            for selector in password_selectors:
                try:
                    if await self.page.query_selector(selector):
                        await self.page.fill(selector, password)
                        password_filled = True
                        break
                except Exception:
                    continue

            if not password_filled:
                return {
                    "success": False,
                    "message": "Could not find password field"
                }

            # Try to find and click the login button
            login_button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'button:has-text("Signin")',
                'a:has-text("Log in")',
                'a:has-text("Login")',
                'a:has-text("Sign in")',
                'a:has-text("Signin")'
            ]

            login_clicked = False
            for selector in login_button_selectors:
                try:
                    if await self.page.query_selector(selector):
                        await self.page.click(selector)
                        login_clicked = True
                        break
                except Exception:
                    continue

            if not login_clicked:
                # Try pressing Enter on the password field
                await self.page.press('input[type="password"]', "Enter")

            # Wait a bit for the login to complete
            await asyncio.sleep(3)

            return {
                "success": True,
                "message": f"Logged into {site} with username {username}",
                "title": await self.page.title()
            }
        except Exception as e:
            logger.error(f"Error logging into {site}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to log into {site}: {str(e)}"
            }

    async def _scroll(self, element: str) -> Dict[str, Any]:
        """
        Scroll to an element.
        """
        try:
            # Try different selectors
            selectors = await self._get_selectors_for_element(element)

            for selector in selectors:
                try:
                    # Wait for the element to be present
                    await self.page.wait_for_selector(selector, timeout=5000)

                    # Scroll to the element
                    await self.page.evaluate(f'document.querySelector("{selector}").scrollIntoView()')

                    return {
                        "success": True,
                        "message": f"Scrolled to {element}",
                        "selector": selector
                    }
                except Exception:
                    continue

            # If we get here, none of the selectors worked
            return {
                "success": False,
                "message": f"Could not find element: {element}"
            }
        except Exception as e:
            logger.error(f"Error scrolling to {element}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to scroll to {element}: {str(e)}"
            }

    async def _wait(self, element: str) -> Dict[str, Any]:
        """
        Wait for an element to appear.
        """
        try:
            # Try different selectors
            selectors = await self._get_selectors_for_element(element)

            for selector in selectors:
                try:
                    # Wait for the element to be visible
                    await self.page.wait_for_selector(selector, state="visible", timeout=10000)

                    return {
                        "success": True,
                        "message": f"Element {element} is now visible",
                        "selector": selector
                    }
                except Exception:
                    continue

            # If we get here, none of the selectors worked
            return {
                "success": False,
                "message": f"Element {element} did not appear within the timeout"
            }
        except Exception as e:
            logger.error(f"Error waiting for {element}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to wait for {element}: {str(e)}"
            }

    async def _press(self, element: str, key: str) -> Dict[str, Any]:
        """
        Press a key on an element.
        """
        try:
            # Try different selectors
            selectors = await self._get_selectors_for_element(element)

            for selector in selectors:
                try:
                    # Wait for the element to be visible
                    await self.page.wait_for_selector(selector, state="visible", timeout=5000)

                    # Press the key
                    await self.page.press(selector, key)

                    return {
                        "success": True,
                        "message": f"Pressed {key} on {element}",
                        "selector": selector
                    }
                except Exception:
                    continue

            # If we get here, none of the selectors worked
            return {
                "success": False,
                "message": f"Could not find element: {element}"
            }
        except Exception as e:
            logger.error(f"Error pressing {key} on {element}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to press {key} on {element}: {str(e)}"
            }

    async def _get_selectors_for_element(self, element: str) -> List[str]:
        """
        Generate a list of possible selectors for an element based on its description.
        """
        selectors = []

        # If the element looks like a CSS selector, use it directly
        if element.startswith('input[') or element.startswith('button[') or element.startswith('a[') or '[' in element and ']' in element:
            selectors.append(element)
            return selectors

        # Clean up the element description
        element = element.strip().lower()

        # Add CSS selectors
        selectors.extend([
            f'button:has-text("{element}")',
            f'a:has-text("{element}")',
            f'input[placeholder*="{element}" i]',
            f'input[name*="{element}" i]',
            f'input[id*="{element}" i]',
            f'input[aria-label*="{element}" i]',
            f'[placeholder*="{element}" i]',
            f'[name*="{element}" i]',
            f'[id*="{element}" i]',
            f'[aria-label*="{element}" i]',
            f'[title*="{element}" i]',
            f'text="{element}"'
        ])

        # Add XPath selectors
        selectors.extend([
            f'//button[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{element}")]',
            f'//a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{element}")]',
            f'//input[contains(translate(@placeholder, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{element}")]',
            f'//input[contains(translate(@name, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{element}")]',
            f'//input[contains(translate(@id, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{element}")]',
            f'//input[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{element}")]',
            f'//*[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{element}")]'
        ])

        return selectors
