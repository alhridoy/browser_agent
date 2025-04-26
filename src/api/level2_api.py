from fastapi import FastAPI, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from src.nlp.parser import CommandParser
from src.native.controller import NativeBrowserController
from src.native.extractor import DataExtractor
from src.native.config import BrowserConfig
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Browser Automation Agent - Level 2",
    description="An AI agent that automates browser workflows using OS-level APIs",
    version="2.0.0",
)

# Define request models
class InteractRequest(BaseModel):
    command: str
    browser: str = "chrome"
    headless: bool = False
    slow_mo: int = 50

class ExtractRequest(BaseModel):
    extraction_type: str
    params: Dict[str, Any]
    browser: str = "chrome"

class ProxyConfigRequest(BaseModel):
    proxy_type: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    browser: str = "chrome"

class ExtensionRequest(BaseModel):
    extension_path: str
    browser: str = "chrome"

class UserAgentRequest(BaseModel):
    user_agent: str
    browser: str = "chrome"

class WindowSizeRequest(BaseModel):
    width: int
    height: int
    browser: str = "chrome"

class CookieRequest(BaseModel):
    domain: str
    name: str
    value: str
    path: str = "/"
    secure: bool = False
    http_only: bool = False
    expiry: Optional[int] = None
    browser: str = "chrome"

class InteractResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Initialize components
parser = CommandParser()
browser_controllers = {}
data_extractors = {}
browser_configs = {}

# Helper function to get or create a browser controller
async def get_browser_controller(browser: str, headless: bool = False, slow_mo: int = 50) -> NativeBrowserController:
    """
    Get or create a browser controller for the specified browser.
    """
    browser_key = f"{browser}_{headless}_{slow_mo}"
    
    if browser_key not in browser_controllers:
        browser_controllers[browser_key] = NativeBrowserController(browser, headless=headless, slow_mo=slow_mo)
    
    return browser_controllers[browser_key]

# Helper function to get or create a data extractor
def get_data_extractor() -> DataExtractor:
    """
    Get or create a data extractor.
    """
    if "extractor" not in data_extractors:
        data_extractors["extractor"] = DataExtractor()
    
    return data_extractors["extractor"]

# Helper function to get or create a browser config
def get_browser_config(browser: str) -> BrowserConfig:
    """
    Get or create a browser config for the specified browser.
    """
    if browser not in browser_configs:
        browser_configs[browser] = BrowserConfig(browser)
    
    return browser_configs[browser]

@app.post("/interact", response_model=InteractResponse)
async def interact(request: InteractRequest):
    """
    Process a natural language command and perform browser automation actions.
    """
    try:
        logger.info(f"Received command: {request.command}")
        
        # Parse the command
        actions = parser.parse(request.command)
        logger.info(f"Parsed actions: {actions}")
        
        # Get or create a browser controller
        browser_controller = await get_browser_controller(request.browser, request.headless, request.slow_mo)
        
        # Execute the actions
        result = await browser_controller.execute(actions)
        
        return InteractResponse(
            status="success",
            message="Command executed successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract", response_model=InteractResponse)
async def extract(request: ExtractRequest):
    """
    Extract data from a web page.
    """
    try:
        logger.info(f"Received extraction request: {request.extraction_type}")
        
        # Get or create a data extractor
        data_extractor = get_data_extractor()
        
        # Extract the data
        result = await data_extractor.extract(request.extraction_type, request.params)
        
        return InteractResponse(
            status="success",
            message="Data extracted successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/proxy", response_model=InteractResponse)
async def set_proxy(request: ProxyConfigRequest):
    """
    Set the proxy configuration.
    """
    try:
        logger.info(f"Received proxy configuration request: {request.proxy_type}://{request.host}:{request.port}")
        
        # Get or create a browser config
        browser_config = get_browser_config(request.browser)
        
        # Set the proxy
        result = browser_config.set_proxy(
            request.proxy_type,
            request.host,
            request.port,
            request.username or "",
            request.password or ""
        )
        
        return InteractResponse(
            status="success",
            message="Proxy configuration set successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error setting proxy configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/config/proxy", response_model=InteractResponse)
async def disable_proxy(browser: str = Query("chrome")):
    """
    Disable the proxy configuration.
    """
    try:
        logger.info(f"Received request to disable proxy for {browser}")
        
        # Get or create a browser config
        browser_config = get_browser_config(browser)
        
        # Disable the proxy
        result = browser_config.disable_proxy()
        
        return InteractResponse(
            status="success",
            message="Proxy configuration disabled successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error disabling proxy configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/proxy", response_model=InteractResponse)
async def get_proxy(browser: str = Query("chrome")):
    """
    Get the current proxy configuration.
    """
    try:
        logger.info(f"Received request to get proxy configuration for {browser}")
        
        # Get or create a browser config
        browser_config = get_browser_config(browser)
        
        # Get the proxy configuration
        result = browser_config.get_proxy_config()
        
        return InteractResponse(
            status="success",
            message="Proxy configuration retrieved successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error getting proxy configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/extension", response_model=InteractResponse)
