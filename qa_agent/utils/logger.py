"""
Logger utility module for the Autonomous QA Agent.
Provides centralized logging configuration for the entire application.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_file: str = None, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with console and optional file output.
    
    Args:
        name: Name of the logger (typically __name__ of the calling module)
        log_file: Optional path to log file. If None, logs only to console
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with default configuration.
    
    Args:
        name: Name of the logger (typically __name__ of the calling module)
    
    Returns:
        Logger instance
    """
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"qa_agent_{datetime.now().strftime('%Y%m%d')}.log"
    
    return setup_logger(name, str(log_file))
