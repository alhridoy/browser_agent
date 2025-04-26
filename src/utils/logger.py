import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "browser_agent", level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: The name of the logger.
        level: The logging level.
        
    Returns:
        A configured logger.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    os.makedirs("logs", exist_ok=True)
    file_handler = RotatingFileHandler(
        "logs/browser_agent.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