async def add_extension(request: ExtensionRequest):
    """
    Add a browser extension.
    """
    try:
        logger.info(f"Received request to add extension: {request.extension_path}")
        
        # Get or create a browser config
        browser_config = get_browser_config(request.browser)
        
        # Add the extension
        result = browser_config.add_extension(request.extension_path)
        
        return InteractResponse(
            status="success",
            message="Extension added successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error adding extension: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/config/extension/{extension_name}", response_model=InteractResponse)
async def remove_extension(extension_name: str, browser: str = Query("chrome")):
    """
    Remove a browser extension.
    """
    try:
        logger.info(f"Received request to remove extension: {extension_name}")
        
        # Get or create a browser config
        browser_config = get_browser_config(browser)
        
        # Remove the extension
        result = browser_config.remove_extension(extension_name)
        
        return InteractResponse(
            status="success",
            message="Extension removed successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error removing extension: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/extensions", response_model=InteractResponse)
async def list_extensions(browser: str = Query("chrome")):
    """
    List all installed extensions.
    """
    try:
        logger.info(f"Received request to list extensions for {browser}")
        
        # Get or create a browser config
        browser_config = get_browser_config(browser)
        
        # List the extensions
        result = browser_config.list_extensions()
        
        return InteractResponse(
            status="success",
            message="Extensions listed successfully",
            data={"extensions": result}
        )
    except Exception as e:
        logger.error(f"Error listing extensions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/user-agent", response_model=InteractResponse)
async def set_user_agent(request: UserAgentRequest):
    """
    Set the user agent.
    """
    try:
        logger.info(f"Received request to set user agent: {request.user_agent}")
        
        # Get or create a browser config
        browser_config = get_browser_config(request.browser)
        
        # Set the user agent
        result = browser_config.set_user_agent(request.user_agent)
        
        return InteractResponse(
            status="success",
            message="User agent set successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error setting user agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/user-agent", response_model=InteractResponse)
async def get_user_agent(browser: str = Query("chrome")):
    """
    Get the current user agent.
    """
    try:
        logger.info(f"Received request to get user agent for {browser}")
        
        # Get or create a browser config
        browser_config = get_browser_config(browser)
        
        # Get the user agent
        result = browser_config.get_user_agent()
        
        return InteractResponse(
            status="success",
            message="User agent retrieved successfully",
            data={"user_agent": result}
        )
    except Exception as e:
        logger.error(f"Error getting user agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/window-size", response_model=InteractResponse)
async def set_window_size(request: WindowSizeRequest):
    """
    Set the window size.
    """
    try:
        logger.info(f"Received request to set window size: {request.width}x{request.height}")
        
        # Get or create a browser config
        browser_config = get_browser_config(request.browser)
        
        # Set the window size
        result = browser_config.set_window_size(request.width, request.height)
        
        return InteractResponse(
            status="success",
            message="Window size set successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error setting window size: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/window-size", response_model=InteractResponse)
async def get_window_size(browser: str = Query("chrome")):
    """
    Get the current window size.
    """
    try:
        logger.info(f"Received request to get window size for {browser}")
        
        # Get or create a browser config
        browser_config = get_browser_config(browser)
        
        # Get the window size
        result = browser_config.get_window_size()
        
        return InteractResponse(
            status="success",
            message="Window size retrieved successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error getting window size: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/cookie", response_model=InteractResponse)
async def add_cookie(request: CookieRequest):
    """
    Add a cookie.
    """
    try:
        logger.info(f"Received request to add cookie: {request.name} for {request.domain}")
        
        # Get or create a browser config
        browser_config = get_browser_config(request.browser)
        
        # Add the cookie
        result = browser_config.add_cookie(
            request.domain,
            request.name,
            request.value,
            request.path,
            request.secure,
            request.http_only,
            request.expiry
        )
        
        return InteractResponse(
            status="success",
            message="Cookie added successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error adding cookie: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/config/cookie", response_model=InteractResponse)
async def remove_cookie(domain: str, name: str, browser: str = Query("chrome")):
    """
    Remove a cookie.
    """
    try:
        logger.info(f"Received request to remove cookie: {name} for {domain}")
        
        # Get or create a browser config
        browser_config = get_browser_config(browser)
        
        # Remove the cookie
        result = browser_config.remove_cookie(domain, name)
        
        return InteractResponse(
            status="success",
            message="Cookie removed successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error removing cookie: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/cookies", response_model=InteractResponse)
async def get_cookies(browser: str = Query("chrome")):
    """
    Get all cookies.
    """
    try:
        logger.info(f"Received request to get cookies for {browser}")
        
        # Get or create a browser config
        browser_config = get_browser_config(browser)
        
        # Get the cookies
        result = browser_config.get_cookies()
        
        return InteractResponse(
            status="success",
            message="Cookies retrieved successfully",
            data={"cookies": result}
        )
    except Exception as e:
        logger.error(f"Error getting cookies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.level2_api:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True
    )
