import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to Google
        await page.goto('https://www.google.com')
        
        # Wait for the page to load
        await page.wait_for_load_state('networkidle')
        
        # Type in the search box
        await page.fill('textarea[name="q"]', 'browser automation')
        
        # Press Enter to search
        await page.press('textarea[name="q"]', 'Enter')
        
        # Wait for the search results to load
        await page.wait_for_load_state('networkidle')
        
        # Wait a bit to see the results
        await asyncio.sleep(5)
        
        # Close the browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
