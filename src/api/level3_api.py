from fastapi import FastAPI, HTTPException, Depends, Query, Body, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import json
import asyncio
import uuid
import datetime
from dotenv import load_dotenv
from src.level3.agent import BrowserAgent
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Browser Automation Agent - Level 3",
    description="An AI agent with contextual intelligence and advanced workflows",
    version="3.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request models
class MessageRequest(BaseModel):
    user_id: str
    message: str

class TaskRequest(BaseModel):
    task_id: Optional[str] = None
    name: str
    actions: List[Dict[str, Any]]
    schedule_type: str = "interval"
    interval: int = 3600
    cron: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    max_runs: Optional[int] = None

class MessageResponse(BaseModel):
    user_id: str
    message: str
    response: str
    actions: Optional[List[Dict[str, Any]]] = None
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    name: str
    schedule_type: str
    interval: int
    cron: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    max_runs: Optional[int] = None
    enabled: bool
    run_count: int
    last_run: Optional[str] = None
    next_run: Optional[str] = None

# Initialize the browser agent
browser_agent = BrowserAgent()

# WebSocket connections
websocket_connections = {}

@app.post("/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """
    Process a message and generate a response.
    """
    try:
        logger.info(f"Received message from user {request.user_id}: {request.message}")
        
        # Process the message
        result = await browser_agent.process_message(request.user_id, request.message)
        
        return result
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/task", response_model=TaskResponse)
async def schedule_task(request: TaskRequest):
    """
    Schedule a task to be executed periodically.
    """
    try:
        logger.info(f"Received task scheduling request: {request.name}")
        
        # Generate a task ID if not provided
        task_id = request.task_id or str(uuid.uuid4())
        
        # Parse start and end times
        start_time = None
        if request.start_time:
            try:
                start_time = datetime.datetime.fromisoformat(request.start_time)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start time format: {request.start_time}")
        
        end_time = None
        if request.end_time:
            try:
                end_time = datetime.datetime.fromisoformat(request.end_time)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end time format: {request.end_time}")
        
        # Schedule the task
        success = browser_agent.schedule_task(
            task_id=task_id,
            name=request.name,
            actions=request.actions,
            schedule_type=request.schedule_type,
            interval=request.interval,
            cron=request.cron,
            start_time=start_time,
            end_time=end_time,
            max_runs=request.max_runs
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to schedule task {task_id}")
        
        # Get the task details
        tasks = browser_agent.get_scheduled_tasks()
        task = next((t for t in tasks if t["task_id"] == task_id), None)
        
        if not task:
            raise HTTPException(status_code=500, detail=f"Task {task_id} was scheduled but could not be retrieved")
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks():
    """
    Get all scheduled tasks.
    """
    try:
        logger.info("Received request to get all tasks")
        
        # Get all tasks
        tasks = browser_agent.get_scheduled_tasks()
        
        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/{task_id}/run")
async def run_task(task_id: str):
    """
    Run a task immediately.
    """
    try:
        logger.info(f"Received request to run task {task_id}")
        
        # Run the task
        result = browser_agent.run_task(task_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return {
            "task_id": task_id,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    Delete a task.
    """
    try:
        logger.info(f"Received request to delete task {task_id}")
        
        # Get the task scheduler from the browser agent
        task_scheduler = browser_agent.task_scheduler
        
        # Remove the task
        success = task_scheduler.remove_task(task_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return {
            "task_id": task_id,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{user_id}")
async def get_conversation_history(user_id: str, limit: int = Query(None)):
    """
    Get the conversation history for a user.
    """
    try:
        logger.info(f"Received request to get conversation history for user {user_id}")
        
        # Get the dialog manager from the browser agent
        dialog_manager = browser_agent.dialog_manager
        
        # Get the conversation history
        history = dialog_manager.get_conversation_history(user_id, limit=limit)
        
        return {
            "user_id": user_id,
            "messages": history
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversation/{user_id}")
async def clear_conversation_history(user_id: str):
    """
    Clear the conversation history for a user.
    """
    try:
        logger.info(f"Received request to clear conversation history for user {user_id}")
        
        # Get the dialog manager from the browser agent
        dialog_manager = browser_agent.dialog_manager
        
        # Clear the conversation history
        success = dialog_manager.clear_conversation_history(user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Conversation history for user {user_id} not found")
        
        return {
            "user_id": user_id,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/{user_id}")
async def get_user_memory(user_id: str):
    """
    Get the memory for a user.
    """
    try:
        logger.info(f"Received request to get memory for user {user_id}")
        
        # Get the dialog manager from the browser agent
        dialog_manager = browser_agent.dialog_manager
        
        # Get the user memory
        memory = dialog_manager.get_user_memory(user_id)
        
        if memory is None:
            raise HTTPException(status_code=404, detail=f"Memory for user {user_id} not found")
        
        return {
            "user_id": user_id,
            "memory": memory
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/memory/{user_id}")
async def clear_user_memory(user_id: str):
    """
    Clear the memory for a user.
    """
    try:
        logger.info(f"Received request to clear memory for user {user_id}")
        
        # Get the dialog manager from the browser agent
        dialog_manager = browser_agent.dialog_manager
        
        # Clear the user memory
        success = dialog_manager.clear_user_memory(user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Memory for user {user_id} not found")
        
        return {
            "user_id": user_id,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing user memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time communication.
    """
    await websocket.accept()
    websocket_connections[user_id] = websocket
    
    try:
        while True:
            # Receive message from the client
            data = await websocket.receive_text()
            
            try:
                # Parse the message
                message_data = json.loads(data)
                message = message_data.get("message", "")
                
                # Process the message
                result = await browser_agent.process_message(user_id, message)
                
                # Send the response back to the client
                await websocket.send_json(result)
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                await websocket.send_json({
                    "error": str(e)
                })
    except WebSocketDisconnect:
        # Remove the connection when the client disconnects
        if user_id in websocket_connections:
            del websocket_connections[user_id]
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if user_id in websocket_connections:
            del websocket_connections[user_id]

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

@app.on_event("shutdown")
def shutdown_event():
    """
    Clean up resources when the application shuts down.
    """
    browser_agent.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.level3_api:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True
    )
