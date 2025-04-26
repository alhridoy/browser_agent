import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.nlp.parser import CommandParser
from src.browser.controller import BrowserController
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Browser Automation Agent",
    description="An AI agent that automates browser workflows using natural language commands",
    version="1.0.0",
)

# Define request models
class InteractRequest(BaseModel):
    command: str

class InteractResponse(BaseModel):
    status: str
    message: str
    data: dict = None
    error: str = None

# Initialize components
parser = CommandParser()
browser_controller = BrowserController(
    headless=os.getenv("HEADLESS", "false").lower() == "true",
    slow_mo=int(os.getenv("SLOW_MO", "50"))
)

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

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True
    )
